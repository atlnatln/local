package com.akn.mathlock

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.databinding.ActivityChallengePickerBinding

class ChallengePickerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityChallengePickerBinding
    private var lockedPackage: String? = null
    private var timerExpired: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityChallengePickerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        lockedPackage = intent.getStringExtra("locked_package")
        timerExpired  = intent.getBooleanExtra("timer_expired", false)

        // Kilitli uygulamanın adını göster
        lockedPackage?.let { pkg ->
            try {
                val appName = packageManager.getApplicationLabel(
                    packageManager.getApplicationInfo(pkg, 0)
                ).toString()
                binding.tvLockedAppName.text = "($appName)"
            } catch (e: Exception) {
                binding.tvLockedAppName.text = ""
            }
        }

        // Süre doldu banneri
        if (timerExpired) {
            binding.cardTimerExpired.visibility = View.VISIBLE
        }

        setupListeners()
    }

    private fun setupListeners() {
        binding.cardMath.setOnClickListener {
            val intent = Intent(this, MathChallengeActivity::class.java).apply {
                putExtra("locked_package", lockedPackage)
                putExtra("timer_expired", timerExpired)
            }
            startActivity(intent)
            finish()
        }

        binding.cardGuess.setOnClickListener {
            val intent = Intent(this, NumberGuessActivity::class.java).apply {
                putExtra("locked_package", lockedPackage)
                putExtra("timer_expired", timerExpired)
            }
            startActivity(intent)
            finish()
        }

        binding.cardParent.setOnClickListener {
            val intent = Intent(this, ParentAuthActivity::class.java).apply {
                putExtra("locked_package", lockedPackage)
                putExtra("timer_expired", timerExpired)
            }
            startActivity(intent)
            finish()
        }
    }

    override fun onBackPressed() {
        super.onBackPressed()
        // Geri tuşu - ana ekrana gönder
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(homeIntent)
        finish()
    }
}
