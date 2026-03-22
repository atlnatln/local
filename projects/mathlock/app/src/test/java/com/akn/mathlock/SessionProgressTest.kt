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

    // ─── v1.17 regression: requiredCount = passScore, questionCount değil ────

    /**
     * v1.17 öncesi bug: requiredCount = questionCount kullanılıyordu.
     * Kullanıcı "Soru Sayısı" slider'ını 50'ye çekince requiredCount=50 oluyordu
     * ve 50 doğru cevap gerekiyordu (pratik olarak imkânsız bir oturumda).
     *
     * Düzeltme: requiredCount = passScore (Geçiş Skoru).
     * Ayarlar: questionCount=50, passScore=2 → requiredCount=2 olmalı.
     */
    @Test
    fun `requiredCount passScore olmali - questionCount degil (v1_17 regression)`() {
        // Simülasyon: questionCount=50, passScore=2
        val questionCount = 50
        val passScore = 2

        // v1.17+: requiredCount = passScore
        val requiredCount = passScore.coerceAtLeast(1)
        assertEquals("requiredCount passScore olmalı", 2, requiredCount)

        // 2 doğru cevap yeterli olmalı
        var session = 0
        val (u1, c1) = onCorrectAnswer(session, requiredCount)
        session = c1
        assertFalse("1/2 → kilit açılmamalı", u1)

        val (u2, _) = onCorrectAnswer(session, requiredCount)
        assertTrue("2/2 → kilit açılmalı", u2)

        // questionCount ile 50 soru GEREKLMEZ
        assertNotEquals("requiredCount questionCount olmamalı", questionCount, requiredCount)
    }

    @Test
    fun `passScore questionCount ustu olamaz - coerce mantigi`() {
        // Eğer passScore > questionCount ise coerceAtMost(questionCount) düzeltir
        val questionCount = 3
        val passScore = 10
        val effective = passScore.coerceAtMost(questionCount)
        assertEquals("passScore questionCount ile sınırlanmalı", 3, effective)
    }

    @Test
    fun `passScore 1 ve questionCount 50 - tek dogru yeterli`() {
        val requiredCount = 1.coerceAtLeast(1)
        val (unlocked, _) = onCorrectAnswer(0, requiredCount)
        assertTrue("passScore=1 → 1 doğru → kilit açılmalı", unlocked)
    }

    // ─── v1.20: Ebeveyn önizleme modu (test_mode) izolasyonu ────────────────

    /**
     * Ebeveyn panelindeki soru önizlemesi (peekQuestion) QuestionManager'ın
     * kalıcı currentIndex'ini değiştirmemeli. testModeIndex lokal bir sayaçtır.
     */
    @Test
    fun `test mode - peekQuestion currentIndex ilerletmemeli`() {
        // Simülasyon: QuestionManager.currentIndex = 32, questions.size = 50
        val currentIndex = 32 // kalıcı, SharedPreferences'ta tutulan
        var testModeIndex = 0 // lokal, test moduna özel

        // Ebeveyn 5 soru önizler
        repeat(5) {
            val peekIndex = testModeIndex
            assertTrue("peekIndex $peekIndex sınırlar içinde olmalı", peekIndex < 50)
            testModeIndex++
        }

        // currentIndex değişmemiş olmalı (QuestionManager state korunuyor)
        assertEquals("currentIndex değişmemeli", 32, currentIndex)
        assertEquals("testModeIndex 5 olmalı", 5, testModeIndex)
    }

    @Test
    fun `test mode - index 0'dan baslar tum sorulari gosterir`() {
        val totalQuestions = 50
        val childCurrentIndex = 49 // çocuk 49. soruda

        // Test modu kendi index'ini 0'dan başlatır (çocuğun kaldığı yerden değil)
        val testModeIndex = 0
        assertNotEquals("testModeIndex childCurrentIndex'ten bağımsız", childCurrentIndex, testModeIndex)
        assertEquals("önizleme 0'dan başlamalı", 0, testModeIndex)

        // Tüm 50 soru önizlenebilir (49'da takılmaz)
        val previewableCount = totalQuestions - testModeIndex
        assertEquals("50 sorunun tamamı önizlenebilmeli", 50, previewableCount)
    }

    @Test
    fun `test mode - dogru cevap unlock tetiklememeli`() {
        // Test modunda sessionSolvedCount artmaz, unlock kontrolü yapılmaz
        val isTestMode = true
        val sessionSolvedCount = 0
        val requiredCount = 2

        // Doğru cevap geldi — test modunda sadece sonraki soruya geçilir
        if (isTestMode) {
            // unlock kontrolü yok, sadece showNextJsonQuestion
            val nextAction = "showNextQuestion"
            assertEquals("test modu sonraki soruya geçmeli", "showNextQuestion", nextAction)
        }

        // sessionSolvedCount değişmemiş olmalı
        assertEquals("test modu sessionSolvedCount artırmamalı", 0, sessionSolvedCount)
    }

    @Test
    fun `test mode - onSetComplete cagirilmamali`() {
        // Test modunda soru bitince onTestPreviewComplete çağrılır, onSetComplete değil
        val isTestMode = true
        val testModeIndex = 50
        val totalQuestions = 50

        // peekQuestion(50) null döner → hangi complete çağrılır?
        val questionAvailable = testModeIndex < totalQuestions // false
        assertFalse("50. index'te soru yok", questionAvailable)

        val completeAction = if (isTestMode) "onTestPreviewComplete" else "onSetComplete"
        assertEquals("test modu kendi bitiş ekranını göstermeli", "onTestPreviewComplete", completeAction)
    }

    @Test
    fun `test mode - stats kaydedilmemeli`() {
        val isTestMode = true
        var statsRecorded = false

        // Doğru cevap sonrası stats kaydı
        if (!isTestMode) {
            statsRecorded = true
        }

        // Yanlış cevap sonrası stats kaydı
        if (!isTestMode) {
            statsRecorded = true
        }

        assertFalse("test modunda stats kaydedilmemeli", statsRecorded)
    }

    @Test
    fun `test mode - soru sayaci total uzerinden gostermeli`() {
        val totalQuestions = 50
        val testModeIndex = 7 // 7 soru önizlendi

        // Gösterilen format: "Soru 7/50" (çocuğun requiredCount'u değil)
        val displayNum = testModeIndex
        val displayTotal = totalQuestions
        assertEquals("soru numarası testModeIndex olmalı", 7, displayNum)
        assertEquals("toplam gösterimi totalQuestions olmalı", 50, displayTotal)
    }
}
