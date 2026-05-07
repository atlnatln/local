package com.akn.mathlock

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.widget.Toast
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.akn.mathlock.databinding.ActivityMainBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager

class MainActivity : BaseActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var prefManager: PreferenceManager

    // Gizli ebeveyn girişi: logoya 5 kez hızlı tıklama
    private var logoTapCount = 0
    private var lastLogoTapTime = 0L
    private val TAP_THRESHOLD = 500L
    private val REQUIRED_TAPS = 5

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)

        if (!prefManager.hasPin()) {
            prefManager.setPin("1234")
        }

        // İlk kurulumda disclosure ekranını göster
        if (prefManager.isFirstRun) {
            startActivity(Intent(this, DisclosureActivity::class.java))
        }

        setupListeners()
    }

    override fun onResume() {
        super.onResume()
        // Servis aktif olması gerekiyorsa ama çalışmıyorsa yeniden başlat
        if (prefManager.isServiceEnabled && !AppLockService.isRunning) {
            AppLockService.start(this)
        }
        updateServiceStatus()
    }

    private fun updateServiceStatus() {
        val isEnabled = prefManager.isServiceEnabled

        if (isEnabled) {
            binding.tvServiceStatus.text = getString(R.string.service_status_active)
            binding.tvServiceStatus.setTextColor(getColor(R.color.correct_green))
        } else {
            binding.tvServiceStatus.text = getString(R.string.service_status_inactive)
            binding.tvServiceStatus.setTextColor(getColor(R.color.wrong_red))
        }

        val lockedCount = prefManager.getLockedApps().size
        binding.tvLockedAppCount.text = if (lockedCount > 0)
            "$lockedCount uygulama koruma altında"
        else
            "Henüz kilitli uygulama yok"
    }

    private fun setupListeners() {
        // Ebeveyn erişim butonu (🫆) → parmak izi doğrulama doğrudan bu ekranda
        binding.btnParentAccess.setOnClickListener {
            showParentAuthOptions()
        }

        // Pratik modu: çocuk matematik sorusu çözer
        binding.cardPractice.setOnClickListener {
            val intent = Intent(this, MathChallengeActivity::class.java).apply {
                putExtra("practice_mode", true)
            }
            startActivity(intent)
        }

        // Pratik modu: çocuk sayı oyunu oynar (limit kendisi seçer)
        binding.cardPracticeGuess.setOnClickListener {
            val intent = Intent(this, NumberGuessActivity::class.java).apply {
                putExtra("practice_mode", true)
            }
            startActivity(intent)
        }

        // Pratik modu: çocuk bulmaca oynar
        binding.cardPracticePuzzle.setOnClickListener {
            val intent = Intent(this, SayiYolculuguActivity::class.java).apply {
                putExtra("practice_mode", true)
            }
            startActivity(intent)
        }

        // Pratik modu: çocuk hafıza oynar
        binding.cardPracticeMemory.setOnClickListener {
            val intent = Intent(this, MemoryGameActivity::class.java).apply {
                putExtra("practice_mode", true)
            }
            startActivity(intent)
        }

        // Gizli ebeveyn girişi: logoya 5 kez hızlı tıklama (yedek)
        binding.tvLogo.setOnClickListener {
            val now = SystemClock.elapsedRealtime()
            if (now - lastLogoTapTime > TAP_THRESHOLD) {
                logoTapCount = 1
            } else {
                logoTapCount++
            }
            lastLogoTapTime = now

            if (logoTapCount >= REQUIRED_TAPS) {
                logoTapCount = 0
                showParentAuthOptions()
            }
        }
    }

    private fun showParentAuthOptions() {
        val options = mutableListOf<String>()
        val actions = mutableListOf<() -> Unit>()

        val authenticators = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.DEVICE_CREDENTIAL
        } else {
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        }
        val bm = BiometricManager.from(this)
        val hasBiometric = bm.canAuthenticate(authenticators) == BiometricManager.BIOMETRIC_SUCCESS

        if (hasBiometric) {
            options.add("👆 Parmak izi / Ekran kilidi")
            actions.add { showParentBiometricAuth() }
        }

        if (prefManager.hasPattern() && prefManager.isPatternEnabled) {
            options.add("🔢 Desen kullan")
            actions.add { launchPatternVerify() }
        }

        if (options.isEmpty()) {
            Toast.makeText(this, "⚠️ Doğrulama yöntemi bulunamadı", Toast.LENGTH_SHORT).show()
            return
        }

        MaterialAlertDialogBuilder(this)
            .setTitle("Ebeveyn Doğrulaması")
            .setItems(options.toTypedArray()) { _, which ->
                actions[which]()
            }
            .setNegativeButton("İptal", null)
            .show()
    }

    private fun launchPatternVerify() {
        val intent = Intent(this, PatternActivity::class.java).apply {
            putExtra("mode", "verify")
        }
        startActivityForResult(intent, REQUEST_PATTERN)
    }

    private fun showParentBiometricAuth() {
        val authenticators = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.DEVICE_CREDENTIAL
        } else {
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        }

        val bm = BiometricManager.from(this)
        if (bm.canAuthenticate(authenticators) != BiometricManager.BIOMETRIC_SUCCESS) {
            Toast.makeText(this, "⚠️ Bu cihazda parmak izi veya desen kilidi bulunamadı", Toast.LENGTH_SHORT).show()
            return
        }

        val executor = ContextCompat.getMainExecutor(this)
        val prompt = BiometricPrompt(this, executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    startActivity(Intent(this@MainActivity, SettingsActivity::class.java))
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    if (errorCode != BiometricPrompt.ERROR_USER_CANCELED &&
                        errorCode != BiometricPrompt.ERROR_NEGATIVE_BUTTON
                    ) {
                        Toast.makeText(this@MainActivity, "Hata: $errString", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    Toast.makeText(this@MainActivity, "❌ Kimlik doğrulama başarısız, tekrar deneyin", Toast.LENGTH_SHORT).show()
                }
            })

        val promptInfoBuilder = BiometricPrompt.PromptInfo.Builder()
            .setTitle(getString(R.string.biometric_title))
            .setSubtitle(getString(R.string.biometric_subtitle))

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            promptInfoBuilder.setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                        BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
        } else {
            promptInfoBuilder.setNegativeButtonText(getString(R.string.biometric_cancel))
        }

        prompt.authenticate(promptInfoBuilder.build())
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_PATTERN && resultCode == RESULT_OK) {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
    }

    companion object {
        private const val REQUEST_PATTERN = 1001
    }
}
