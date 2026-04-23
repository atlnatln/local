package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

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
        private const val KEY_LAST_UPLOADED_TIME = "last_uploaded_time"
        private const val API_STATS_URL = "https://mathlock.com.tr/api/mathlock/stats/"
    }

    private val prefManager = PreferenceManager(context)
    private var sessionStartTime: Long = 0

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

    /** Oturumu başlat — MathChallengeActivity açılışında çağır */
    fun startSession() {
        sessionStartTime = System.currentTimeMillis()
    }

    /** Oturumu bitir — günlük süreyi biriktir */
    fun endSession() {
        if (sessionStartTime <= 0) return
        val durationSec = (System.currentTimeMillis() - sessionStartTime) / 1000
        sessionStartTime = 0
        if (durationSec <= 0) return
        val today = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        val key = "time_$today"
        val dailyTotal = prefs.getLong(key, 0) + durationSec
        prefs.edit().putLong(key, dailyTotal).apply()
    }

    /** Bugünkü toplam çalışma süresi (saniye) */
    fun todayTimeSeconds(): Long {
        val today = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        return prefs.getLong("time_$today", 0)
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
     * Backend API'ye stats yükle. IO thread'den çağır.
     * @return true: yükleme başarılı ve local state temizlendi
     */
    fun uploadStats(questionVersion: Int): Boolean {
        val statsJson = buildStatsJson(questionVersion)
        val accountPrefs = context.getSharedPreferences("mathlock_account", Context.MODE_PRIVATE)
        val deviceToken = accountPrefs.getString("device_token", null)
        if (deviceToken == null) {
            Log.w(TAG, "device_token yok — stats yüklenemedi")
            return false
        }
        val childName = prefManager.activeChildName ?: "Çocuk"
        val totalTime = todayTimeSeconds()
        val lastUploaded = prefs.getLong(KEY_LAST_UPLOADED_TIME, 0)
        val sessionTimeDelta = (totalTime - lastUploaded).coerceAtLeast(0)

        // API endpoint'ine POST
        val apiBody = JSONObject().apply {
            put("device_token", deviceToken)
            put("child_name", childName)
            put("question_version", questionVersion)
            put("session_time_seconds", sessionTimeDelta)
            put("stats", JSONObject(statsJson))
        }

        return try {
            val conn = URL(API_STATS_URL).openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.connectTimeout = 5000
            conn.readTimeout = 10000
            OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(apiBody.toString()) }
            val code = conn.responseCode
            conn.disconnect()
            if (code in 200..299) {
                results.clear()
                prefs.edit()
                    .remove(KEY_RESULTS)
                    .putLong(KEY_LAST_UPLOADED_TIME, totalTime)
                    .apply()
                Log.d(TAG, "Stats API'ye yüklendi (v$questionVersion)")
                true
            } else {
                Log.w(TAG, "Stats API yükleme başarısız: HTTP $code")
                false
            }
        } catch (e: Exception) {
            Log.w(TAG, "Stats API yükleme hatası: ${e.message}")
            false
        }
    }

    fun buildStatsJson(questionVersion: Int): String {
        val root = JSONObject()
        root.put("questionVersion", questionVersion)
        root.put("completedAt", System.currentTimeMillis() / 1000)
        root.put("totalShown", results.size)
        root.put("totalCorrect", results.count { it.correct })
        val childId = prefManager.activeChildId
        if (childId > 0) root.put("childId", childId)
        root.put("educationPeriod", prefManager.activeEducationPeriod)

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
