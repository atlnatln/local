package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * VPS'ten questions.json indirir, local cache'ler, sırayla sunar.
 * Fallback: ağ yoksa cache'ten, cache yoksa MathQuestionGenerator'a düşer.
 */
class QuestionManager(private val context: Context) {

    companion object {
        private const val TAG = "QuestionManager"
        private const val PREFS_NAME = "mathlock_questions"
        private const val KEY_CACHED_JSON = "cached_json"
        private const val KEY_CURRENT_INDEX = "current_index"
        private const val KEY_VERSION = "cached_version"
        private const val BASE_URL = "http://89.252.152.222/mathlock/data"
        private const val CONNECT_TIMEOUT = 5000
        private const val READ_TIMEOUT = 10000
    }

    data class JsonQuestion(
        val id: Int,
        val type: String,
        val text: String,
        val answer: Int,
        val difficulty: Int,
        val hint: String
    )

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private var questions: List<JsonQuestion> = emptyList()
    private var currentIndex: Int = 0
    private var version: Int = 0
    private var _isJsonMode = false

    val isJsonMode get() = _isJsonMode

    /**
     * VPS'ten questions.json indir ve parse et.
     * IO thread'den çağır.
     * @return true ise JSON mode aktif, false ise fallback'e düş
     */
    fun sync(): Boolean {
        // Önce ağdan dene
        try {
            val url = URL("$BASE_URL/questions.json")
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = CONNECT_TIMEOUT
            conn.readTimeout = READ_TIMEOUT
            conn.requestMethod = "GET"

            if (conn.responseCode == 200) {
                val json = conn.inputStream.bufferedReader().readText()
                conn.disconnect()
                if (parseQuestions(json)) {
                    prefs.edit().putString(KEY_CACHED_JSON, json).apply()
                    currentIndex = prefs.getInt(KEY_CURRENT_INDEX, 0)
                    _isJsonMode = true
                    Log.d(TAG, "VPS'ten indirildi: v$version, ${questions.size} soru, index=$currentIndex")
                    return true
                }
            }
            conn.disconnect()
        } catch (e: Exception) {
            Log.w(TAG, "VPS bağlantısı başarısız: ${e.message}")
        }

        // Ağ başarısızsa cache'ten yükle
        return loadFromCache()
    }

    private fun loadFromCache(): Boolean {
        val cached = prefs.getString(KEY_CACHED_JSON, null)
        if (cached != null && parseQuestions(cached)) {
            currentIndex = prefs.getInt(KEY_CURRENT_INDEX, 0)
            _isJsonMode = true
            Log.d(TAG, "Cache'ten yüklendi: v$version, ${questions.size} soru, index=$currentIndex")
            return true
        }
        _isJsonMode = false
        Log.d(TAG, "JSON bulunamadı, fallback mode")
        return false
    }

    private fun parseQuestions(json: String): Boolean {
        return try {
            val root = JSONObject(json)
            version = root.getInt("version")
            val arr = root.getJSONArray("questions")
            val parsed = mutableListOf<JsonQuestion>()
            for (i in 0 until arr.length()) {
                val q = arr.getJSONObject(i)
                parsed.add(
                    JsonQuestion(
                        id = q.getInt("id"),
                        type = q.getString("type"),
                        text = q.getString("text"),
                        answer = q.getInt("answer"),
                        difficulty = q.getInt("difficulty"),
                        hint = q.getString("hint")
                    )
                )
            }
            questions = parsed
            prefs.edit().putInt(KEY_VERSION, version).apply()
            true
        } catch (e: Exception) {
            Log.e(TAG, "JSON parse hatası: ${e.message}")
            false
        }
    }

    /** Sıradaki soruyu getir. Set tamamlandıysa null döner. */
    fun nextQuestion(): JsonQuestion? {
        if (currentIndex >= questions.size) return null
        val q = questions[currentIndex]
        currentIndex++
        prefs.edit().putInt(KEY_CURRENT_INDEX, currentIndex).apply()
        return q
    }

    /** Belirli bir index'teki soruyu al (peek, index ilerlemez) */
    fun peekQuestion(index: Int): JsonQuestion? {
        return questions.getOrNull(index)
    }

    fun totalCount() = questions.size
    fun solvedCount() = currentIndex
    fun isSetComplete() = questions.isNotEmpty() && currentIndex >= questions.size
    fun getVersion() = version

    /** Yeni set başlat (50 soru tamamlanınca) */
    fun resetProgress() {
        currentIndex = 0
        prefs.edit().putInt(KEY_CURRENT_INDEX, 0).apply()
    }
}
