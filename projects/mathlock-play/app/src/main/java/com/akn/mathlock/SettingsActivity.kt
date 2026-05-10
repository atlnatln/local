package com.akn.mathlock

import android.app.AppOpsManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.os.Process
import android.provider.Settings
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.akn.mathlock.databinding.ActivitySettingsBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager

class SettingsActivity : BaseActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var prefManager: PreferenceManager
    private lateinit var accountManager: AccountManager
    private var permissionCheckPending = false
    // Xiaomi wizard: hangi adımdan dönüyoruz (0 = yok, 1 = autostart'tan, 2 = perm editor'dan, 3 = app settings'ten)
    private var xiaomiStepPending = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)
        accountManager = AccountManager(this)

        loadSettings()
        setupListeners()
    }

    override fun onResume() {
        super.onResume()
        updateProtectionStatus()
        updateLockedAppCount()
        updateAiModeInfo()
        updateActiveChildInfo()

        // Xiaomi wizard adımından döndüyse önce onu tamamla (diğer kontrollere geçme)
        if (xiaomiStepPending > 0) {
            val step = xiaomiStepPending
            xiaomiStepPending = 0
            when (step) {
                1 -> showXiaomiStep2()
                2 -> showXiaomiStep3()
                // 3 = son adım, otomatik devam gerekmiyor
            }
            return
        }

        // İzin ayarlarından döndüyse otomatik devam et
        if (permissionCheckPending) {
            permissionCheckPending = false
            checkAndRequestPermissions()
        }
    }

    private fun updateAiModeInfo() {
        val qm = QuestionManager(this)
        Thread {
            val authToken = accountManager.getOrRegister()
            val hasJson = qm.sync(authToken)
            val email = accountManager.getEmail()
            val credits = accountManager.getCachedCredits()
            val childName = prefManager.activeChildName ?: "Çocuk"
            runOnUiThread {
                // Hesap durumu (ayrı kartta) — tıklanınca AccountActivity'ye git
                if (!email.isNullOrBlank()) {
                    binding.tvAccountStatus.text = "📧 $email  •  💰 $credits kredi"
                    binding.btnRegisterEmail.text = "Hesabım →"
                } else {
                    binding.tvAccountStatus.text = "Kayıtlı hesap yok"
                    binding.btnRegisterEmail.text = "📧 Hesap Oluştur / Kayıt Ol"
                }
                binding.btnRegisterEmail.setOnClickListener {
                    startActivity(android.content.Intent(this, AccountActivity::class.java))
                }
                // Soru modu bilgisi — çocuğa özel
                if (hasJson) {
                    val total = qm.totalCount()
                    val solved = qm.solvedCount()
                    val sets = qm.accessibleBatches().size
                    binding.tvMathModeInfo.text = "👤 $childName — $total soru ($solved çözüldü), $sets set"
                } else {
                    binding.tvMathModeInfo.text = "⚡ Klasik mod — rastgele sorular"
                }
            }
        }.start()
    }

    private fun updateProtectionStatus() {
        val isEnabled = prefManager.isServiceEnabled
        if (isEnabled) {
            binding.tvProtectionStatus.text = "🟢 Koruma aktif"
            binding.tvProtectionStatus.setTextColor(getColor(R.color.correct_green))
            binding.btnToggleService.text = "Korumayı Kapat"
        } else {
            binding.tvProtectionStatus.text = "🔴 Koruma kapalı"
            binding.tvProtectionStatus.setTextColor(getColor(R.color.wrong_red))
            binding.btnToggleService.text = "Korumayı Aç"
        }
    }

    private fun updateLockedAppCount() {
        val count = prefManager.getLockedApps().size
        binding.tvLockedAppCount.text = "$count uygulama"
    }

    private fun updateActiveChildInfo() {
        val periodLabels = mapOf(
            "okul_oncesi" to "Okul Öncesi",
            "sinif_1" to "1. Sınıf",
            "sinif_2" to "2. Sınıf",
            "sinif_3" to "3. Sınıf",
            "sinif_4" to "4. Sınıf"
        )
        val childName = prefManager.activeChildName ?: "Çocuk"
        val period = prefManager.activeEducationPeriod
        val label = periodLabels[period] ?: period
        binding.tvActiveChild.text = "👤 $childName  •  📚 $label"
    }

    private fun loadSettings() {
        updateAiModeInfo()

        // Geçiş skoru ayarı
        val passScore = prefManager.passScore.toFloat()

        binding.sliderPassScore.value = passScore.coerceAtMost(10f)
        binding.tvPassScore.text = getString(R.string.settings_pass_score, passScore.toInt())

        // Sayı Yolculuğu seviye sayısı
        val levelsToUnlock = prefManager.levelsToUnlock.toFloat()
        binding.sliderLevelsToUnlock.value = levelsToUnlock.coerceAtMost(12f)
        binding.tvLevelsToUnlock.text = getString(R.string.settings_levels_to_unlock, levelsToUnlock.toInt())

        // Sayı Hafızası ayarları
        val memoryPairs = prefManager.memoryGamePairCount.toFloat()
        binding.sliderMemoryPairs.value = memoryPairs.coerceIn(4f, 30f)
        binding.tvMemoryPairs.text = getString(R.string.settings_memory_pairs, memoryPairs.toInt())

        val memoryPreview = prefManager.memoryGamePreviewSeconds.toFloat()
        binding.sliderMemoryPreview.value = memoryPreview.coerceIn(0f, 10f)
        binding.tvMemoryPreview.text = getString(R.string.settings_memory_preview, memoryPreview.toInt())

        val memoryRounds = prefManager.memoryGameRequiredRounds.toFloat()
        binding.sliderMemoryRounds.value = memoryRounds.coerceIn(1f, 10f)
        binding.tvMemoryRounds.text = getString(R.string.settings_memory_rounds, memoryRounds.toInt())

        // Sayı tahmin ayarları
        val guessMax = prefManager.guessMaxNumber.toFloat()
        binding.sliderGuessMax.value = guessMax.coerceIn(10f, 500f)
        binding.tvGuessMax.text = getString(R.string.settings_guess_max, guessMax.toInt())

        // Sayı Bul tur sayısı
        val guessRounds = prefManager.guessRequiredRounds.toFloat()
        binding.sliderGuessRounds.value = guessRounds.coerceIn(1f, 10f)
        binding.tvGuessRounds.text = getString(R.string.settings_guess_rounds, guessRounds.toInt())

        // Kilit açma süresi (sınırsız kaldırıldı, minimum 1 dk)
        val duration = prefManager.unlockDurationMinutes.toFloat().coerceIn(1f, 60f)
        binding.sliderUnlockDuration.value = duration
        binding.tvUnlockDuration.text = formatDurationLabel(duration.toInt())
        if (prefManager.unlockExpiredAction == PreferenceManager.EXPIRE_ACTION_CLOSE) {
            binding.rbCloseApp.isChecked = true
        } else {
            binding.rbRelock.isChecked = true
        }

        updateProtectionStatus()
        updateLockedAppCount()
        updateActiveChildInfo()
    }

    private fun setupListeners() {
        binding.btnBack.setOnClickListener { finish() }

        // Çocuk Profilleri kartı
        binding.cardChildProfiles.setOnClickListener {
            startActivity(Intent(this, ChildProfilesActivity::class.java))
        }

        // Performans Raporu kartı
        binding.cardPerformanceReport.setOnClickListener {
            val childName = prefManager.activeChildName
            if (childName.isNullOrEmpty()) {
                Toast.makeText(this, "Önce çocuk profili oluşturun", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val intent = Intent(this, PerformanceReportActivity::class.java)
            intent.putExtra("child_name", childName)
            startActivity(intent)
        }

        // Korumayı Aç/Kapat
        binding.btnToggleService.setOnClickListener {
            if (prefManager.isServiceEnabled) {
                AppLockService.stop(this)
                prefManager.isServiceEnabled = false
                updateProtectionStatus()
                Toast.makeText(this, "Koruma kapatıldı", Toast.LENGTH_SHORT).show()
            } else {
                checkAndRequestPermissions()
            }
        }

        // Kilitli Uygulamalar
        binding.cardSelectApps.setOnClickListener {
            startActivity(Intent(this, AppSelectionActivity::class.java))
        }

        // Geçiş skoru slider
        binding.sliderPassScore.addOnChangeListener { _, value, _ ->
            val score = value.toInt()
            prefManager.passScore = score
            binding.tvPassScore.text = getString(R.string.settings_pass_score, score)
        }

        // Sayı Yolculuğu seviye sayısı slider
        binding.sliderLevelsToUnlock.addOnChangeListener { _, value, _ ->
            val levels = value.toInt()
            prefManager.levelsToUnlock = levels
            binding.tvLevelsToUnlock.text = getString(R.string.settings_levels_to_unlock, levels)
        }

        // Sayı tahmin üst sınır slider
        binding.sliderGuessMax.addOnChangeListener { _, value, _ ->
            val max = value.toInt()
            prefManager.guessMaxNumber = max
            binding.tvGuessMax.text = getString(R.string.settings_guess_max, max)
        }

        // Sayı Bul tur sayısı slider
        binding.sliderGuessRounds.addOnChangeListener { _, value, _ ->
            val rounds = value.toInt()
            prefManager.guessRequiredRounds = rounds
            binding.tvGuessRounds.text = getString(R.string.settings_guess_rounds, rounds)
        }

        // Kilit açma süresi slider
        binding.sliderUnlockDuration.addOnChangeListener { _, value, _ ->
            val minutes = value.toInt()
            prefManager.unlockDurationMinutes = minutes
            binding.tvUnlockDuration.text = formatDurationLabel(minutes)
        }

        // Süre dolduğunda davranış
        binding.rgExpiredAction.setOnCheckedChangeListener { _, checkedId ->
            prefManager.unlockExpiredAction = when (checkedId) {
                R.id.rbCloseApp -> PreferenceManager.EXPIRE_ACTION_CLOSE
                else -> PreferenceManager.EXPIRE_ACTION_RELOCK
            }
        }

        // Test butonları
        binding.btnTestMath.setOnClickListener {
            val intent = Intent(this, MathChallengeActivity::class.java).apply {
                putExtra("test_mode", true)
            }
            startActivity(intent)
        }

        binding.btnTestGuess.setOnClickListener {
            val intent = Intent(this, NumberGuessActivity::class.java).apply {
                putExtra("test_mode", true)
            }
            startActivity(intent)
        }

        binding.btnTestPuzzle.setOnClickListener {
            val intent = Intent(this, SayiYolculuguActivity::class.java).apply {
                putExtra("test_mode", true)
            }
            startActivity(intent)
        }

        binding.btnTestMemory.setOnClickListener {
            val intent = Intent(this, MemoryGameActivity::class.java).apply {
                putExtra("test_mode", true)
            }
            startActivity(intent)
        }

        // Oyun görünürlük toggleları
        binding.switchMath.isChecked = prefManager.isMathEnabled
        binding.switchMath.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isMathEnabled = isChecked
        }

        binding.switchGuess.isChecked = prefManager.isGuessEnabled
        binding.switchGuess.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isGuessEnabled = isChecked
        }

        binding.switchPuzzle.isChecked = prefManager.isPuzzleEnabled
        binding.switchPuzzle.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isPuzzleEnabled = isChecked
        }

        binding.switchMemory.isChecked = prefManager.isMemoryGameEnabled
        binding.switchMemory.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isMemoryGameEnabled = isChecked
        }

        // Sayı Hafızası slider'ları
        binding.sliderMemoryPairs.addOnChangeListener { _, value, _ ->
            val count = value.toInt()
            prefManager.memoryGamePairCount = count
            binding.tvMemoryPairs.text = getString(R.string.settings_memory_pairs, count)
        }

        binding.sliderMemoryPreview.addOnChangeListener { _, value, _ ->
            val seconds = value.toInt()
            prefManager.memoryGamePreviewSeconds = seconds
            binding.tvMemoryPreview.text = getString(R.string.settings_memory_preview, seconds)
        }

        binding.sliderMemoryRounds.addOnChangeListener { _, value, _ ->
            val rounds = value.toInt()
            prefManager.memoryGameRequiredRounds = rounds
            binding.tvMemoryRounds.text = getString(R.string.settings_memory_rounds, rounds)
        }

    }

    private fun checkAndRequestPermissions() {
        // ── Zorunlu izin 1: Kullanım Erişimi ──
        if (!hasUsageStatsPermission()) {
            permissionCheckPending = true
            AlertDialog.Builder(this)
                .setTitle("📱 Kullanım Erişimi (1/2)")
                .setMessage(
                    "MathLock'un hangi uygulamanın açık olduğunu görebilmesi için bu izin zorunludur.\n\n" +
                    "Bu izin yalnızca ön plandaki uygulama adını okur — " +
                    "kişisel verilerinize erişmez.\n\n" +
                    "⚠️ Sonraki ekranda Android kırmızı bir uyarı gösterecek. " +
                    "Bu tüm uygulamalar için gösterilen standart bir uyarıdır. " +
                    "Onay kutusunu işaretleyip \"Tamam\" demeniz yeterli."
                )
                .setPositiveButton("Devam") { _, _ ->
                    startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
                }
                .setNegativeButton("İptal") { _, _ -> permissionCheckPending = false }
                .setCancelable(false)
                .show()
            return
        }

        // ── Zorunlu izin 2: Üzerine çizim ──
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            permissionCheckPending = true
            AlertDialog.Builder(this)
                .setTitle("🪟 Ekran Üstü Gösterim (2/2)")
                .setMessage(
                    "Kilitli uygulama açıldığında soru ekranının görünmesi için bu izin gereklidir.\n\n" +
                    "Açılacak sayfada MathLock'u bulup izni etkinleştirin."
                )
                .setPositiveButton("Ayarlara Git") { _, _ ->
                    startActivity(Intent(
                        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:$packageName")
                    ))
                }
                .setNegativeButton("İptal") { _, _ -> permissionCheckPending = false }
                .setCancelable(false)
                .show()
            return
        }

        // Zorunlu izinler tamam — servisi başlat, opsiyonelleri sonra sor
        startLockService()
    }

    private fun startLockService() {
        permissionCheckPending = false
        if (!AppLockService.isRunning) {
            AppLockService.start(this)
        }
        prefManager.isServiceEnabled = true
        updateProtectionStatus()
        Toast.makeText(this, "🛡️ Koruma etkinleştirildi!", Toast.LENGTH_SHORT).show()

        // Opsiyonel izinler — servis zaten çalışıyor, atlanabilir
        showOptionalSetup()
    }

    private fun showOptionalSetup() {
        // Xiaomi cihazlarda önce MIUI-specific adımlar
        if (isXiaomiDevice() && !prefManager.prefs.getBoolean("xiaomi_setup_done", false)) {
            showXiaomiSetupWizard()
            return
        }
        showOptionalNotificationPermission()
    }

    private fun showOptionalNotificationPermission() {
        if (prefManager.prefs.getBoolean("notification_prompted", false)) {
            showOptionalBatteryPermission()
            return
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != android.content.pm.PackageManager.PERMISSION_GRANTED
        ) {
            prefManager.prefs.edit().putBoolean("notification_prompted", true).apply()
            requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), REQUEST_NOTIFICATION)
            return
        }
        showOptionalBatteryPermission()
    }

    private fun showOptionalBatteryPermission() {
        if (prefManager.prefs.getBoolean("battery_prompted", false)) return
        if (isIgnoringBatteryOptimizations()) return

        prefManager.prefs.edit().putBoolean("battery_prompted", true).apply()
        AlertDialog.Builder(this)
            .setTitle("🔋 Batarya Optimizasyonu (Önerilen)")
            .setMessage(
                "Korumanın arka planda kesintisiz çalışması için önerilir.\n\n" +
                "Bu adımı atlayabilirsiniz — koruma yine de çalışacak."
            )
            .setPositiveButton("İzin Ver") { _, _ ->
                try {
                    @Suppress("BatteryLife")
                    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
                        data = Uri.parse("package:$packageName")
                    }
                    startActivity(intent)
                } catch (_: Exception) {
                    startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
                }
            }
            .setNegativeButton("Atla", null)
            .setCancelable(true)
            .show()
    }

    // ─── Xiaomi / MIUI Adım Adım Kurulum ───

    private fun isXiaomiDevice(): Boolean {
        val manufacturer = Build.MANUFACTURER.lowercase()
        return manufacturer.contains("xiaomi") || manufacturer.contains("redmi") || manufacturer.contains("poco")
    }

    private fun showXiaomiSetupWizard() {
        if (prefManager.prefs.getBoolean("xiaomi_setup_done", false)) return
        showXiaomiStep1()
    }

    private fun showXiaomiStep1() {
        // Bu adım daha önce yapıldıysa atla
        if (prefManager.prefs.getBoolean("xiaomi_step1_done", false)) {
            showXiaomiStep2()
            return
        }
        AlertDialog.Builder(this)
            .setTitle("📋 Xiaomi Kurulum (1/3)")
            .setMessage(
                "Otomatik Başlatma\n\n" +
                "MathLock'un cihaz yeniden başlatıldığında otomatik açılması için gerekli.\n\n" +
                "Açılacak sayfada MathLock'u bulup izni açın."
            )
            .setPositiveButton("Ayarlara Git") { _, _ ->
                prefManager.prefs.edit().putBoolean("xiaomi_step1_done", true).apply()
                xiaomiStepPending = 1
                openMiuiAutostart()
            }
            .setNeutralButton("Sonraki ▸") { _, _ ->
                prefManager.prefs.edit().putBoolean("xiaomi_step1_done", true).apply()
                showXiaomiStep2()
            }
            .setCancelable(false)
            .show()
    }

    private fun showXiaomiStep2() {
        // Bu adım daha önce yapıldıysa atla
        if (prefManager.prefs.getBoolean("xiaomi_step2_done", false)) {
            showXiaomiStep3()
            return
        }
        AlertDialog.Builder(this)
            .setTitle("📋 Xiaomi Kurulum (2/3)")
            .setMessage(
                "Arka Planda Açılır Pencere\n\n" +
                "Kilitli uygulama açıldığında soru ekranının görünmesi için bu izin şart.\n\n" +
                "Bu en kritik adımdır — açılacak sayfada \"Arka planda açılır pencere göster\" iznini etkinleştirin."
            )
            .setPositiveButton("Ayarlara Git") { _, _ ->
                prefManager.prefs.edit().putBoolean("xiaomi_step2_done", true).apply()
                xiaomiStepPending = 2
                openMiuiPermissionEditor()
            }
            .setNeutralButton("Sonraki ▸") { _, _ ->
                prefManager.prefs.edit().putBoolean("xiaomi_step2_done", true).apply()
                showXiaomiStep3()
            }
            .setCancelable(false)
            .show()
    }

    private fun showXiaomiStep3() {
        prefManager.prefs.edit().putBoolean("xiaomi_setup_done", true).apply()
        prefManager.prefs.edit()
            .putBoolean("autostart_prompted", true)
            .putBoolean("miui_popup_prompted", true)
            .apply()
        AlertDialog.Builder(this)
            .setTitle("📋 Xiaomi Kurulum (3/3)")
            .setMessage(
                "Arka Planda Çalışma\n\n" +
                "Son olarak, uygulama ayarlarından şunu kontrol edin:\n\n" +
                "• Batarya tasarrufu → Kısıtlama yok\n" +
                "• Diğer izinler → Arka planda başlat → İzin ver\n\n" +
                "Bu adımları tamamladıktan sonra MathLock tam koruma sağlayacak."
            )
            .setPositiveButton("Uygulama Ayarlarına Git") { _, _ ->
                startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.parse("package:$packageName")
                })
            }
            .setNegativeButton("Tamamla") { _, _ ->
                Toast.makeText(this, "✅ Kurulum tamamlandı!", Toast.LENGTH_SHORT).show()
            }
            .setCancelable(false)
            .show()
    }

    private fun openMiuiAutostart() {
        try {
            val intent = Intent().apply {
                setClassName(
                    "com.miui.securitycenter",
                    "com.miui.permcenter.autostart.AutoStartManagementActivity"
                )
            }
            startActivity(intent)
        } catch (_: Exception) {
            startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = Uri.parse("package:$packageName")
            })
        }
    }

    private fun openMiuiPermissionEditor() {
        try {
            val intent = Intent("miui.intent.action.APP_PERM_EDITOR").apply {
                setClassName(
                    "com.miui.securitycenter",
                    "com.miui.permcenter.permissions.PermissionsEditorActivity"
                )
                putExtra("extra_pkgname", packageName)
            }
            startActivity(intent)
        } catch (_: Exception) {
            try {
                val intent = Intent("miui.intent.action.APP_PERM_EDITOR").apply {
                    setClassName(
                        "com.miui.securitycenter",
                        "com.miui.permcenter.permissions.AppPermissionsEditorActivity"
                    )
                    putExtra("extra_pkgname", packageName)
                }
                startActivity(intent)
            } catch (_: Exception) {
                startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.parse("package:$packageName")
                })
            }
        }
    }

    private fun isIgnoringBatteryOptimizations(): Boolean {
        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        return pm.isIgnoringBatteryOptimizations(packageName)
    }

    private fun formatDurationLabel(minutes: Int): String {
        return getString(R.string.settings_unlock_duration_minutes, minutes)
    }

    private fun hasUsageStatsPermission(): Boolean {
        val appOps = getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
        @Suppress("DEPRECATION")
        val mode = appOps.checkOpNoThrow(
            AppOpsManager.OPSTR_GET_USAGE_STATS,
            Process.myUid(),
            packageName
        )
        return mode == AppOpsManager.MODE_ALLOWED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_NOTIFICATION) {
            // Bildirim opsiyonel — sonucu ne olursa olsun bataryaya geç
            showOptionalBatteryPermission()
        }
    }

    companion object {
        private const val REQUEST_NOTIFICATION = 3002
    }
}
