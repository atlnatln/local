package com.akn.mathlock

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.akn.mathlock.databinding.ActivityChallengePickerBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager

class ChallengePickerActivity : BaseActivity() {

    private lateinit var binding: ActivityChallengePickerBinding
    private var lockedPackage: String? = null
    private var timerExpired: Boolean = false
    private lateinit var prefManager: PreferenceManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Kilit ekranı üzerinde gösterilmesini sağla (ekran kapatılıp açıldığında)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
            )
        }

        binding = ActivityChallengePickerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        lockedPackage = intent.getStringExtra("locked_package")
        timerExpired  = intent.getBooleanExtra("timer_expired", false)
        prefManager = PreferenceManager(this)

        // Kilitli uygulamanın adını göster
        lockedPackage?.let { pkg ->
            try {
                val appName = packageManager.getApplicationLabel(
                    packageManager.getApplicationInfo(pkg, 0)
                ).toString()
                binding.tvLockedAppName.text = "($appName)"
            } catch (e: Exception) {
                binding.tvLockedAppName.text = ""
            }
        }

        // Süre doldu banneri
        if (timerExpired) {
            binding.cardTimerExpired.visibility = View.VISIBLE
        }

        setupListeners()
    }

    private fun setupListeners() {
        // Matematik
        if (prefManager.isMathEnabled) {
            binding.cardMath.visibility = View.VISIBLE
            binding.cardMath.setOnClickListener {
                val intent = Intent(this, MathChallengeActivity::class.java).apply {
                    putExtra("locked_package", lockedPackage)
                    putExtra("timer_expired", timerExpired)
                }
                startActivity(intent)
            }
        } else {
            binding.cardMath.visibility = View.GONE
        }

        // Sayı Yolculuğu
        if (prefManager.isPuzzleEnabled) {
            binding.cardPuzzle.visibility = View.VISIBLE
            binding.cardPuzzle.setOnClickListener {
                val intent = Intent(this, SayiYolculuguActivity::class.java).apply {
                    putExtra("locked_package", lockedPackage)
                    putExtra("timer_expired", timerExpired)
                }
                startActivity(intent)
            }
        } else {
            binding.cardPuzzle.visibility = View.GONE
        }

        // Kilit açma ekranında sayı tahmin görünmez
        binding.cardGuess.visibility = View.GONE

        // Sayı Hafızası
        if (prefManager.isMemoryGameEnabled) {
            binding.cardMemory.visibility = View.VISIBLE
            binding.cardMemory.setOnClickListener {
                val intent = Intent(this, MemoryGameActivity::class.java).apply {
                    putExtra("locked_package", lockedPackage)
                    putExtra("timer_expired", timerExpired)
                }
                startActivity(intent)
            }
        } else {
            binding.cardMemory.visibility = View.GONE
        }

        binding.cardParent.setOnClickListener {
            showParentAuthOptions()
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
                    onParentAuthSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    if (errorCode != BiometricPrompt.ERROR_USER_CANCELED &&
                        errorCode != BiometricPrompt.ERROR_NEGATIVE_BUTTON
                    ) {
                        Toast.makeText(this@ChallengePickerActivity, "Hata: $errString", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    Toast.makeText(this@ChallengePickerActivity, "❌ Kimlik doğrulama başarısız, tekrar deneyin", Toast.LENGTH_SHORT).show()
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

    private fun onParentAuthSuccess() {
        lockedPackage?.let { pkg ->
            LockStateManager.notifyParentUnlocked(pkg)
            AppLockService.removeBlockingOverlay()
            val launchIntent = packageManager.getLaunchIntentForPackage(pkg)
            if (launchIntent != null) {
                startActivity(launchIntent)
            }
        }
        finish()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_PATTERN && resultCode == RESULT_OK) {
            onParentAuthSuccess()
        }
    }

    override fun onBackPressed() {
        super.onBackPressed()
        // Geri tuşu - ana ekrana gönder
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
        finish()
    }

    companion object {
        private const val REQUEST_PATTERN = 1001
    }
}
