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
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.databinding.ActivitySettingsBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var prefManager: PreferenceManager
    private lateinit var accountManager: AccountManager
    private var permissionCheckPending = false

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
        // İzin ayarlarından döndüyse otomatik devam et
        if (permissionCheckPending) {
            permissionCheckPending = false
            checkAndRequestPermissions()
        }
    }

    private fun updateAiModeInfo() {
        val qm = QuestionManager(this)
        Thread {
            val token = accountManager.getOrRegister()
            val hasJson = qm.sync(token)
            val email = accountManager.getEmail()
            runOnUiThread {
                val accountLine = if (!email.isNullOrBlank()) {
                    "\n📧 Hesap: $email"
                } else {
                    "\n👤 Hesap yok — kredi almak için kayıt gerekli"
                }
                if (hasJson) {
                    binding.tvMathModeInfo.text = "🤖 AI mod aktif — ${qm.totalCount()} soru, ${qm.accessibleBatches().size} set$accountLine"
                } else {
                    binding.tvMathModeInfo.text = "⚡ Klasik mod — rastgele sorular$accountLine"
                }
                // Email kayıt için tıkla
                binding.tvMathModeInfo.setOnClickListener {
                    showEmailRegistrationDialog()
                }
            }
        }.start()
    }

    private fun showEmailRegistrationDialog() {
        val currentEmail = accountManager.getEmail()
        if (!currentEmail.isNullOrBlank()) {
            AlertDialog.Builder(this)
                .setTitle("📧 Hesap")
                .setMessage("Kayıtlı email: $currentEmail\n\nEmail adresinizi değiştirmek ister misiniz?")
                .setPositiveButton("Değiştir") { _, _ -> showEmailInputDialog() }
                .setNegativeButton("Tamam", null)
                .show()
        } else {
            AlertDialog.Builder(this)
                .setTitle("👤 Hesap Oluştur")
                .setMessage(
                    "Kredi satın alarak daha fazla soru açmak için email adresinizle kayıt olun.\n\n" +
                    "İlk 50 soru tamamen ücretsiz — kayıt gerekmez."
                )
                .setPositiveButton("Email ile Kayıt Ol") { _, _ -> showEmailInputDialog() }
                .setNegativeButton("Şimdi Değil", null)
                .show()
        }
    }

    private fun showEmailInputDialog() {
        val input = android.widget.EditText(this).apply {
            hint = "ornek@email.com"
            inputType = android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS or
                        android.text.InputType.TYPE_CLASS_TEXT
            setPadding(48, 32, 48, 32)
            accountManager.getEmail()?.let { setText(it) }
        }

        AlertDialog.Builder(this)
            .setTitle("Email Adresiniz")
            .setView(input)
            .setPositiveButton("Kaydet") { _, _ ->
                val email = input.text.toString().trim()
                if (email.isBlank()) {
                    Toast.makeText(this, "Email adresi boş olamaz", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                registerEmailInBackground(email)
            }
            .setNegativeButton("İptal", null)
            .show()
    }

    private fun registerEmailInBackground(email: String) {
        Toast.makeText(this, "Kaydediliyor...", Toast.LENGTH_SHORT).show()
        Thread {
            val result = accountManager.registerEmail(email)
            runOnUiThread {
                when (result) {
                    is AccountManager.RegisterEmailResult.Success -> {
                        Toast.makeText(this, "✅ Email kaydedildi: $email", Toast.LENGTH_LONG).show()
                        updateAiModeInfo()
                    }
                    is AccountManager.RegisterEmailResult.Error -> {
                        Toast.makeText(this, "❌ ${result.message}", Toast.LENGTH_LONG).show()
                    }
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

    private fun loadSettings() {
        updateAiModeInfo()

        // Geçiş skoru ayarı
        val passScore = prefManager.passScore.toFloat()

        binding.sliderPassScore.value = passScore.coerceAtMost(10f)
        binding.tvPassScore.text = getString(R.string.settings_pass_score, passScore.toInt())

        // Sayı tahmin ayarları
        val guessMax = prefManager.guessMaxNumber.toFloat()
        binding.sliderGuessMax.value = guessMax.coerceIn(10f, 500f)
        binding.tvGuessMax.text = getString(R.string.settings_guess_max, guessMax.toInt())

        // Kilit açma süresi
        val duration = prefManager.unlockDurationMinutes.toFloat().coerceIn(0f, 60f)
        binding.sliderUnlockDuration.value = duration
        binding.tvUnlockDuration.text = formatDurationLabel(duration.toInt())
        if (prefManager.unlockExpiredAction == PreferenceManager.EXPIRE_ACTION_CLOSE) {
            binding.rbCloseApp.isChecked = true
        } else {
            binding.rbRelock.isChecked = true
        }

        updateProtectionStatus()
        updateLockedAppCount()
    }

    private fun setupListeners() {
        binding.btnBack.setOnClickListener { finish() }

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

        // Sayı tahmin üst sınır slider
        binding.sliderGuessMax.addOnChangeListener { _, value, _ ->
            val max = value.toInt()
            prefManager.guessMaxNumber = max
            binding.tvGuessMax.text = getString(R.string.settings_guess_max, max)
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
        AlertDialog.Builder(this)
            .setTitle("📋 Xiaomi Kurulum (1/3)")
            .setMessage(
                "Otomatik Başlatma\n\n" +
                "MathLock'un cihaz yeniden başlatıldığında otomatik açılması için gerekli.\n\n" +
                "Açılacak sayfada MathLock'u bulup izni açın."
            )
            .setPositiveButton("Ayarlara Git") { _, _ ->
                openMiuiAutostart()
            }
            .setNeutralButton("Sonraki ▸") { _, _ -> showXiaomiStep2() }
            .setCancelable(false)
            .show()
    }

    private fun showXiaomiStep2() {
        AlertDialog.Builder(this)
            .setTitle("📋 Xiaomi Kurulum (2/3)")
            .setMessage(
                "Arka Planda Açılır Pencere\n\n" +
                "Kilitli uygulama açıldığında soru ekranının görünmesi için bu izin şart.\n\n" +
                "Bu en kritik adımdır — açılacak sayfada \"Arka planda açılır pencere göster\" iznini etkinleştirin."
            )
            .setPositiveButton("Ayarlara Git") { _, _ ->
                openMiuiPermissionEditor()
            }
            .setNeutralButton("Sonraki ▸") { _, _ -> showXiaomiStep3() }
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
        return if (minutes == 0) getString(R.string.settings_unlock_duration_unlimited)
        else getString(R.string.settings_unlock_duration_minutes, minutes)
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
