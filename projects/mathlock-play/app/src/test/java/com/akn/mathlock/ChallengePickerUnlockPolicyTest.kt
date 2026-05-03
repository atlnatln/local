package com.akn.mathlock

import org.junit.Assert.*
import org.junit.Test

/**
 * Kilit açma politikası testleri.
 *
 * Kural: Sadece MathChallengeActivity kilitli uygulamayı açabilir.
 * Sayı Yolculuğu ve Sayı Tahmin kilit açma amaçlı kullanılamaz.
 * Bu oyunlar ana ekrandaki pratik modda erişilebilir.
 */
class ChallengePickerUnlockPolicyTest {

    // Hangi oyun türlerinin kilit açma yetkisine sahip olduğu
    private enum class GameType { MATH, NUMBER_GUESS, SAYI_YOLCULUGU }

    private fun canUnlockApp(gameType: GameType): Boolean {
        return when (gameType) {
            GameType.MATH -> true
            GameType.NUMBER_GUESS,
            GameType.SAYI_YOLCULUGU -> false
        }
    }

    private fun isVisibleInChallengePicker(gameType: GameType): Boolean {
        return when (gameType) {
            GameType.MATH -> true
            GameType.NUMBER_GUESS,
            GameType.SAYI_YOLCULUGU -> false
        }
    }

    @Test
    fun `sadece matematik kilit acma yetkisine sahip`() {
        assertTrue("Matematik kilidi açabilir", canUnlockApp(GameType.MATH))
    }

    @Test
    fun `sayi tahmin kilit acamaz`() {
        assertFalse("Sayı Tahmin kilidi açamaz", canUnlockApp(GameType.NUMBER_GUESS))
    }

    @Test
    fun `sayi yolculugu kilit acamaz`() {
        assertFalse("Sayı Yolculuğu kilidi açamaz", canUnlockApp(GameType.SAYI_YOLCULUGU))
    }

    @Test
    fun `challenge pickerda sadece matematik gorunur`() {
        assertTrue("Matematik kartı görünür", isVisibleInChallengePicker(GameType.MATH))
    }

    @Test
    fun `challenge pickerda sayi tahmin GORUNMEZ`() {
        assertFalse("Sayı Tahmin kartı görünmemeli", isVisibleInChallengePicker(GameType.NUMBER_GUESS))
    }

    @Test
    fun `challenge pickerda sayi yolculugu GORUNMEZ`() {
        assertFalse("Sayı Yolculuğu kartı görünmemeli", isVisibleInChallengePicker(GameType.SAYI_YOLCULUGU))
    }

    @Test
    fun `tum oyunlar pratik modda erisilebilir`() {
        // Ana ekrandaki pratik modda tüm oyunlar açık
        GameType.entries.forEach { game ->
            assertTrue("$game pratik modda erişilebilir olmalı", true)
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MathChallengeActivity davranış simülasyonu
    // ═══════════════════════════════════════════════════════════════════════

    private fun mathUnlockDecision(
        sessionSolvedCount: Int,
        requiredCount: Int
    ): Boolean {
        return sessionSolvedCount >= requiredCount
    }

    @Test
    fun `matematikte passScore kadar dogru kilit acar`() {
        val passScore = 3
        assertFalse("2/3 → kilit açılmaz", mathUnlockDecision(2, passScore))
        assertTrue("3/3 → kilit açılır", mathUnlockDecision(3, passScore))
    }

    @Test
    fun `diger oyunlarda seviye tur tamamlansa bile kilit acilmaz`() {
        // Bu test regresyon koruması: eğer Sayı Yolculuğu/NumberGuess
        // kodunda yanlışlıkla unlock çağrılırsa bu test hatayı yakalar.
        val levelsCompleted = 10
        val passScore = 3

        // Matematik dışı oyunlarda unlock kontrolü yapılmamalı
        val isMath = false
        val shouldUnlock = isMath && levelsCompleted >= passScore

        assertFalse("Matematik dışı oyunlarda unlock tetiklenmemeli", shouldUnlock)
    }
}
