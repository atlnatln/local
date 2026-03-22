package com.akn.mathlock

import android.app.AppOpsManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
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
        binding.tvLockedAppCount.text = "$count uygulama kilitli"
    }

    private fun loadSettings() {
        // AI mod bilgisi
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

        // Matematik ayarları (fallback mod için)
        val questionCount = prefManager.questionCount.toFloat()
        val passScore = prefManager.passScore.toFloat()

        binding.sliderQuestionCount.value = questionCount
        binding.sliderPassScore.value = passScore.coerceAtMost(questionCount)
        binding.sliderPassScore.valueTo = questionCount

        binding.tvQuestionCount.text = getString(R.string.settings_question_count, questionCount.toInt())
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

        // Kimlik doğrulama yöntemleri
        binding.switchFingerprint.isChecked = prefManager.isFingerprintEnabled
        binding.switchPin.isChecked = prefManager.isPinEnabled
        binding.switchPattern.isChecked = prefManager.isPatternEnabled

        // Desen durumu
        binding.tvPatternStatus.text = if (prefManager.hasPattern())
            "✅ Desen ayarlanmış" else "Henüz desen ayarlanmamış"

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

        // PIN kaydetme
        binding.btnSavePin.setOnClickListener {
            val newPin = binding.etNewPin.text.toString().trim()
            val confirmPin = binding.etConfirmPin.text.toString().trim()

            when {
                newPin.length < 4 -> {
                    binding.tvPinStatus.text = getString(R.string.pin_too_short)
                    binding.tvPinStatus.setTextColor(getColor(R.color.wrong_red))
                }
                newPin != confirmPin -> {
                    binding.tvPinStatus.text = getString(R.string.pin_mismatch)
                    binding.tvPinStatus.setTextColor(getColor(R.color.wrong_red))
                }
                else -> {
                    prefManager.setPin(newPin)
                    binding.tvPinStatus.text = getString(R.string.pin_saved)
                    binding.tvPinStatus.setTextColor(getColor(R.color.correct_green))
                    binding.etNewPin.setText("")
                    binding.etConfirmPin.setText("")
                }
            }
        }

        // Desen ayarlama
        binding.btnSetPattern.setOnClickListener {
            val intent = Intent(this, PatternActivity::class.java).apply {
                putExtra("mode", "set")
            }
            startActivityForResult(intent, REQUEST_SET_PATTERN)
        }

        // Soru sayısı slider
        binding.sliderQuestionCount.addOnChangeListener { _, value, _ ->
            val count = value.toInt()
            prefManager.questionCount = count
            binding.tvQuestionCount.text = getString(R.string.settings_question_count, count)

            binding.sliderPassScore.valueTo = value
            if (binding.sliderPassScore.value > value) {
                binding.sliderPassScore.value = value
                prefManager.passScore = count
            }
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

        // Kimlik doğrulama switch'leri
        binding.switchFingerprint.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isFingerprintEnabled = isChecked
        }

        binding.switchPin.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isPinEnabled = isChecked
        }

        binding.switchPattern.setOnCheckedChangeListener { _, isChecked ->
            prefManager.isPatternEnabled = isChecked
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
        // 1. Usage Stats izni
        if (!hasUsageStatsPermission()) {
            AlertDialog.Builder(this)
                .setTitle("İzin Gerekli")
                .setMessage("Uygulama kilidi için \"Kullanım Erişimi\" izni gereklidir.\n\nAçılan ayar ekranında MathLock uygulamasına izin verin.")
                .setPositiveButton("Ayarlara Git") { _, _ ->
                    startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
                }
                .setNegativeButton("İptal", null)
                .show()
            return
        }

        // 2. Overlay izni (API 23+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            AlertDialog.Builder(this)
                .setTitle("İzin Gerekli")
                .setMessage("Uygulama kilidi için \"Diğer uygulamaların üzerinde göster\" izni gereklidir.")
                .setPositiveButton("Ayarlara Git") { _, _ ->
                    val intent = Intent(
                        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:$packageName")
                    )
                    startActivity(intent)
                }
                .setNegativeButton("İptal", null)
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
            AlertDialog.Builder(this)
                .setTitle("Bildirim Gerekli")
                .setMessage("Geri sayım ve koruma bildirimi için MathLock bildirimleri açık olmalı.")
                .setPositiveButton("Ayarları Aç") { _, _ ->
                    val intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
                        putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
                    }
                    startActivity(intent)
                }
                .setNegativeButton("İptal", null)
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
        promptXiaomiAutostart()
    }

    private fun promptXiaomiAutostart() {
        val manufacturer = Build.MANUFACTURER.lowercase()
        if (!manufacturer.contains("xiaomi") && !manufacturer.contains("redmi") && !manufacturer.contains("poco")) return
        if (prefManager.prefs.getBoolean("autostart_prompted", false)) return
        prefManager.prefs.edit().putBoolean("autostart_prompted", true).apply()
        AlertDialog.Builder(this)
            .setTitle("⚠️ Xiaomi/MIUI Ayarı Gerekli")
            .setMessage("Koruma sürekli çalışsın diye şu adımları yapın:\n\n" +
                "1. Güvenlik → İzinler → Otomatik Başlatma → MathLock → AÇ\n\n" +
                "2. Ayarlar → Uygulamalar → MathLock → Batarya tasarrufu → Kısıtlama yok\n\n" +
                "3. Ayarlar → Uygulamalar → MathLock → Diğer izinler → Arka planda başlat → İzin ver")
            .setPositiveButton("Anladım", null)
            .show()
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

    @Suppress("DEPRECATION")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_SET_PATTERN && resultCode == RESULT_OK) {
            binding.tvPatternStatus.text = "✅ Desen kaydedildi!"
            binding.tvPatternStatus.setTextColor(getColor(R.color.correct_green))
        }
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
        private const val REQUEST_SET_PATTERN = 3001
        private const val REQUEST_NOTIFICATION = 3002
    }
}
