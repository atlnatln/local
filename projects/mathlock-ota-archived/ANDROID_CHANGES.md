# MathLock Android — Adaptif AI Soru Sistemi Değişiklikleri

Bu doküman, VPS tarafındaki AI soru üretim sistemi ile Android uygulamasının entegrasyonu için gerekli değişiklikleri tanımlar.

## Genel Akış

```
┌──────────────────────────────────────────────────────────────────┐
│               📱 Telefon (Android)                               │
│                                                                  │
│  1. Uygulama açılır → questions.json + topics.json indirilir     │
│  2. Kilitli uygulama açılırsa → JSON'dan sırayla soru gösterilir │
│  3. Yanlış cevap → ipucu göster → hâlâ yanlışsa konu anlatımı   │
│  4. 50 soru tamamlanınca → stats.json VPS'e POST edilir          │
│  5. Yeni questions.json otomatik kontrol edilir                  │
└───────────────────────────────────────┬──────────────────────────┘
                                        │ stats.json
                                        ▼
┌──────────────────────────────────────────────────────────────────┐
│               🖥️ VPS Sunucusu                                    │
│                                                                  │
│  nginx endpoint'leri:                                            │
│    GET  /mathlock/data/questions.json  → sorular                 │
│    GET  /mathlock/data/topics.json     → konu anlatımları        │
│    PUT  /mathlock/data/stats.json      → istatistik yükleme      │
│                                                                  │
│  ai-generate.sh (cron veya webhook ile tetiklenir):              │
│    stats.json analiz → Copilot yeni 50 soru üretir → doğrula    │
└──────────────────────────────────────────────────────────────────┘
```

## Yeni Dosyalar

### 1. `util/QuestionManager.kt`
JSON soru setini VPS'ten indirir, local'de cache'ler, sırayla sunar.

```kotlin
package com.akn.mathlock.util

import android.content.Context
import org.json.JSONObject
import java.net.URL

data class JsonQuestion(
    val id: Int,
    val type: String,        // "toplama", "cikarma", "carpma", "bolme", "siralama", "eksik_sayi"
    val text: String,         // "7 + 5 = ?"
    val answer: Int,
    val difficulty: Int,      // 1-5
    val hint: String          // "Parmakla say: 7 parmak + 5 parmak"
)

class QuestionManager(private val context: Context) {
    private val prefs = context.getSharedPreferences("mathlock_questions", Context.MODE_PRIVATE)
    private val baseUrl = "http://89.252.152.222/mathlock/data"
    
    private var questions: List<JsonQuestion> = emptyList()
    private var currentIndex: Int = 0
    private var version: Int = 0
    
    /**
     * VPS'ten questions.json indir, parse et, cache'le.
     * Arka planda çağır (IO thread).
     */
    fun sync(): Boolean {
        return try {
            val json = URL("$baseUrl/questions.json").readText()
            val parsed = parseQuestions(json)
            if (parsed.isNotEmpty()) {
                // Cache'e kaydet
                prefs.edit()
                    .putString("cached_json", json)
                    .putInt("version", version)
                    .apply()
                questions = parsed
                currentIndex = prefs.getInt("current_index", 0)
                true
            } else false
        } catch (e: Exception) {
            // Ağ hatası → cache'ten yükle
            loadFromCache()
        }
    }
    
    private fun loadFromCache(): Boolean {
        val cached = prefs.getString("cached_json", null) ?: return false
        questions = parseQuestions(cached)
        currentIndex = prefs.getInt("current_index", 0)
        return questions.isNotEmpty()
    }
    
    private fun parseQuestions(json: String): List<JsonQuestion> {
        val root = JSONObject(json)
        version = root.getInt("version")
        val arr = root.getJSONArray("questions")
        return (0 until arr.length()).map { i ->
            val q = arr.getJSONObject(i)
            JsonQuestion(
                id = q.getInt("id"),
                type = q.getString("type"),
                text = q.getString("text"),
                answer = q.getInt("answer"),
                difficulty = q.getInt("difficulty"),
                hint = q.getString("hint")
            )
        }
    }
    
    /** Sıradaki soruyu getir. 50 tamamlandıysa null döner. */
    fun nextQuestion(): JsonQuestion? {
        if (currentIndex >= questions.size) return null
        val q = questions[currentIndex]
        currentIndex++
        prefs.edit().putInt("current_index", currentIndex).apply()
        return q
    }
    
    /** Toplam soru sayısı */
    fun totalCount() = questions.size
    
    /** Çözülen soru sayısı */
    fun solvedCount() = currentIndex
    
    /** Tüm 50 soru tamamlandı mı? */
    fun isSetComplete() = currentIndex >= questions.size
    
    /** Yeni set başlat (index sıfırla) */
    fun resetProgress() {
        currentIndex = 0
        prefs.edit().putInt("current_index", 0).apply()
    }
    
    /** Mevcut version */
    fun getVersion() = version
}
```

### 2. `util/StatsTracker.kt`
Her soru için sonucu kaydeder, 50 tamamlanınca VPS'e yükler.

```kotlin
package com.akn.mathlock.util

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

data class QuestionResult(
    val questionId: Int,
    val type: String,
    val difficulty: Int,
    val correct: Boolean,
    val attempts: Int,         // Kaç denemede doğru bildi
    val timeSeconds: Double,   // Cevaplama süresi
    val sawHint: Boolean,      // İpucu gösterildi mi
    val sawTopic: Boolean      // Konu anlatımı gösterildi mi
)

class StatsTracker(private val context: Context) {
    private val prefs = context.getSharedPreferences("mathlock_stats", Context.MODE_PRIVATE)
    private val results = mutableListOf<QuestionResult>()
    private val uploadUrl = "http://89.252.152.222/mathlock/data/stats.json"
    
    init { loadSaved() }
    
    fun addResult(result: QuestionResult) {
        results.add(result)
        save()
    }
    
    /**
     * VPS'e stats.json yükle. 50 soru tamamlanınca çağır.
     * Arka planda çağır (IO thread).
     */
    fun uploadStats(questionVersion: Int): Boolean {
        val json = buildStatsJson(questionVersion)
        return try {
            val conn = URL(uploadUrl).openConnection() as HttpURLConnection
            conn.requestMethod = "PUT"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true
            conn.connectTimeout = 5000
            conn.readTimeout = 10000
            OutputStreamWriter(conn.outputStream).use { it.write(json) }
            val code = conn.responseCode
            conn.disconnect()
            if (code in 200..299) {
                // Başarılı → local state temizle
                results.clear()
                prefs.edit().remove("saved_results").apply()
                true
            } else false
        } catch (e: Exception) {
            false // Ağ hatası — sonra tekrar denenecek
        }
    }
    
    private fun buildStatsJson(questionVersion: Int): String {
        val root = JSONObject()
        root.put("questionVersion", questionVersion)
        root.put("completedAt", System.currentTimeMillis() / 1000)
        root.put("totalShown", results.size)
        root.put("totalCorrect", results.count { it.correct })
        
        // Tip bazlı istatistikler
        val byType = JSONObject()
        results.groupBy { it.type }.forEach { (type, items) ->
            val t = JSONObject()
            t.put("shown", items.size)
            t.put("correct", items.count { it.correct })
            t.put("avgTime", items.map { it.timeSeconds }.average())
            t.put("hintUsed", items.count { it.sawHint })
            t.put("topicUsed", items.count { it.sawTopic })
            byType.put(type, t)
        }
        root.put("byType", byType)
        
        // Zorluk bazlı istatistikler
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
            d.put("time", r.timeSeconds)
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
        prefs.edit().putString("saved_results", arr.toString()).apply()
    }
    
    private fun loadSaved() {
        val saved = prefs.getString("saved_results", null) ?: return
        val arr = JSONArray(saved)
        for (i in 0 until arr.length()) {
            val j = arr.getJSONObject(i)
            results.add(QuestionResult(
                questionId = j.getInt("qid"),
                type = j.getString("type"),
                difficulty = j.getInt("diff"),
                correct = j.getBoolean("ok"),
                attempts = j.getInt("att"),
                timeSeconds = j.getDouble("t"),
                sawHint = j.getBoolean("hint"),
                sawTopic = j.getBoolean("topic")
            ))
        }
    }
}
```

### 3. `util/TopicHelper.kt`
Konu anlatımlarını topics.json'dan yükler.

```kotlin
package com.akn.mathlock.util

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.net.URL

data class TopicExplanation(
    val type: String,
    val title: String,
    val explanation: String,
    val example: String,
    val tips: List<String>
)

class TopicHelper(private val context: Context) {
    private val prefs = context.getSharedPreferences("mathlock_topics", Context.MODE_PRIVATE)
    private var topics = mutableMapOf<String, TopicExplanation>()
    
    fun sync(): Boolean {
        return try {
            val json = URL("http://89.252.152.222/mathlock/data/topics.json").readText()
            parseAndCache(json)
            true
        } catch (e: Exception) {
            loadFromCache()
        }
    }
    
    fun getTopicFor(questionType: String): TopicExplanation? = topics[questionType]
    
    private fun parseAndCache(json: String) {
        prefs.edit().putString("cached_topics", json).apply()
        parseTopics(json)
    }
    
    private fun loadFromCache(): Boolean {
        val cached = prefs.getString("cached_topics", null) ?: return false
        parseTopics(cached)
        return topics.isNotEmpty()
    }
    
    private fun parseTopics(json: String) {
        val arr = JSONArray(json)
        for (i in 0 until arr.length()) {
            val t = arr.getJSONObject(i)
            val tips = mutableListOf<String>()
            val tipsArr = t.getJSONArray("tips")
            for (j in 0 until tipsArr.length()) tips.add(tipsArr.getString(j))
            
            val topic = TopicExplanation(
                type = t.getString("type"),
                title = t.getString("title"),
                explanation = t.getString("explanation"),
                example = t.getString("example"),
                tips = tips
            )
            topics[topic.type] = topic
        }
    }
}
```

## Mevcut Dosya Değişiklikleri

### 4. `MathChallengeActivity.kt` — Kapsamlı Güncelleme

**Mevcut davranış:** Random `MathQuestionGenerator` ile 5 soru üretir.

**Yeni davranış:**
- `QuestionManager`'dan sıradaki soruyu çeker (JSON tabanlı)
- Yanlış cevap → **ipucu** gösterir (soru'nun `hint` alanı)
- İpucu sonrası tekrar yanlış → **konu anlatımı** dialogu gösterir
- Her cevap `StatsTracker`'a kaydedilir
- 50 soru tamamlanınca arka planda stats upload başlar

```kotlin
// === TEMEL DEĞİŞİKLİKLER ===

class MathChallengeActivity : AppCompatActivity() {
    private lateinit var questionManager: QuestionManager
    private lateinit var statsTracker: StatsTracker
    private lateinit var topicHelper: TopicHelper
    
    private var currentQuestion: JsonQuestion? = null
    private var attempts = 0
    private var startTime = 0L
    private var sawHint = false
    private var sawTopic = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ...
        questionManager = QuestionManager(this)
        statsTracker = StatsTracker(this)
        topicHelper = TopicHelper(this)
        
        // İlk sync (cache varsa hızlı)
        Thread {
            questionManager.sync()
            topicHelper.sync()
            runOnUiThread { showNextQuestion() }
        }.start()
    }
    
    private fun showNextQuestion() {
        currentQuestion = questionManager.nextQuestion()
        if (currentQuestion == null) {
            // 50 soru tamamlandı!
            onSetComplete()
            return
        }
        
        val q = currentQuestion!!
        questionText.text = q.text
        answerInput.text.clear()
        hintText.visibility = View.GONE
        attempts = 0
        sawHint = false
        sawTopic = false
        startTime = System.currentTimeMillis()
        
        // İlerleme göster: "Soru 23/50"
        progressText.text = "${questionManager.solvedCount()}/${questionManager.totalCount()}"
    }
    
    private fun checkAnswer() {
        val userAnswer = answerInput.text.toString().toIntOrNull() ?: return
        val q = currentQuestion ?: return
        val elapsed = (System.currentTimeMillis() - startTime) / 1000.0
        attempts++
        
        if (userAnswer == q.answer) {
            // ✅ Doğru!
            showCorrectFeedback()
            statsTracker.addResult(QuestionResult(
                questionId = q.id, type = q.type, difficulty = q.difficulty,
                correct = true, attempts = attempts, timeSeconds = elapsed,
                sawHint = sawHint, sawTopic = sawTopic
            ))
            // Kilitli uygulamayı aç (mevcut unlock mantığını koru)
            unlockAndLaunch()
        } else {
            // ❌ Yanlış
            if (attempts == 1 && !sawHint) {
                // İlk yanlış → ipucu göster
                showHint(q.hint)
                sawHint = true
            } else if (attempts >= 2 && !sawTopic) {
                // İkinci yanlış → konu anlatımı
                showTopicExplanation(q.type)
                sawTopic = true
            } else {
                // Devam et, doğru cevabı küçük bir süre göster
                showWrongFeedback(q.answer)
                statsTracker.addResult(QuestionResult(
                    questionId = q.id, type = q.type, difficulty = q.difficulty,
                    correct = false, attempts = attempts, timeSeconds = elapsed,
                    sawHint = sawHint, sawTopic = sawTopic
                ))
            }
        }
    }
    
    private fun showHint(hint: String) {
        hintText.text = "💡 $hint"
        hintText.visibility = View.VISIBLE
        // Titreşim geri bildirimi
    }
    
    private fun showTopicExplanation(questionType: String) {
        val topic = topicHelper.getTopicFor(questionType) ?: return
        
        AlertDialog.Builder(this)
            .setTitle("📚 ${topic.title}")
            .setMessage(buildTopicMessage(topic))
            .setPositiveButton("Anladım! ✨") { _, _ -> }
            .setCancelable(false)
            .show()
    }
    
    private fun buildTopicMessage(topic: TopicExplanation): CharSequence {
        return buildString {
            appendLine(topic.explanation)
            appendLine()
            appendLine("📝 Örnek:")
            appendLine(topic.example)
            appendLine()
            topic.tips.forEach { tip ->
                appendLine("• $tip")
            }
        }
    }
    
    private fun onSetComplete() {
        // 50 soru tamamlandı — stats yükle
        Thread {
            val uploaded = statsTracker.uploadStats(questionManager.getVersion())
            runOnUiThread {
                if (uploaded) {
                    // Başarılı → yeni set bekle
                    questionManager.resetProgress()
                    Toast.makeText(this, "🎉 Harika! 50 soruyu tamamladın!", Toast.LENGTH_LONG).show()
                }
            }
        }.start()
    }
}
```

### 5. `res/layout/activity_math_challenge.xml` — Yeni Elemanlar

Mevcut layout'a eklenmesi gereken bileşenler:

```xml
<!-- İlerleme çubuğu -->
<ProgressBar
    android:id="@+id/progressBar"
    style="?android:attr/progressBarStyleHorizontal"
    android:layout_width="match_parent"
    android:layout_height="8dp"
    android:max="50"
    android:progress="0" />

<!-- Soru numarası: "Soru 12/50" -->
<TextView
    android:id="@+id/progressText"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="14sp"
    android:textColor="#666" />

<!-- İpucu alanı (varsayılan gizli) -->
<TextView
    android:id="@+id/hintText"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:visibility="gone"
    android:textSize="16sp"
    android:textColor="#FF9800"
    android:background="#FFF3E0"
    android:padding="12dp"
    android:layout_marginTop="8dp" />

<!-- Konu anlatımı butonu (yanlış cevap sonrası görünür) -->
<Button
    android:id="@+id/topicButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="📚 Konu Anlatımı"
    android:visibility="gone" />
```

## VPS Tarafı Tamamlanan İşler

| Dosya | Durum | Açıklama |
|-------|-------|----------|
| `AGENTS.md` | ✅ | 2. sınıf kuralları, 6 soru tipi, zorluk yönetimi |
| `data/questions.json` | ✅ | 50 soru, toplama(20)+cikarma(15)+carpma(8)+bolme(4)+siralama(2)+eksik_sayi(1) |
| `data/topics.json` | ✅ | 6 konu anlatımı, emoji'li çocuk dostu açıklamalar |
| `validate-questions.py` | ✅ | Tam doğrulama: matematik, şema, kurallar |
| `ai-generate.sh` | ✅ | Arşivle → Copilot üret → doğrula → retry → VPS sync |
| `deploy.sh` | ✅ | Data sync eklendi (questions.json + topics.json) |
| `mathlock.conf` (nginx) | ✅ | `/mathlock/data/` endpoint eklendi |
| `docker-compose.yml` | ✅ | Data volume mount eklendi |

## Otomasyon Tetikleme Seçenekleri

### Seçenek A: Cron (basit)
```bash
# Her gün 03:00'te stats.json varsa ai-generate çalıştır
0 3 * * * [ -f /home/akn/vps/projects/mathlock/data/stats.json ] && /home/akn/vps/projects/mathlock/ai-generate.sh >> /var/log/mathlock-ai.log 2>&1
```

### Seçenek B: stats.json upload webhook
Telefon stats yüklediğinde nginx → script tetikle (daha karmaşık ama gerçek zamanlı).

### Seçenek C: Manuel
```bash
cd /home/akn/vps/projects/mathlock && ./ai-generate.sh
```

## Uygulama Sırası

1. ~~VPS: AGENTS.md, questions.json, topics.json, validate-questions.py~~ ✅
2. ~~VPS: ai-generate.sh, deploy.sh, nginx, docker-compose~~ ✅
3. **Android: QuestionManager, StatsTracker, TopicHelper** (yeni dosyalar)
4. **Android: MathChallengeActivity güncelle** (JSON tabanlı sorular + ipucu + konu anlatımı)
5. **Android: Layout güncellemeleri** (ilerleme çubuğu, ipucu alanı)
6. **Test: End-to-end** (VPS → telefon → çöz → stats upload → AI üret → yeni set)
7. **Cron: ai-generate.sh otomasyonu** (isteğe bağlı)
