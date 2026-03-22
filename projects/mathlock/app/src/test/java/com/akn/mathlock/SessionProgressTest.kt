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
}
