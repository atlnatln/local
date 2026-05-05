package com.akn.mathlock.util

import kotlin.random.Random

/**
 * Sayı Hafızası oyun mantığı — View'dan bağımsız, test edilebilir.
 */
class MemoryGameEngine(val pairCount: Int) {

    data class Card(
        val id: Int,
        val value: Int,
        var isFlipped: Boolean = false,
        var isMatched: Boolean = false
    )

    enum class FlipResult {
        INVALID,      // Kart açık/eşleşmiş veya processing
        FIRST_CARD,   // İlk kart açıldı, ikinciyi bekle
        MATCH,        // Eşleşti
        NO_MATCH,     // Eşleşmedi, kapatılacak
        GAME_COMPLETE // Eşleşti ve oyun bitti
    }

    val cards: MutableList<Card> = mutableListOf()
    var moves: Int = 0
        private set
    var matches: Int = 0
        private set
    var firstSelectedIndex: Int? = null
        private set
    var isProcessing: Boolean = false
        private set

    init {
        require(pairCount in 4..20) { "pairCount 4-20 arası olmalı" }
        shuffle()
    }

    fun shuffle() {
        cards.clear()
        val temp = mutableListOf<Int>()
        for (i in 1..pairCount) {
            temp.add(i)
            temp.add(i)
        }
        // Fisher-Yates shuffle
        for (i in temp.size - 1 downTo 1) {
            val j = Random.nextInt(0, i + 1)
            val swap = temp[i]
            temp[i] = temp[j]
            temp[j] = swap
        }
        temp.forEachIndexed { index, value ->
            cards.add(Card(id = index, value = value))
        }
        moves = 0
        matches = 0
        firstSelectedIndex = null
        isProcessing = false
    }

    /**
     * Kart çevirme girişimi.
     * @return FlipResult ile ne olduğu bildirilir.
     */
    fun flipCard(index: Int): FlipResult {
        if (isProcessing) return FlipResult.INVALID
        if (index !in cards.indices) return FlipResult.INVALID
        val card = cards[index]
        if (card.isFlipped || card.isMatched) return FlipResult.INVALID

        card.isFlipped = true

        val first = firstSelectedIndex
        if (first == null) {
            firstSelectedIndex = index
            return FlipResult.FIRST_CARD
        }

        // İkinci kart seçildi
        isProcessing = true
        moves++
        val firstCard = cards[first]

        return if (firstCard.value == card.value) {
            firstCard.isMatched = true
            card.isMatched = true
            matches++
            firstSelectedIndex = null
            isProcessing = false
            if (matches == pairCount) FlipResult.GAME_COMPLETE else FlipResult.MATCH
        } else {
            FlipResult.NO_MATCH
        }
    }

    /**
     * Eşleşmeyen kartları kapat (UI gecikmesinden sonra çağrılır).
     */
    fun closeUnmatched() {
        val first = firstSelectedIndex ?: return
        cards[first].isFlipped = false
        // İkinci kartı bul (isFlipped=true ama isMatched=false olan)
        val second = cards.indexOfFirst { it.isFlipped && !it.isMatched }
        if (second != -1) {
            cards[second].isFlipped = false
        }
        firstSelectedIndex = null
        isProcessing = false
    }

    fun isGameComplete(): Boolean = matches == pairCount

    fun getColumnCount(): Int = when {
        pairCount <= 6 -> 2
        pairCount <= 12 -> 3
        else -> 4
    }
}
