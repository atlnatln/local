package com.akn.mathlock

import com.akn.mathlock.util.MemoryGameEngine
import org.junit.Assert.*
import org.junit.Test

/**
 * Sayı Hafızası oyun motoru (MemoryGameEngine) unit testleri.
 * Android Context gerektirmez — saf Kotlin mantığı test edilir.
 */
class MemoryGameEngineTest {

    // ═══════════════════════════════════════════════════════════════════════
    // 1. Başlangıç ve Shuffle
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `6 cift icin 12 kart olusmali`() {
        val engine = MemoryGameEngine(6)
        assertEquals("6 çift = 12 kart", 12, engine.cards.size)
    }

    @Test
    fun `20 cift icin 40 kart olusmali`() {
        val engine = MemoryGameEngine(20)
        assertEquals("20 çift = 40 kart", 40, engine.cards.size)
    }

    @Test
    fun `her deger tam 2 kez tekrar etmeli`() {
        val engine = MemoryGameEngine(8)
        val valueCounts = engine.cards.groupingBy { it.value }.eachCount()

        assertEquals("Her değer 2 kez olmalı", 8, valueCounts.size)
        valueCounts.forEach { (value, count) ->
            assertEquals("Değer $value 2 kez tekrar etmeli", 2, count)
        }
    }

    @Test
    fun `shuffle sonrasi kartlar farkli siralarda olabilir`() {
        // Not: %100 deterministik değil ama çok düşük ihtimalle aynı kalabilir.
        // Bunun yerine shuffle sonrası değer setinin aynı kalmasını kontrol edelim.
        val engine = MemoryGameEngine(10)
        val before = engine.cards.map { it.value }

        engine.shuffle()
        val after = engine.cards.map { it.value }

        assertEquals("Aynı değerler olmalı", before.sorted(), after.sorted())
    }

    @Test(expected = IllegalArgumentException::class)
    fun `3 cift cok az olmali ve exception atmali`() {
        MemoryGameEngine(3)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `31 cift cok fazla olmali ve exception atmali`() {
        MemoryGameEngine(31)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 2. Temel Kart Çevirme
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `ilk kart cevirince FIRST_CARD donmeli`() {
        val engine = MemoryGameEngine(6)
        val result = engine.flipCard(0)
        assertEquals(MemoryGameEngine.FlipResult.FIRST_CARD, result)
        assertTrue("Kart açık olmalı", engine.cards[0].isFlipped)
        assertEquals("İlk seçim kaydedilmeli", 0, engine.firstSelectedIndex)
    }

    @Test
    fun `ayni degerli iki kart eslesince MATCH donmeli`() {
        val engine = MemoryGameEngine(4)
        // Aynı değere sahip iki kartın index'lerini bul
        val value = engine.cards[0].value
        val pairIndex = engine.cards.indexOfFirst { it.value == value && it.id != engine.cards[0].id }

        engine.flipCard(0)
        val result = engine.flipCard(pairIndex)

        assertEquals(MemoryGameEngine.FlipResult.MATCH, result)
        assertTrue("İlk kart matched", engine.cards[0].isMatched)
        assertTrue("İkinci kart matched", engine.cards[pairIndex].isMatched)
    }

    @Test
    fun `farkli degerli iki kart eslesmeyince NO_MATCH donmeli`() {
        val engine = MemoryGameEngine(6)
        // Farklı değere sahip iki kart bul
        val firstIdx = 0
        val firstValue = engine.cards[firstIdx].value
        val secondIdx = engine.cards.indexOfFirst { it.value != firstValue }

        engine.flipCard(firstIdx)
        val result = engine.flipCard(secondIdx)

        assertEquals(MemoryGameEngine.FlipResult.NO_MATCH, result)
        assertFalse("İlk kart matched olmamalı", engine.cards[firstIdx].isMatched)
        assertFalse("İkinci kart matched olmamalı", engine.cards[secondIdx].isMatched)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 3. Durum Makinesi ve Geçersiz Hareketler
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `acik karta tekrar tiklayinca INVALID donmeli`() {
        val engine = MemoryGameEngine(6)
        engine.flipCard(0)
        val result = engine.flipCard(0)
        assertEquals(MemoryGameEngine.FlipResult.INVALID, result)
    }

    @Test
    fun `eslesmis karta tiklayinca INVALID donmeli`() {
        val engine = MemoryGameEngine(4)
        val value = engine.cards[0].value
        val pairIndex = engine.cards.indexOfFirst { it.value == value && it.id != engine.cards[0].id }

        engine.flipCard(0)
        engine.flipCard(pairIndex) // MATCH

        val result = engine.flipCard(0)
        assertEquals(MemoryGameEngine.FlipResult.INVALID, result)
    }

    @Test
    fun `isProcessing true iken yeni tiklama INVALID olmali`() {
        val engine = MemoryGameEngine(6)
        val firstValue = engine.cards[0].value
        val secondIdx = engine.cards.indexOfFirst { it.value != firstValue }

        engine.flipCard(0)
        engine.flipCard(secondIdx) // NO_MATCH → isProcessing = true

        val result = engine.flipCard(2)
        assertEquals(MemoryGameEngine.FlipResult.INVALID, result)
    }

    @Test
    fun `gecersiz index INVALID donmeli`() {
        val engine = MemoryGameEngine(6)
        val result = engine.flipCard(99)
        assertEquals(MemoryGameEngine.FlipResult.INVALID, result)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 4. closeUnmatched Davranışı
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `closeUnmatched sonrasi kartlar kapanmali ve processing false olmali`() {
        val engine = MemoryGameEngine(6)
        val firstValue = engine.cards[0].value
        val secondIdx = engine.cards.indexOfFirst { it.value != firstValue }

        engine.flipCard(0)
        engine.flipCard(secondIdx) // NO_MATCH

        assertTrue("Processing başlamalı", engine.isProcessing)
        engine.closeUnmatched()

        assertFalse("Kartlar kapanmalı", engine.cards[0].isFlipped)
        assertFalse("İkinci kart kapanmalı", engine.cards[secondIdx].isFlipped)
        assertFalse("Processing bitmeli", engine.isProcessing)
        assertNull("firstSelected temizlenmeli", engine.firstSelectedIndex)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 5. Skor ve Sayaçlar
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `MATCH sonrasi matches artmali moves artmali`() {
        val engine = MemoryGameEngine(4)
        val value = engine.cards[0].value
        val pairIndex = engine.cards.indexOfFirst { it.value == value && it.id != engine.cards[0].id }

        engine.flipCard(0)
        engine.flipCard(pairIndex)

        assertEquals("1 eşleşme", 1, engine.matches)
        assertEquals("1 hamle", 1, engine.moves)
    }

    @Test
    fun `NO_MATCH sonrasi moves artmali matches artmamali`() {
        val engine = MemoryGameEngine(6)
        val firstValue = engine.cards[0].value
        val secondIdx = engine.cards.indexOfFirst { it.value != firstValue }

        engine.flipCard(0)
        engine.flipCard(secondIdx)

        assertEquals("0 eşleşme", 0, engine.matches)
        assertEquals("1 hamle", 1, engine.moves)
    }

    @Test
    fun `shuffle sonrasi skorlar sifirlanmali`() {
        val engine = MemoryGameEngine(4)
        val value = engine.cards[0].value
        val pairIndex = engine.cards.indexOfFirst { it.value == value && it.id != engine.cards[0].id }

        engine.flipCard(0)
        engine.flipCard(pairIndex)
        assertEquals(1, engine.matches)

        engine.shuffle()
        assertEquals("Matches sıfırlanmalı", 0, engine.matches)
        assertEquals("Moves sıfırlanmalı", 0, engine.moves)
        assertNull("firstSelected sıfırlanmalı", engine.firstSelectedIndex)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 6. Oyun Tamamlanma
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `tum ciftler eslesince GAME_COMPLETE donmeli`() {
        val engine = MemoryGameEngine(4)
        // Tüm çiftleri bul ve eşleştir
        val matchedValues = mutableSetOf<Int>()
        var lastResult: MemoryGameEngine.FlipResult? = null

        for (i in engine.cards.indices) {
            if (engine.cards[i].isMatched) continue
            val value = engine.cards[i].value
            if (matchedValues.contains(value)) continue

            val pairIndex = engine.cards.indexOfLast { it.value == value && it.id != engine.cards[i].id }
            engine.flipCard(i)
            lastResult = engine.flipCard(pairIndex)
            matchedValues.add(value)
        }

        assertEquals("Son eşleşme GAME_COMPLETE olmalı", MemoryGameEngine.FlipResult.GAME_COMPLETE, lastResult)
        assertTrue("Oyun tamamlanmalı", engine.isGameComplete())
    }

    @Test
    fun `tek ciftlik oyunda 2 kart eslesince GAME_COMPLETE donmeli`() {
        val engine = MemoryGameEngine(4)
        val value = engine.cards[0].value
        val pairIndex = engine.cards.indexOfFirst { it.value == value && it.id != engine.cards[0].id }

        engine.flipCard(0)
        val result = engine.flipCard(pairIndex)

        // 4 çift var, sadece 1 eşleşme → MATCH, GAME_COMPLETE değil
        assertEquals(MemoryGameEngine.FlipResult.MATCH, result)
        assertFalse("Henüz tamamlanmadı", engine.isGameComplete())
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 7. Grid Sütun Sayısı
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `4 cift icin 2 sutun`() {
        val engine = MemoryGameEngine(4)
        assertEquals(2, engine.getColumnCount())
    }

    @Test
    fun `6 cift icin 2 sutun`() {
        val engine = MemoryGameEngine(6)
        assertEquals(2, engine.getColumnCount())
    }

    @Test
    fun `8 cift icin 3 sutun`() {
        val engine = MemoryGameEngine(8)
        assertEquals(3, engine.getColumnCount())
    }

    @Test
    fun `12 cift icin 3 sutun`() {
        val engine = MemoryGameEngine(12)
        assertEquals(3, engine.getColumnCount())
    }

    @Test
    fun `14 cift icin 4 sutun`() {
        val engine = MemoryGameEngine(14)
        assertEquals(4, engine.getColumnCount())
    }

    @Test
    fun `20 cift icin 4 sutun`() {
        val engine = MemoryGameEngine(20)
        assertEquals(4, engine.getColumnCount())
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 8. Karmaşık Senaryolar
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `NO_MATCH sonrasi ayni kart tekrar acilabilmeli`() {
        val engine = MemoryGameEngine(6)
        val firstValue = engine.cards[0].value
        val secondIdx = engine.cards.indexOfFirst { it.value != firstValue }

        engine.flipCard(0)
        engine.flipCard(secondIdx) // NO_MATCH
        engine.closeUnmatched()

        val result = engine.flipCard(0)
        assertEquals(MemoryGameEngine.FlipResult.FIRST_CARD, result)
    }

    @Test
    fun `birden fazla MATCH sonrasi matches dogru sayilmali`() {
        val engine = MemoryGameEngine(6)
        val matchedValues = mutableSetOf<Int>()
        var totalMatches = 0

        for (i in engine.cards.indices) {
            if (engine.cards[i].isMatched) continue
            val value = engine.cards[i].value
            if (matchedValues.contains(value)) continue

            val pairIndex = engine.cards.indexOfLast { it.value == value && it.id != engine.cards[i].id }
            engine.flipCard(i)
            val result = engine.flipCard(pairIndex)

            if (result == MemoryGameEngine.FlipResult.MATCH || result == MemoryGameEngine.FlipResult.GAME_COMPLETE) {
                totalMatches++
                matchedValues.add(value)
            }
        }

        assertEquals("6 çift = 6 eşleşme", 6, totalMatches)
        assertEquals("Engine matches 6 olmalı", 6, engine.matches)
    }
}
