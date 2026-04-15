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

        // Çocuk challenge → notifyUnlocked çağrılır
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

        // 4. Ebeveyn giriş yapıyor → notifyParentUnlocked çağrılıyor
        LockStateManager.notifyParentUnlocked(PKG_OPERA)

        // 5. Uygulama açık, timer YOK (getActiveUnlocks'ta yer almıyor)
        assertTrue("Uygulama açık olmalı", LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse("Timer flag temizlenmeli", LockStateManager.isTimerExpired(PKG_OPERA))
        assertTrue("Parent bypass olmalı", LockStateManager.isParentBypassed(PKG_OPERA))
        assertFalse("getActiveUnlocks timer için çağrılmaz", LockStateManager.getActiveUnlocks().containsKey(PKG_OPERA))
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

    // ─── Ebeveyn bypass testleri ─────────────────────────────────────────────

    @Test
    fun `notifyParentUnlocked - isUnlocked true döner`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertTrue("Ebeveyn bypass: isUnlocked true olmalı", LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `notifyParentUnlocked - isParentBypassed true döner`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertTrue(LockStateManager.isParentBypassed(PKG_OPERA))
    }

    @Test
    fun `notifyParentUnlocked - getActiveUnlocks içinde YOK (timer başlamaz)`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertFalse(
            "Ebeveyn bypass timer map'ine girmemeli",
            LockStateManager.getActiveUnlocks().containsKey(PKG_OPERA)
        )
    }

    @Test
    fun `notifyParentUnlocked - timerExpired bayrağını temizler`() {
        LockStateManager.markTimerExpired(PKG_OPERA)
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertFalse(LockStateManager.isTimerExpired(PKG_OPERA))
    }

    @Test
    fun `notifyParentUnlocked - çocuk unlock varsa onu temizler`() {
        LockStateManager.notifyUnlocked(PKG_OPERA)         // çocuk unlock
        LockStateManager.notifyParentUnlocked(PKG_OPERA)   // ebeveyn geçiyor

        assertFalse("unlockedApps'ta kalmamalı", LockStateManager.getActiveUnlocks().containsKey(PKG_OPERA))
        assertTrue("parentBypassApps'ta olmalı", LockStateManager.isParentBypassed(PKG_OPERA))
        assertTrue("isUnlocked hâlâ true", LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `forceRelock - parent bypass da temizler`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        LockStateManager.forceRelock(PKG_OPERA)
        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse(LockStateManager.isParentBypassed(PKG_OPERA))
    }

    @Test
    fun `clearParentBypass - sadece bypass bayrağını temizler`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        LockStateManager.clearParentBypass(PKG_OPERA)
        assertFalse(LockStateManager.isParentBypassed(PKG_OPERA))
        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
    }

    @Test
    fun `clearAll - parent bypass da temizlenmeli`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        LockStateManager.clearAll()
        assertFalse(LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse(LockStateManager.isParentBypassed(PKG_OPERA))
    }

    @Test
    fun `notifyUnlocked - parent bypass varsa onu temizler (çocuk devraliyor)`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertTrue(LockStateManager.isParentBypassed(PKG_OPERA))

        LockStateManager.notifyUnlocked(PKG_OPERA)  // çocuk challenge kazandı
        assertFalse("Parent bypass temizlenmeli", LockStateManager.isParentBypassed(PKG_OPERA))
        assertTrue("unlockedApps'ta olmalı (timer işleyecek)", LockStateManager.getActiveUnlocks().containsKey(PKG_OPERA))
    }

    @Test
    fun `ebeveyn bypass - diğer uygulamayı etkilemez`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertFalse(LockStateManager.isUnlocked(PKG_YOUTUBE))
        assertFalse(LockStateManager.isParentBypassed(PKG_YOUTUBE))
    }

    // ─── Ebeveyn bypass — ekran kapanınca temizlenir ─────────────────────

    @Test
    fun `clearParentBypass - bypass temizlendikten sonra isUnlocked false döner`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertTrue("Bypass sonrası isUnlocked true", LockStateManager.isUnlocked(PKG_OPERA))

        LockStateManager.clearParentBypass(PKG_OPERA)

        assertFalse("Bypass temizlendikten sonra isUnlocked false olmalı", LockStateManager.isUnlocked(PKG_OPERA))
        assertFalse(LockStateManager.isParentBypassed(PKG_OPERA))
    }

    @Test
    fun `ebeveyn bypass - uygulama arka plana geçse de bypass korunur`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        assertTrue(LockStateManager.isUnlocked(PKG_OPERA))

        // Arka plana geçiş, bypass'ı temizlemez — sadece ekran kapanınca temizlenir
        assertTrue("Arka plana geçince bypass korunmalı", LockStateManager.isUnlocked(PKG_OPERA))
        assertTrue(LockStateManager.isParentBypassed(PKG_OPERA))
        assertFalse(LockStateManager.isUnlocked(PKG_YOUTUBE))
    }

    @Test
    fun `clearAllParentBypasses - tüm bypass kayıtları temizlenir`() {
        LockStateManager.notifyParentUnlocked(PKG_OPERA)
        LockStateManager.notifyParentUnlocked(PKG_YOUTUBE)
        assertTrue(LockStateManager.isParentBypassed(PKG_OPERA))
        assertTrue(LockStateManager.isParentBypassed(PKG_YOUTUBE))

        val cleared = LockStateManager.clearAllParentBypasses()
        assertEquals(2, cleared)
        assertFalse(LockStateManager.isParentBypassed(PKG_OPERA))
        assertFalse(LockStateManager.isParentBypassed(PKG_YOUTUBE))
    }


}

