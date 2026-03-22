package com.akn.mathlock

/**
 * Kilit durumunu servis ve activity'ler arasında paylaşmak için
 * basit bir singleton manager.
 *
 * İki tür "açık" vardır:
 *  1. notifyUnlocked       → çocuk challenge kazandı, TIMER çalışır
 *  2. notifyParentUnlocked → ebeveyn giriş yaptı, TIMER ÇALIŞMAZ / geri sayım gösterilmez
 */
object LockStateManager {

    // package -> unlock timestamp  (çocuk challenge — timer çalışır)
    private val unlockedApps = mutableMapOf<String, Long>()

    // Ebeveyn girişiyle açılan paketler — timer YOK, geri sayım YOK
    private val parentBypassApps = mutableSetOf<String>()

    // Timer dolduğunda işaretlenir; challenge ekranında "süreniz doldu" bannerı için
    private val timerExpiredApps = mutableSetOf<String>()

    // ─── Çocuk unlock (timer çalışır) ───────────────────────────────────────

    fun notifyUnlocked(packageName: String) {
        unlockedApps[packageName] = System.currentTimeMillis()
        parentBypassApps.remove(packageName)
        timerExpiredApps.remove(packageName)
    }

    /** Test için: belirli bir zamanda unlock kaydı oluştur. */
    fun notifyUnlockedAt(packageName: String, timestamp: Long) {
        unlockedApps[packageName] = timestamp
        parentBypassApps.remove(packageName)
        timerExpiredApps.remove(packageName)
    }

    // ─── Ebeveyn bypass (timer YOK) ─────────────────────────────────────────

    /**
     * Ebeveyn kimlik doğrulamasıyla açılan uygulamayı işaretle.
     * Bu paket için asla geri sayım başlamaz ve timer expire etmez.
     */
    fun notifyParentUnlocked(packageName: String) {
        parentBypassApps.add(packageName)
        unlockedApps.remove(packageName)   // varsa çocuk timer'ını temizle
        timerExpiredApps.remove(packageName)
    }

    fun isParentBypassed(packageName: String): Boolean =
        parentBypassApps.contains(packageName)

    fun clearParentBypass(packageName: String) {
        parentBypassApps.remove(packageName)
    }

    // ─── Ortak sorgular ─────────────────────────────────────────────────────

    /** Hem çocuk unlock hem ebeveyn bypass: kilit açık mı? */
    fun isUnlocked(packageName: String): Boolean =
        unlockedApps.containsKey(packageName) || parentBypassApps.contains(packageName)

    fun getUnlockTime(packageName: String): Long =
        unlockedApps[packageName] ?: 0L

    /**
     * Sadece timer'lı (çocuk) unlockları döner.
     * Ebeveyn bypass buraya GİRMEZ → updateTimerNotification timer başlatmaz.
     */
    fun getActiveUnlocks(): Map<String, Long> = unlockedApps.toMap()

    fun forceRelock(packageName: String) {
        unlockedApps.remove(packageName)
        parentBypassApps.remove(packageName)
    }

    // ─── Timer süresi doldu işaretleri ──────────────────────────────────────

    fun markTimerExpired(packageName: String) {
        timerExpiredApps.add(packageName)
    }

    fun isTimerExpired(packageName: String): Boolean =
        timerExpiredApps.contains(packageName)

    fun clearTimerExpired(packageName: String) {
        timerExpiredApps.remove(packageName)
    }

    fun clearAll() {
        unlockedApps.clear()
        parentBypassApps.clear()
        timerExpiredApps.clear()
    }
}
