package com.akn.mathlock

import android.annotation.SuppressLint
import android.os.Bundle
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import com.akn.mathlock.service.AppLockService
import org.json.JSONObject

class RobotopiaActivity : BaseActivity() {

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
        // Oyun içindeyse (hash #tutorial/... ise) → menüye dön (app'in kendi geri butonu gibi)
        webView.evaluateJavascript(
            "(function(){ if(window.location.hash && window.location.hash.indexOf('#tutorial/') === 0) { RobotopiaMenu.show(); return 'menu'; } return 'exit'; })()"
        ) { result ->
            val value = result?.replace("\"", "") ?: "exit"
            if (value == "menu") {
                // RobotopiaMenu.show() çağrıldı, WebView menüye döndü
                return@evaluateJavascript
            }
            // Menüdeyiz veya hash boş — Activity'den çık
            runOnUiThread {
                if (isPracticeMode || isTestMode) {
                    @Suppress("DEPRECATION")
                    super.onBackPressed()
                } else {
                    // Kilit modunda geri tuşu ana ekrana gönderir
                    val homeIntent = android.content.Intent(android.content.Intent.ACTION_MAIN).apply {
                        addCategory(android.content.Intent.CATEGORY_HOME)
                        flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    startActivity(homeIntent)
                    finish()
                }
            }
        }
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

                            // NOT: Robotopia artık kilit açma amaçlı kullanılmıyor.
                            // Kilit açma sadece MathChallengeActivity üzerinden yapılır.
                        }
                        "allComplete" -> {
                            Log.d(TAG, "Tüm seviyeler tamamlandı!")
                        }
                        "finish" -> {
                            // Pratik/test modunda veya kilit modunda activity'i kapat
                            finish()
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Game event parse hatası", e)
                }
            }
        }
    }
}
