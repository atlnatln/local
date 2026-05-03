package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Konu anlatımlarını topics.json'dan yükler.
 * Çocuk yanlış cevap verdiğinde ilgili konunun açıklamasını gösterir.
 */
class TopicHelper(private val context: Context) {

    companion object {
        private const val TAG = "TopicHelper"
        private const val PREFS_NAME = "mathlock_topics"
        private const val KEY_CACHED = "cached_topics"
        private const val BASE_URL = "https://mathlock.com.tr/mathlock/data"
    }

    data class TopicExplanation(
        val type: String,
        val title: String,
        val explanation: String,
        val example: String,
        val tips: List<String>
    )

    private val prefs = SecurePrefs.get(context, PREFS_NAME)
    private val topics = mutableMapOf<String, TopicExplanation>()

    /**
     * VPS'ten topics.json indir ve cache'le.
     * IO thread'den çağır.
     */
    fun sync(): Boolean {
        try {
            val url = URL("$BASE_URL/topics.json")
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = 5000
            conn.readTimeout = 10000
            if (conn.responseCode == 200) {
                val json = conn.inputStream.bufferedReader().readText()
                conn.disconnect()
                if (parseTopics(json)) {
                    prefs.edit().putString(KEY_CACHED, json).apply()
                    Log.d(TAG, "VPS'ten indirildi: ${topics.size} konu")
                    return true
                }
            }
            conn.disconnect()
        } catch (e: Exception) {
            Log.w(TAG, "VPS bağlantısı başarısız: ${e.message}")
        }
        return loadFromCache()
    }

    fun getTopicFor(questionType: String): TopicExplanation? = topics[questionType]

    private fun loadFromCache(): Boolean {
        val cached = prefs.getString(KEY_CACHED, null)
        if (cached != null && parseTopics(cached)) {
            Log.d(TAG, "Cache'ten yüklendi: ${topics.size} konu")
            return true
        }
        return false
    }

    private fun parseTopics(json: String): Boolean {
        return try {
            val root = JSONObject(json)
            topics.clear()
            for (key in root.keys()) {
                val t = root.getJSONObject(key)
                val tips = mutableListOf<String>()
                val tipsArr = t.getJSONArray("tips")
                for (j in 0 until tipsArr.length()) tips.add(tipsArr.getString(j))
                topics[key] = TopicExplanation(
                    type = key,
                    title = t.getString("title"),
                    explanation = t.getString("explanation"),
                    example = t.getString("example"),
                    tips = tips
                )
            }
            true
        } catch (e: Exception) {
            Log.e(TAG, "Topics parse hatası: ${e.message}")
            false
        }
    }
}
