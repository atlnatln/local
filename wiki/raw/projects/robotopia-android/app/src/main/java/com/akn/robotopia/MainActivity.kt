package com.akn.robotopia

import android.annotation.SuppressLint
import android.os.Bundle
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONObject

class MainActivity : BaseActivity() {

    companion object {
        private const val TAG = "Robotopia"
    }

    private lateinit var webView: WebView
    private var levelsCompleted = 0

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Debug modda Chrome DevTools ile canlı CSS/JS düzenleme (sadece debug)
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)

        window.statusBarColor = android.graphics.Color.parseColor("#1a1a2e")

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
                @Suppress("DEPRECATION")
                super.onBackPressed()
            }
        }
    }

    override fun onDestroy() {
        webView.stopLoading()
        webView.loadUrl("about:blank")
        webView.clearHistory()
        webView.removeAllViews()
        webView.destroy()
        super.onDestroy()
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
                        }
                        "allComplete" -> {
                            Log.d(TAG, "Tüm seviyeler tamamlandı!")
                        }
                        "finish" -> {
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
