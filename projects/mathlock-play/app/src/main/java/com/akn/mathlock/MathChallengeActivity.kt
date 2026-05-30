package com.akn.mathlock

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.akn.mathlock.databinding.ActivityMathChallengeBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.AccountManager

import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager
import com.akn.mathlock.util.StatsTracker
import com.akn.mathlock.util.TopicHelper
import com.akn.mathlock.util.CreditApiClient
import com.akn.mathlock.util.ErrorReporter

class MathChallengeActivity : BaseActivity() {

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_AUTH_ACCOUNT && resultCode == RESULT_OK) {
            startActivity(Intent(this, AccountActivity::class.java))
        }
    }

    companion object {
        private const val TAG = "MathChallenge"
        private const val REQUEST_AUTH_ACCOUNT = 5001
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
    // Test modunda soru ilerlemesi için lokal index (questionManager.currentIndex ilerlemez)
    private var testModeIndex = 0

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
            val authToken = accountManager.getOrRefreshToken()
            if (authToken != null) {
                questionManager.uploadProgress(authToken)
            }
            val jsonAvailable = questionManager.sync(authToken)
            topicHelper.sync()
            runOnUiThread {
                // JSON soru varsa ve set tamamlanmadıysa JSON mode, yoksa internet gerekli
                val hasQuestions = jsonAvailable && questionManager.totalCount() > 0
                if (hasQuestions && (!questionManager.isSetComplete() || isTestMode || isPracticeMode)) {
                    startJsonMode()
                } else {
                    showNoInternetDialog()
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

    private fun showKeyboard() {
        val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        binding.etAnswer.post {
            showKeyboard()
            imm.showSoftInput(binding.etAnswer, InputMethodManager.SHOW_IMPLICIT)
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

        val batchNum = currentJsonQuestion?.batch ?: 0
        binding.tvBatch.text = if (batchNum > 0) getString(R.string.batch_label, batchNum) else getString(R.string.free_set)

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
            binding.tvQuestionNum.text = getString(R.string.math_question_single, sessionSolvedCount + 1)
            binding.tvScore.text = getString(R.string.practice_score, sessionSolvedCount)
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

        // Sıralama ve karşılaştırma tiplerinde seçenek butonları (2 sayı ise),
        // diğer tiplerde ve çok sayılı sıralamada yazı input
        if (q.type == "sıralama" || q.type == "karşılaştırma") {
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
            binding.tvResult.text = getString(R.string.test_answer_preview, q.answer)
            binding.tvResult.setTextColor(getColor(R.color.correct_green))
            binding.tvResult.visibility = View.VISIBLE
            if (q.hint.isNotBlank()) {
                binding.tvHint.text = getString(R.string.hint_prefix, q.hint)
                binding.tvHint.visibility = View.VISIBLE
            }
            binding.btnSkip.text = getString(R.string.btn_next_question)
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
                binding.tvHint.text = getString(R.string.hint_prefix, q.hint)
                binding.tvHint.visibility = View.VISIBLE
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = getString(R.string.almost_try_again)
                binding.tvResult.setTextColor(getColor(R.color.accent))
                binding.etAnswer.setText("")
                binding.etAnswer.requestFocus()
            } else if (attempts == 2 && !sawTopic) {
                // İkinci yanlış → konu anlatımı göster
                sawTopic = true
                showTopicDialog(q.type)
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = getString(R.string.more_hint_available)
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
            appendLine(getString(R.string.example_label))
            appendLine(topic.example)
            appendLine()
            topic.tips.forEach { tip ->
                appendLine("• $tip")
            }
        }

        AlertDialog.Builder(this)
            .setTitle(getString(R.string.topic_dialog_title, topic.title))
            .setMessage(message)
            .setPositiveButton(getString(R.string.btn_understood), null)
            .setCancelable(false)
            .show()
    }

    // Sıralama / karşılaştırma tiplerinde soru metninden sayıları çıkarıp seçenek butonlarına ata
    private fun setupOptionsForSiralama(text: String) {
        val numbers = Regex("\\d+").findAll(text).map { it.value.toInt() }.toList()
        if (numbers.size != 2) {
            // 2 sayı yoksa (çok sayılı sıralama veya parse hatası) → normal input'a geri dön
            binding.tilAnswer.visibility = View.VISIBLE
            binding.layoutOptions.visibility = View.GONE
            binding.btnCheck.visibility = View.VISIBLE
            binding.etAnswer.requestFocus()
            return
        }
        // Buton sırasını karıştır (doğru cevap her zaman sağda olmasın)
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
        binding.tvResult.text = getString(R.string.test_preview_complete, questionManager.totalCount())
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
        statsTracker.endSession()
        // Stats yükle ve progress sıfırla
        Thread {
            val authToken = accountManager.getAccessToken()
            val uploaded = statsTracker.uploadStats(questionManager.getVersion(), authToken)
            if (authToken != null) {
                questionManager.uploadProgress(authToken)
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
        binding.tvResult.text = getString(R.string.practice_set_complete, sessionSolvedCount)
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
                    val authToken = accountManager.getAccessToken()
                    questionManager.sync(authToken)
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
        binding.tvResult.text = getString(R.string.set_complete_congrats)
        binding.tvResult.setTextColor(getColor(R.color.correct_green))
        binding.btnCheck.visibility = View.GONE
        binding.btnSkip.visibility = View.GONE
        binding.btnNext.visibility = View.GONE
        binding.etAnswer.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.progressBar.max = questionManager.totalCount()
        binding.progressBar.progress = questionManager.totalCount()

        statsTracker.endSession()

        // Stats yükle + kredi kullan + sıradaki set için soruları arka planda hazırla
        Thread {
            val authToken = accountManager.getAccessToken()
            val childName = prefManager.activeChildName ?: "Çocuk"
            val uploaded = statsTracker.uploadStats(questionManager.getVersion(), authToken)
            if (authToken != null) {
                questionManager.uploadProgress(authToken)
            }
            if (uploaded) {
                questionManager.resetProgress()
                Log.d(TAG, "Stats yüklendi, progress sıfırlandı")
            } else {
                Log.w(TAG, "Stats yükleme başarısız, sonra tekrar denenecek")
                ErrorReporter.report(
                    category = "challenge",
                    message = "Stats upload failed",
                    extras = mapOf("version" to questionManager.getVersion().toString())
                )
            }
            // Yeni set üretmek için kredi kullan (ilk set ücretsiz)
            if (authToken != null) {
                val statsJson = statsTracker.buildStatsJson(questionManager.getVersion())
                val creditResult = creditClient.useCredit(authToken, childName, statsJson)
                when {
                    creditResult.creditsRefunded -> {
                        Log.w(TAG, "Kredi iade edildi: ${creditResult.error}")
                        ErrorReporter.report(
                            category = "challenge",
                            message = "Credit refunded: ${creditResult.error}",
                            extras = mapOf("version" to questionManager.getVersion().toString(), "error" to (creditResult.error ?: "unknown"))
                        )
                        runOnUiThread {
                            Toast.makeText(
                                this@MathChallengeActivity,
                                getString(R.string.credit_refunded_retry),
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }
                    creditResult.success -> {
                        Log.d(TAG, "Kredi kullanıldı: kalan=${creditResult.creditsRemaining}, ücretsiz=${creditResult.isFree}, set_version=${creditResult.setVersion}")
                    }
                    else -> {
                        Log.w(TAG, "Kredi kullanılamadı: ${creditResult.error}")
                        ErrorReporter.report(
                            category = "challenge",
                            message = "Credit use failed: ${creditResult.error}",
                            extras = mapOf("version" to questionManager.getVersion().toString(), "error" to (creditResult.error ?: "unknown"))
                        )
                        runOnUiThread {
                            MaterialAlertDialogBuilder(this@MathChallengeActivity)
                                .setTitle(getString(R.string.dialog_credit_needed_title))
                                .setMessage(getString(R.string.dialog_credit_needed_message))
                                .setPositiveButton(getString(R.string.btn_get_credits)) { _, _ ->
                                    val authIntent = Intent(this@MathChallengeActivity, ParentAuthActivity::class.java).apply {
                                        putExtra("forward_to", AccountActivity::class.java.name)
                                    }
                                    startActivityForResult(authIntent, REQUEST_AUTH_ACCOUNT)
                                }
                                .setNegativeButton(getString(R.string.btn_close), null)
                                .setCancelable(false)
                                .show()
                        }
                    }
                }
            }
            // Soruları şimdi sync et — VPS'te yeni set hazır olunca sessizce çeker
            questionManager.sync(authToken)
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

    private fun showNoInternetDialog() {
        AlertDialog.Builder(this)
            .setTitle(getString(R.string.dialog_no_internet_title))
            .setMessage(getString(R.string.dialog_no_internet_message))
            .setPositiveButton("Tamam") { _, _ ->
                if (!isTestMode && !isPracticeMode) {
                    sendUserHome()
                } else {
                    finish()
                }
            }
            .setCancelable(false)
            .show()
    }

    // ═══════════════════════════════════════════════════════════════════════
    // Common
    // ═══════════════════════════════════════════════════════════════════════

    private fun unlockAndLaunchApp() {
        if (isTestMode) {
            Toast.makeText(this, getString(R.string.test_success_toast), Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        if (isPracticeMode) {
            // Pratik modda unlock yok — çıkmamalı, soru akışı devam eder
            return
        }

        // Pending solved soruları sunucuya gönder (kaybolmasın)
        Thread {
            val authToken = accountManager.getAccessToken()
            if (authToken != null) questionManager.uploadProgress(authToken)
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
            checkJsonAnswer()
        }

        binding.btnSkip.setOnClickListener {
            // Ebeveyn önizleme: soruyu atla, sonrakine geç
            binding.btnSkip.visibility = View.GONE
            binding.btnCheck.visibility = View.GONE
            showNextJsonQuestion()
        }

        binding.btnNext.setOnClickListener {
            showNextJsonQuestion()
        }

        binding.btnOption1.setOnClickListener {
            checkOptionAnswer(binding.btnOption1.text.toString().toIntOrNull() ?: return@setOnClickListener)
        }

        binding.btnOption2.setOnClickListener {
            checkOptionAnswer(binding.btnOption2.text.toString().toIntOrNull() ?: return@setOnClickListener)
        }

        binding.btnRetry.setOnClickListener {
            // Retry: internet bağlantısını tekrar dene
            if (!isFinishing && !isDestroyed) {
                val authToken = accountManager.getOrRefreshToken()
                Thread {
                    val jsonAvailable = questionManager.sync(authToken)
                    runOnUiThread {
                        val hasQuestions = jsonAvailable && questionManager.totalCount() > 0
                        if (hasQuestions && (!questionManager.isSetComplete() || isTestMode || isPracticeMode)) {
                            startJsonMode()
                        } else {
                            showNoInternetDialog()
                        }
                    }
                }.start()
            }
        }

        binding.etAnswer.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                checkJsonAnswer()
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
        val authToken = accountManager.getAccessToken()
        if (authToken != null) {
            try {
                questionManager.uploadProgress(authToken)
            } catch (e: Exception) {
                Log.w(TAG, "onDestroy progress upload hatası: ${e.message}")
                ErrorReporter.report(
                    category = "challenge",
                    message = "onDestroy progress upload failed: ${e.message}",
                    throwable = e
                )
            }
        }
        super.onDestroy()
    }
}
