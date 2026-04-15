package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * Her sorunun sonucunu kaydeder, 50 tamamlanınca VPS'e yükler.
 * Veriler SharedPreferences'da persist edilir (uygulama kapansa da kaybolmaz).
 */
class StatsTracker(private val context: Context) {

    companion object {
        private const val TAG = "StatsTracker"
        private const val PREFS_NAME = "mathlock_stats"
        private const val KEY_RESULTS = "saved_results"
        private const val KEY_TOTAL_CORRECT = "total_correct_alltime"
        private const val KEY_TOTAL_SHOWN = "total_shown_alltime"
        private const val UPLOAD_URL = "http://89.252.152.222/mathlock/data/stats.json"
    }

    data class QuestionResult(
        val questionId: Int,
        val type: String,
        val difficulty: Int,
        val correct: Boolean,
        val attempts: Int,
        val timeSeconds: Double,
        val sawHint: Boolean,
        val sawTopic: Boolean
    )

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val results = mutableListOf<QuestionResult>()

    init {
        loadSaved()
    }

    fun addResult(result: QuestionResult) {
        results.add(result)
        // Tüm zamanlar istatistiği
        val allCorrect = prefs.getInt(KEY_TOTAL_CORRECT, 0) + if (result.correct) 1 else 0
        val allShown = prefs.getInt(KEY_TOTAL_SHOWN, 0) + 1
        prefs.edit()
            .putInt(KEY_TOTAL_CORRECT, allCorrect)
            .putInt(KEY_TOTAL_SHOWN, allShown)
            .apply()
        save()
    }

    fun currentSetSize() = results.size

    /**
     * VPS'e stats.json yükle. IO thread'den çağır.
     * @return true: yükleme başarılı ve local state temizlendi
     */
    fun uploadStats(questionVersion: Int): Boolean {
        val json = buildStatsJson(questionVersion)
        return try {
            val conn = URL(UPLOAD_URL).openConnection() as HttpURLConnection
            conn.requestMethod = "PUT"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.connectTimeout = 5000
            conn.readTimeout = 10000
            OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(json) }
            val code = conn.responseCode
            conn.disconnect()
            if (code in 200..299) {
                results.clear()
                prefs.edit().remove(KEY_RESULTS).apply()
                Log.d(TAG, "Stats başarıyla yüklendi (v$questionVersion)")
                true
            } else {
                Log.w(TAG, "Stats yükleme başarısız: HTTP $code")
                false
            }
        } catch (e: Exception) {
            Log.w(TAG, "Stats yükleme hatası: ${e.message}")
            false
        }
    }

    private fun buildStatsJson(questionVersion: Int): String {
        val root = JSONObject()
        root.put("questionVersion", questionVersion)
        root.put("completedAt", System.currentTimeMillis() / 1000)
        root.put("totalShown", results.size)
        root.put("totalCorrect", results.count { it.correct })

        // Tip bazlı
        val byType = JSONObject()
        results.groupBy { it.type }.forEach { (type, items) ->
            val t = JSONObject()
            t.put("shown", items.size)
            t.put("correct", items.count { it.correct })
            t.put("avgTime", "%.1f".format(items.map { it.timeSeconds }.average()))
            t.put("hintUsed", items.count { it.sawHint })
            t.put("topicUsed", items.count { it.sawTopic })
            byType.put(type, t)
        }
        root.put("byType", byType)

        // Zorluk bazlı
        val byDifficulty = JSONObject()
        results.groupBy { it.difficulty }.forEach { (diff, items) ->
            val d = JSONObject()
            d.put("shown", items.size)
            d.put("correct", items.count { it.correct })
            byDifficulty.put(diff.toString(), d)
        }
        root.put("byDifficulty", byDifficulty)

        // Detay dizisi
        val details = JSONArray()
        results.forEach { r ->
            val d = JSONObject()
            d.put("questionId", r.questionId)
            d.put("correct", r.correct)
            d.put("attempts", r.attempts)
            d.put("time", "%.1f".format(r.timeSeconds))
            d.put("sawHint", r.sawHint)
            d.put("sawTopic", r.sawTopic)
            details.put(d)
        }
        root.put("details", details)

        return root.toString(2)
    }

    private fun save() {
        val arr = JSONArray()
        results.forEach { r ->
            val j = JSONObject()
            j.put("qid", r.questionId)
            j.put("type", r.type)
            j.put("diff", r.difficulty)
            j.put("ok", r.correct)
            j.put("att", r.attempts)
            j.put("t", r.timeSeconds)
            j.put("hint", r.sawHint)
            j.put("topic", r.sawTopic)
            arr.put(j)
        }
        prefs.edit().putString(KEY_RESULTS, arr.toString()).apply()
    }

    private fun loadSaved() {
        val saved = prefs.getString(KEY_RESULTS, null) ?: return
        try {
            val arr = JSONArray(saved)
            for (i in 0 until arr.length()) {
                val j = arr.getJSONObject(i)
                results.add(
                    QuestionResult(
                        questionId = j.getInt("qid"),
                        type = j.getString("type"),
                        difficulty = j.getInt("diff"),
                        correct = j.getBoolean("ok"),
                        attempts = j.getInt("att"),
                        timeSeconds = j.getDouble("t"),
                        sawHint = j.getBoolean("hint"),
                        sawTopic = j.getBoolean("topic")
                    )
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "Saved stats parse hatası: ${e.message}")
        }
    }
}
