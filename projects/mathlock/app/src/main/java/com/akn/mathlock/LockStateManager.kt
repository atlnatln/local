package com.akn.mathlock

/**
 * Kilit durumunu servis ve activity'ler arasında paylaşmak için
 * basit bir singleton manager.
 */
object LockStateManager {

    // package -> unlock timestamp
    private val unlockedApps = mutableMapOf<String, Long>()

    // Timer dolduğunda işaretlenir; challenge ekranında "süreniz doldu" bannerı göstermek için
    private val timerExpiredApps = mutableSetOf<String>()

    fun notifyUnlocked(packageName: String) {
        unlockedApps[packageName] = System.currentTimeMillis()
        timerExpiredApps.remove(packageName)   // yeniden açınca "süre doldu" bayrağı temizlenir
    }

    /** Test için: belirli bir zamanda unlock kaydı oluştur. */
    fun notifyUnlockedAt(packageName: String, timestamp: Long) {
        unlockedApps[packageName] = timestamp
        timerExpiredApps.remove(packageName)
    }

    fun isUnlocked(packageName: String): Boolean {
        return unlockedApps.containsKey(packageName)
    }

    fun getUnlockTime(packageName: String): Long {
        return unlockedApps[packageName] ?: 0L
    }

    /** Aktif kilit açık uygulamaların kopyasını döndürür. */
    fun getActiveUnlocks(): Map<String, Long> {
        return unlockedApps.toMap()
    }

    fun forceRelock(packageName: String) {
        unlockedApps.remove(packageName)
    }

    // ─── Timer süresi doldu işaretleri ──────────────────────────────────────

    /** Timer dolunca servis tarafından çağrılır. */
    fun markTimerExpired(packageName: String) {
        timerExpiredApps.add(packageName)
    }

    /** ChallengePickerActivity'de banner göstermek için kontrol. */
    fun isTimerExpired(packageName: String): Boolean {
        return timerExpiredApps.contains(packageName)
    }

    /** Ebeveyn girişi veya yeni unlock sonrası bayrak temizlenir. */
    fun clearTimerExpired(packageName: String) {
        timerExpiredApps.remove(packageName)
    }

    fun clearAll() {
        unlockedApps.clear()
        timerExpiredApps.clear()
    }
}
