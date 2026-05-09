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
import com.akn.mathlock.util.SecurePrefs
import org.json.JSONArray
import org.json.JSONObject

class SayiYolculuguActivity : BaseActivity() {

    companion object {
        private const val TAG = "SayiYolculugu"
        private const val PREFS_NAME = "sayi_yolculugu"
        private const val KEY_CACHED_LEVELS = "cached_levels"
        private const val KEY_COMPLETED_IDS = "completed_level_ids"
        private const val KEY_CURRENT_SET_ID = "current_set_id"
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

        val accountManager = AccountManager(this)
        apiClient.setAuthToken(accountManager.getAccessToken())

        loadCompletedLevels()
        loadCurrentSetId()
    }

    private fun loadLevelsIntoGame() {
        Thread {
            val oldSetId = currentSetId
            val levels = fetchLevels()
            // isNewSet: sadece önceden bir setId vardı VE şimdi farklı bir set geldiğinde true
            // İlk açılışta (oldSetId==null) forceClear=true göndermek WebView progress'ini siler!
            val isNewSet = oldSetId != null && currentSetId != null && currentSetId != oldSetId
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
                        // Fallback levels: completed_level_ids inject et ve forceClear=false
                        // (forceClear=true local progress'i siler — bu bir bug'dı)
                        val payload = JSONObject(injectCompletedIds(json)).apply {
                            put("locale", locale)
                            put("forceClear", false)
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
        val raw = SecurePrefs.get(this, PREFS_NAME)
            .getString(KEY_COMPLETED_IDS, "") ?: ""
        completedLevelIds.clear()
        raw.split(",").mapNotNull { it.trim().toIntOrNull() }.forEach { completedLevelIds.add(it) }
        Log.d(TAG, "Local completedLevelIds yüklendi: ${completedLevelIds.size}")
    }

    private fun loadCurrentSetId() {
        val stored = SecurePrefs.get(this, PREFS_NAME)
            .getInt(KEY_CURRENT_SET_ID, 0)
        currentSetId = if (stored > 0) stored else null
        Log.d(TAG, "Local currentSetId yüklendi: $currentSetId")
    }

    private fun saveCurrentSetId() {
        currentSetId?.let {
            SecurePrefs.get(this, PREFS_NAME)
                .edit().putInt(KEY_CURRENT_SET_ID, it).apply()
        } ?: SecurePrefs.get(this, PREFS_NAME)
            .edit().remove(KEY_CURRENT_SET_ID).apply()
    }

    private fun saveCompletedLevels() {
        val raw = completedLevelIds.sorted().joinToString(",")
        SecurePrefs.get(this, PREFS_NAME)
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
        val accessToken = accountManager.getOrRefreshToken()
        var deviceToken = accountManager.getDeviceToken()
        if (deviceToken.isNullOrBlank()) {
            accountManager.getOrRegister()
            deviceToken = accountManager.getDeviceToken()
        }
        apiClient.setAuthToken(accessToken)
        val childId = prefManager.activeChildId
        System.out.println("[SY-FETCH] token=${accessToken?.take(8)} childId=$childId")

        if (!accessToken.isNullOrBlank() && !deviceToken.isNullOrBlank()) {
            try {
                val locale = PreferenceManager(this).appLocale
                fun tryFetch(withChildId: Boolean): String? {
                    var path = "/levels/?device_token=${deviceToken.trim()}"
                    if (withChildId && childId > 0) path += "&child_id=$childId"
                    path += "&locale=$locale"
                    System.out.println("[SY-FETCH] GET $path")
                    val response = apiClient.get(path)
                    System.out.println("[SY-FETCH] response code=${response.statusCode} body=${response.body.toString().take(120)}")
                    if (response.statusCode == 200) {
                        val json = response.body.toString()
                        try {
                            val root = JSONObject(json)
                            val serverSetId = root.optInt("set_id", 0).takeIf { it > 0 }
                            val isNewSet = currentSetId != null && serverSetId != null && serverSetId != currentSetId
                            val idsArr = root.optJSONArray("completed_level_ids")
                            completedLevelIds.clear()
                            if (idsArr != null) {
                                for (i in 0 until idsArr.length()) completedLevelIds.add(idsArr.getInt(i))
                            }
                            if (!isNewSet) {
                                val localRaw = SecurePrefs.get(this, PREFS_NAME)
                                    .getString(KEY_COMPLETED_IDS, "") ?: ""
                                localRaw.split(",").mapNotNull { it.trim().toIntOrNull() }
                                    .forEach { completedLevelIds.add(it) }
                            } else {
                                SecurePrefs.get(this, PREFS_NAME)
                                    .edit().remove(KEY_COMPLETED_IDS).apply()
                            }
                            saveCompletedLevels()
                            currentSetId = serverSetId
                            saveCurrentSetId()
                            System.out.println("[SY-FETCH] API OK set_id=$currentSetId isNewSet=$isNewSet completed=${completedLevelIds.size}")
                        } catch (e: Exception) {
                            System.out.println("[SY-FETCH] API parse exception: ${e.message}")
                        }
                        val injected = injectCompletedIds(json)
                        SecurePrefs.get(this, PREFS_NAME)
                            .edit().putString(KEY_CACHED_LEVELS, injected).apply()
                        System.out.println("[SY-FETCH] cached and returning injected")
                        return injected
                    }
                    return null
                }

                // Önce child_id ile dene; 404 alırsa child_id olmadan dene (backend active child döner)
                var result = tryFetch(true)
                if (result == null && childId > 0) {
                    System.out.println("[SY-FETCH] child_id=$childId not found, retrying without child_id")
                    result = tryFetch(false)
                    if (result != null) {
                        // Backend farklı child döndürdü; local childId'yi sıfırla
                        System.out.println("[SY-FETCH] Resetting local childId from $childId")
                        prefManager.activeChildId = 0
                    }
                }
                if (result != null) return result
            } catch (e: Exception) {
                System.out.println("[SY-FETCH] API exception: ${e.javaClass.simpleName} ${e.message}")
            }
        } else {
            System.out.println("[SY-FETCH] token blank/null")
        }

        val cached = SecurePrefs.get(this, PREFS_NAME)
            .getString(KEY_CACHED_LEVELS, null)
        if (cached != null) {
            try {
                val root = JSONObject(cached)
                val cachedSetId = root.optInt("set_id", 0).takeIf { it > 0 }
                // isNewSet: currentSetId null ise ilk açılış → merge et (silme)
                val isNewSet = currentSetId != null && cachedSetId != null && cachedSetId != currentSetId
                val idsArr = root.optJSONArray("completed_level_ids")
                completedLevelIds.clear()
                if (idsArr != null) {
                    for (i in 0 until idsArr.length()) completedLevelIds.add(idsArr.getInt(i))
                }
                if (!isNewSet) {
                    // Aynı set veya ilk açılış: local cache'tekileri merge et
                    val localRaw = SecurePrefs.get(this, PREFS_NAME)
                        .getString(KEY_COMPLETED_IDS, "") ?: ""
                    localRaw.split(",").mapNotNull { it.trim().toIntOrNull() }
                        .forEach { completedLevelIds.add(it) }
                } else {
                    // Yeni set: eski local tamamlanmış seviyeleri temizle
                    SecurePrefs.get(this, PREFS_NAME)
                        .edit().remove(KEY_COMPLETED_IDS).apply()
                }
                saveCompletedLevels()
                currentSetId = cachedSetId
                saveCurrentSetId()
            } catch (_: Exception) {}
            val injected = injectCompletedIds(cached)
            SecurePrefs.get(this, PREFS_NAME)
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
            var callbackInvoked = false
            fun invokeResult(resp: JSONObject) {
                if (!callbackInvoked) {
                    callbackInvoked = true
                    onResult?.let { runOnUiThread { it(resp) } }
                }
            }
            try {
                val accountManager = AccountManager(this)
                val prefManager = PreferenceManager(this)
                val accessToken = accountManager.getOrRefreshToken()
                var deviceToken = accountManager.getDeviceToken()
                if (deviceToken.isNullOrBlank()) {
                    accountManager.getOrRegister()
                    deviceToken = accountManager.getDeviceToken()
                }
                if (accessToken.isNullOrBlank() || deviceToken.isNullOrBlank()) {
                    System.out.println("[SY-UPLOAD] no token")
                    invokeResult(JSONObject().put("error", "no_token"))
                    return@Thread
                }
                apiClient.setAuthToken(accessToken)
                val childId = prefManager.activeChildId
                System.out.println("[SY-UPLOAD] set_id=$currentSetId childId=$childId completed=${completedLevelIds.sorted()}")

                fun tryUpload(withChildId: Boolean): Boolean {
                    val body = JSONObject().apply {
                        put("device_token", deviceToken)
                        if (withChildId && childId > 0) put("child_id", childId)
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
                            invokeResult(resp)
                            return true
                        } catch (_: Exception) {}
                    } else if (code == 404 && withChildId && childId > 0) {
                        // child_id bulunamadı; child_id olmadan tekrar dene
                        return false
                    } else {
                        // Diğer hatalarda da callback'i çağır (showRenewalError vs. tetiklensin)
                        try {
                            val resp = JSONObject().apply {
                                put("error", "http_$code")
                                put("auto_renewal_started", false)
                            }
                            invokeResult(resp)
                        } catch (_: Exception) {}
                    }
                    return true
                }

                val ok = tryUpload(true)
                if (!ok) {
                    System.out.println("[SY-UPLOAD] child_id=$childId not found, retrying without child_id")
                    tryUpload(false)
                    if (!callbackInvoked) {
                        System.out.println("[SY-UPLOAD] Resetting local childId from $childId")
                        prefManager.activeChildId = 0
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Level progress gönderme hatası: ${e.message}")
                if (!callbackInvoked) {
                    try {
                        invokeResult(JSONObject().put("error", "exception").put("auto_renewal_started", false))
                    } catch (_: Exception) {}
                }
            }
        }.start()
    }

    private fun clearLevelCacheAndReload() {
        completedLevelIds.clear()
        saveCompletedLevels()
        SecurePrefs.get(this, PREFS_NAME)
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

        // NOT: completedLevelIds ve cachedLevels ASLA silinmemeli!
        // Bu veriler kullanıcının seviye ilerlemesidir ve activity lifecycle'ına
        // bağlı değildir. onDestroy() silmek = kilit açma sonrası baştan başlamak.
        // Yeni set geldiğinde zaten fetchLevels() içinde güncellenir.

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
