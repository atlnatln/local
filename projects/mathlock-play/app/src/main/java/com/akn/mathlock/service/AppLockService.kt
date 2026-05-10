package com.akn.mathlock.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.app.usage.UsageEvents
import android.app.usage.UsageStatsManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.util.Log
import android.util.TypedValue
import androidx.core.app.NotificationCompat
import com.akn.mathlock.ChallengePickerActivity
import com.akn.mathlock.LockStateManager
import com.akn.mathlock.MainActivity
import com.akn.mathlock.R
import com.akn.mathlock.util.PreferenceManager

class AppLockService : Service() {

    companion object {
        private const val TAG = "AppLockService"
        private const val CHANNEL_ID = "mathlock_service_channel"
        private const val ALERT_CHANNEL_ID = "mathlock_alert_channel"
        private const val NOTIFICATION_ID = 1001
        private const val ALERT_NOTIFICATION_ID = 2000
        private const val CHECK_INTERVAL = 800L // ms

        @Volatile
        var isRunning = false
            private set

        // Engelleme overlay'ını dışarıdan kaldırmak için (ChallengePickerActivity kullanır)
        private var instance: AppLockService? = null

        fun removeBlockingOverlay() {
            instance?.hideBlockingOverlay()
        }

        fun start(context: Context) {
            if (isRunning) return  // Zaten çalışıyorsa tekrar başlatma
            try {
                val intent = Intent(context, AppLockService::class.java)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    context.startForegroundService(intent)
                } else {
                    context.startService(intent)
                }
            } catch (e: Exception) {
                // Android 12+: arka plandan foreground service başlatma kısıtlaması
                Log.e(TAG, "Servis başlatılamadı: ${e.message}")
            }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, AppLockService::class.java))
        }
    }

    private lateinit var prefManager: PreferenceManager
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var windowManager: WindowManager
    private var timerOverlayView: TextView? = null
    private var lastOverlayText: String? = null

    // Tam ekran engelleme overlay'ı — MIUI gibi ROM'lar Activity başlatamasa bile
    // kilitli uygulamayı kullanılamaz hale getirir.
    private var blockingOverlayView: View? = null
    private var blockingOverlayPackage: String? = null

    // Launcher paketlerini cache'le — polling her 800ms'de çağrılıyor
    private var launcherPackages: Set<String>? = null

    // Son challenge başlatılan paket ve zaman — flood-launch önleme
    private var lastChallengePackage: String? = null
    private var lastChallengeTime: Long = 0
    private val CHALLENGE_MIN_INTERVAL = 3_000L // ms

    // Challenge süreci aktif mi — overlay gösterildi, activity açılmayı bekliyor
    // Bu flag true iken aynı paket için launchChallenge tekrar tetiklenmez
    @Volatile
    private var challengeActive = false

    // Challenge başlatıldığında zaman damgası — stuck durumu tespit etmek için
    private var challengeActiveSince: Long = 0
    private val CHALLENGE_STUCK_TIMEOUT = 5_000L // ms — bu süre içinde activity gelmezse resetle

    // Ekran kapandığında ebeveyn bypass'larını temizleyen receiver
    private val screenOffReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == Intent.ACTION_SCREEN_OFF) {
                val cleared = LockStateManager.clearAllParentBypasses()
                if (cleared > 0) {
                    Log.d(TAG, "Ekran kapandı — tüm ebeveyn bypass'ları temizlendi ($cleared paket)")
                }
            }
        }
    }

    // Ekran açıldığında overlay aktifse challenge'ı yeniden tetikleyen receiver
    private val screenOnReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == Intent.ACTION_SCREEN_ON ||
                intent?.action == Intent.ACTION_USER_PRESENT) {
                val pkg = blockingOverlayPackage
                if (blockingOverlayView != null && pkg != null) {
                    Log.d(TAG, "Ekran açıldı — overlay aktif, challenge yeniden tetikleniyor: $pkg")
                    challengeActive = false
                    // Kısa gecikmeyle activity başlat (keyguard geçişini bekle)
                    handler.postDelayed({
                        reLaunchChallengeActivity(pkg)
                    }, 800)
                }
            }
        }
    }

    // UsageEvents son 5 saniyeye bakar — kullanıcı uygulamada uzun süre beklerse
    // event gelmez ve getForegroundPackageName() null döner. Bu değişken son bilinen
    // ön plan uygulamayı tutar; timer expire olduğunda check kaçırılmaz.
    @Volatile
    private var lastKnownForegroundPackage: String? = null

    private var pollingActive = false
    private var showingCountdown = false

    private val checkRunnable = object : Runnable {
        override fun run() {
            if (!isRunning) return
            // Yeni bir event varsa güncelle; yoksa son bilinen paketi kullan.
            // Bu sayede kullanıcı uygulamada uzun süre kalırken de timer doğru çalışır.
            val foregroundPackage = synchronized(this) {
                val detected = getForegroundPackageName()
                if (detected != null) lastKnownForegroundPackage = detected
                lastKnownForegroundPackage
            }
            checkAndExpireTimers()
            checkForegroundApp(foregroundPackage)
            updateTimerNotification()
            handler.postDelayed(this, CHECK_INTERVAL)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        instance = this
        prefManager = PreferenceManager(this)
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        createNotificationChannel()
        createAlertNotificationChannel()
        registerReceiver(screenOffReceiver, IntentFilter(Intent.ACTION_SCREEN_OFF))
        val screenOnFilter = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_ON)
            addAction(Intent.ACTION_USER_PRESENT)
        }
        registerReceiver(screenOnReceiver, screenOnFilter)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "onStartCommand: servis başlıyor (pollingActive=$pollingActive)")
        // Android 14 (API 34) zorunluluğu: startForeground tip parametresiyle çağrılmalı
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                startForeground(NOTIFICATION_ID, buildNotification(),
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
            } else {
                startForeground(NOTIFICATION_ID, buildNotification())
            }
        } catch (e: Exception) {
            // Android 12+: arka plandan foreground service başlatılamıyor olabilir
            Log.e(TAG, "startForeground başarısız: ${e.message}")
            stopSelf()
            return START_NOT_STICKY
        }
        isRunning = true
        // Polling zaten aktifse tekrar başlatma — duplicate runnable önleme
        if (!pollingActive) {
            pollingActive = true
            handler.removeCallbacks(checkRunnable)
            handler.post(checkRunnable)
            Log.d(TAG, "onStartCommand: polling başladı")
        }
        return START_STICKY
    }

    override fun onDestroy() {
        isRunning = false
        pollingActive = false
        showingCountdown = false
        challengeActive = false
        lastKnownForegroundPackage = null
        try { unregisterReceiver(screenOffReceiver) } catch (_: Exception) {}
        try { unregisterReceiver(screenOnReceiver) } catch (_: Exception) {}
        handler.removeCallbacks(checkRunnable)
        hideBlockingOverlay()
        hideTimerOverlay()
        instance = null
        super.onDestroy()
    }

    /**
     * Arka planda da tüm zamanlayıcıları kontrol eder.
     * Süresi dolan uygulamaları yeniden kilitler.
     * Eğer "kapat" modu seçilmişse ve uygulama ön plandaysa ana ekrana gönderir.
     */
    private fun checkAndExpireTimers() {
        val durationMinutes = prefManager.unlockDurationMinutes
        if (durationMinutes <= 0) return

        val durationMs = durationMinutes * 60_000L
        val now = System.currentTimeMillis()

        for ((pkg, unlockTime) in LockStateManager.getActiveUnlocks()) {
            val elapsed = now - unlockTime
            if (elapsed >= durationMs) {
                Log.d(TAG, "Timer doldu ($durationMinutes dk): $pkg")
                LockStateManager.forceRelock(pkg)
                LockStateManager.markTimerExpired(pkg)   // challenge ekranında banner gösterilecek
                lastChallengePackage = null

                if (prefManager.unlockExpiredAction == PreferenceManager.EXPIRE_ACTION_CLOSE) {
                    // Play sürümü: uygulamayı öldürmek yerine ana ekrana yönlendir
                    // Servis döngüsü zaten challenge başlatacak
                    forceUserHome()
                    handler.postDelayed({ forceUserHome() }, 500)
                    Log.d(TAG, "Timer doldu — HOME gönderildi: $pkg")
                }
                // Her iki modda da: paketi normal servis döngüsü challenge başlatır.
            }
        }
    }

    private fun checkForegroundApp(foregroundPackage: String?) {
        val currentPackage = foregroundPackage ?: return
        Log.v(TAG, "Ön plan: $currentPackage")

        // Süresi dolmuş ebeveyn bypass kontrolü AppLockService.checkDestroyedBypasses() tarafından yapılır

        // Kendi uygulamamızı kilitleme — challenge açıksa overlay'ı kaldır
        if (currentPackage == packageName) {
            lastChallengePackage = null
            challengeActive = false
            hideBlockingOverlay()
            return
        }

        // Ebeveyn yeniden açtıysa (notifyUnlocked çağrıldıysa) — geçir ve overlay'ı kaldır.
        if (LockStateManager.isUnlocked(currentPackage)) {
            lastChallengePackage = null
            hideBlockingOverlay()
            return
        }

        // Ön plandaki uygulama kilitli paket değilse overlay'ı kaldır
        // Ancak: launchChallenge() HOME'a gönderdiği için launcher ön plandaysa overlay'ı koru
        if (currentPackage != blockingOverlayPackage && blockingOverlayView != null) {
            if (!isLauncherApp(currentPackage)) {
                hideBlockingOverlay()
            }
        }

        // Kilitli uygulama mı kontrol et
        if (!prefManager.isAppLocked(currentPackage)) return

        // Challenge zaten aktifse (overlay gösterildi, activity bekleniyor) tekrar tetikleme
        // Ancak stuck durumu kontrolü: 5 saniyeden uzun süredir aktifse resetle
        if (challengeActive) {
            val nowMs = System.currentTimeMillis()
            if (challengeActiveSince > 0 &&
                nowMs - challengeActiveSince > CHALLENGE_STUCK_TIMEOUT) {
                Log.w(TAG, "Challenge $CHALLENGE_STUCK_TIMEOUT ms'den uzun süredir aktif — stuck durumu, resetleniyor")
                challengeActive = false
                challengeActiveSince = 0
                // Overlay varsa activity'yi yeniden başlat
                if (blockingOverlayView != null && blockingOverlayPackage != null) {
                    reLaunchChallengeActivity(blockingOverlayPackage!!)
                }
            }
            return
        }

        // Flood-launch önleme: aynı paket için minimum 3 saniye aralık
        val now = System.currentTimeMillis()
        if (currentPackage == lastChallengePackage &&
            now - lastChallengeTime < CHALLENGE_MIN_INTERVAL) {
            return
        }

        lastChallengePackage = currentPackage
        lastChallengeTime = now

        launchChallenge(currentPackage)
    }

    private fun forceUserHome() {
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
    }



    private fun getForegroundPackageName(): String? {
        val usageStatsManager = getSystemService(Context.USAGE_STATS_SERVICE) as? UsageStatsManager
            ?: return null

        val endTime = System.currentTimeMillis()
        val beginTime = endTime - 5000

        val usageEvents = usageStatsManager.queryEvents(beginTime, endTime)
        var lastPackage: String? = null

        val event = UsageEvents.Event()
        while (usageEvents.hasNextEvent()) {
            usageEvents.getNextEvent(event)
            // ACTIVITY_RESUMED (API 29+) ve eski MOVE_TO_FOREGROUND (API 21+) her ikisini de destekle
            if (event.eventType == UsageEvents.Event.ACTIVITY_RESUMED ||
                event.eventType == UsageEvents.Event.MOVE_TO_FOREGROUND) {
                lastPackage = event.packageName
            }
        }

        return lastPackage
    }

    /**
     * Overlay gösterilirken ChallengePickerActivity'yi yeniden başlatmaya çalışır.
     * Ekran açılışında veya stuck durumunda kullanılır.
     */
    private fun reLaunchChallengeActivity(lockedPackage: String) {
        val timerExpired = LockStateManager.isTimerExpired(lockedPackage)
        val intent = Intent(this, ChallengePickerActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            putExtra("locked_package", lockedPackage)
            putExtra("timer_expired", timerExpired)
        }
        try {
            startActivity(intent)
            Log.d(TAG, "Challenge activity yeniden başlatıldı: $lockedPackage")
        } catch (e: Exception) {
            Log.w(TAG, "Activity yeniden başlatılamadı, bildirim fallback: ${e.message}")
            // Fallback: tam ekran bildirim üzerinden aç
            showChallengeNotification(lockedPackage)
        }
    }

    private fun launchChallenge(lockedPackage: String) {
        challengeActive = true
        challengeActiveSince = System.currentTimeMillis()

        // 1) Ana ekrana gönder — kilitli uygulamayı ön plandan düşür
        forceUserHome()

        // 2) Overlay'ı hemen göster — kilitli uygulama görsel olarak engellenir
        handler.postDelayed({
            if (blockingOverlayView == null) {
                showBlockingOverlay(lockedPackage)
            }
        }, 100)

        // 3) 500ms sonra ChallengePickerActivity'yi otomatik aç (buton beklemeden)
        //    Overlay yarım saniye görünür, ardından activity ön plana gelir.
        //    Activity ön plana gelince checkForegroundApp overlay'ı kaldırır.
        handler.postDelayed({
            val timerExpired = LockStateManager.isTimerExpired(lockedPackage)
            val intent = Intent(this, ChallengePickerActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                putExtra("locked_package", lockedPackage)
                putExtra("timer_expired", timerExpired)
            }
            try {
                startActivity(intent)
                Log.d(TAG, "Challenge activity otomatik başlatıldı: $lockedPackage")
            } catch (e: Exception) {
                Log.w(TAG, "Activity başlatılamadı, overlay kalacak: ${e.message}")
                // Overlay zaten gösteriliyor, kullanıcı butona basabilir
            }
        }, 500)

        Log.d(TAG, "Challenge tetiklendi: $lockedPackage")
    }

    private fun showChallengeNotification(lockedPackage: String) {
        val timerExpired = LockStateManager.isTimerExpired(lockedPackage)
        val intent = Intent(this, ChallengePickerActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            putExtra("locked_package", lockedPackage)
            putExtra("timer_expired", timerExpired)
        }
        val pendingIntent = PendingIntent.getActivity(
            this, lockedPackage.hashCode(), intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val appName = try {
            val ai = packageManager.getApplicationInfo(lockedPackage, 0)
            packageManager.getApplicationLabel(ai).toString()
        } catch (_: Exception) { lockedPackage }
        val nm = getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(this, ALERT_CHANNEL_ID)
            .setContentTitle("🔒 $appName kilitli")
            .setContentText("Görevi tamamlamak için buraya dokun")
            .setSmallIcon(android.R.drawable.ic_lock_lock)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .setFullScreenIntent(pendingIntent, true)
            .build()
        nm?.notify(ALERT_NOTIFICATION_ID + lockedPackage.hashCode(), notification)
    }

    private fun createAlertNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                ALERT_CHANNEL_ID,
                "Uygulama Kilit Uyardı",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Kilitli uygulama açılmaya çalışıldığında görünür"
                setShowBadge(true)
                enableLights(true)
                enableVibration(true)
                lockscreenVisibility = android.app.Notification.VISIBILITY_PUBLIC
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notification_channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getString(R.string.notification_text)
                setShowBadge(false)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.notification_title))
            .setContentText(getString(R.string.notification_text))
            .setSmallIcon(android.R.drawable.ic_lock_lock)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setSilent(true)
            .setColor(getColor(R.color.notification_color))
            .build()
    }

    private fun updateForegroundNotification(notification: Notification) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    /**
     * Aktif zamanlayıcı varsa bildirimde geri sayım gösterir.
     * Tüm zamanlayıcılar bittiyse normal bildirime döner.
     */
    private fun updateTimerNotification() {
        val durationMinutes = prefManager.unlockDurationMinutes
        if (durationMinutes <= 0) {
            if (showingCountdown) {
                showingCountdown = false
                updateForegroundNotification(buildNotification())
            }
            hideTimerOverlay()
            return
        }

        val durationMs = durationMinutes * 60_000L
        val now = System.currentTimeMillis()
        var nearestEnd = Long.MAX_VALUE
        var nearestPkg: String? = null

        for ((pkg, unlockTime) in LockStateManager.getActiveUnlocks()) {
            val endTime = unlockTime + durationMs
            if (endTime > now && endTime < nearestEnd) {
                nearestEnd = endTime
                nearestPkg = pkg
            }
        }

        if (nearestPkg != null) {
            // Geri sayım bildirimini göster
            val remainingMs = nearestEnd - now
            val remainingMin = (remainingMs / 60_000).toInt()
            val remainingSec = ((remainingMs % 60_000) / 1000).toInt()

            val pendingIntent = PendingIntent.getActivity(
                this, 0,
                Intent(this, MainActivity::class.java),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            val appLabel = try {
                val ai = packageManager.getApplicationInfo(nearestPkg, 0)
                packageManager.getApplicationLabel(ai).toString()
            } catch (_: Exception) { nearestPkg }

            updateTimerOverlay(String.format("%02d:%02d", remainingMin, remainingSec))

            val notification = NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("⏳ $appLabel — %02d:%02d".format(remainingMin, remainingSec))
                .setContentText("Kalan süre dolunca uygulama kilitlenecek")
                .setSmallIcon(android.R.drawable.ic_lock_lock)
                .setContentIntent(pendingIntent)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setSilent(true)
                .setColor(getColor(R.color.notification_color))
                .setUsesChronometer(true)
                .setChronometerCountDown(true)
                .setWhen(nearestEnd)
                .setShowWhen(true)
                .build()

            updateForegroundNotification(notification)
            showingCountdown = true
        } else if (showingCountdown) {
            // Zamanlayıcı bitti, normal bildirime dön
            showingCountdown = false
            updateForegroundNotification(buildNotification())
            hideTimerOverlay()
        }
    }

    private fun updateTimerOverlay(text: String) {
        if (!android.provider.Settings.canDrawOverlays(this)) {
            hideTimerOverlay()
            return
        }

        if (timerOverlayView == null) {
            val view = TextView(this).apply {
                setBackgroundColor(android.graphics.Color.TRANSPARENT)
                setTextColor(android.graphics.Color.WHITE)
                textSize = 17f
                setTypeface(Typeface.DEFAULT_BOLD)
                setShadowLayer(6f, 1f, 1f, android.graphics.Color.BLACK)
                setPadding(4, 0, 4, 0)
            }

            val layoutParams = WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                else
                    WindowManager.LayoutParams.TYPE_PHONE,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            ).apply {
                gravity = Gravity.TOP or Gravity.END
                x = 24
                y = 120
            }

            try {
                windowManager.addView(view, layoutParams)
                timerOverlayView = view
            } catch (e: Exception) {
                Log.w(TAG, "Sayaç overlay eklenemedi: ${e.message}")
                timerOverlayView = null
                return
            }
        }

        if (lastOverlayText != text) {
            timerOverlayView?.text = text
            lastOverlayText = text
        }

        timerOverlayView?.visibility = View.VISIBLE
    }

    private fun hideTimerOverlay() {
        val view = timerOverlayView ?: return
        try {
            windowManager.removeView(view)
        } catch (_: Exception) {
        }
        timerOverlayView = null
        lastOverlayText = null
    }

    // ─── Tam Ekran Engelleme Overlay'ı ───

    private fun showBlockingOverlay(lockedPackage: String) {
        if (!android.provider.Settings.canDrawOverlays(this)) return
        if (blockingOverlayView != null) return // Zaten gösteriliyor

        blockingOverlayPackage = lockedPackage

        val appName = try {
            val ai = packageManager.getApplicationInfo(lockedPackage, 0)
            packageManager.getApplicationLabel(ai).toString()
        } catch (_: Exception) { lockedPackage }

        val dp = { value: Int ->
            TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, value.toFloat(),
                resources.displayMetrics
            ).toInt()
        }

        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.argb(240, 15, 15, 15))
            setPadding(dp(32), dp(48), dp(32), dp(48))
        }

        val lockIcon = TextView(this).apply {
            text = "🔒"
            textSize = 64f
            gravity = Gravity.CENTER
        }

        val title = TextView(this).apply {
            text = "Uygulama Kilitli"
            textSize = 24f
            setTextColor(Color.WHITE)
            setTypeface(Typeface.DEFAULT_BOLD)
            gravity = Gravity.CENTER
            setPadding(0, dp(16), 0, dp(8))
        }

        val subtitle = TextView(this).apply {
            text = "$appName kullanmak için görevi tamamla"
            textSize = 16f
            setTextColor(Color.argb(200, 255, 255, 255))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, dp(32))
        }

        val buttonBg = GradientDrawable().apply {
            setColor(Color.argb(255, 33, 150, 243))
            cornerRadius = dp(12).toFloat()
        }

        val challengeBtn = Button(this).apply {
            text = "📝 Görevi Tamamla"
            textSize = 18f
            setTextColor(Color.WHITE)
            background = buttonBg
            setPadding(dp(24), dp(14), dp(24), dp(14))
            isAllCaps = false
            setOnClickListener {
                val timerExpired = LockStateManager.isTimerExpired(lockedPackage)
                val intent = Intent(this@AppLockService, ChallengePickerActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                    putExtra("locked_package", lockedPackage)
                    putExtra("timer_expired", timerExpired)
                }
                try {
                    startActivity(intent)
                } catch (e: Exception) {
                    Log.w(TAG, "Overlay'dan challenge başlatılamadı: ${e.message}")
                    // Fallback: tam ekran bildirim üzerinden aç
                    showChallengeNotification(lockedPackage)
                }
            }
        }

        container.addView(lockIcon)
        container.addView(title)
        container.addView(subtitle)
        container.addView(challengeBtn, LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { gravity = Gravity.CENTER })

        val layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            else
                WindowManager.LayoutParams.TYPE_PHONE,
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.OPAQUE
        )

        try {
            windowManager.addView(container, layoutParams)
            blockingOverlayView = container
            Log.d(TAG, "Engelleme overlay'ı gösterildi: $lockedPackage")
        } catch (e: Exception) {
            Log.w(TAG, "Engelleme overlay eklenemedi: ${e.message}")
            blockingOverlayView = null
            blockingOverlayPackage = null
        }
    }

    /**
     * Verilen paketin bir launcher (ana ekran) uygulaması olup olmadığını kontrol eder.
     * launchChallenge() HOME'a gönderdiğinde, launcher'ı tanıyıp overlay'ı korumak için kullanılır.
     */
    private fun isLauncherApp(pkg: String): Boolean {
        if (launcherPackages == null) {
            val intent = Intent(Intent.ACTION_MAIN).apply {
                addCategory(Intent.CATEGORY_HOME)
            }
            launcherPackages = packageManager.queryIntentActivities(intent, 0)
                .mapNotNull { it.activityInfo?.packageName }
                .toSet()
        }
        return pkg in launcherPackages!!
    }

    private fun hideBlockingOverlay() {
        val view = blockingOverlayView ?: return
        try {
            windowManager.removeView(view)
            Log.d(TAG, "Engelleme overlay'ı kaldırıldı")
        } catch (_: Exception) {}
        blockingOverlayView = null
        blockingOverlayPackage = null
        challengeActive = false
        challengeActiveSince = 0
    }
}
