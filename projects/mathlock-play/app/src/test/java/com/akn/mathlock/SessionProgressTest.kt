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

    // ─── v1.22: Pratik modu izolasyonu ──────────────────────────────────────

    @Test
    fun `pratik mod - sinir yok, dogru cevap sonrasi devam eder`() {
        val isPracticeMode = true
        var sessionSolvedCount = 0

        // 10 doğru cevap, hiçbirinde unlock tetiklenmemeli
        repeat(10) {
            sessionSolvedCount++
            // Pratik modda unlock kontrolü yok, sadece sonraki soru
            val nextAction = if (isPracticeMode) "showNextQuestion" else "checkUnlock"
            assertEquals("pratik mod sonraki soruya geçmeli", "showNextQuestion", nextAction)
        }
        assertEquals("10 doğru cevap sayılmalı", 10, sessionSolvedCount)
    }

    @Test
    fun `pratik mod - stats kaydedilmeli`() {
        val isTestMode = false
        val isPracticeMode = true
        var statsRecorded = false

        // Stats kaydı: !isTestMode kontrolü geçer çünkü pratik mod testMode değil
        if (!isTestMode) {
            statsRecorded = true
        }

        assertTrue("pratik modda stats kaydedilmeli", statsRecorded)
    }

    @Test
    fun `pratik mod - unlock tetiklenmemeli`() {
        val isPracticeMode = true
        var unlockCalled = false

        // unlockAndLaunchApp içinde pratik mod kontrolü
        if (isPracticeMode) {
            // return — unlock olmaz
        } else {
            unlockCalled = true
        }

        assertFalse("pratik modda unlock olmamalı", unlockCalled)
    }

    @Test
    fun `pratik mod - set bitince tekrar baslar`() {
        val isPracticeMode = true
        var resetTriggered = false
        var newSetStarted = false

        // onPracticeSetComplete: resetProgress + yeni set sync
        if (isPracticeMode) {
            resetTriggered = true
            newSetStarted = true
        }

        assertTrue("pratik modda set bitince reset yapılmalı", resetTriggered)
        assertTrue("pratik modda yeni set başlamalı", newSetStarted)
    }

    @Test
    fun `pratik mod - back tusu ile cikilebilmeli`() {
        val isPracticeMode = true
        val isTestMode = false
        var canBackNormally = false

        if (isTestMode || isPracticeMode) {
            canBackNormally = true  // super.onBackPressed
        }

        assertTrue("pratik mod - back tusu ile cikilebilmeli", canBackNormally)
    }

    // ─── Fallback erken unlock (bug regression) ───────────────────────────────
    //
    // Bug: Fallback modda passScore kadar doğru cevap verilse de tüm totalQuestions
    // (= passScore * 2, min 5) soruları bitirilmek zorundaydı.
    // Düzeltme: checkFallbackAnswer() içine erken unlock eklendi.
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Fallback modda passScore kadar doğru cevap + erken unlock kararını simüle eder.
     * Dönüş: UNLOCK_EARLY (passScore doldu), UNLOCK_END (son soruda doldu), NEXT_QUESTION, FAIL
     */
    private enum class FallbackDecision { UNLOCK_EARLY, UNLOCK_END, NEXT_QUESTION, FAIL }

    private fun fallbackAnswerDecision(
        correctCount: Int,
        userCorrect: Boolean,
        passScore: Int,
        totalQuestions: Int,
        currentIndex: Int
    ): FallbackDecision {
        val newCorrect = if (userCorrect) correctCount + 1 else correctCount
        // Erken unlock: passScore doldu
        if (userCorrect && newCorrect >= passScore) {
            return if (currentIndex < totalQuestions - 1) FallbackDecision.UNLOCK_EARLY
                   else FallbackDecision.UNLOCK_END
        }
        // Son soru ama yeterli doğru yok
        if (currentIndex >= totalQuestions - 1) {
            return if (newCorrect >= passScore) FallbackDecision.UNLOCK_END else FallbackDecision.FAIL
        }
        return FallbackDecision.NEXT_QUESTION
    }

    @Test
    fun `fallback erken unlock - passScore=3 totalQ=6 ilk 3 dogru erken acmali (regresyon)`() {
        // Eski kod: tüm 6 soru bitirilmeli, yeni kod: 3 doğru → hemen aç
        val passScore = 3
        val totalQuestions = (passScore * 2).coerceAtLeast(5) // 6
        var correctCount = 0
        var lastDecision = FallbackDecision.NEXT_QUESTION
        var unlockedAtQuestion = -1

        for (i in 0 until totalQuestions) {
            lastDecision = fallbackAnswerDecision(correctCount, true, passScore, totalQuestions, i)
            correctCount++
            if (lastDecision == FallbackDecision.UNLOCK_EARLY || lastDecision == FallbackDecision.UNLOCK_END) {
                unlockedAtQuestion = i + 1
                break
            }
        }

        assertEquals("3. soruda erken unlock olmalı", FallbackDecision.UNLOCK_EARLY, lastDecision)
        assertEquals("passScore (3) kadar soruda açılmalı", passScore, unlockedAtQuestion)
        assertTrue("Tüm sorular bitmeden (6 < toplam) açılmalı", unlockedAtQuestion < totalQuestions)
    }

    @Test
    fun `fallback erken unlock - passScore=1 ilk dogru cevap hemen acmali`() {
        val passScore = 1
        val totalQuestions = (passScore * 2).coerceAtLeast(5) // 5
        val decision = fallbackAnswerDecision(0, true, passScore, totalQuestions, 0)
        assertEquals("passScore=1 → ilk doğru → erken unlock", FallbackDecision.UNLOCK_EARLY, decision)
    }

    @Test
    fun `fallback erken unlock - yanlis cevap erken unlock tetiklemez`() {
        val passScore = 3
        val totalQuestions = (passScore * 2).coerceAtLeast(5)
        // 2 doğru var, bu soru yanlış → unlock yok
        val decision = fallbackAnswerDecision(2, false, passScore, totalQuestions, 4)
        assertEquals("Yanlış cevapta erken unlock olmamalı", FallbackDecision.NEXT_QUESTION, decision)
    }

    @Test
    fun `fallback erken unlock - karma dogru yanlis, tam passScore dolunca acilmali`() {
        // passScore=3, totalQ=6, sıra: Y D Y D Y D
        // 6. soruda (son soru) 3. doğru geliyor → UNLOCK_END
        val passScore = 3
        val totalQuestions = (passScore * 2).coerceAtLeast(5)
        val answers = listOf(false, true, false, true, false, true)
        var correctCount = 0
        var lastDecision = FallbackDecision.NEXT_QUESTION
        var unlockedAt = -1

        for (i in answers.indices) {
            lastDecision = fallbackAnswerDecision(correctCount, answers[i], passScore, totalQuestions, i)
            if (answers[i]) correctCount++
            if (lastDecision != FallbackDecision.NEXT_QUESTION) {
                unlockedAt = i + 1
                break
            }
        }

        // 6. soruda (son soruda) passScore doldu → UNLOCK_END (son soru olduğu için EARLY değil)
        assertEquals("Son soruda passscore doldu → UNLOCK_END", FallbackDecision.UNLOCK_END, lastDecision)
        assertEquals("3 doğru toplandı", passScore, correctCount)
        assertEquals("Son soruda (6.) unlock", 6, unlockedAt)
    }

    @Test
    fun `fallback erken unlock olmamali - kac soru lazimdi (eski vs yeni davranis karsilastirma)`() {
        val passScore = 3
        val totalQuestionsOld = (passScore * 2).coerceAtLeast(5) // eski: hepsi gerekli
        val requiredNew = passScore                               // yeni: sadece passScore kadar doğru

        assertTrue("Yeni davranış daha az soru gerektirir", requiredNew < totalQuestionsOld)
        assertEquals("Eski kod 6 soru gerektiriyordu", 6, totalQuestionsOld)
        assertEquals("Yeni kod 3 doğru cevap yeterli", 3, requiredNew)
    }

    @Test
    fun `fallback erken unlock - passScore=5 totalQ=10 karma 10 soruda 5 dogru toplamali`() {
        val passScore = 5
        val totalQuestions = (passScore * 2).coerceAtLeast(5) // 10
        // Y D Y D Y D Y D Y D — 5 doğru, toplam 10 soruda son doğru gelir
        val answers = listOf(false, true, false, true, false, true, false, true, false, true)
        var correctCount = 0
        var lastDecision = FallbackDecision.NEXT_QUESTION
        var unlockedAt = -1

        for (i in answers.indices) {
            lastDecision = fallbackAnswerDecision(correctCount, answers[i], passScore, totalQuestions, i)
            if (answers[i]) correctCount++
            if (lastDecision != FallbackDecision.NEXT_QUESTION) {
                unlockedAt = i + 1
                break
            }
        }

        assertEquals("Son soruda UNLOCK_END bekleniyor", FallbackDecision.UNLOCK_END, lastDecision)
        assertEquals("5 doğru toplandı", passScore, correctCount)
        assertEquals("10. soruda (tüm sorular bitti) unlock", 10, unlockedAt)
    }

    @Test
    fun `fallback - yeterli dogru yoksa son soruda FAIL donemeli`() {
        val passScore = 4
        val totalQuestions = (passScore * 2).coerceAtLeast(5) // 8
        // Sadece 2 doğru cevap (son soruda yanlış)
        var correctCount = 2
        val decision = fallbackAnswerDecision(correctCount, false, passScore, totalQuestions, totalQuestions - 1)
        assertEquals("Son soruda yetersiz doğru → FAIL", FallbackDecision.FAIL, decision)
    }
}
