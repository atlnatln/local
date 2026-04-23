package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * VPS API'sinden kullanıcıya özel soruları indirir, rotasyon mantığıyla sunar.
 *
 * Rotasyon kuralları:
 *   - Batch 0 (ücretsiz 50): her zaman erişilebilir, kayıt gerekmez.
 *   - Her kullanılan kredi 1 yeni batch açar (50 soru).
 *   - Yeni batch soruları önce gösterilir; hepsi çözülünce tüm erişilebilir sorular döner.
 *   - Tüm sorular çözüldüğünde resetProgress() çağrılır ve döngü baştan başlar.
 *
 * API: GET /api/mathlock/questions/?device_token=<uuid>
 * İlerleme: POST /api/mathlock/questions/progress/
 */
class QuestionManager(private val context: Context) {

    companion object {
        private const val TAG = "QuestionManager"
        private const val PREFS_NAME = "mathlock_questions"
        private const val KEY_CACHED_JSON_PREFIX = "cached_json_v2_child_" // child-specific cache
        private const val KEY_PENDING_SOLVED_PREFIX = "pending_solved_child_" // child-specific pending
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val CONNECT_TIMEOUT = 5000
        private const val READ_TIMEOUT = 10000
    }

    private val prefManager = PreferenceManager(context)

    /** Aktif çocuğa göre cache anahtarı */
    private fun cacheKey(): String {
        val childId = prefManager.activeChildId
        return if (childId > 0) "${KEY_CACHED_JSON_PREFIX}$childId" else "${KEY_CACHED_JSON_PREFIX}0"
    }

    /** Aktif çocuğa göre pending solved anahtarı */
    private fun pendingKey(): String {
        val childId = prefManager.activeChildId
        return if (childId > 0) "${KEY_PENDING_SOLVED_PREFIX}$childId" else "${KEY_PENDING_SOLVED_PREFIX}0"
    }

    data class JsonQuestion(
        val id: Int,
        val type: String,
        val text: String,
        val answer: Int,
        val difficulty: Int,
        val hint: String,
        val batch: Int = 0,
        val solved: Boolean = false,
    )

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    /** Mevcut rotasyon listesi (önce çözülmemiş/yeni, sonra hepsi döner). */
    private var rotationQueue: MutableList<JsonQuestion> = mutableListOf()
    private var currentRotationIndex = 0
    private var _isJsonMode = false
    private var _accessibleBatches: List<Int> = listOf(0)

    val isJsonMode get() = _isJsonMode

    /**
     * API'den soruları çek ve rotasyon sırasını oluştur.
     * IO thread'den çağır.
     * @return true ise JSON mode kullanılabilir
     */
    fun sync(deviceToken: String?): Boolean {
        if (deviceToken.isNullOrBlank()) {
            return loadFromCache()
        }

        return try {
            val childId = prefManager.activeChildId
            var apiUrl = "$API_BASE/questions/?device_token=${deviceToken.trim()}"
            if (childId > 0) apiUrl += "&child_id=$childId"
            val url = URL(apiUrl)
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = CONNECT_TIMEOUT
            conn.readTimeout = READ_TIMEOUT
            conn.requestMethod = "GET"

            if (conn.responseCode == 200) {
                val json = conn.inputStream.bufferedReader().readText()
                conn.disconnect()
                if (parseApiResponse(json)) {
                    prefs.edit().putString(cacheKey(), json).apply()
                    buildRotationQueue()
                    _isJsonMode = true
                    Log.d(TAG, "API'den indirildi: ${rotationQueue.size} soru, batches=$_accessibleBatches")
                    return true
                }
            }
            conn.disconnect()
            loadFromCache()
        } catch (e: Exception) {
            Log.w(TAG, "API bağlantısı başarısız: ${e.message}")
            loadFromCache()
        }
    }

    /** Eski imza: device_token olmadan çağrı — static JSON'dan yüklemeye benzer davranış. */
    fun sync(): Boolean = sync(null)

    private fun loadFromCache(): Boolean {
        val cached = prefs.getString(cacheKey(), null)
        if (cached != null && parseApiResponse(cached)) {
            // Bekleyen çözüm ID'lerini cache'deki veriye uygula
            val pending = getPendingSolvedIds()
            if (pending.isNotEmpty()) {
                _allQuestions = _allQuestions.map { q ->
                    if (q.id in pending) q.copy(solved = true) else q
                }
            }
            buildRotationQueue()
            _isJsonMode = true
            Log.d(TAG, "Cache'ten yüklendi: ${rotationQueue.size} soru (pending=${pending.size})")
            return true
        }
        _isJsonMode = false
        Log.d(TAG, "Soru bulunamadı, fallback mode")
        return false
    }

    private var _allQuestions: List<JsonQuestion> = emptyList()

    private fun parseApiResponse(json: String): Boolean {
        return try {
            val root = JSONObject(json)
            // API response formatı: { questions: [...], accessible_batches: [...] }
            // Eski format (sorgu.json): { version: ..., questions: [...] }
            val arr = root.getJSONArray("questions")
            val parsed = mutableListOf<JsonQuestion>()

            val batchesArr = root.optJSONArray("accessible_batches")
            _accessibleBatches = if (batchesArr != null) {
                (0 until batchesArr.length()).map { batchesArr.getInt(it) }
            } else {
                listOf(0)
            }

            for (i in 0 until arr.length()) {
                val q = arr.getJSONObject(i)
                parsed.add(
                    JsonQuestion(
                        id = q.getInt("id"),
                        type = q.optString("type", ""),
                        text = q.getString("text"),
                        answer = q.getInt("answer"),
                        difficulty = q.optInt("difficulty", 1),
                        hint = q.optString("hint", ""),
                        batch = q.optInt("batch", 0),
                        solved = q.optBoolean("solved", false),
                    )
                )
            }
            _allQuestions = parsed
            true
        } catch (e: Exception) {
            Log.e(TAG, "JSON parse hatası: ${e.message}")
            false
        }
    }

    /**
     * Rotasyon sırasını oluştur:
     *   1. En yüksek batch'te çözülmemiş sorular (yeni içerik önce)
     *   2. Diğer batch'lerde çözülmemiş sorular
     *   3. Tüm sorular (döngü)
     *
     * Eğer hiç çözülmemiş soru yoksa tüm sorular sıfırlanır ve tamamı döner.
     */
    private fun buildRotationQueue() {
        val unsolvedByBatch = _allQuestions
            .filter { !it.solved }
            .sortedWith(compareByDescending<JsonQuestion> { it.batch }.thenBy { it.id })

        if (unsolvedByBatch.isNotEmpty()) {
            rotationQueue = unsolvedByBatch.toMutableList()
        } else {
            // Tüm sorular çözüldü → rotasyonu sıfırla, hepsini döndür
            rotationQueue = _allQuestions.toMutableList()
        }
        currentRotationIndex = 0
    }

    /** Sıradaki soruyu getir. Rotasyon bittiğinde döngüyü baştan başlatır. */
    fun nextQuestion(): JsonQuestion? {
        if (rotationQueue.isEmpty()) return null

        if (currentRotationIndex >= rotationQueue.size) {
            // Döngü bitti → bir sonraki sync'e kadar baştan döndür
            currentRotationIndex = 0
        }
        return rotationQueue[currentRotationIndex++]
    }

    /** Belirli bir index'teki soruyu al (peek, index ilerlemez) */
    fun peekQuestion(index: Int): JsonQuestion? = rotationQueue.getOrNull(index)

    fun totalCount() = rotationQueue.size
    fun solvedCount() = _allQuestions.count { it.solved }
    fun isSetComplete() = rotationQueue.isNotEmpty() && currentRotationIndex >= rotationQueue.size
    fun getVersion() = _accessibleBatches.maxOrNull() ?: 0
    fun accessibleBatches() = _accessibleBatches

    /**
     * Soru çözüldü — pending listesine ekle (sonraki sync'te API'ye bildir).
     * Thread-safe değil, UI thread veya tek IO thread'den çağır.
     */
    fun markSolved(questionId: Int) {
        val pending = getPendingSolvedIds().toMutableSet()
        pending.add(questionId)
        prefs.edit().putString(pendingKey(), pending.joinToString(",")).apply()

        // Lokal listede de güncelle
        _allQuestions = _allQuestions.map {
            if (it.id == questionId) it.copy(solved = true) else it
        }
    }

    /**
     * Bekleyen çözüm ID'lerini sunucuya gönder.
     * IO thread'den çağır.
     */
    fun uploadProgress(deviceToken: String): Boolean {
        val pendingIds = getPendingSolvedIds()
        if (pendingIds.isEmpty()) return true

        return try {
            val url = URL("$API_BASE/questions/progress/")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.connectTimeout = CONNECT_TIMEOUT
            conn.readTimeout = READ_TIMEOUT

            val body = JSONObject().apply {
                put("device_token", deviceToken)
                val childId = prefManager.activeChildId
                if (childId > 0) put("child_id", childId)
                val arr = JSONArray()
                pendingIds.forEach { arr.put(it) }
                put("solved_questions", arr)
            }
            conn.outputStream.bufferedWriter().use { it.write(body.toString()) }
            val code = conn.responseCode
            conn.disconnect()

            if (code in 200..299) {
                prefs.edit().remove(pendingKey()).apply()
                Log.d(TAG, "İlerleme gönderildi: ${pendingIds.size} soru")
                true
            } else {
                Log.w(TAG, "İlerleme gönderme başarısız: $code")
                false
            }
        } catch (e: Exception) {
            Log.w(TAG, "İlerleme gönderme hatası: ${e.message}")
            false
        }
    }

    private fun getPendingSolvedIds(): Set<Int> {
        val raw = prefs.getString(pendingKey(), "") ?: ""
        if (raw.isBlank()) return emptySet()
        return raw.split(",").mapNotNull { it.trim().toIntOrNull() }.toSet()
    }

    /** Mevcut rotasyonu sıfırla (yeni batch açılınca veya set tamamlanınca) */
    fun resetProgress() {
        currentRotationIndex = 0
        buildRotationQueue()
    }
}

