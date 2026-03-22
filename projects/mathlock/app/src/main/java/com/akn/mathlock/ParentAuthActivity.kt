package com.akn.mathlock

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import com.akn.mathlock.databinding.ActivityParentAuthBinding
import com.akn.mathlock.util.PreferenceManager

class ParentAuthActivity : AppCompatActivity() {

    private lateinit var binding: ActivityParentAuthBinding
    private lateinit var prefManager: PreferenceManager

    private var lockedPackage: String? = null
    private var isTestMode = false
    private var returnToSettings = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityParentAuthBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)
        lockedPackage = intent.getStringExtra("locked_package")
        isTestMode = intent.getBooleanExtra("test_mode", false)
        returnToSettings = intent.getBooleanExtra("return_to_settings", false)

        setupUI()
        setupListeners()
    }

    private fun setupUI() {
        // Parmak izi desteğini kontrol et
        val canBiometric = canUseBiometric()
        binding.btnFingerprint.visibility =
            if (canBiometric && prefManager.isFingerprintEnabled) View.VISIBLE else View.GONE

        // PIN desteği
        binding.btnPin.visibility =
            if (prefManager.isPinEnabled && prefManager.hasPin()) View.VISIBLE else View.GONE

        // Desen desteği
        binding.btnPattern.visibility =
            if (prefManager.isPatternEnabled && prefManager.hasPattern()) View.VISIBLE else View.GONE

        // Hiçbir yöntem yoksa PIN'i zorla göster (ilk kullanım)
        if (binding.btnFingerprint.visibility == View.GONE &&
            binding.btnPin.visibility == View.GONE &&
            binding.btnPattern.visibility == View.GONE
        ) {
            // Henüz PIN ayarlanmamışsa, varsayılan PIN göster
            if (!prefManager.hasPin()) {
                binding.tvAuthStatus.text = "⚠️ Henüz şifre ayarlanmamış!\nVarsayılan PIN: 1234"
                binding.tvAuthStatus.setTextColor(getColor(R.color.accent))
                prefManager.setPin("1234")
            }
            binding.btnPin.visibility = View.VISIBLE
        }
    }

    private fun setupListeners() {
        binding.btnFingerprint.setOnClickListener {
            showBiometricPrompt()
        }

        binding.btnPin.setOnClickListener {
            // PIN giriş alanını aç/kapat
            binding.cardPinInput.visibility =
                if (binding.cardPinInput.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }

        binding.btnPinSubmit.setOnClickListener {
            val pin = binding.etPin.text.toString().trim()
            if (pin.isEmpty()) return@setOnClickListener

            if (prefManager.verifyPin(pin)) {
                onAuthSuccess()
            } else {
                binding.tvAuthStatus.text = getString(R.string.pin_wrong)
                binding.tvAuthStatus.setTextColor(getColor(R.color.wrong_red))
                binding.etPin.setText("")
            }
        }

        binding.btnPattern.setOnClickListener {
            val intent = Intent(this, PatternActivity::class.java).apply {
                putExtra("mode", "verify")
                putExtra("locked_package", lockedPackage)
                putExtra("test_mode", isTestMode)
                putExtra("return_to_settings", returnToSettings)
            }
            startActivityForResult(intent, REQUEST_PATTERN)
        }
    }

    private fun canUseBiometric(): Boolean {
        val biometricManager = BiometricManager.from(this)
        return biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG) ==
                BiometricManager.BIOMETRIC_SUCCESS
    }

    private fun showBiometricPrompt() {
        val executor = ContextCompat.getMainExecutor(this)

        val biometricPrompt = BiometricPrompt(this, executor,
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
                    binding.tvAuthStatus.text = "❌ Parmak izi tanınmadı"
                    binding.tvAuthStatus.setTextColor(getColor(R.color.wrong_red))
                }
            })

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(getString(R.string.biometric_title))
            .setSubtitle(getString(R.string.biometric_subtitle))
            .setNegativeButtonText(getString(R.string.biometric_cancel))
            .build()

        biometricPrompt.authenticate(promptInfo)
    }

    private fun onAuthSuccess() {
        binding.tvAuthStatus.text = getString(R.string.pin_success)
        binding.tvAuthStatus.setTextColor(getColor(R.color.correct_green))

        if (returnToSettings) {
            // Ayarlara dönme sebebi varsa
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
            LockStateManager.notifyParentUnlocked(pkg)  // timer YOK; geri sayım başlamaz
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
            onAuthSuccess()
        }
    }

    companion object {
        private const val REQUEST_PATTERN = 2001
    }
}
