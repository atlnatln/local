package com.akn.mathlock

import android.app.AlertDialog
import android.app.ProgressDialog
import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import androidx.appcompat.app.AppCompatActivity
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
        // Her zaman görünür küçük ebeveyn erişim butonu
        binding.btnParentAccess.setOnClickListener {
            val intent = Intent(this, ParentAuthActivity::class.java).apply {
                putExtra("return_to_settings", true)
            }
            startActivityForResult(intent, REQUEST_AUTH_SETTINGS)
        }

        // Pratik modu: çocuk istediğinde soru çözer
        binding.cardPractice.setOnClickListener {
            val intent = Intent(this, MathChallengeActivity::class.java).apply {
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
                // Ebeveyn doğrulaması iste → sonra ayarlara yönlendir
                val intent = Intent(this, ParentAuthActivity::class.java).apply {
                    putExtra("return_to_settings", true)
                }
                startActivityForResult(intent, REQUEST_AUTH_SETTINGS)
            }
        }
    }

    @Suppress("DEPRECATION")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_AUTH_SETTINGS && resultCode == RESULT_OK) {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
    }

    companion object {
        private const val REQUEST_AUTH_SETTINGS = 1001
    }
}
