package com.akn.mathlock

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.SeekBar
import android.widget.Toast
import com.akn.mathlock.databinding.ActivityNumberGuessBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager
import kotlin.random.Random

class NumberGuessActivity : BaseActivity() {

    private lateinit var binding: ActivityNumberGuessBinding
    private lateinit var prefManager: PreferenceManager

    private var lockedPackage: String? = null
    private var isTestMode = false
    private var isPracticeMode = false

    private var secretNumber = 0
    private var attempts = 0
    private var rangeMin = 0
    private var rangeMax = 100
    private var gameMax = 100
    // Oturum: kaç tur çözüldü / kaç gerekli
    private var sessionSolvedCount = 0
    private var requiredCount = 1

    // Limit seçici için basamak dizisi: 10,20,30,...,100,200,...,1000
    private val limitSteps = intArrayOf(10,20,30,50,100,200,300,500,750,1000)

    private fun sendUserHome() {
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityNumberGuessBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)
        lockedPackage = intent.getStringExtra("locked_package")
        isTestMode = intent.getBooleanExtra("test_mode", false)
        isPracticeMode = intent.getBooleanExtra("practice_mode", false)
        requiredCount = prefManager.guessRequiredRounds.coerceAtLeast(1)
        sessionSolvedCount = 0

        if (isPracticeMode) {
            showLimitPicker()
        } else {
            binding.layoutLimitPicker.visibility = View.GONE
            binding.layoutGame.visibility = View.VISIBLE
            startNewGame()
        }
        setupListeners()
    }

    // ─── Limit seçici (sadece pratik mod) ────────────────────────────────────

    private fun showLimitPicker() {
        binding.layoutLimitPicker.visibility = View.VISIBLE
        binding.layoutGame.visibility = View.GONE

        // SeekBar başlangıç değeri — mevcut indeks
        val defaultIdx = limitSteps.indexOfFirst { it >= 100 }.coerceAtLeast(0)
        binding.seekBarLimit.max = limitSteps.size - 1
        binding.seekBarLimit.progress = defaultIdx
        binding.tvLimitValue.text = limitSteps[defaultIdx].toString()

        binding.seekBarLimit.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar, progress: Int, fromUser: Boolean) {
                binding.tvLimitValue.text = limitSteps[progress].toString()
            }
            override fun onStartTrackingTouch(sb: SeekBar) {}
            override fun onStopTrackingTouch(sb: SeekBar) {}
        })

        binding.btnStartGame.setOnClickListener {
            gameMax = limitSteps[binding.seekBarLimit.progress]
            binding.layoutLimitPicker.visibility = View.GONE
            binding.layoutGame.visibility = View.VISIBLE
            startNewGame()
        }
    }

    private fun startNewGame() {
        if (!isPracticeMode) {
            gameMax = prefManager.guessMaxNumber
        }
        secretNumber = Random.nextInt(0, gameMax + 1)
        attempts = 0
        rangeMin = 0
        rangeMax = gameMax

        binding.tvSubtitle.text = if (!isPracticeMode && requiredCount > 1) {
            "Tur ${sessionSolvedCount + 1}/$requiredCount • " + getString(R.string.guess_subtitle, gameMax)
        } else {
            getString(R.string.guess_subtitle, gameMax)
        }
        binding.tvAttempt.text = getString(R.string.guess_attempt, 0)
        binding.tvRange.text = getString(R.string.guess_range, rangeMin, rangeMax)
        binding.tvHint.text = ""
        binding.tvSuccess.visibility = View.GONE
        binding.etGuess.setText("")
        binding.etGuess.isEnabled = true
        binding.btnGuess.isEnabled = true
        binding.etGuess.requestFocus()
    }

    private fun makeGuess() {
        val guessText = binding.etGuess.text.toString().trim()
        if (guessText.isEmpty()) return

        val guess = guessText.toIntOrNull()
        if (guess == null || guess < 0 || guess > gameMax) {
            binding.tvHint.text = getString(R.string.guess_invalid, gameMax)
            binding.tvHint.setTextColor(getColor(R.color.wrong_red))
            return
        }

        attempts++
        binding.tvAttempt.text = getString(R.string.guess_attempt, attempts)
        binding.etGuess.setText("")

        when {
            guess == secretNumber -> {
                // Doğru tahmin!
                onCorrectGuess()
            }
            guess < secretNumber -> {
                rangeMin = maxOf(rangeMin, guess + 1)
                binding.tvHint.text = getString(R.string.guess_higher)
                binding.tvHint.setTextColor(getColor(R.color.hint_blue))
                binding.tvRange.text = getString(R.string.guess_range, rangeMin, rangeMax)
            }
            else -> {
                rangeMax = minOf(rangeMax, guess - 1)
                binding.tvHint.text = getString(R.string.guess_lower)
                binding.tvHint.setTextColor(getColor(R.color.accent))
                binding.tvRange.text = getString(R.string.guess_range, rangeMin, rangeMax)
            }
        }
    }

    private fun onCorrectGuess() {
        sessionSolvedCount++
        binding.tvHint.text = ""
        binding.etGuess.isEnabled = false
        binding.btnGuess.isEnabled = false

        if (isPracticeMode) {
            // Pratik modda: tebrik → tekrar oyna (limit seçiciye dön)
            binding.tvSuccess.visibility = View.VISIBLE
            binding.tvSuccess.text = getString(R.string.guess_correct, attempts) + "\n⭐ Toplam: $sessionSolvedCount"
            binding.root.postDelayed({
                if (!isFinishing && !isDestroyed) {
                    binding.tvSuccess.visibility = View.GONE
                    showLimitPicker()
                }
            }, 2000)
            return
        }

        if (sessionSolvedCount >= requiredCount) {
            // Yeterli tur tamamlandı — aktiviteyi kapat
            // NOT: Sayı Tahmin artık kilit açma amaçlı kullanılmıyor.
            // Kilit açma sadece MathChallengeActivity üzerinden yapılır.
            binding.tvSuccess.visibility = View.VISIBLE
            binding.tvSuccess.text = getString(R.string.guess_correct, attempts)
            binding.root.postDelayed({ finish() }, 2000)
        } else {
            // Daha tur var — kısa mesaj, sonra yeni oyun
            binding.tvSuccess.visibility = View.VISIBLE
            binding.tvSuccess.text = "✅ Doğru! ($sessionSolvedCount/$requiredCount) Sonraki tur..."
            binding.root.postDelayed({
                if (!isFinishing && !isDestroyed) {
                    binding.tvSuccess.visibility = View.GONE
                    binding.etGuess.isEnabled = true
                    binding.btnGuess.isEnabled = true
                    startNewGame()
                }
            }, 1500)
        }
    }

    private fun setupListeners() {
        binding.btnGuess.setOnClickListener { makeGuess() }

        binding.etGuess.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                makeGuess()
                true
            } else false
        }
    }

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        finish()
    }
}
