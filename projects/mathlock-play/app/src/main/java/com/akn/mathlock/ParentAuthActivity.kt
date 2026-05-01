package com.akn.mathlock

import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import com.akn.mathlock.databinding.ActivityParentAuthBinding

class ParentAuthActivity : BaseActivity() {

    private lateinit var binding: ActivityParentAuthBinding

    private var lockedPackage: String? = null
    private var isTestMode = false
    private var returnToSettings = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityParentAuthBinding.inflate(layoutInflater)
        setContentView(binding.root)

        lockedPackage = intent.getStringExtra("locked_package")
        isTestMode = intent.getBooleanExtra("test_mode", false)
        returnToSettings = intent.getBooleanExtra("return_to_settings", false)

        binding.layoutFingerprint.setOnClickListener { showBiometricPrompt() }

        if (canUseBiometric()) {
            showBiometricPrompt()
        } else {
            binding.tvAuthStatus.text = "⚠️ Bu cihazda parmak izi sensörü bulunamadı"
            binding.tvAuthStatus.setTextColor(getColor(R.color.wrong_red))
        }
    }

    private fun canUseBiometric(): Boolean {
        val authenticators = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.DEVICE_CREDENTIAL
        } else {
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        }
        val bm = BiometricManager.from(this)
        return bm.canAuthenticate(authenticators) == BiometricManager.BIOMETRIC_SUCCESS
    }

    private fun showBiometricPrompt() {
        val executor = ContextCompat.getMainExecutor(this)
        val prompt = BiometricPrompt(this, executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    onAuthSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    if (errorCode != BiometricPrompt.ERROR_USER_CANCELED &&
                        errorCode != BiometricPrompt.ERROR_NEGATIVE_BUTTON
                    ) {
                        binding.tvAuthStatus.text = "Hata: $errString"
                        binding.tvAuthStatus.setTextColor(getColor(R.color.wrong_red))
                    }
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    binding.tvAuthStatus.text = "❌ Kimlik doğrulama başarısız, tekrar deneyin"
                    binding.tvAuthStatus.setTextColor(getColor(R.color.wrong_red))
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

    private fun onAuthSuccess() {
        binding.tvAuthStatus.text = getString(R.string.pin_success)
        binding.tvAuthStatus.setTextColor(getColor(R.color.correct_green))

        if (returnToSettings) {
            setResult(RESULT_OK)
            finish()
            return
        }

        if (isTestMode) {
            Toast.makeText(this, "✅ Kimlik doğrulama başarılı!", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        lockedPackage?.let { pkg ->
            LockStateManager.notifyParentUnlocked(pkg)
            val launchIntent = packageManager.getLaunchIntentForPackage(pkg)
            if (launchIntent != null) {
                startActivity(launchIntent)
            }
        }
        finish()
    }
}

