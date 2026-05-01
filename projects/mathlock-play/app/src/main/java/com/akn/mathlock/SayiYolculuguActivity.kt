package com.akn.mathlock

import android.annotation.SuppressLint
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.ConsoleMessage
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebViewClient
import android.widget.Toast
import com.akn.mathlock.api.ApiClient
import com.akn.mathlock.api.RealApiClient
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.PreferenceManager
import org.json.JSONArray
import org.json.JSONObject

class SayiYolculuguActivity : BaseActivity() {

    companion object {
        private const val TAG = "SayiYolculugu"
        private const val PREFS_NAME = "sayi_yolculugu"
        private const val KEY_CACHED_LEVELS = "cached_levels"
        private const val KEY_COMPLETED_IDS = "completed_level_ids"
    }

    private lateinit var webView: WebView
    private var lockedPackage: String? = null
    private var isPracticeMode = false
    private var isTestMode = false
    private var timerExpired = false
    private var levelsCompleted = 0
    private var currentSetId: Int? = null
    private val completedLevelIds = mutableSetOf<Int>()
    private val apiClient: ApiClient = RealApiClient()
    private val handler = Handler(Looper.getMainLooper())

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sayi_yolculugu)

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
        webView.settings.cacheMode = WebSettings.LOAD_NO_CACHE
        webView.clearCache(true)
        webView.addJavascriptInterface(GameBridge(), "Android")

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                loadLevelsIntoGame()
            }
        }
        webView.webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(message: ConsoleMessage?): Boolean {
                Log.i(TAG, "[WebView] ${message?.message()} (${message?.sourceId()}:${message?.lineNumber()})")
                return true
            }
        }

        webView.loadUrl("file:///android_asset/sayi-yolculugu/game.html")

        loadCompletedLevels()
    }

    private fun loadLevelsIntoGame() {
        Thread {
            val oldSetId = currentSetId
            val levels = fetchLevels()
            val isNewSet = currentSetId != null && currentSetId != oldSetId
            runOnUiThread {
                if (levels != null) {
                    val locale = PreferenceManager(this).appLocale
                    val payload = JSONObject(levels).apply {
                        put("locale", locale)
                        put("forceClear", isNewSet)
                    }
                    val escaped = payload.toString()
                        .replace("\\", "\\\\")
                        .replace("'", "\\'")
                        .replace("\n", "\\n")
                        .replace("\r", "")
                    webView.evaluateJavascript("initGame('$escaped');", null)
                } else {
                    try {
                        val locale = PreferenceManager(this).appLocale
                        val path = "sayi-yolculugu/fallback-levels/$locale.json"
                        val json = try {
                            assets.open(path).bufferedReader().readText()
                        } catch (_: Exception) {
                            assets.open("sayi-yolculugu/fallback-levels/tr.json")
                                .bufferedReader().readText()
                        }
                        val payload = JSONObject(json).apply {
                            put("locale", locale)
                            put("forceClear", true)
                        }
                        val escaped = payload.toString()
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

    private fun loadCompletedLevels() {
        val raw = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .getString(KEY_COMPLETED_IDS, "") ?: ""
        completedLevelIds.clear()
        raw.split(",").mapNotNull { it.trim().toIntOrNull() }.forEach { completedLevelIds.add(it) }
        Log.d(TAG, "Local completedLevelIds yüklendi: ${completedLevelIds.size}")
    }

    private fun saveCompletedLevels() {
        val raw = completedLevelIds.sorted().joinToString(",")
        getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .edit().putString(KEY_COMPLETED_IDS, raw).apply()
    }

    private fun injectCompletedIds(json: String): String {
        return try {
            val root = JSONObject(json)
            val arr = JSONArray()
            completedLevelIds.sorted().forEach { arr.put(it) }
            root.put("completed_level_ids", arr)
            currentSetId?.let { root.put("set_id", it) }
            root.toString()
        } catch (e: Exception) {
            json
        }
    }

    private fun fetchLevels(): String? {
        val accountManager = AccountManager(this)
        val prefManager = PreferenceManager(this)
        var token = accountManager.getDeviceToken()
        if (token.isNullOrBlank()) {
            token = accountManager.getOrRegister()
        }
        val childId = prefManager.activeChildId
        System.out.println("[SY-FETCH] token=${token?.take(8)} childId=$childId")

        if (!token.isNullOrBlank()) {
            try {
                val locale = PreferenceManager(this).appLocale
                var path = "/levels/?device_token=${token.trim()}"
                if (childId > 0) path += "&child_id=$childId"
                path += "&locale=$locale"
                System.out.println("[SY-FETCH] GET $path")
                val response = apiClient.get(path)
                System.out.println("[SY-FETCH] response code=${response.statusCode} body=${response.body.toString().take(120)}")
                if (response.statusCode == 200) {
                    val json = response.body.toString()
                    try {
                        val root = JSONObject(json)
                        val serverSetId = root.optInt("set_id", 0).takeIf { it > 0 }
                        val isNewSet = (serverSetId != null && serverSetId != currentSetId)
                        val idsArr = root.optJSONArray("completed_level_ids")
                        // Server'dan gelen verileri al
                        completedLevelIds.clear()
                        if (idsArr != null) {
                            for (i in 0 until idsArr.length()) completedLevelIds.add(idsArr.getInt(i))
                        }
                        if (!isNewSet) {
                            // Aynı set: local cache'teki tamamlanan ID'leri de ekle (merge)
                            // (Kullanıcı uygulamayı kapatırsa upload thread kesilebilir)
                            val localRaw = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                                .getString(KEY_COMPLETED_IDS, "") ?: ""
                            localRaw.split(",").mapNotNull { it.trim().toIntOrNull() }
                                .forEach { completedLevelIds.add(it) }
                        } else {
                            // Yeni set: eski local tamamlanmış seviyeleri temizle
                            getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                                .edit().remove(KEY_COMPLETED_IDS).apply()
                        }
                        saveCompletedLevels()
                        currentSetId = serverSetId
                        System.out.println("[SY-FETCH] API OK set_id=$currentSetId isNewSet=$isNewSet completed=${completedLevelIds.size}")
                    } catch (e: Exception) {
                        System.out.println("[SY-FETCH] API parse exception: ${e.message}")
                    }
                    val injected = injectCompletedIds(json)
                    getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                        .edit().putString(KEY_CACHED_LEVELS, injected).apply()
                    System.out.println("[SY-FETCH] cached and returning injected")
                    return injected
                } else {
                    System.out.println("[SY-FETCH] API non-200 status=${response.statusCode}")
                }
            } catch (e: Exception) {
                System.out.println("[SY-FETCH] API exception: ${e.javaClass.simpleName} ${e.message}")
            }
        } else {
            System.out.println("[SY-FETCH] token blank/null")
        }

        val cached = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .getString(KEY_CACHED_LEVELS, null)
        if (cached != null) {
            try {
                val root = JSONObject(cached)
                val cachedSetId = root.optInt("set_id", 0).takeIf { it > 0 }
                val isNewSet = (cachedSetId != null && cachedSetId != currentSetId)
                val idsArr = root.optJSONArray("completed_level_ids")
                completedLevelIds.clear()
                if (idsArr != null) {
                    for (i in 0 until idsArr.length()) completedLevelIds.add(idsArr.getInt(i))
                }
                if (!isNewSet) {
                    // Aynı set: local cache'tekileri merge et
                    val localRaw = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                        .getString(KEY_COMPLETED_IDS, "") ?: ""
                    localRaw.split(",").mapNotNull { it.trim().toIntOrNull() }
                        .forEach { completedLevelIds.add(it) }
                } else {
                    // Yeni set: eski local tamamlanmış seviyeleri temizle
                    getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                        .edit().remove(KEY_COMPLETED_IDS).apply()
                }
                saveCompletedLevels()
                currentSetId = cachedSetId
            } catch (_: Exception) {}
            val injected = injectCompletedIds(cached)
            getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                .edit().putString(KEY_CACHED_LEVELS, injected).apply()
            System.out.println("[SY-FETCH] cache loaded set=$currentSetId completed=${completedLevelIds.size}")
            return injected
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
        val homeIntent = android.content.Intent(android.content.Intent.ACTION_MAIN).apply {
            addCategory(android.content.Intent.CATEGORY_HOME)
            flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
        finish()
    }

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
                            Log.i(TAG, "Seviye tamamlandı: ${data.optInt("levelId")}, yıldız: ${data.optInt("stars")}")
                            if (levelId > 0) {
                                completedLevelIds.add(levelId)
                                saveCompletedLevels()
                                if (!isTestMode) {
                                    uploadLevelProgress(listOf(levelId))
                                }
                            }
                            // Kilitli uygulama açma hedefi kontrolü
                            if (lockedPackage != null && !isPracticeMode && !isTestMode) {
                                val required = PreferenceManager(this@SayiYolculuguActivity).levelsToUnlock
                                if (levelsCompleted >= required) {
                                    Log.i(TAG, "Kilitli uygulama açma hedefine ulaşıldı: $levelsCompleted / $required")
                                    unlockAndFinish()
                                }
                            }
                        }
                        "allComplete" -> {
                            Log.i(TAG, "Tüm seviyeler tamamlandı: ${data.optInt("totalStars")}/${data.optInt("maxStars")} yıldız")
                            if (!isTestMode) {
                                uploadLevelProgress(completedLevelIds.toList()) { resp ->
                                    val autoRenewal = resp.optBoolean("auto_renewal_started", false)
                                    val creditsRemaining = resp.optInt("credits_remaining", -1)
                                    Log.i(TAG, "allComplete response: autoRenewal=$autoRenewal, credits=$creditsRemaining")
                                    if (autoRenewal) {
                                        showRenewalLoading()
                                        pollForNewSet()
                                    } else {
                                        showCreditRequired(creditsRemaining)
                                    }
                                }
                            } else {
                                clearLevelCacheAndReload()
                            }
                        }
                        "finish" -> {
                            finish()
                        }
                        "buyCredits" -> {
                            startActivity(android.content.Intent(this@SayiYolculuguActivity, AccountActivity::class.java))
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Game event parse hatası", e)
                }
            }
        }
    }

    private fun uploadLevelProgress(newlyCompletedIds: List<Int>, onResult: ((JSONObject) -> Unit)? = null) {
        Thread {
            try {
                val accountManager = AccountManager(this)
                val prefManager = PreferenceManager(this)
                var token = accountManager.getDeviceToken()
                if (token.isNullOrBlank()) {
                    token = accountManager.getOrRegister()
                }
                if (token.isNullOrBlank()) {
                    System.out.println("[SY-UPLOAD] no token")
                    return@Thread
                }
                val childId = prefManager.activeChildId
                System.out.println("[SY-UPLOAD] set_id=$currentSetId childId=$childId completed=${completedLevelIds.sorted()}")

                val body = JSONObject().apply {
                    put("device_token", token)
                    if (childId > 0) put("child_id", childId)
                    currentSetId?.let { put("set_id", it) }
                    val arr = JSONArray()
                    completedLevelIds.forEach { arr.put(it) }
                    put("completed_level_ids", arr)
                    put("locale", PreferenceManager(this@SayiYolculuguActivity).appLocale)
                }
                val response = apiClient.post("/levels/progress/", body)
                val code = response.statusCode
                val responseText = response.body.toString()
                System.out.println("[SY-UPLOAD] response code=$code body=${responseText.take(120)}")

                if (code in 200..299 && responseText.isNotBlank()) {
                    try {
                        val resp = JSONObject(responseText)
                        onResult?.let { runOnUiThread { it(resp) } }
                    } catch (_: Exception) {}
                }
            } catch (e: Exception) {
                Log.w(TAG, "Level progress gönderme hatası: ${e.message}")
            }
        }.start()
    }

    private fun clearLevelCacheAndReload() {
        completedLevelIds.clear()
        saveCompletedLevels()
        getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .edit().remove(KEY_CACHED_LEVELS).apply()
        Log.i(TAG, "Level cache temizlendi, yeni seviyeler çekiliyor...")
        loadLevelsIntoGame()
    }

    // ── Yeni set hazırlanana kadar polling ─────────────────────────────────

    private fun showRenewalLoading() {
        runOnUiThread {
            webView.evaluateJavascript("showRenewalLoading();", null)
        }
    }

    private fun showCreditRequired(creditsRemaining: Int) {
        runOnUiThread {
            webView.evaluateJavascript("showCreditRequired();", null)
            Toast.makeText(
                this,
                getString(R.string.credit_required_toast, creditsRemaining),
                Toast.LENGTH_LONG
            ).show()
        }
    }

    override fun onDestroy() {
        // Polling handler'ını temizle — activity öldükten sonra callback çalışmasın
        handler.removeCallbacksAndMessages(null)

        // WebView temizlik
        webView.stopLoading()
        webView.loadUrl("about:blank")
        webView.clearHistory()
        webView.removeAllViews()
        webView.destroy()

        getSharedPreferences(PREFS_NAME, MODE_PRIVATE).edit()
            .remove(KEY_CACHED_LEVELS)
            .remove(KEY_COMPLETED_IDS)
            .apply()

        super.onDestroy()
    }

    private fun showRenewalError() {
        runOnUiThread {
            webView.evaluateJavascript("showRenewalError();", null)
        }
    }

    private fun pollForNewSet(attempt: Int = 0) {
        if (attempt >= 120) {
            Log.w(TAG, "Yeni set 10 dk içinde gelmedi, hata gösteriliyor")
            showRenewalError()
            return
        }
        Thread {
            val levels = fetchLevels()
            runOnUiThread {
                if (levels != null) {
                    try {
                        val root = JSONObject(levels)
                        val idsArr = root.optJSONArray("completed_level_ids")
                        val completedCount = idsArr?.length() ?: 0
                        val levelsArr = root.optJSONArray("levels")
                        val totalLevels = levelsArr?.length() ?: 0
                        if (completedCount < totalLevels) {
                            Log.i(TAG, "Yeni set geldi! (tamamlanan=$completedCount / toplam=$totalLevels)")
                            val escaped = levels
                                .replace("\\", "\\\\")
                                .replace("'", "\\'")
                                .replace("\n", "\\n")
                                .replace("\r", "")
                            webView.evaluateJavascript("initGame('$escaped');", null)
                        } else {
                            Log.d(TAG, "Set hâlâ tamamlanmış, tekrar deneniyor (deneme=${attempt + 1})")
                            handler.postDelayed({
                                pollForNewSet(attempt + 1)
                            }, 5000)
                        }
                    } catch (_: Exception) {
                        handler.postDelayed({
                            pollForNewSet(attempt + 1)
                        }, 5000)
                    }
                } else {
                    handler.postDelayed({
                        pollForNewSet(attempt + 1)
                    }, 5000)
                }
            }
        }.start()
    }
}
