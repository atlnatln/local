package com.akn.mathlock

import android.os.Bundle
import android.view.Gravity
import android.widget.GridLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.databinding.ActivityPatternBinding
import com.akn.mathlock.util.PreferenceManager
import com.google.android.material.button.MaterialButton

class PatternActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPatternBinding
    private lateinit var prefManager: PreferenceManager

    private var mode = "verify" // "verify" veya "set" veya "confirm"
    private var selectedPattern = mutableListOf<Int>()
    private var firstPattern: String? = null // "set" modunda ilk desen

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPatternBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)
        mode = intent.getStringExtra("mode") ?: "verify"

        setupGrid()
        setupListeners()
        updateTitle()
    }

    private fun setupGrid() {
        binding.patternGrid.removeAllViews()

        for (i in 1..9) {
            val button = MaterialButton(this).apply {
                text = i.toString()
                textSize = 20f
                id = i
                val params = GridLayout.LayoutParams().apply {
                    width = 0
                    height = 0
                    columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f)
                    rowSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f)
                    setMargins(4, 4, 4, 4)
                }
                layoutParams = params
                gravity = Gravity.CENTER

                setOnClickListener {
                    if (!selectedPattern.contains(i)) {
                        selectedPattern.add(i)
                        isEnabled = false
                        alpha = 0.5f
                        updateSequenceDisplay()
                    }
                }
            }
            binding.patternGrid.addView(button)
        }
    }

    private fun updateSequenceDisplay() {
        binding.tvPatternSequence.text = selectedPattern.joinToString(" → ")
    }

    private fun updateTitle() {
        binding.tvPatternTitle.text = when (mode) {
            "set" -> getString(R.string.pattern_set_new)
            "confirm" -> getString(R.string.pattern_confirm)
            else -> getString(R.string.pattern_draw)
        }
    }

    private fun setupListeners() {
        binding.btnPatternClear.setOnClickListener {
            clearPattern()
        }

        binding.btnPatternConfirm.setOnClickListener {
            if (selectedPattern.size < 3) {
                binding.tvPatternStatus.text = "⚠️ En az 3 nokta seçin!"
                binding.tvPatternStatus.setTextColor(getColor(R.color.wrong_red))
                return@setOnClickListener
            }

            val patternStr = selectedPattern.joinToString(",")

            when (mode) {
                "verify" -> {
                    if (prefManager.verifyPattern(patternStr)) {
                        setResult(RESULT_OK)
                        finish()
                    } else {
                        binding.tvPatternStatus.text = getString(R.string.pattern_wrong)
                        binding.tvPatternStatus.setTextColor(getColor(R.color.wrong_red))
                        clearPattern()
                    }
                }
                "set" -> {
                    // İlk deseni kaydet, onay moduna geç
                    firstPattern = patternStr
                    mode = "confirm"
                    updateTitle()
                    clearPattern()
                    binding.tvPatternStatus.text = ""
                }
                "confirm" -> {
                    // İlk desenle karşılaştır
                    if (patternStr == firstPattern) {
                        prefManager.setPattern(patternStr)
                        Toast.makeText(this, getString(R.string.pattern_saved), Toast.LENGTH_SHORT).show()
                        setResult(RESULT_OK)
                        finish()
                    } else {
                        binding.tvPatternStatus.text = getString(R.string.pattern_mismatch)
                        binding.tvPatternStatus.setTextColor(getColor(R.color.wrong_red))
                        // İlk adıma geri dön
                        mode = "set"
                        firstPattern = null
                        updateTitle()
                        clearPattern()
                    }
                }
            }
        }
    }

    private fun clearPattern() {
        selectedPattern.clear()
        binding.tvPatternSequence.text = ""

        // Butonları geri etkinleştir
        for (i in 0 until binding.patternGrid.childCount) {
            val child = binding.patternGrid.getChildAt(i)
            child.isEnabled = true
            child.alpha = 1.0f
        }
    }
}
