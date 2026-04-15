package com.akn.mathlock

import android.annotation.SuppressLint
import android.os.Bundle
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.service.AppLockService
import org.json.JSONObject

class RobotopiaActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "Robotopia"
    }

    private lateinit var webView: WebView
    private var lockedPackage: String? = null
    private var isPracticeMode = false
    private var isTestMode = false
    private var timerExpired = false
    private var levelsCompleted = 0

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_robotopia)

        // Debug modda Chrome DevTools ile canlı CSS/JS düzenleme
        WebView.setWebContentsDebuggingEnabled(true)

        window.statusBarColor = android.graphics.Color.parseColor("#1a1a2e")

        lockedPackage = intent.getStringExtra("locked_package")
        isPracticeMode = intent.getBooleanExtra("practice_mode", false)
        isTestMode = intent.getBooleanExtra("test_mode", false)
        timerExpired = intent.getBooleanExtra("timer_expired", false)

        webView = findViewById(R.id.webView)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false          // file system erişimi kapalı (güvenlik)
        webView.settings.allowContentAccess = false
        @Suppress("DEPRECATION")
        webView.settings.allowFileAccessFromFileURLs = true // aynı origin dosya yükleme (assets için gerekli)
        webView.addJavascriptInterface(GameBridge(), "Android")

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                Log.d(TAG, "Robotopia yüklendi")
            }
        }

        webView.loadUrl("file:///android_asset/robotopia/game.html")
    }

    private fun unlockAndFinish() {
        if (isTestMode) {
            Toast.makeText(this, "Test başarılı!", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        if (isPracticeMode) {
            finish()
            return
        }

        lockedPackage?.let { pkg ->
            LockStateManager.notifyUnlocked(pkg)
            AppLockService.removeBlockingOverlay()
            val launchIntent = packageManager.getLaunchIntentForPackage(pkg)
            if (launchIntent != null) {
                startActivity(launchIntent)
            }
        }
        finish()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
            return
        }
        if (isPracticeMode || isTestMode) {
            super.onBackPressed()
            return
        }
        // Kilit modunda geri tuşu ana ekrana gönderir
        val homeIntent = android.content.Intent(android.content.Intent.ACTION_MAIN).apply {
            addCategory(android.content.Intent.CATEGORY_HOME)
            flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
        finish()
    }

    // ── JavaScript Bridge ────────────────────────────────
    inner class GameBridge {
        @JavascriptInterface
        fun onGameEvent(event: String, dataJson: String) {
            runOnUiThread {
                try {
                    val data = JSONObject(dataJson)
                    when (event) {
                        "ready" -> {
                            Log.d(TAG, "Oyun hazır. Toplam seviye: ${data.optInt("totalLevels")}")
                        }
                        "levelComplete" -> {
                            levelsCompleted++
                            Log.d(TAG, "Seviye tamamlandı: ${data.optString("category")}/${data.optInt("levelIndex")}, " +
                                    "toplam: ${data.optInt("totalCompleted")}/${data.optInt("totalLevels")}")

                            // Kilit modunda: belirli sayıda seviye tamamlanınca unlock
                            if (!isPracticeMode && !isTestMode) {
                                val passScore = com.akn.mathlock.util.PreferenceManager(this@RobotopiaActivity).passScore
                                if (levelsCompleted >= passScore) {
                                    unlockAndFinish()
                                }
                            }
                        }
                        "allComplete" -> {
                            Log.d(TAG, "Tüm seviyeler tamamlandı!")
                            if (!isPracticeMode && !isTestMode) {
                                unlockAndFinish()
                            }
                        }
                        "finish" -> {
                            if (isPracticeMode || isTestMode) {
                                finish()
                            } else {
                                unlockAndFinish()
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Game event parse hatası", e)
                }
            }
        }
    }
}
