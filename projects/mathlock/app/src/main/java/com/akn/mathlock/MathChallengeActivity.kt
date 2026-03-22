package com.akn.mathlock

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.databinding.ActivityMathChallengeBinding
import com.akn.mathlock.util.MathQuestionGenerator
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager
import com.akn.mathlock.util.StatsTracker
import com.akn.mathlock.util.TopicHelper

class MathChallengeActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "MathChallenge"
    }

    private lateinit var binding: ActivityMathChallengeBinding
    private lateinit var prefManager: PreferenceManager
    private lateinit var questionManager: QuestionManager
    private lateinit var statsTracker: StatsTracker
    private lateinit var topicHelper: TopicHelper

    private var lockedPackage: String? = null
    private var isTestMode = false

    // JSON mode state
    private var currentJsonQuestion: QuestionManager.JsonQuestion? = null
    private var attempts = 0
    private var startTime = 0L
    private var sawHint = false
    private var sawTopic = false

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
        questionManager = QuestionManager(this)
        statsTracker = StatsTracker(this)
        topicHelper = TopicHelper(this)

        lockedPackage = intent.getStringExtra("locked_package")
        isTestMode = intent.getBooleanExtra("test_mode", false)

        // İpucu alanı başlangıçta gizli
        binding.tvHint.visibility = View.GONE

        // JSON modunu arka planda sync et, sonra soruları göster
        Thread {
            val jsonAvailable = questionManager.sync()
            topicHelper.sync()
            runOnUiThread {
                if (jsonAvailable && !questionManager.isSetComplete()) {
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
        showNextJsonQuestion()
    }

    private fun showNextJsonQuestion() {
        currentJsonQuestion = questionManager.nextQuestion()

        if (currentJsonQuestion == null) {
            // Set tamamlandı veya bitti
            onSetComplete()
            return
        }

        val q = currentJsonQuestion!!
        attempts = 0
        sawHint = false
        sawTopic = false
        startTime = System.currentTimeMillis()

        binding.tvQuestion.text = q.text
        binding.tvQuestionNum.text = getString(R.string.math_question_num, questionManager.solvedCount(), questionManager.totalCount())
        binding.tvScore.text = ""
        binding.progressBar.max = questionManager.totalCount()
        binding.progressBar.progress = questionManager.solvedCount() - 1

        binding.etAnswer.setText("")
        binding.etAnswer.isEnabled = true
        binding.tvResult.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.btnCheck.visibility = View.VISIBLE
        binding.btnNext.visibility = View.GONE
        binding.btnRetry.visibility = View.GONE
        binding.etAnswer.requestFocus()
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
            }

            // Kilidi aç ve uygulamayı başlat
            unlockAndLaunchApp()
        } else {
            // ❌ Yanlış cevap
            if (attempts == 1 && !sawHint) {
                // İlk yanlış → ipucu göster
                sawHint = true
                binding.tvHint.text = "💡 ${q.hint}"
                binding.tvHint.visibility = View.VISIBLE
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = "❌ Tekrar dene!"
                binding.tvResult.setTextColor(getColor(R.color.wrong_red))
                binding.etAnswer.setText("")
                binding.etAnswer.requestFocus()
            } else if (attempts == 2 && !sawTopic) {
                // İkinci yanlış → konu anlatımı göster
                sawTopic = true
                showTopicDialog(q.type)
                binding.tvResult.visibility = View.VISIBLE
                binding.tvResult.text = "❌ Bir daha dene!"
                binding.tvResult.setTextColor(getColor(R.color.wrong_red))
                binding.etAnswer.setText("")
                binding.etAnswer.requestFocus()
            } else {
                // Üçüncü veya daha fazla yanlış → doğru cevabı göster, kaydet, devam et
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

                // 1.5 saniye sonra sonraki soruya geç
                binding.root.postDelayed({
                    if (!isFinishing && !isDestroyed) {
                        showNextJsonQuestion()
                    }
                }, 1500)
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

    private fun onSetComplete() {
        Log.d(TAG, "50 soru tamamlandı! Stats yükleniyor...")
        binding.tvQuestion.text = "🎉"
        binding.tvResult.visibility = View.VISIBLE
        binding.tvResult.text = "Harika! 50 soruyu tamamladın! 🌟"
        binding.tvResult.setTextColor(getColor(R.color.correct_green))
        binding.btnCheck.visibility = View.GONE
        binding.btnNext.visibility = View.GONE
        binding.etAnswer.visibility = View.GONE
        binding.tvHint.visibility = View.GONE
        binding.progressBar.max = questionManager.totalCount()
        binding.progressBar.progress = questionManager.totalCount()

        // Stats'ı arka planda yükle (test modunda yükleme)
        if (!isTestMode) {
            Thread {
                val uploaded = statsTracker.uploadStats(questionManager.getVersion())
                if (uploaded) {
                    questionManager.resetProgress()
                    Log.d(TAG, "Stats yüklendi, progress sıfırlandı")
                } else {
                    Log.w(TAG, "Stats yükleme başarısız, sonra tekrar denenecek")
                }
            }.start()
        }

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
        totalQuestions = prefManager.questionCount
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
        binding.tvQuestionNum.text = getString(R.string.math_question_num, currentIndex + 1, totalQuestions)
        binding.tvScore.text = getString(R.string.math_score, correctCount, totalQuestions)
        binding.progressBar.max = totalQuestions
        binding.progressBar.progress = currentIndex

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

        binding.tvScore.text = getString(R.string.math_score, correctCount, totalQuestions)

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
            binding.tvResult.text = getString(R.string.math_success)
            binding.tvResult.setTextColor(getColor(R.color.correct_green))
            binding.btnCheck.visibility = View.GONE
            binding.btnNext.visibility = View.GONE
            binding.etAnswer.visibility = View.GONE
            binding.progressBar.progress = totalQuestions
            binding.root.postDelayed({ unlockAndLaunchApp() }, 1500)
        } else {
            binding.tvQuestion.text = "😔"
            binding.tvResult.visibility = View.VISIBLE
            binding.tvResult.text = getString(R.string.math_fail)
            binding.tvResult.setTextColor(getColor(R.color.wrong_red))
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

        lockedPackage?.let { pkg ->
            LockStateManager.notifyUnlocked(pkg)
            val launchIntent = packageManager.getLaunchIntentForPackage(pkg)
            if (launchIntent != null) {
                startActivity(launchIntent)
            }
        }
        finish()
    }

    private fun setupListeners() {
        binding.btnCheck.setOnClickListener {
            if (questionManager.isJsonMode) {
                checkJsonAnswer()
            } else {
                checkFallbackAnswer()
            }
        }

        binding.btnNext.setOnClickListener {
            // Sadece fallback modda kullanılır
            currentIndex++
            showFallbackQuestion()
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
                if (questionManager.isJsonMode) {
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
        if (isTestMode) {
            super.onBackPressed()
        } else {
            sendUserHome()
            finish()
        }
    }
}
