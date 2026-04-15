package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONObject

/**
 * Offline mod: assets'teki topics.json'dan konu anlatımlarını yükler.
 */
class TopicHelper(private val context: Context) {

    companion object {
        private const val TAG = "TopicHelper"
        private const val PREFS_NAME = "mathlock_topics"
        private const val KEY_CACHED = "cached_topics"
    }

    data class TopicExplanation(
        val type: String,
        val title: String,
        val explanation: String,
        val example: String,
        val tips: List<String>
    )

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val topics = mutableMapOf<String, TopicExplanation>()

    /**
     * Offline mod: assets'ten topics.json yükle.
     */
    fun sync(): Boolean {
        if (loadFromCache()) return true
        return loadFromAssets()
    }

    private fun loadFromAssets(): Boolean {
        return try {
            val json = context.assets.open("topics.json").bufferedReader().readText()
            if (parseTopics(json)) {
                prefs.edit().putString(KEY_CACHED, json).apply()
                Log.d(TAG, "Assets'ten yüklendi: ${topics.size} konu")
                true
            } else false
        } catch (e: Exception) {
            Log.e(TAG, "Assets yükleme hatası: ${e.message}")
            false
        }
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
