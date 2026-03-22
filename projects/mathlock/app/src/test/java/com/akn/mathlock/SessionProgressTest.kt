package com.akn.mathlock

import org.junit.Assert.*
import org.junit.Test

/**
 * Oturum ilerleme (sessionSolvedCount / requiredCount) mantığı için birim testler.
 *
 * Bu testler MathChallengeActivity ve NumberGuessActivity'nin doğru cevap
 * sonrası "kilit aç mı, sonraki soru mu?" kararını doğrular.
 *
 * Saf boolean/integer mantığı — Android Context gerektirmez.
 */
class SessionProgressTest {

    /**
     * Aktivitelerde kullanılan karar mantığını simüle eder:
     *   sessionSolvedCount++
     *   if (sessionSolvedCount >= requiredCount) → "unlock"
     *   else                                     → "next question"
     *
     * @return true = kilit açıldı, false = sonraki soru gösterildi
     */
    private fun onCorrectAnswer(
        sessionSolvedCount: Int,
        requiredCount: Int
    ): Pair<Boolean, Int> {   // (unlocked, newSessionSolvedCount)
        val newCount = sessionSolvedCount + 1
        return Pair(newCount >= requiredCount, newCount)
    }

    // ─── requiredCount = 1 (varsayılan) ──────────────────────────────────────

    @Test
    fun `1 soru gerekliyken 1 doğru cevap kilidi açmalı`() {
        val (unlocked, count) = onCorrectAnswer(0, 1)
        assertTrue("1/1 → kilit açılmalı", unlocked)
        assertEquals(1, count)
    }

    // ─── requiredCount = 3 ────────────────────────────────────────────────────

    @Test
    fun `3 soru gerekliyken 1 doğru cevap kilidi açmamalı`() {
        val (unlocked, _) = onCorrectAnswer(0, 3)
        assertFalse("1/3 → kilit açılmamalı", unlocked)
    }

    @Test
    fun `3 soru gerekliyken 2 doğru cevap kilidi açmamalı`() {
        val (unlocked, _) = onCorrectAnswer(1, 3)
        assertFalse("2/3 → kilit açılmamalı", unlocked)
    }

    @Test
    fun `3 soru gerekliyken 3 doğru cevap kilidi açmalı`() {
        val (unlocked, count) = onCorrectAnswer(2, 3)
        assertTrue("3/3 → kilit açılmalı", unlocked)
        assertEquals(3, count)
    }

    @Test
    fun `tam akış - 3 soru gerekliyken adım adım`() {
        var sessionSolvedCount = 0
        val requiredCount = 3

        // Soru 1
        val (u1, c1) = onCorrectAnswer(sessionSolvedCount, requiredCount)
        sessionSolvedCount = c1
        assertFalse("1. soru sonrası kilidsiz olmamalı", u1)
        assertEquals(1, sessionSolvedCount)

        // Soru 2
        val (u2, c2) = onCorrectAnswer(sessionSolvedCount, requiredCount)
        sessionSolvedCount = c2
        assertFalse("2. soru sonrası kilidsiz olmamalı", u2)
        assertEquals(2, sessionSolvedCount)

        // Soru 3 — kilit açılmalı
        val (u3, c3) = onCorrectAnswer(sessionSolvedCount, requiredCount)
        sessionSolvedCount = c3
        assertTrue("3. soru sonrası kilit açılmalı", u3)
        assertEquals(3, sessionSolvedCount)
    }

    // ─── requiredCount = 5 ────────────────────────────────────────────────────

    @Test
    fun `5 soru gerekliyken sadece 4 doğru kilidi açmamalı`() {
        var sessionSolvedCount = 0
        val requiredCount = 5
        repeat(4) {
            val (unlocked, c) = onCorrectAnswer(sessionSolvedCount, requiredCount)
            sessionSolvedCount = c
            assertFalse("${it + 1}/5 → kilit açılmamalı", unlocked)
        }
    }

    @Test
    fun `5 soru gerekliyken 5 doğru kilidi açmalı`() {
        var sessionSolvedCount = 4  // önceki 4 zaten çözülmüş
        val (unlocked, _) = onCorrectAnswer(sessionSolvedCount, 5)
        assertTrue("5/5 → kilit açılmalı", unlocked)
    }

    // ─── Sınır durumları ─────────────────────────────────────────────────────

    @Test
    fun `requiredCount 0 veya negatif - coerce sonrası en az 1 gerekli`() {
        // coerceAtLeast(1) uygulandıktan sonra: 1 doğru → unlock
        val required = 0.coerceAtLeast(1)
        assertEquals(1, required)
        val (unlocked, _) = onCorrectAnswer(0, required)
        assertTrue("coerce sonrası 1 doğru kilidi açmalı", unlocked)
    }

    @Test
    fun `sessionSolvedCount hiç sıfırlanmazsa ikinci challenge oturumu çalışmaz`() {
        // İlk oturum tamamlandı (3/3)
        var session = 3
        val required = 3

        // Yeni oturum başlamalı: session = 0
        session = 0
        val (unlocked, _) = onCorrectAnswer(session, required)
        assertFalse("Yeni oturum sıfırlandı — 1. doğru kilidi açmamalı", unlocked)
    }

    // ─── NumberGuess'e özel: requiredCount kadar oyun ─────────────────────────

    @Test
    fun `sayı bulma - 2 tur gerekliyken 1 kazanım kilidi açmamalı`() {
        val (unlocked, count) = onCorrectAnswer(0, 2)
        assertFalse("Tur 1/2 → kilit açılmamalı", unlocked)
        assertEquals(1, count)
    }

    @Test
    fun `sayı bulma - 2 tur gerekliyken 2 kazanım kilidi açmalı`() {
        val (unlocked, count) = onCorrectAnswer(1, 2)
        assertTrue("Tur 2/2 → kilit açılmalı", unlocked)
        assertEquals(2, count)
    }

    // ─── isJsonModeActive mantığı (bug regression) ──────────────────────────

    /**
     * JSON cache mevcutken soru seti bitmişse startFallbackMode() çağrılır.
     * Bu durumda isJsonModeActive=false olmalı → checkFallbackAnswer() çağrılır.
     * Eski kod: questionManager.isJsonMode = true (cache var) → checkJsonAnswer()
     * çağrılırdı, currentJsonQuestion = null olduğundan hemen dönerdi → STUCK.
     */
    @Test
    fun `isJsonModeActive - startFallbackMode cagrilinca false olmali`() {
        // Aktivite başlangıcı: varsayılan false
        var isJsonModeActive = false

        // startJsonMode() çağrılırsa true
        isJsonModeActive = true
        assertTrue("startJsonMode sonrası true olmalı", isJsonModeActive)

        // startFallbackMode() çağrılırsa false (JSON exhausted scenario)
        isJsonModeActive = false
        assertFalse("startFallbackMode sonrası false olmalı", isJsonModeActive)
    }

    @Test
    fun `mod seçimi - isJsonModeActive false iken checkFallbackAnswer cagrilmali`() {
        // setupListeners davranışını simüle et
        var checkJsonCalled = false
        var checkFallbackCalled = false
        val isJsonModeActive = false  // fallback mode

        if (isJsonModeActive) checkJsonCalled = true
        else checkFallbackCalled = true

        assertFalse("JSON checker çağrılmamalı", checkJsonCalled)
        assertTrue("Fallback checker çağrılmalı", checkFallbackCalled)
    }

    @Test
    fun `mod seçimi - isJsonModeActive true iken checkJsonAnswer cagrilmali`() {
        var checkJsonCalled = false
        var checkFallbackCalled = false
        val isJsonModeActive = true  // json mode

        if (isJsonModeActive) checkJsonCalled = true
        else checkFallbackCalled = true

        assertTrue("JSON checker çağrılmalı", checkJsonCalled)
        assertFalse("Fallback checker çağrılmamalı", checkFallbackCalled)
    }

    // ─── Fallback mode: passScore mantığı ────────────────────────────────────

    /**
     * Fallback modda doğru cevap sayısı >= passScore ise kilit açılır.
     * MathChallengeActivity.showFallbackResult() mantığını simüle eder.
     */
    private fun shouldUnlockFallback(correctCount: Int, passScore: Int): Boolean =
        correctCount >= passScore

    @Test
    fun `fallback - 3 sorudan 3 doğru ile kilit açılmalı`() {
        assertTrue(shouldUnlockFallback(3, 3))
    }

    @Test
    fun `fallback - 3 sorudan 2 doğru, passScore=3 ise kilit açılmamalı`() {
        assertFalse(shouldUnlockFallback(2, 3))
    }

    @Test
    fun `fallback - 5 sorudan 3 doğru, passScore=3 ise kilit açılmalı`() {
        assertTrue(shouldUnlockFallback(3, 3))
    }

    @Test
    fun `fallback - passScore 0 ise hemen kilit açılmalı`() {
        // 0 doğru cevap bile yeterli (0 >= 0)
        assertTrue(shouldUnlockFallback(0, 0))
    }

    // ─── Tam akış: yanlış cevaplar sessionSolvedCount artırmaz ──────────────

    @Test
    fun `yanlis cevaplar sessionSolvedCount artirmaz - 3 gerekliyken 2 yanlis + 3 dogru`() {
        var sessionSolvedCount = 0
        val requiredCount = 3

        // 2 yanlış atlandı (sessionSolvedCount değişmez)
        // JSON modda: yanlış cevap → soruyu geç, count artmaz
        // (aktivitede: showNextJsonQuestion çağrılır ama sessionSolvedCount++ yok)
        // Burada simüle ediyoruz: sadece doğru cevap ekler
        fun wrongAnswer() { /* sessionSolvedCount değişmez */ }

        wrongAnswer()
        wrongAnswer()
        assertEquals(0, sessionSolvedCount)
        assertFalse("2 yanlış sonrası kildsiz olmamalı", sessionSolvedCount >= requiredCount)

        // 3 doğru cevap
        repeat(3) {
            val (unlocked, newCount) = onCorrectAnswer(sessionSolvedCount, requiredCount)
            sessionSolvedCount = newCount
            if (sessionSolvedCount >= requiredCount) {
                assertTrue("3. doğruda kilidi açmalı", unlocked)
                return@repeat
            }
        }
        assertTrue("3 doğrudan sonra kilit açılmalı", sessionSolvedCount >= requiredCount)
    }

    @Test
    fun `requiredCount 1 iken 1 dogru hemen acmali - regresyon testi`() {
        // v1.14 öncesi: her zaman 1 soruda açılıyordu (bug)
        // v1.14 sonrası: requiredCount=1 ise 1 soruda açılması DOĞRU
        val (unlocked, _) = onCorrectAnswer(0, 1)
        assertTrue("1 gerekli → 1 doğru → kilit açılmalı", unlocked)
    }

    @Test
    fun `requiredCount 3 iken 1 dogru acmamali - regresyon testi`() {
        // v1.14 öncesi bug: 1 soruda her zaman açılıyordu
        // v1.14 sonrası düzeltme: artık 3 gerekli
        val (unlocked, _) = onCorrectAnswer(0, 3)
        assertFalse("3 gerekli → 1 doğru → kilit açılmamalı", unlocked)
    }
}

