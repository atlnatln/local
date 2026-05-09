package com.akn.mathlock

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.FrameLayout
import android.widget.GridLayout
import androidx.appcompat.app.AlertDialog
import com.akn.mathlock.databinding.ActivityMemoryGameBinding
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.MemoryGameEngine
import com.akn.mathlock.util.PreferenceManager
import com.google.android.material.card.MaterialCardView

class MemoryGameActivity : BaseActivity() {

    companion object {
        private const val TAG = "MemoryGame"
        private const val FLIP_DURATION = 180L
        private const val MATCH_DELAY = 400L
        private const val CLOSE_DELAY = 800L
    }

    private lateinit var binding: ActivityMemoryGameBinding
    private lateinit var prefManager: PreferenceManager
    private var engine: MemoryGameEngine? = null

    private var lockedPackage: String? = null
    private var isTestMode = false
    private var isPracticeMode = false

    private var pairCount = 6
    private var requiredRounds = 2
    private var previewSeconds = 2
    private var sessionSolvedCount = 0
    private var isProcessing = false

    private val handler = Handler(Looper.getMainLooper())
    private val cardViews = mutableListOf<ViewHolder>()

    private data class ViewHolder(
        val container: FrameLayout,
        val front: MaterialCardView,
        val back: MaterialCardView,
        val valueText: android.widget.TextView,
        val matchedOverlay: View
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMemoryGameBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)
        lockedPackage = intent.getStringExtra("locked_package")
        isTestMode = intent.getBooleanExtra("test_mode", false)
        isPracticeMode = intent.getBooleanExtra("practice_mode", false)

        pairCount = prefManager.memoryGamePairCount
        requiredRounds = prefManager.memoryGameRequiredRounds
        previewSeconds = prefManager.memoryGamePreviewSeconds

        setupListeners()

        if (isPracticeMode || isTestMode) {
            showSetupScreen()
        } else {
            // Kilit açma modu: ebeveyn ayarlarıyla doğrudan başla
            binding.setupContainer.visibility = View.GONE
            binding.gameScroll.visibility = View.VISIBLE
            startGame()
        }
    }

    private fun setupListeners() {
        binding.btnBack.setOnClickListener { finish() }
        binding.btnRestart.setOnClickListener { restartGame() }
        binding.btnPlayAgain.setOnClickListener {
            binding.winOverlay.visibility = View.GONE
            if (isPracticeMode || isTestMode) {
                showSetupScreen()
            } else {
                restartGame()
            }
        }

        binding.sliderPairCount.addOnChangeListener { _, value, _ ->
            val count = value.toInt()
            pairCount = count
            binding.tvPairCountLabel.text = "$count çift (${count * 2} kart)"
        }
        binding.sliderPairCount.valueTo = 30f

        binding.btnStart.setOnClickListener {
            binding.setupContainer.visibility = View.GONE
            binding.gameScroll.visibility = View.VISIBLE
            startGame()
        }
    }

    private fun showSetupScreen() {
        binding.setupContainer.visibility = View.VISIBLE
        binding.gameScroll.visibility = View.GONE
        binding.winOverlay.visibility = View.GONE
        binding.btnRestart.visibility = View.GONE
        binding.tvRounds.visibility = View.VISIBLE
        updateRoundDisplay()
        binding.sliderPairCount.value = pairCount.toFloat()
        binding.tvPairCountLabel.text = "$pairCount çift (${pairCount * 2} kart)"
    }

    private fun startGame() {
        engine = MemoryGameEngine(pairCount)
        isProcessing = false
        cardViews.clear()
        buildGrid()
        updateScore()
        binding.btnRestart.visibility = View.VISIBLE
        binding.tvRounds.visibility = View.VISIBLE
        updateRoundDisplay()

        if (previewSeconds > 0) {
            showPreviewThenHide()
        }
    }

    private fun showPreviewThenHide() {
        isProcessing = true
        // Tüm kartları aç (animasyonsuz)
        cardViews.forEach { holder ->
            holder.front.visibility = View.INVISIBLE
            holder.back.visibility = View.VISIBLE
        }
        handler.postDelayed({
            // Tüm kartları kapat
            cardViews.forEach { holder ->
                holder.back.visibility = View.INVISIBLE
                holder.front.visibility = View.VISIBLE
            }
            isProcessing = false
        }, previewSeconds * 1000L)
    }

    private fun restartGame() {
        engine?.shuffle()
        isProcessing = false
        cardViews.forEachIndexed { index, holder ->
            holder.back.visibility = View.INVISIBLE
            holder.front.visibility = View.VISIBLE
            holder.matchedOverlay.visibility = View.INVISIBLE
            holder.container.isClickable = true
            holder.container.rotationY = 0f
            // Yeni turda kart değerlerini güncelle — önceki turun sayıları kalmasın
            engine?.cards?.getOrNull(index)?.let { card ->
                holder.valueText.text = card.value.toString()
            }
        }
        updateScore()
        binding.winOverlay.visibility = View.GONE
        if (previewSeconds > 0) {
            showPreviewThenHide()
        }
    }

    private fun buildGrid() {
        val grid = binding.cardGrid
        grid.removeAllViews()
        val columnCount = engine?.getColumnCount() ?: 3
        grid.columnCount = columnCount

        val inflater = LayoutInflater.from(this)
        val density = resources.displayMetrics.density
        val displayMetrics = resources.displayMetrics
        val screenWidth = displayMetrics.widthPixels

        val gridPadding = (16 * density).toInt()
        val cardMargin = (6 * density).toInt()
        val availableWidth = screenWidth - gridPadding * 2
        val cardSize = (availableWidth - cardMargin * 2 * columnCount) / columnCount
        val finalCardSize = cardSize.coerceAtLeast((40 * density).toInt())
        val textSize = (finalCardSize / density * 0.35f).coerceIn(12f, 28f)

        engine?.cards?.forEachIndexed { index, card ->
            val view = inflater.inflate(R.layout.item_memory_card, grid, false)
            val container = view.findViewById<FrameLayout>(R.id.cardContainer)
            val front = view.findViewById<MaterialCardView>(R.id.cardFront)
            val back = view.findViewById<MaterialCardView>(R.id.cardBack)
            val valueText = view.findViewById<android.widget.TextView>(R.id.tvCardValue)
            val matchedOverlay = view.findViewById<View>(R.id.matchedOverlay)

            valueText.text = card.value.toString()
            valueText.textSize = textSize
            container.cameraDistance = 8000 * density

            // Dinamik kart boyutu
            val lp = FrameLayout.LayoutParams(finalCardSize, finalCardSize)
            lp.setMargins(cardMargin, cardMargin, cardMargin, cardMargin)
            view.layoutParams = lp

            val cardLp = FrameLayout.LayoutParams(finalCardSize, finalCardSize)
            front.layoutParams = cardLp
            back.layoutParams = cardLp
            matchedOverlay.layoutParams = cardLp

            val holder = ViewHolder(container, front, back, valueText, matchedOverlay)
            cardViews.add(holder)

            container.setOnClickListener { onCardClick(index, holder) }
            grid.addView(view)
        }
    }

    private fun onCardClick(index: Int, holder: ViewHolder) {
        if (isProcessing) return
        val eng = engine ?: return
        val result = eng.flipCard(index)

        when (result) {
            MemoryGameEngine.FlipResult.INVALID -> return
            MemoryGameEngine.FlipResult.FIRST_CARD -> {
                flipOpen(holder)
            }
            MemoryGameEngine.FlipResult.MATCH,
            MemoryGameEngine.FlipResult.GAME_COMPLETE -> {
                flipOpen(holder)
                isProcessing = true
                handler.postDelayed({
                    markMatchedCards()
                    updateScore()
                    isProcessing = false
                    if (result == MemoryGameEngine.FlipResult.GAME_COMPLETE) {
                        onRoundComplete()
                    }
                }, MATCH_DELAY)
            }
            MemoryGameEngine.FlipResult.NO_MATCH -> {
                flipOpen(holder)
                isProcessing = true
                updateScore()
                handler.postDelayed({
                    closeUnmatchedCards()
                    eng.closeUnmatched()
                    isProcessing = false
                }, CLOSE_DELAY)
            }
        }
    }

    private fun flipOpen(holder: ViewHolder) {
        holder.container.animate()
            .rotationY(90f)
            .setDuration(FLIP_DURATION)
            .withEndAction {
                holder.front.visibility = View.INVISIBLE
                holder.back.visibility = View.VISIBLE
                holder.container.rotationY = -90f
                holder.container.animate()
                    .rotationY(0f)
                    .setDuration(FLIP_DURATION)
                    .start()
            }
            .start()
    }

    private fun closeUnmatchedCards() {
        cardViews.forEachIndexed { index, holder ->
            val card = engine?.cards?.getOrNull(index) ?: return@forEachIndexed
            if (card.isFlipped && !card.isMatched) {
                holder.container.animate()
                    .rotationY(90f)
                    .setDuration(FLIP_DURATION)
                    .withEndAction {
                        holder.back.visibility = View.INVISIBLE
                        holder.front.visibility = View.VISIBLE
                        holder.container.rotationY = -90f
                        holder.container.animate()
                            .rotationY(0f)
                            .setDuration(FLIP_DURATION)
                            .start()
                    }
                    .start()
            }
        }
    }

    private fun markMatchedCards() {
        cardViews.forEachIndexed { index, holder ->
            val card = engine?.cards?.getOrNull(index) ?: return@forEachIndexed
            if (card.isMatched && holder.matchedOverlay.visibility != View.VISIBLE) {
                holder.matchedOverlay.visibility = View.VISIBLE
                holder.container.isClickable = false
                // Hafif scale animasyonu
                val scaleX = ObjectAnimator.ofFloat(holder.container, "scaleX", 1f, 1.1f, 1f)
                val scaleY = ObjectAnimator.ofFloat(holder.container, "scaleY", 1f, 1.1f, 1f)
                AnimatorSet().apply {
                    playTogether(scaleX, scaleY)
                    duration = 300
                    start()
                }
            }
        }
    }

    private fun updateScore() {
        val eng = engine ?: return
        binding.tvMoves.text = "Hamle: ${eng.moves}"
        binding.tvMatches.text = "Eşleşme: ${eng.matches}/${eng.pairCount}"
    }

    private fun updateRoundDisplay() {
        binding.tvRounds.text = "Set: $sessionSolvedCount/$requiredRounds"
    }

    private fun onRoundComplete() {
        sessionSolvedCount++
        updateRoundDisplay()

        if (isTestMode) {
            showWinDialog("Test tamamlandı!", "$pairCount çifti ${engine?.moves ?: 0} hamlede eşleştirdin.")
            return
        }

        if (isPracticeMode) {
            showWinDialog("Tebrikler!", "${engine?.moves ?: 0} hamlede bitirdin.\n⭐ Toplam: $sessionSolvedCount tur")
            return
        }

        if (sessionSolvedCount >= requiredRounds) {
            // Kilit açma hedefine ulaşıldı
            showWinDialog("Kilit Açılıyor!", "$sessionSolvedCount tur tamamlandı. Uygulama açılıyor...")
            handler.postDelayed({ unlockAndLaunchApp() }, 1500)
        } else {
            // Daha tur var, kısa mesaj sonra yeni oyun
            showWinDialog("Set Tamamlandı!", "$sessionSolvedCount/$requiredRounds set bitti.\nSonraki set başlıyor...")
            handler.postDelayed({
                binding.winOverlay.visibility = View.GONE
                restartGame()
            }, 1500)
        }
    }

    private fun showWinDialog(title: String, message: String) {
        binding.tvWinTitle.text = title
        binding.tvWinMessage.text = message
        binding.winOverlay.visibility = View.VISIBLE
    }

    private fun unlockAndLaunchApp() {
        if (isTestMode) {
            AlertDialog.Builder(this)
                .setTitle("Test Başarılı")
                .setMessage("Uygulama açılacaktı.")
                .setPositiveButton("Tamam") { _, _ -> finish() }
                .show()
            return
        }

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

    override fun onBackPressed() {
        if (isTestMode || isPracticeMode) {
            super.onBackPressed()
        } else {
            val homeIntent = Intent(Intent.ACTION_MAIN).apply {
                addCategory(Intent.CATEGORY_HOME)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            startActivity(homeIntent)
            finish()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }
}
