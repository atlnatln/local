package com.akn.mathlock.service

import android.app.ActivityManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.app.usage.UsageEvents
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.TextView
import android.util.Log
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

        fun start(context: Context) {
            if (isRunning) return  // Zaten çalışıyorsa tekrar başlatma
            val intent = Intent(context, AppLockService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
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

    // Son challenge başlatılan paket ve zaman — flood-launch önleme
    private var lastChallengePackage: String? = null
    private var lastChallengeTime: Long = 0
    private val CHALLENGE_MIN_INTERVAL = 3_000L // ms

    // Ebeveyn bypass: uygulama arka plana geçince bypass temizlenir
    private var previousForegroundPackage: String? = null

    // UsageEvents son 5 saniyeye bakar — kullanıcı uygulamada uzun süre beklerse
    // event gelmez ve getForegroundPackageName() null döner. Bu değişken son bilinen
    // ön plan uygulamayı tutar; timer expire olduğunda check kaçırılmaz.
    private var lastKnownForegroundPackage: String? = null

    private var pollingActive = false
    private var showingCountdown = false

    private val checkRunnable = object : Runnable {
        override fun run() {
            if (!isRunning) return
            // Yeni bir event varsa güncelle; yoksa son bilinen paketi kullan.
            // Bu sayede kullanıcı uygulamada uzun süre kalırken de timer doğru çalışır.
            val detected = getForegroundPackageName()
            if (detected != null) lastKnownForegroundPackage = detected
            val foregroundPackage = lastKnownForegroundPackage
            checkAndExpireTimers()
            checkForegroundApp(foregroundPackage)
            updateTimerNotification()
            handler.postDelayed(this, CHECK_INTERVAL)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        prefManager = PreferenceManager(this)
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        createNotificationChannel()
        createAlertNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "onStartCommand: servis başlıyor (pollingActive=$pollingActive)")
        // Android 14 (API 34) zorunluluğu: startForeground tip parametresiyle çağrılmalı
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(NOTIFICATION_ID, buildNotification(),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, buildNotification())
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
        lastKnownForegroundPackage = null
        previousForegroundPackage = null
        handler.removeCallbacks(checkRunnable)
        hideTimerOverlay()
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
                    // Uygulamayı kapat ve ana ekrana gönder.
                    // pendingForceClose KULLANILMIYOR — challenge'ın açılmasını engeller.
                    forceUserHome()
                    killApp(pkg)
                    handler.postDelayed({ forceUserHome() }, 500)
                    Log.d(TAG, "Force-close: HOME gönderildi + süreç öldürüldü: $pkg")
                }
                // Her iki modda da: paketi normal servis döngüsü challenge başlatır.
            }
        }
    }

    private fun checkForegroundApp(foregroundPackage: String?) {
        val currentPackage = foregroundPackage ?: return
        Log.v(TAG, "Ön plan: $currentPackage")

        // Ebeveyn bypass temizle: önceki paket parent-bypassed iken başka uygulamaya geçildi
        val prev = previousForegroundPackage
        if (prev != null && prev != currentPackage && LockStateManager.isParentBypassed(prev)) {
            LockStateManager.clearParentBypass(prev)
            Log.d(TAG, "Ebeveyn bypass temizlendi (arka plana geçti): $prev")
        }
        previousForegroundPackage = currentPackage

        // Kendi uygulamamızı kilitleme
        if (currentPackage == packageName) {
            lastChallengePackage = null
            return
        }

        // Ebeveyn yeniden açtıysa (notifyUnlocked çağrıldıysa) — geçir.
        if (LockStateManager.isUnlocked(currentPackage)) {
            lastChallengePackage = null
            return
        }

        // Kilitli uygulama mı kontrol et
        if (!prefManager.isAppLocked(currentPackage)) return

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

    private fun killApp(pkg: String) {
        try {
            val am = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            am.killBackgroundProcesses(pkg)
            Log.d(TAG, "killBackgroundProcesses: $pkg")
        } catch (e: Exception) {
            Log.w(TAG, "killBackgroundProcesses başarısız: ${e.message}")
        }
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

    private fun launchChallenge(lockedPackage: String) {
        // Önce ana ekrana gönder — kilitli uygulamayı ön plandan düşür.
        // Bu, MIUI/Samsung gibi özel ROM'larda en güvenilir yöntemdir.
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)

        val timerExpired = LockStateManager.isTimerExpired(lockedPackage)

        // Hemen ardından challenge ekranını aç
        val intent = Intent(this, ChallengePickerActivity::class.java).apply {
            addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK or
                Intent.FLAG_ACTIVITY_CLEAR_TOP
            )
            putExtra("locked_package", lockedPackage)
            putExtra("timer_expired", timerExpired)
        }
        try {
            startActivity(intent)
            Log.d(TAG, "Challenge activity başlatıldı: $lockedPackage (timerExpired=$timerExpired)")
        } catch (e: Exception) {
            Log.w(TAG, "startActivity başarısız (MIUI kısıtlaması?): ${e.message}")
            showChallengeNotification(lockedPackage)
        }
    }

    private fun showChallengeNotification(lockedPackage: String) {
        val intent = Intent(this, ChallengePickerActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            putExtra("locked_package", lockedPackage)
        }
        val pendingIntent = PendingIntent.getActivity(
            this, lockedPackage.hashCode(), intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val nm = getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(this, ALERT_CHANNEL_ID)
            .setContentTitle("🔒 Uygulama Kilitli")
            .setContentText("İçeri girmek için buraya dokun ve görevi tamamla")
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
}
