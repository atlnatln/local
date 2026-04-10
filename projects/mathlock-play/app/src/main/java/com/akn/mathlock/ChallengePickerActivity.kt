package com.akn.mathlock

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import com.akn.mathlock.databinding.ActivityChallengePickerBinding
import com.akn.mathlock.service.AppLockService

class ChallengePickerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityChallengePickerBinding
    private var lockedPackage: String? = null
    private var timerExpired: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityChallengePickerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        lockedPackage = intent.getStringExtra("locked_package")
        timerExpired  = intent.getBooleanExtra("timer_expired", false)

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
        binding.cardMath.setOnClickListener {
            val intent = Intent(this, MathChallengeActivity::class.java).apply {
                putExtra("locked_package", lockedPackage)
                putExtra("timer_expired", timerExpired)
            }
            startActivity(intent)
        }

        binding.cardGuess.setOnClickListener {
            val intent = Intent(this, NumberGuessActivity::class.java).apply {
                putExtra("locked_package", lockedPackage)
                putExtra("timer_expired", timerExpired)
            }
            startActivity(intent)
        }

        binding.cardParent.setOnClickListener {
            showParentBiometricAuth()
        }
    }

    private fun showParentBiometricAuth() {
        val bm = BiometricManager.from(this)
        if (bm.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            != BiometricManager.BIOMETRIC_SUCCESS
        ) {
            Toast.makeText(this, "⚠️ Bu cihazda parmak izi sensörü bulunamadı", Toast.LENGTH_SHORT).show()
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
                    Toast.makeText(this@ChallengePickerActivity, "❌ Parmak izi tanınmadı, tekrar deneyin", Toast.LENGTH_SHORT).show()
                }
            })

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(getString(R.string.biometric_title))
            .setSubtitle(getString(R.string.biometric_subtitle))
            .setNegativeButtonText(getString(R.string.biometric_cancel))
            .build()

        prompt.authenticate(promptInfo)
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
}
