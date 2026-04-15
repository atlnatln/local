package com.akn.mathlock

import android.app.AlertDialog
import android.app.ProgressDialog
import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import com.akn.mathlock.databinding.ActivityMainBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.UpdateChecker
import com.akn.mathlock.util.UpdateInfo

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var prefManager: PreferenceManager
    private lateinit var updateChecker: UpdateChecker
    private var updateCheckDone = false

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
        updateChecker = UpdateChecker(this)

        if (!prefManager.hasPin()) {
            prefManager.setPin("1234")
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

        // Uygulama her açılışında bir kez güncelleme kontrol et
        if (!updateCheckDone) {
            updateCheckDone = true
            checkForUpdates()
        }
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

    private fun checkForUpdates() {
        updateChecker.checkForUpdate { info ->
            runOnUiThread {
                if (!isFinishing && !isDestroyed) {
                    showUpdateDialog(info)
                }
            }
        }
    }

    @Suppress("DEPRECATION")
    private fun showUpdateDialog(info: UpdateInfo) {
        if (isFinishing || isDestroyed) return

        val notes = info.releaseNotes.takeIf { it.isNotBlank() }

        val message = buildString {
            append(getString(R.string.update_message, info.versionName))
            if (notes != null) {
                append("\n\n")
                append(notes)
            }
        }

        AlertDialog.Builder(this)
            .setTitle(getString(R.string.update_title))
            .setMessage(message)
            .setPositiveButton(getString(R.string.update_now)) { _, _ ->
                startDownload(info.apkUrl)
            }
            .setNegativeButton(getString(R.string.update_later), null)
            .setCancelable(true)
            .show()
    }

    @Suppress("DEPRECATION")
    private fun startDownload(apkUrl: String) {
        if (isFinishing || isDestroyed) return

        val progress = ProgressDialog(this).apply {
            setTitle(getString(R.string.update_downloading))
            setMessage("0%")
            setCancelable(false)
            show()
        }

        updateChecker.downloadAndInstall(
            apkUrl = apkUrl,
            onProgress = { percent ->
                runOnUiThread {
                    if (!isFinishing && !isDestroyed) progress.setMessage("$percent%")
                }
            },
            onComplete = {
                runOnUiThread {
                    if (!isFinishing && !isDestroyed) progress.dismiss()
                }
            },
            onError = { msg ->
                runOnUiThread {
                    if (!isFinishing && !isDestroyed) {
                        progress.dismiss()
                        AlertDialog.Builder(this)
                            .setTitle(getString(R.string.update_error_title))
                            .setMessage(msg)
                            .setPositiveButton("Tamam", null)
                            .show()
                    }
                }
            }
        )
    }

    private fun setupListeners() {
        // Ebeveyn erişim butonu (🔑) → parmak izi doğrulama doğrudan bu ekranda
        binding.btnParentAccess.setOnClickListener {
            showParentBiometricAuth()
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
                showParentBiometricAuth()
            }
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
                    Toast.makeText(this@MainActivity, "❌ Parmak izi tanınmadı, tekrar deneyin", Toast.LENGTH_SHORT).show()
                }
            })

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(getString(R.string.biometric_title))
            .setSubtitle(getString(R.string.biometric_subtitle))
            .setNegativeButtonText(getString(R.string.biometric_cancel))
            .build()

        prompt.authenticate(promptInfo)
    }
}
