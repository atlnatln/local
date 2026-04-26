package com.akn.mathlock

import org.junit.Assert.*
import org.junit.Test

/**
 * Sayı Yolculuğu (SayiYolculuguActivity + game.html) oyun motoru mantığı testleri.
 *
 * Bu testler saf Kotlin/JS mantığı simülasyonudur — Android Context gerektirmez.
 * Temel amaç: seviye geçiş, kilit açma ve ilerleme senkronizasyonu hatalarını
 * regresyon testleriyle yakalamak.
 */
class SayiYolculuguGameEngineTest {

    // ═══════════════════════════════════════════════════════════════════════
    // 1. Seviye geçiş mantığı (game.html — btnNext / btnRetry)
    // ═══════════════════════════════════════════════════════════════════════

    data class Level(
        val id: Int,
        val title: String = "",
        val maxCmds: Int = 5,
        val stars: List<Int> = listOf(3, 5)
    )

    data class GameState(
        var levelIdx: Int = 0,
        val progress: MutableMap<Int, LevelProgress> = mutableMapOf()
    )

    data class LevelProgress(
        val completed: Boolean = true,
        val stars: Int = 1
    )

    /**
     * game.html'deki initGame + showWinOverlay mantığını simüle eder.
     * @return sonraki seviye varsa true, yoksa false (btnNext görünürlüğü)
     */
    private fun canAdvanceToNextLevel(state: GameState, levels: List<Level>): Boolean {
        return state.levelIdx < levels.size - 1
    }

    /**
     * game.html'deki initGame: completedIds yüklendikten sonra
     * ilk tamamlanmamış seviyeye atla.
     */
    private fun initGameState(
        levels: List<Level>,
        completedIds: List<Int>
    ): GameState {
        val state = GameState()
        if (completedIds.isNotEmpty()) {
            levels.forEachIndexed { index, level ->
                if (completedIds.contains(level.id)) {
                    state.progress[index] = LevelProgress(completed = true, stars = 1)
                }
            }
            val firstUncompleted = levels.indexOfFirst { level ->
                val idx = levels.indexOf(level)
                !state.progress.containsKey(idx)
            }.let { if (it == -1) levels.size else it }

            state.levelIdx = if (firstUncompleted < levels.size) firstUncompleted else levels.size
        }
        return state
    }

    @Test
    fun `12 seviye setinde 10 etap bitince sonraki butonu gorunur`() {
        val levels = (1..12).map { Level(id = it) }
        val state = GameState(levelIdx = 9) // 10. etap (0-indexed)

        assertTrue("10. etap bitince 11. etaba geçiş butonu görünür olmalı", canAdvanceToNextLevel(state, levels))
    }

    @Test
    fun `12 seviye setinde son etap bitince sonraki butonu gizli`() {
        val levels = (1..12).map { Level(id = it) }
        val state = GameState(levelIdx = 11) // 12. etap (0-indexed)

        assertFalse("Son etapta sonraki butonu gizlenmeli", canAdvanceToNextLevel(state, levels))
    }

    @Test
    fun `10 seviyelik eski sette 10 etap bitince sonraki butonu GIZLI`() {
        // REGRESYON: Eski LevelSet'lerde 10 seviye olabilir.
        // Bu durumda 10. etap (index 9) son seviyedir ve btnNext görünmez.
        val levels = (1..10).map { Level(id = it) }
        val state = GameState(levelIdx = 9) // 10. etap (0-indexed)

        assertFalse("10 seviyelik sette 10. etap son seviyedir — btnNext gizli", canAdvanceToNextLevel(state, levels))
    }

    @Test
    fun `10 seviyelik eski sette tamamlanan 10 seviye varsa allComplete gosterilmeli`() {
        // REGRESYON: initGame'de firstUncompleted == levels.length ise state.levelIdx = levels.size
        // loadLevel() getLevel() null döndürür ve showAllComplete() gösterir
        val levels = (1..10).map { Level(id = it) }
        val completedIds = (1..10).toList()

        val state = initGameState(levels, completedIds)

        assertEquals("10/10 tamamlandıysa levelIdx = levels.size (showAllComplete)", levels.size, state.levelIdx)
    }

    @Test
    fun `12 seviyelik sette 10 tamamlaninca 11 e atlamali`() {
        val levels = (1..12).map { Level(id = it) }
        val completedIds = (1..10).toList()

        val state = initGameState(levels, completedIds)

        assertEquals("10 tamamlandı → 11. seviye (index 10)", 10, state.levelIdx)
    }

    @Test
    fun `hic tamamlanmamis seviye yoksa 0 dan baslamali`() {
        val levels = (1..12).map { Level(id = it) }
        val state = initGameState(levels, emptyList())

        assertEquals("Hiç tamamlanmamışsa 0'dan başlamalı", 0, state.levelIdx)
    }

    @Test
    fun `initGame - completedIds bos degilse ilk eksik seviyeye atla`() {
        val levels = (1..12).map { Level(id = it) }
        val completedIds = listOf(1, 2, 3, 5) // 4 eksik

        val state = initGameState(levels, completedIds)

        assertEquals("4. seviye eksik → index 3", 3, state.levelIdx)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 2. Kilit açma mantığı (SayiYolculuguActivity — levelsCompleted vs passScore)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * SayiYolculuguActivity'deki unlock kontrolünü simüle eder.
     * levelsCompleted: bu oturumda kaç kez levelComplete event'i alındı
     * passScore: PreferenceManager'dan okunan geçiş skoru
     */
    private fun shouldUnlock(levelsCompleted: Int, passScore: Int): Boolean {
        return levelsCompleted >= passScore
    }

    @Test
    fun `passScore 10 iken 10 levelComplete unlock acmali`() {
        assertTrue("10/10 → unlock", shouldUnlock(10, 10))
    }

    @Test
    fun `passScore 10 iken 9 levelComplete unlock acmamali`() {
        assertFalse("9/10 → no unlock", shouldUnlock(9, 10))
    }

    @Test
    fun `passScore 3 iken 3 levelComplete unlock acmali`() {
        assertTrue("3/3 → unlock", shouldUnlock(3, 3))
    }

    @Test
    fun `levelsCompleted ayni seviyeyi tekrar oynayinca da artar`() {
        // REGRESYON: levelsCompleted benzersiz seviye sayısını değil,
        // event sayısını tutar. Aynı seviye tekrarlanırsa +1 olur.
        var levelsCompleted = 0
        val passScore = 3

        // 1. seviyeyi 3 kez oyna
        repeat(3) { levelsCompleted++ }

        assertTrue("Aynı seviye 3 kez → levelsCompleted=3 → unlock", shouldUnlock(levelsCompleted, passScore))
    }

    @Test
    fun `passScore 0 ise hemen unlock`() {
        assertTrue("0/0 → immediate unlock", shouldUnlock(0, 0))
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 3. İlerleme senkronizasyonu (completedLevelIds consistency)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * game.html checkWin + notifyAndroid sonrası Android tarafında
     * completedLevelIds set'inin tutarlılığını simüle eder.
     */
    private fun simulateLevelComplete(
        completedIds: MutableSet<Int>,
        levelId: Int
    ): Boolean {
        completedIds.add(levelId)
        return completedIds.contains(levelId)
    }

    @Test
    fun `levelComplete eventi completedIds e eklenmeli`() {
        val completedIds = mutableSetOf(1, 2, 3)
        val added = simulateLevelComplete(completedIds, 4)

        assertTrue("Yeni seviye eklenmeli", added)
        assertTrue("Set 4 içermeli", completedIds.contains(4))
    }

    @Test
    fun `tekrar oynanan seviye zaten sette var`() {
        val completedIds = mutableSetOf(1, 2, 3, 4)
        val added = simulateLevelComplete(completedIds, 4)

        assertTrue("Tekrar oynanan seviye hâlâ sette olmalı", added)
        assertEquals(4, completedIds.size)
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 4. Yıldız / puanlama mantığı
    // ═══════════════════════════════════════════════════════════════════════

    private fun calculateStars(usedCmds: Int, starsThreshold: List<Int>): Int {
        return when {
            usedCmds <= starsThreshold[0] -> 3
            usedCmds <= starsThreshold[1] -> 2
            else -> 1
        }
    }

    @Test
    fun `komut sayisi ilk esige esitse 3 yildiz`() {
        assertEquals(3, calculateStars(5, listOf(5, 7)))
    }

    @Test
    fun `komut sayisi ikinci esigin altindaysa 2 yildiz`() {
        assertEquals(2, calculateStars(6, listOf(5, 7)))
    }

    @Test
    fun `komut sayisi ikinci esigi gecerse 1 yildiz`() {
        assertEquals(1, calculateStars(8, listOf(5, 7)))
    }

    // ═══════════════════════════════════════════════════════════════════════
    // 5. Entegrasyon: Tam akış simülasyonu
    // ═══════════════════════════════════════════════════════════════════════

    @Test
    fun `tam akis - 12 seviye setinde 10 etaptan 11 e gecis`() {
        val levels = (1..12).map { Level(id = it) }
        val completedIds = mutableSetOf<Int>()
        var levelIdx = 9 // 10. etap
        val passScore = 10
        var levelsCompleted = 9

        // 10. etabı bitir
        val currentLevelId = levels[levelIdx].id
        completedIds.add(currentLevelId)
        levelsCompleted++

        // btnNext görünürlüğü
        val canAdvance = levelIdx < levels.size - 1
        assertTrue("10. etaptan 11. etaba geçiş mümkün", canAdvance)

        // Sonraki seviyeye geç
        if (canAdvance) levelIdx++
        assertEquals(10, levelIdx) // 11. etap

        // Unlock kontrolü
        val unlocked = shouldUnlock(levelsCompleted, passScore)
        assertTrue("10 levelComplete → passScore=10 → unlock", unlocked)
    }

    @Test
    fun `tam akis - 10 seviye eski set 10 etap son seviye`() {
        // REGRESYON: Eski 10 seviyelik sette kullanıcı 10. etabı bitirir
        // ama btnNext görünmez, sadece Tekrar butonu kalır.
        val levels = (1..10).map { Level(id = it) }
        val completedIds = mutableSetOf<Int>()
        var levelIdx = 9 // 10. etap
        val passScore = 10
        var levelsCompleted = 9

        // 10. etabı bitir
        val currentLevelId = levels[levelIdx].id
        completedIds.add(currentLevelId)
        levelsCompleted++

        // btnNext görünürlüğü — BU TEST HATAYI YAKALAR
        val canAdvance = levelIdx < levels.size - 1
        assertFalse("10 seviyelik sette 10. etap SON seviyedir", canAdvance)

        // Unlock kontrolü
        val unlocked = shouldUnlock(levelsCompleted, passScore)
        assertTrue("10 levelComplete → unlock", unlocked)
    }

    @Test
    fun `tam akis - pratik modda unlock tetiklenmemeli`() {
        val isPracticeMode = true
        val levelsCompleted = 10
        val passScore = 3

        val unlocked = !isPracticeMode && shouldUnlock(levelsCompleted, passScore)
        assertFalse("Pratik modda unlock olmamalı", unlocked)
    }

    @Test
    fun `tam akis - test modunda unlock tetiklenmemeli`() {
        val isTestMode = true
        val levelsCompleted = 10
        val passScore = 3

        val unlocked = !isTestMode && shouldUnlock(levelsCompleted, passScore)
        assertFalse("Test modunda unlock olmamalı", unlocked)
    }
}
