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
    fun `clearAll - tüm kilitler ve bayraklar temizlenmeli`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        LockStateManager.notifyUnlocked(PKG_YOUTUBE)
        LockStateManager.markTimerExpired(PKG_OPERA)

        LockStateManager.clearAll()

        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse(LockStateManager.isUnlocked(PKG_YOUTUBE))
        assertFalse(LockStateManager.isTimerExpired(PKG_OPERA))
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

    // ─── Timer expired bayrağı testleri ─────────────────────────────────────

    @Test
    fun `markTimerExpired - bayrak set edilmeli`() {
        LockStateManager.markTimerExpired(PKG_OPERA)
        assertTrue(LockStateManager.isTimerExpired(PKG_OPERA))
    }

    @Test
    fun `isTimerExpired - işaretlenmeden false döner`() {
        assertFalse(LockStateManager.isTimerExpired(PKG_OPERA))
    }

    @Test
    fun `clearTimerExpired - bayrak temizlenmeli`() {
        LockStateManager.markTimerExpired(PKG_OPERA)
        LockStateManager.clearTimerExpired(PKG_OPERA)
        assertFalse(LockStateManager.isTimerExpired(PKG_OPERA))
    }

    @Test
    fun `notifyUnlocked - timerExpired bayrağını da temizlemeli`() {
        // Timer doldu → bayrak set edildi
        LockStateManager.markTimerExpired(PKG_OPERA)
        assertTrue(LockStateManager.isTimerExpired(PKG_OPERA))

        // Ebeveyn girişi → notifyUnlocked çağrılır
        LockStateManager.notifyUnlocked(PKG_OPERA)

        // Bayrak temizlenmiş olmalı
        assertFalse("notifyUnlocked timerExpired bayrağını temizlemeli", LockStateManager.isTimerExpired(PKG_OPERA))
        assertTrue("Uygulama unlocked olmalı", LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `notifyUnlockedAt - timerExpired bayrağını da temizlemeli`() {
        LockStateManager.markTimerExpired(PKG_OPERA)
        LockStateManager.notifyUnlockedAt(PKG_OPERA, System.currentTimeMillis())
        assertFalse(LockStateManager.isTimerExpired(PKG_OPERA))
    }

    @Test
    fun `timerExpired - farklı paketler birbirini etkilemez`() {
        LockStateManager.markTimerExpired(PKG_OPERA)
        assertFalse(LockStateManager.isTimerExpired(PKG_YOUTUBE))
    }

    // ─── Timer simülasyonu (checkAndExpireTimers mantığı) ───────────────────

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
    fun `timer - unlock zamanını geçmişe alınca expire etmeli + bayrak setlenmeli`() {
        LockStateManager.notifyUnlockedAt(PKG_OPERA, System.currentTimeMillis() - 61_000L)

        val unlockTime = LockStateManager.getUnlockTime(PKG_OPERA)
        val durationMs = 60_000L
        val elapsed = System.currentTimeMillis() - unlockTime

        assertTrue("61 saniye geçti, expire olmalı", elapsed >= durationMs)

        // Servisin yapacağı işlemi simüle et
        if (elapsed >= durationMs) {
            LockStateManager.forceRelock(PKG_OPERA)
            LockStateManager.markTimerExpired(PKG_OPERA)
        }

        assertFalse("Relock sonrası unlocked olmamalı", LockStateManager.isUnlocked(PKG_OPERA))
        assertTrue("Expire sonrası timerExpired bayrağı set olmalı", LockStateManager.isTimerExpired(PKG_OPERA))
    }

    @Test
    fun `tam akış - timer doldu, çocuk açıyor (banner), ebeveyn giriyor (reset)`() {
        // 1. Çocuk challenge kazandı → kilit açıldı
        LockStateManager.notifyUnlocked(PKG_OPERA)
        assertTrue(LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse(LockStateManager.isTimerExpired(PKG_OPERA))

        // 2. Timer doldu (servis simülasyonu)
        LockStateManager.forceRelock(PKG_OPERA)
        LockStateManager.markTimerExpired(PKG_OPERA)
        assertFalse("Relock: unlocked olmamalı", LockStateManager.isUnlocked(PKG_OPERA))
        assertTrue("Timer flag: set edilmeli", LockStateManager.isTimerExpired(PKG_OPERA))

        // 3. Çocuk uygulamayı açıyor → ChallengePickerActivity timer_expired=true ile açılır
        val shouldShowBanner = LockStateManager.isTimerExpired(PKG_OPERA)
        assertTrue("Challenge ekranı banner göstermeli", shouldShowBanner)

        // 4. Ebeveyn giriş yapıyor → notifyUnlocked çağrılıyor
        LockStateManager.notifyUnlocked(PKG_OPERA)

        // 5. Her şey sıfırlanmış olmalı, uygulama açık
        assertTrue("Uygulama açık olmalı", LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse("Timer flag temizlenmeli", LockStateManager.isTimerExpired(PKG_OPERA))
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
    fun `getActiveUnlocks - döndürülen map değiştirilemez (immutable kopya)`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)
        val snapshot1 = LockStateManager.getActiveUnlocks()

        LockStateManager.forceRelock(PKG_OPERA)
        val snapshot2 = LockStateManager.getActiveUnlocks()

        assertTrue("Snapshot1 hâlâ opera içermeli", snapshot1.containsKey(PKG_OPERA))
        assertFalse("Snapshot2 opera içermemeli", snapshot2.containsKey(PKG_OPERA))
    }
}
