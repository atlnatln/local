package com.akn.mathlock

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.akn.mathlock.databinding.ActivityMathChallengeBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.MathQuestionGenerator
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager
import com.akn.mathlock.util.StatsTracker
import com.akn.mathlock.util.TopicHelper
import com.akn.mathlock.util.CreditApiClient

class MathChallengeActivity : BaseActivity() {

    companion object {
        private const val TAG = "MathChallenge"
    }

    private lateinit var binding: ActivityMathChallengeBinding
    private lateinit var prefManager: PreferenceManager
    private lateinit var accountManager: AccountManager
    private lateinit var questionManager: QuestionManager
    private lateinit var statsTracker: StatsTracker
    private lateinit var topicHelper: TopicHelper
    private lateinit var creditClient: CreditApiClient

    private var lockedPackage: String? = null
    private var isTestMode = false
    private var isPracticeMode = false

    // JSON mode state
    private var currentJsonQuestion: QuestionManager.JsonQuestion? = null
    private var attempts = 0
    private var startTime = 0L
    private var sawHint = false
    private var sawTopic = false
    // Bu kilit açma oturumunda kaç doğru cevap verildi / kaç gerekli
    private var sessionSolvedCount = 0
    private var requiredCount = 1
    // Hangi mod çalışıyor: true=JSON, false=fallback
    // questionManager.isJsonMode KULLANILMAZ — JSON cache varken set bitmişse
    // isSetComplete()=true olup startFallbackMode() çağrılır ama _isJsonMode
    // hâlâ true kalır; bu durumda checkJsonAnswer() çalışır ve currentJsonQuestion
    // null olduğundan hemen döner → kullanıcı soruyu çözemez.
    private var isJsonModeActive = false

    // Test modunda soru ilerlemesi için lokal index (questionManager.currentIndex ilerlemez)
    private var testModeIndex = 0

    // Fallback mode state (eski sistem)
    private var fallbackQuestions = mutableListOf<com.akn.mathlock.util.MathQuestion>()
    private var currentIndex = 0
    private var correctCount = 0
    private var totalQuestions = 5
    private var passScore = 3

    private fun sendUserHome() {
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMathChallengeBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)
        accountManager = AccountManager(this)
        questionManager = QuestionManager(this)
        statsTracker = StatsTracker(this)
        statsTracker.startSession()
        topicHelper = TopicHelper(this)
        creditClient = CreditApiClient()

        lockedPackage = intent.getStringExtra("locked_package")
        isTestMode = intent.getBooleanExtra("test_mode", false)
        isPracticeMode = intent.getBooleanExtra("practice_mode", false)

        // İpucu alanı başlangıçta gizli
        binding.tvHint.visibility = View.GONE

        // JSON modunu arka planda sync et, sonra soruları göster
        Thread {
            // Cihaz kaydı + bekleyen ilerleme gönderimi
            val token = accountManager.getOrRegister()
            if (token != null) {
                questionManager.uploadProgress(token)
            }
            val jsonAvailable = questionManager.sync(token)
            topicHelper.sync()
            runOnUiThread {
                // JSON soru varsa ve set tamamlanmadıysa JSON mode, yoksa fallback
                val hasQuestions = jsonAvailable && questionManager.totalCount() > 0
                if (hasQuestions && (!questionManager.isSetComplete() || isTestMode || isPracticeMode)) {
                    startJsonMode()
                } else {
                    startFallbackMode()
                }
            }
        }.start()

        setupListeners()
    }

    // ═══════════════════════════════════════════════════════════════════════
    // JSON Mode — VPS'ten gelen sorular, ipucu, konu anlatımı
    // ═══════════════════════════════════════════════════════════════════════

    private fun startJsonMode() {
        Log.d(TAG, "JSON mode başlatılıyor (v${questionManager.getVersion()})")
        isJsonModeActive = true
        if (isTestMode) {
            // Ebeveyn önizleme: tüm soruları index 0'dan göster, unlock mekanizması yok
            testModeIndex = 0
            showNextJsonQuestion()
        } else if (isPracticeMode) {
            // Pratik mod: sınırsız soru, stats kaydedilir, unlock yok
            sessionSolvedCount = 0
            showNextJsonQuestion()
        } else {
            // Normal mod: passScore kadar doğru cevap → kilit açılır
            requiredCount = prefManager.passScore.coerceAtLeast(1)
            sessionSolvedCount = 0
            showNextJsonQuestion()
        }
    }

    private fun showNextJsonQuestion() {
        // Normal modda set tamamlandıysa onSetComplete çağır
        // (nextQuestion() index'i 0'a resetler, null dönmez — bu yüzden önce kontrol et)
        if (!isTestMode && !isPracticeMode && questionManager.isSetComplete()) {
            onSetComplete()
            return
        }

        currentJsonQuestion = if (isTestMode) {
            questionManager.peekQuestion(testModeIndex)
        } else {
            questionManager.nextQuestion()
        }

        if (currentJsonQuestion == null) {
            if (isTestMode) {
                onTestPreviewComplete()
            } else if (isPracticeMode) {
                onPracticeSetComplete()
            } else {
                onSetComplete()
            }
            return
        }

        if (isTestMode) testModeIndex++

        val q = currentJsonQuestion!!
        attempts = 0
        sawHint = false
        sawTopic = false
        startTime = System.currentTimeMillis()

        // Ekran gösterimi için dönüşümler
        binding.tvQuestion.text = q.text
            .replace(" / ", " ÷ ")
            .replace("_", "?")

        if (isTestMode) {
            // Ebeveyn önizleme: "Soru 3/50" — toplam soru sayısını göster
            val totalQ = questionManager.totalCount()
            binding.tvQuestionNum.text = getString(R.string.math_question_num, testModeIndex, totalQ)
            binding.tvScore.text = ""
            binding.progressBar.max = totalQ
            binding.progressBar.progress = testModeIndex
            binding.cardTestBanner.visibility = View.VISIBLE
        } else if (isPracticeMode) {
            // Pratik mod: çözülen soru sayısını göster
            binding.tvQuestionNum.text = "Soru ${sessionSolvedCount + 1}"
            binding.tvScore.text = "⭐ $sessionSolvedCount doğru"
            binding.progressBar.visibility = View.GONE
        } else {
            // Normal mod: "2/3" — oturum ilerleme
            binding.tvQuestionNum.text = getString(R.string.math_question_num, sessionSolvedCount + 1, requiredCount)
            binding.tvScore.text = ""
            binding.progressBar.max = requiredCount
            binding.progressBar.progress = sessionSolvedCount
        }

        binding.etAnswer.setText("")
        binding.etAnswer.isEnabled = true
        binding.tvResult.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.btnSkip.visibility = if (isTestMode) View.VISIBLE else View.GONE
        binding.btnNext.visibility = View.GONE
        binding.btnRetry.visibility = View.GONE

        // Sıralama tipinde seçenek butonları, diğer tiplerde yazı input
        if (q.type == "siralama") {
            setupOptionsForSiralama(q.text)
        } else {
            binding.tilAnswer.visibility = View.VISIBLE
            binding.layoutOptions.visibility = View.GONE
            binding.btnCheck.visibility = View.VISIBLE
            binding.etAnswer.requestFocus()
        }

        // ── Ebeveyn önizleme: cevabı ve ipucunu anında göster, input gizle ──────
        if (isTestMode) {
            binding.tilAnswer.visibility = View.GONE
            binding.layoutOptions.visibility = View.GONE
            binding.btnCheck.visibility = View.GONE
            binding.tvResult.text = "✅ Cevap: ${q.answer}"
            binding.tvResult.setTextColor(getColor(R.color.correct_green))
            binding.tvResult.visibility = View.VISIBLE
            if (q.hint.isNotBlank()) {
                binding.tvHint.text = "💡 ${q.hint}"
                binding.tvHint.visibility = View.VISIBLE
            }
            binding.btnSkip.text = "Sonraki Soru →"
            binding.btnSkip.visibility = View.VISIBLE
        }
    }

    private fun checkJsonAnswer() {
        val answerText = binding.etAnswer.text.toString().trim()
        if (answerText.isEmpty()) return
        val userAnswer = answerText.toIntOrNull() ?: return
        val q = currentJsonQuestion ?: return

        attempts++
        val elapsed = (System.currentTimeMillis() - startTime) / 1000.0

        if (userAnswer == q.answer) {
            // ✅ Doğru cevap
            binding.etAnswer.isEnabled = false
            binding.btnCheck.visibility = View.GONE
            binding.tvResult.visibility = View.VISIBLE
            binding.tvResult.text = getString(R.string.math_correct)
            binding.tvResult.setTextColor(getColor(R.color.correct_green))
            binding.tvHint.visibility = View.GONE

            if (!isTestMode) {
                statsTracker.addResult(
                    StatsTracker.QuestionResult(
                        questionId = q.id, type = q.type, difficulty = q.difficulty,
                        correct = true, attempts = attempts, timeSeconds = elapsed,
                        sawHint = sawHint, sawTopic = sawTopic
                    )
                )
                questionManager.markSolved(q.id)
            }

            if (isTestMode) {
                // Ebeveyn önizleme: doğru cevap → 800ms sonra sonraki soru
                binding.root.postDelayed({
                    if (!isFinishing && !isDestroyed) showNextJsonQuestion()
                }, 800)
            } else if (isPracticeMode) {
                // Pratik mod: doğru cevap → skoru artır, sonraki soru
                sessionSolvedCount++
                binding.root.postDelayed({
                    if (!isFinishing && !isDestroyed) showNextJsonQuestion()
                }, 800)
            } else {
                // Normal mod: oturum ilerleme
                sessionSolvedCount++
                if (sessionSolvedCount >= requiredCount) {
                    unlockAndLaunchApp()
                } else {
                    binding.root.postDelayed({
                        if (!isFinishing && !isDestroyed) showNextJsonQuestion()
                    }, 800)
                }
            }
        } else {
            // ❌ Yanlış cevap
            if (attempts == 1 && !sawHint) {
                // İlk yanlış → ipucu göster
                sawHint = true
                binding.tvHint.text = "💡 ${q.hint}"
                binding.tvHint.visibility = View.VISIBLE
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = "Neredeyse! Tekrar dene 🤔"
                binding.tvResult.setTextColor(getColor(R.color.accent))
                binding.etAnswer.setText("")
                binding.etAnswer.requestFocus()
            } else if (attempts == 2 && !sawTopic) {
                // İkinci yanlış → konu anlatımı göster
                sawTopic = true
                showTopicDialog(q.type)
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = "Bir ipucu daha var! 📚"
                binding.tvResult.setTextColor(getColor(R.color.accent))
                binding.etAnswer.setText("")
                binding.etAnswer.requestFocus()
            } else {
                // Üçüncü veya daha fazla yanlış → doğru cevabı göster, kaydet, çocuk hazır olunca geçsin
                binding.etAnswer.isEnabled = false
                binding.btnCheck.visibility = View.GONE
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = getString(R.string.math_wrong, q.answer)
                binding.tvResult.setTextColor(getColor(R.color.wrong_red))

                if (!isTestMode) {
                    statsTracker.addResult(
                        StatsTracker.QuestionResult(
                            questionId = q.id, type = q.type, difficulty = q.difficulty,
                            correct = false, attempts = attempts, timeSeconds = elapsed,
                            sawHint = sawHint, sawTopic = sawTopic
                        )
                    )
                }

                // Çocuk doğru cevabı okuyup hazır olunca gecer
                binding.btnNext.visibility = View.VISIBLE
            }
        }
    }

    private fun showTopicDialog(questionType: String) {
        val topic = topicHelper.getTopicFor(questionType) ?: return
        if (isFinishing || isDestroyed) return

        val message = buildString {
            appendLine(topic.explanation)
            appendLine()
            appendLine("📝 Örnek:")
            appendLine(topic.example)
            appendLine()
            topic.tips.forEach { tip ->
                appendLine("• $tip")
            }
        }

        AlertDialog.Builder(this)
            .setTitle("📚 ${topic.title}")
            .setMessage(message)
            .setPositiveButton("Anladım! ✨", null)
            .setCancelable(false)
            .show()
    }

    // Sıralama tipinde soru metninden sayıları çıkarıp seçenek butonlarına ata
    private fun setupOptionsForSiralama(text: String) {
        val numbers = Regex("\\d+").findAll(text).map { it.value.toInt() }.toList()
        if (numbers.size < 2) {
            // Parse başarısız → normal input'a geri dön
            binding.tilAnswer.visibility = View.VISIBLE
            binding.layoutOptions.visibility = View.GONE
            binding.btnCheck.visibility = View.VISIBLE
            binding.etAnswer.requestFocus()
            return
        }
        // Buton sırasını karıştır (büyük sayı hep sağda olmasın)
        val opts = if (Math.random() > 0.5) listOf(numbers[0], numbers[1])
                   else listOf(numbers[1], numbers[0])
        binding.tilAnswer.visibility = View.GONE
        binding.btnCheck.visibility = View.GONE
        binding.layoutOptions.visibility = View.VISIBLE
        binding.btnOption1.text = opts[0].toString()
        binding.btnOption2.text = opts[1].toString()
    }

    // Seçenek butonundan gelen cevabı kontrol et
    private fun checkOptionAnswer(selected: Int) {
        val q = currentJsonQuestion ?: return
        attempts++
        val elapsed = (System.currentTimeMillis() - startTime) / 1000.0

        binding.layoutOptions.visibility = View.GONE
        binding.tvResult.visibility = View.VISIBLE

        if (selected == q.answer) {
            binding.tvResult.text = getString(R.string.math_correct)
            binding.tvResult.setTextColor(getColor(R.color.correct_green))

            if (!isTestMode) {
                statsTracker.addResult(StatsTracker.QuestionResult(
                    questionId = q.id, type = q.type, difficulty = q.difficulty,
                    correct = true, attempts = attempts, timeSeconds = elapsed,
                    sawHint = sawHint, sawTopic = sawTopic
                ))
                questionManager.markSolved(q.id)
            }

            if (isTestMode) {
                binding.root.postDelayed({ if (!isFinishing && !isDestroyed) showNextJsonQuestion() }, 800)
            } else if (isPracticeMode) {
                sessionSolvedCount++
                binding.root.postDelayed({ if (!isFinishing && !isDestroyed) showNextJsonQuestion() }, 800)
            } else {
                sessionSolvedCount++
                if (sessionSolvedCount >= requiredCount) unlockAndLaunchApp()
                else binding.root.postDelayed({ if (!isFinishing && !isDestroyed) showNextJsonQuestion() }, 800)
            }
        } else {
            binding.tvResult.text = getString(R.string.math_wrong, q.answer)
            binding.tvResult.setTextColor(getColor(R.color.wrong_red))

            if (!isTestMode) {
                statsTracker.addResult(StatsTracker.QuestionResult(
                    questionId = q.id, type = q.type, difficulty = q.difficulty,
                    correct = false, attempts = attempts, timeSeconds = elapsed,
                    sawHint = sawHint, sawTopic = sawTopic
                ))
            }
            binding.btnNext.visibility = View.VISIBLE
        }
    }

    private fun onTestPreviewComplete() {
        Log.d(TAG, "Ebeveyn önizleme tamamlandı (${questionManager.totalCount()} soru)")
        binding.tvQuestion.text = "✅"
        binding.tvResult.visibility = View.VISIBLE
        binding.tvResult.text = "Önizleme tamamlandı — ${questionManager.totalCount()} soru incelendi"
        binding.tvResult.setTextColor(getColor(R.color.correct_green))
        binding.btnCheck.visibility = View.GONE
        binding.btnSkip.visibility = View.GONE
        binding.btnNext.visibility = View.GONE
        binding.etAnswer.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.progressBar.max = questionManager.totalCount()
        binding.progressBar.progress = questionManager.totalCount()

        binding.root.postDelayed({
            if (!isFinishing && !isDestroyed) finish()
        }, 2000)
    }

    private fun onPracticeSetComplete() {
        Log.d(TAG, "Pratik mod: set tamamlandı, stats yükleniyor...")
        // Stats yükle ve progress sıfırla
        Thread {
            val token = accountManager.getDeviceToken()
            val uploaded = statsTracker.uploadStats(questionManager.getVersion())
            if (token != null) {
                questionManager.uploadProgress(token)
            }
            questionManager.resetProgress()
            if (uploaded) {
                Log.d(TAG, "Pratik: stats yüklendi, progress sıfırlandı")
            } else {
                Log.w(TAG, "Pratik: stats yükleme başarısız, progress yine de sıfırlandı")
            }
        }.start()

        // Tebrik mesajı göster, 2s sonra yeni set başlat
        binding.tvQuestion.text = "🎉"
        binding.tvResult.visibility = View.VISIBLE
        binding.tvResult.text = "Üstbeyinsin! 🌟 Toplam $sessionSolvedCount doğru!\nYeni sorular geliyor..."
        binding.tvResult.setTextColor(getColor(R.color.correct_green))
        binding.btnCheck.visibility = View.GONE
        binding.etAnswer.visibility = View.GONE
        binding.tvHint.visibility = View.GONE

        binding.root.postDelayed({
            if (!isFinishing && !isDestroyed) {
                binding.etAnswer.visibility = View.VISIBLE
                binding.tvResult.visibility = View.GONE
                // Yeni seti sync et ve devam et
                Thread {
                    val token = accountManager.getDeviceToken()
                    questionManager.sync(token)
                    runOnUiThread {
                        if (!isFinishing && !isDestroyed) showNextJsonQuestion()
                    }
                }.start()
            }
        }, 2500)
    }

    private fun onSetComplete() {
        Log.d(TAG, "50 soru tamamlandı! Stats yükleniyor...")
        binding.tvQuestion.text = "🎉"
        binding.tvResult.visibility = View.VISIBLE
        binding.tvResult.text = "Harika! 50 soruyu tamamladın! 🌟"
        binding.tvResult.setTextColor(getColor(R.color.correct_green))
        binding.btnCheck.visibility = View.GONE
        binding.btnSkip.visibility = View.GONE
        binding.btnNext.visibility = View.GONE
        binding.etAnswer.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.progressBar.max = questionManager.totalCount()
        binding.progressBar.progress = questionManager.totalCount()

        // Stats yükle + kredi kullan + sıradaki set için soruları arka planda hazırla
        Thread {
            val token = accountManager.getDeviceToken()
            val childName = prefManager.activeChildName ?: "Çocuk"
            val uploaded = statsTracker.uploadStats(questionManager.getVersion())
            if (token != null) {
                questionManager.uploadProgress(token)
            }
            if (uploaded) {
                questionManager.resetProgress()
                Log.d(TAG, "Stats yüklendi, progress sıfırlandı")
            } else {
                Log.w(TAG, "Stats yükleme başarısız, sonra tekrar denenecek")
            }
            // Yeni set üretmek için kredi kullan (ilk set ücretsiz)
            if (token != null) {
                val statsJson = statsTracker.buildStatsJson(questionManager.getVersion())
                val creditResult = creditClient.useCredit(token, childName, statsJson)
                if (creditResult.success) {
                    Log.d(TAG, "Kredi kullanıldı: kalan=${creditResult.creditsRemaining}, ücretsiz=${creditResult.isFree}, set_version=${creditResult.setVersion}")
                } else {
                    Log.w(TAG, "Kredi kullanılamadı: ${creditResult.error}")
                    runOnUiThread {
                        Toast.makeText(
                            this@MathChallengeActivity,
                            "🎉 50 soru tamamlandı! Yeni sorular için kredi satın alabilirsin.",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }
            // Soruları şimdi sync et — VPS'te yeni set hazır olunca sessizce çeker
            questionManager.sync(token)
            Log.d(TAG, "Sonraki set için sorular sync edildi")
        }.start()

        // Kilidi aç
        binding.root.postDelayed({
            if (!isFinishing && !isDestroyed) {
                unlockAndLaunchApp()
            }
        }, 2000)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // Fallback Mode — JSON yoksa eski random soru sistemi
    // ═══════════════════════════════════════════════════════════════════════

    private fun startFallbackMode() {
        Log.d(TAG, "Fallback mode (random sorular)")
        isJsonModeActive = false
        // totalQuestions: passScore'un 2 katı, minimum 5 (questionCount ayarı kaldırıldı)
        totalQuestions = (prefManager.passScore * 2).coerceAtLeast(5)
        passScore = prefManager.passScore.coerceAtMost(totalQuestions)
        binding.tvHint.visibility = View.GONE
        generateFallbackQuestions()
        showFallbackQuestion()
    }

    private fun generateFallbackQuestions() {
        fallbackQuestions.clear()
        repeat(totalQuestions) {
            fallbackQuestions.add(MathQuestionGenerator.generate())
        }
    }

    private fun showFallbackQuestion() {
        if (currentIndex >= totalQuestions) {
            showFallbackResult()
            return
        }

        val question = fallbackQuestions[currentIndex]
        binding.tvQuestion.text = question.text
        // Soru sayacı ve bar: hedefe (passScore) göre — totalQuestions iç detay
        binding.tvQuestionNum.text = getString(R.string.math_question_num, correctCount + 1, passScore)
        binding.tvScore.text = ""
        binding.progressBar.max = passScore
        binding.progressBar.progress = correctCount

        binding.etAnswer.setText("")
        binding.etAnswer.isEnabled = true
        binding.tvResult.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.btnCheck.visibility = View.VISIBLE
        binding.btnNext.visibility = View.GONE
        binding.btnRetry.visibility = View.GONE
        binding.etAnswer.requestFocus()
    }

    private fun checkFallbackAnswer() {
        val answerText = binding.etAnswer.text.toString().trim()
        if (answerText.isEmpty()) return
        val userAnswer = answerText.toIntOrNull() ?: return
        val correctAnswer = fallbackQuestions[currentIndex].answer

        binding.etAnswer.isEnabled = false
        binding.btnCheck.visibility = View.GONE
        binding.tvResult.visibility = View.VISIBLE

        if (userAnswer == correctAnswer) {
            correctCount++
            binding.tvResult.text = getString(R.string.math_correct)
            binding.tvResult.setTextColor(getColor(R.color.correct_green))
        } else {
            binding.tvResult.text = getString(R.string.math_wrong, correctAnswer)
            binding.tvResult.setTextColor(getColor(R.color.wrong_red))
        }

        binding.tvQuestionNum.text = getString(R.string.math_question_num, correctCount + 1, passScore)
        binding.progressBar.progress = correctCount

        // Erken unlock: passScore kadar doğru cevap toplandıysa kalan soruları bekleme
        if (userAnswer == correctAnswer && correctCount >= passScore) {
            binding.progressBar.progress = passScore
            if (isPracticeMode) {
                // Pratik modda devam et — yeni sorular üret
                sessionSolvedCount += correctCount
                correctCount = 0
                currentIndex = 0
                generateFallbackQuestions()
                binding.root.postDelayed({
                    if (!isFinishing && !isDestroyed) {
                        binding.etAnswer.visibility = View.VISIBLE
                        showFallbackQuestion()
                    }
                }, 1200)
                return
            }
            binding.root.postDelayed({ unlockAndLaunchApp() }, 1000)
            return
        }

        if (currentIndex < totalQuestions - 1) {
            binding.btnNext.visibility = View.VISIBLE
        } else {
            binding.root.postDelayed({ showFallbackResult() }, 1200)
        }
    }

    private fun showFallbackResult() {
        if (correctCount >= passScore) {
            binding.tvQuestion.text = "🎉"
            binding.tvResult.visibility = View.VISIBLE
            binding.tvResult.setTextColor(getColor(R.color.correct_green))
            binding.btnCheck.visibility = View.GONE
            binding.btnNext.visibility = View.GONE
            binding.etAnswer.visibility = View.GONE
            binding.progressBar.progress = totalQuestions
            if (isPracticeMode) {
                sessionSolvedCount += correctCount
                binding.tvResult.text = "⭐ $sessionSolvedCount doğru! Devam ediyor..."
                correctCount = 0
                currentIndex = 0
                generateFallbackQuestions()
                binding.root.postDelayed({
                    if (!isFinishing && !isDestroyed) {
                        binding.etAnswer.visibility = View.VISIBLE
                        binding.tvResult.visibility = View.GONE
                        showFallbackQuestion()
                    }
                }, 1500)
                return
            }
            binding.tvResult.text = getString(R.string.math_success)
            binding.root.postDelayed({ unlockAndLaunchApp() }, 1500)
        } else {
            binding.tvQuestion.text = "�"
            binding.tvResult.visibility = View.VISIBLE
            binding.tvResult.text = getString(R.string.math_fail)
            binding.tvResult.setTextColor(getColor(R.color.accent))
            binding.btnCheck.visibility = View.GONE
            binding.btnNext.visibility = View.GONE
            binding.etAnswer.visibility = View.GONE
            binding.btnRetry.visibility = View.VISIBLE
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // Common
    // ═══════════════════════════════════════════════════════════════════════

    private fun unlockAndLaunchApp() {
        if (isTestMode) {
            Toast.makeText(this, "Test başarılı! Uygulama açılacaktı.", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        if (isPracticeMode) {
            // Pratik modda unlock yok — çıkmamalı, soru akışı devam eder
            return
        }

        // Pending solved soruları sunucuya gönder (kaybolmasın)
        Thread {
            val token = accountManager.getDeviceToken()
            if (token != null) questionManager.uploadProgress(token)
        }.start()

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

    private fun setupListeners() {
        binding.btnCheck.setOnClickListener {
            if (isJsonModeActive) {
                checkJsonAnswer()
            } else {
                checkFallbackAnswer()
            }
        }

        binding.btnSkip.setOnClickListener {
            // Ebeveyn önizleme: soruyu atla, sonrakine geç
            binding.btnSkip.visibility = View.GONE
            binding.btnCheck.visibility = View.GONE
            showNextJsonQuestion()
        }

        binding.btnNext.setOnClickListener {
            if (isJsonModeActive) {
                showNextJsonQuestion()
            } else {
                currentIndex++
                showFallbackQuestion()
            }
        }

        binding.btnOption1.setOnClickListener {
            checkOptionAnswer(binding.btnOption1.text.toString().toIntOrNull() ?: return@setOnClickListener)
        }

        binding.btnOption2.setOnClickListener {
            checkOptionAnswer(binding.btnOption2.text.toString().toIntOrNull() ?: return@setOnClickListener)
        }

        binding.btnRetry.setOnClickListener {
            // Sadece fallback modda kullanılır
            currentIndex = 0
            correctCount = 0
            binding.etAnswer.visibility = View.VISIBLE
            binding.btnRetry.visibility = View.GONE
            generateFallbackQuestions()
            showFallbackQuestion()
        }

        binding.etAnswer.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                if (isJsonModeActive) {
                    checkJsonAnswer()
                } else {
                    checkFallbackAnswer()
                }
                true
            } else false
        }
    }

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (isTestMode || isPracticeMode) {
            super.onBackPressed()
        } else {
            finish()
        }
    }

    override fun onDestroy() {
        statsTracker.endSession()
        // Activity yok olmadan önce pending progress'i son kez göndermeye çalış
        // (unlockAndLaunchApp() içindeki Thread async çalıştığı için finish() öncesinde kaybolabilir)
        val token = accountManager.getDeviceToken()
        if (token != null) {
            try {
                questionManager.uploadProgress(token)
            } catch (e: Exception) {
                Log.w(TAG, "onDestroy progress upload hatası: ${e.message}")
            }
        }
        super.onDestroy()
    }
}
