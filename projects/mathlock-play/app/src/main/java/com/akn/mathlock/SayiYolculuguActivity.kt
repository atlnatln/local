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
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.PreferenceManager
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class SayiYolculuguActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "SayiYolculugu"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val PREFS_NAME = "sayi_yolculugu"
        private const val KEY_CACHED_LEVELS = "cached_levels"
        private const val CONNECT_TIMEOUT = 5000
        private const val READ_TIMEOUT = 10000
    }

    private lateinit var webView: WebView
    private var lockedPackage: String? = null
    private var isPracticeMode = false
    private var isTestMode = false
    private var timerExpired = false
    private var levelsCompleted = 0
    private var currentSetId: Int? = null
    private val completedLevelIds = mutableSetOf<Int>()

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sayi_yolculugu)

        // Status bar rengini oyun temasına uyumlu yap
        window.statusBarColor = android.graphics.Color.parseColor("#0f0f1a")

        lockedPackage = intent.getStringExtra("locked_package")
        isPracticeMode = intent.getBooleanExtra("practice_mode", false)
        isTestMode = intent.getBooleanExtra("test_mode", false)
        timerExpired = intent.getBooleanExtra("timer_expired", false)

        webView = findViewById(R.id.webView)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false
        webView.settings.allowContentAccess = false
        webView.addJavascriptInterface(GameBridge(), "Android")

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                loadLevelsIntoGame()
            }
        }

        webView.loadUrl("file:///android_asset/sayi-yolculugu/game.html")
    }

    private fun loadLevelsIntoGame() {
        Thread {
            val levels = fetchLevels()
            runOnUiThread {
                if (levels != null) {
                    val escaped = levels
                        .replace("\\", "\\\\")
                        .replace("'", "\\'")
                        .replace("\n", "\\n")
                        .replace("\r", "")
                    webView.evaluateJavascript("initGame('$escaped');", null)
                } else {
                    // Fallback: bundled asset
                    try {
                        val json = assets.open("sayi-yolculugu/fallback-levels.json")
                            .bufferedReader().readText()
                        val escaped = json
                            .replace("\\", "\\\\")
                            .replace("'", "\\'")
                            .replace("\n", "\\n")
                            .replace("\r", "")
                        webView.evaluateJavascript("initGame('$escaped');", null)
                    } catch (e: Exception) {
                        Log.e(TAG, "Fallback levels da yüklenemedi", e)
                        Toast.makeText(this, "Seviyeler yüklenemedi", Toast.LENGTH_SHORT).show()
                        finish()
                    }
                }
            }
        }.start()
    }

    private fun fetchLevels(): String? {
        val accountManager = AccountManager(this)
        val prefManager = PreferenceManager(this)
        val token = accountManager.getDeviceToken()
        val childId = prefManager.activeChildId

        // 1. API'den çocuğa özel seviye ve ilerleme bilgisini al
        if (!token.isNullOrBlank()) {
            try {
                var apiUrl = "$API_BASE/levels/?device_token=${token.trim()}"
                if (childId > 0) apiUrl += "&child_id=$childId"
                val url = URL(apiUrl)
                val conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = CONNECT_TIMEOUT
                conn.readTimeout = READ_TIMEOUT
                conn.requestMethod = "GET"

                if (conn.responseCode == 200) {
                    val json = conn.inputStream.bufferedReader().readText()
                    conn.disconnect()
                    // set_id ve completed_level_ids'i sakla
                    try {
                        val root = JSONObject(json)
                        currentSetId = root.optInt("set_id", 0).takeIf { it > 0 }
                        val idsArr = root.optJSONArray("completed_level_ids")
                        if (idsArr != null) {
                            completedLevelIds.clear()
                            for (i in 0 until idsArr.length()) completedLevelIds.add(idsArr.getInt(i))
                        }
                    } catch (_: Exception) {}
                    // Cache'e yaz ve döndür
                    getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                        .edit().putString(KEY_CACHED_LEVELS, json).apply()
                    Log.d(TAG, "API'den seviyeler indirildi (set=$currentSetId, tamamlanan=${completedLevelIds.size})")
                    return json
                }
                conn.disconnect()
            } catch (e: Exception) {
                Log.w(TAG, "API bağlantısı başarısız: ${e.message}")
            }
        }

        // 2. Cache'ten oku
        val cached = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .getString(KEY_CACHED_LEVELS, null)
        if (cached != null) {
            try {
                val root = JSONObject(cached)
                currentSetId = root.optInt("set_id", 0).takeIf { it > 0 }
                val idsArr = root.optJSONArray("completed_level_ids")
                if (idsArr != null) {
                    completedLevelIds.clear()
                    for (i in 0 until idsArr.length()) completedLevelIds.add(idsArr.getInt(i))
                }
            } catch (_: Exception) {}
            Log.d(TAG, "Cache'ten seviyeler yüklendi (set=$currentSetId, tamamlanan=${completedLevelIds.size})")
            return cached
        }

        return null
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

    override fun onBackPressed() {
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
                        "levelComplete" -> {
                            levelsCompleted++
                            val levelId = data.optInt("levelId", 0)
                            Log.d(TAG, "Seviye tamamlandı: ${data.optInt("levelId")}, yıldız: ${data.optInt("stars")}")
                            if (levelId > 0) {
                                completedLevelIds.add(levelId)
                                if (!isPracticeMode && !isTestMode) {
                                    uploadLevelProgress(listOf(levelId))
                                }
                            }

                            // Kilit modunda: belirli sayıda seviye tamamlanınca unlock
                            if (!isPracticeMode && !isTestMode) {
                                val passScore = com.akn.mathlock.util.PreferenceManager(this@SayiYolculuguActivity).passScore
                                if (levelsCompleted >= passScore) {
                                    unlockAndFinish()
                                }
                            }
                        }
                        "allComplete" -> {
                            Log.d(TAG, "Tüm seviyeler tamamlandı: ${data.optInt("totalStars")}/${data.optInt("maxStars")} yıldız")
                            if (!isPracticeMode && !isTestMode) {
                                uploadLevelProgress(completedLevelIds.toList())
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

    private fun uploadLevelProgress(newlyCompletedIds: List<Int>) {
        Thread {
            try {
                val accountManager = AccountManager(this)
                val prefManager = PreferenceManager(this)
                val token = accountManager.getDeviceToken() ?: return@Thread
                val childId = prefManager.activeChildId

                val url = URL("$API_BASE/levels/progress/")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.connectTimeout = CONNECT_TIMEOUT
                conn.readTimeout = READ_TIMEOUT

                val body = JSONObject().apply {
                    put("device_token", token)
                    if (childId > 0) put("child_id", childId)
                    currentSetId?.let { put("set_id", it) }
                    val arr = JSONArray()
                    completedLevelIds.forEach { arr.put(it) }
                    put("completed_level_ids", arr)
                }
                conn.outputStream.bufferedWriter().use { it.write(body.toString()) }
                val code = conn.responseCode
                conn.disconnect()
                Log.d(TAG, "Level progress gönderildi (kod=$code, tamamlanan=${completedLevelIds.size})")
            } catch (e: Exception) {
                Log.w(TAG, "Level progress gönderme hatası: ${e.message}")
            }
        }.start()
    }
}
