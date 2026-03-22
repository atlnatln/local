package com.akn.mathlock

import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * LockStateManager birim testleri.
 *
 * Çalıştırmak için:
 *   cd projects/mathlock
 *   ./gradlew test
 */
class LockStateManagerTest {

    private val PKG_OPERA = "com.opera.browser"
    private val PKG_YOUTUBE = "com.google.android.youtube"

    @Before
    fun setUp() {
        LockStateManager.clearAll()
    }

    @After
    fun tearDown() {
        LockStateManager.clearAll()
    }

    // ─── Temel kilit/aç testleri ─────────────────────────────────────────────

    @Test
    fun `notifyUnlocked - uygulama kilidi açık görünmeli`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        assertTrue(LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `isUnlocked - unlock çağrılmamışsa false döner`() {
        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `forceRelock - kilit tekrar kapanmalı`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        assertTrue(LockStateManager.isUnlocked(PKG_OPERA))

        LockStateManager.forceRelock(PKG_OPERA)
        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `clearAll - tüm kilitler kapanmalı`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        LockStateManager.notifyUnlocked(PKG_YOUTUBE)

        LockStateManager.clearAll()

        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse(LockStateManager.isUnlocked(PKG_YOUTUBE))
    }

    @Test
    fun `getUnlockTime - doğru zaman döner`() {
        val before = System.currentTimeMillis()
        LockStateManager.notifyUnlocked(PKG_OPERA)
        val after = System.currentTimeMillis()

        val time = LockStateManager.getUnlockTime(PKG_OPERA)
        assertTrue("Unlock zamanı geçerli aralıkta olmalı", time in before..after)
    }

    @Test
    fun `getUnlockTime - unlock olmadan 0 döner`() {
        assertEquals(0L, LockStateManager.getUnlockTime(PKG_OPERA))
    }

    // ─── Timer simülasyonu (checkAndExpireTimers mantığı) ───────────────────

    /**
     * Bu test, AppLockService.checkAndExpireTimers() mantığını simüle eder.
     * Gerçek servisi çağırmak yerine aynı hesaplamayı burada doğruluyoruz.
     */
    @Test
    fun `timer - 1 dakika geçmeden expire olmamalı`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        val unlockTime = LockStateManager.getUnlockTime(PKG_OPERA)

        val durationMs = 60_000L
        val elapsed = System.currentTimeMillis() - unlockTime

        assertFalse("1 dakika dolmadan expire olmamalı", elapsed >= durationMs)
        assertTrue("Hâlâ kilitli açık görünmeli", LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `timer - unlock zamanını geçmişe alınca expire etmeli`() {
        // Unlock zamanını 61 saniye öncesine set et (manuel manipülasyon)
        LockStateManager.notifyUnlockedAt(PKG_OPERA, System.currentTimeMillis() - 61_000L)

        val unlockTime = LockStateManager.getUnlockTime(PKG_OPERA)
        val durationMs = 60_000L
        val elapsed = System.currentTimeMillis() - unlockTime

        assertTrue("61 saniye geçti, expire olmalı", elapsed >= durationMs)

        // Servisin yapacağı işlemi simüle et
        if (elapsed >= durationMs) {
            LockStateManager.forceRelock(PKG_OPERA)
        }

        assertFalse("Relock sonrası unlocked olmamalı", LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `timer - relock sonrası ebeveyn tekrar açabilmeli`() {
        // Timer expire → relock
        LockStateManager.notifyUnlockedAt(PKG_OPERA, System.currentTimeMillis() - 61_000L)
        LockStateManager.forceRelock(PKG_OPERA)
        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))

        // Ebeveyn tekrar açıyor
        LockStateManager.notifyUnlocked(PKG_OPERA)
        assertTrue("Ebeveyn bypass sonrası tekrar açık olmalı", LockStateManager.isUnlocked(PKG_OPERA))
    }

    // ─── getActiveUnlocks ────────────────────────────────────────────────────

    @Test
    fun `getActiveUnlocks - doğru paketleri döner`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        LockStateManager.notifyUnlocked(PKG_YOUTUBE)

        val active = LockStateManager.getActiveUnlocks()
        assertEquals(2, active.size)
        assertTrue(active.containsKey(PKG_OPERA))
        assertTrue(active.containsKey(PKG_YOUTUBE))
    }

    @Test
    fun `getActiveUnlocks - relock sonrası paketi içermemeli`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        LockStateManager.notifyUnlocked(PKG_YOUTUBE)
        LockStateManager.forceRelock(PKG_OPERA)

        val active = LockStateManager.getActiveUnlocks()
        assertEquals(1, active.size)
        assertFalse(active.containsKey(PKG_OPERA))
        assertTrue(active.containsKey(PKG_YOUTUBE))
    }

    @Test
    fun `getActiveUnlocks - döndürülen map değiştirilemez (immutable kopya)`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        val snapshot1 = LockStateManager.getActiveUnlocks()

        LockStateManager.forceRelock(PKG_OPERA)
        val snapshot2 = LockStateManager.getActiveUnlocks()

        // snapshot1 değişmemiş olmalı (toMap() ile kopyalandı)
        assertTrue("Snapshot1 hâlâ opera içermeli", snapshot1.containsKey(PKG_OPERA))
        assertFalse("Snapshot2 opera içermemeli", snapshot2.containsKey(PKG_OPERA))
    }
}
