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
import androidx.core.app.NotificationManagerCompat
import com.akn.mathlock.databinding.ActivitySettingsBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var prefManager: PreferenceManager
    private var permissionCheckPending = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)

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
            val hasJson = qm.sync()
            runOnUiThread {
                if (hasJson) {
                    binding.tvMathModeInfo.text = "🤖 AI mod aktif — VPS'ten ${qm.totalCount()} soru (v${qm.getVersion()}), ${qm.solvedCount()} çözüldü"
                } else {
                    binding.tvMathModeInfo.text = "⚡ Klasik mod — rastgele sorular (AI soru seti bulunamadı)"
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
        // 1. Kullanım Erişimi — en önemli izin
        if (!hasUsageStatsPermission()) {
            permissionCheckPending = true
            AlertDialog.Builder(this)
                .setTitle("📱 Kullanım Erişimi")
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

        // 2. Üzerine çizim izni
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            permissionCheckPending = true
            AlertDialog.Builder(this)
                .setTitle("🪟 Ekran Üstü Gösterim")
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

        // 3. Bildirim izni (API 33+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != android.content.pm.PackageManager.PERMISSION_GRANTED
            ) {
                requestPermissions(
                    arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),
                    REQUEST_NOTIFICATION
                )
                return
            }
        }

        if (!NotificationManagerCompat.from(this).areNotificationsEnabled()) {
            permissionCheckPending = true
            AlertDialog.Builder(this)
                .setTitle("🔔 Bildirim İzni")
                .setMessage("Geri sayım ve koruma bildirimi için MathLock bildirimlerinin açık olması gerekli.")
                .setPositiveButton("Ayarlara Git") { _, _ ->
                    startActivity(Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
                        putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
                    })
                }
                .setNegativeButton("İptal") { _, _ -> permissionCheckPending = false }
                .setCancelable(false)
                .show()
            return
        }

        // 4. Batarya optimizasyonu (tüm cihazlar)
        if (!isIgnoringBatteryOptimizations()) {
            permissionCheckPending = true
            AlertDialog.Builder(this)
                .setTitle("🔋 Batarya Optimizasyonu")
                .setMessage(
                    "Koruma servisinin arka planda kesintisiz çalışması için " +
                    "batarya optimizasyonundan muaf tutulması gerekli.\n\n" +
                    "Açılacak diyalogda \"İzin ver\" seçin."
                )
                .setPositiveButton("Devam") { _, _ ->
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
                .setNegativeButton("Atla") { _, _ ->
                    permissionCheckPending = false
                    startLockService()
                }
                .setCancelable(false)
                .show()
            return
        }

        startLockService()
    }

    private fun startLockService() {
        AppLockService.start(this)
        prefManager.isServiceEnabled = true
        updateProtectionStatus()
        Toast.makeText(this, "🛡️ Koruma etkinleştirildi!", Toast.LENGTH_SHORT).show()
        // Xiaomi cihazlarda ek adımlar
        if (isXiaomiDevice()) {
            showXiaomiSetupWizard()
        }
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
            checkAndRequestPermissions()
        }
    }

    companion object {
        private const val REQUEST_NOTIFICATION = 3002
    }
}
