package com.akn.mathlock

/**
 * Kilit durumunu servis ve activity'ler arasında paylaşmak için
 * basit bir singleton manager.
 */
object LockStateManager {

    // package -> unlock timestamp
    private val unlockedApps = mutableMapOf<String, Long>()

    fun notifyUnlocked(packageName: String) {
        unlockedApps[packageName] = System.currentTimeMillis()
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

    fun clearAll() {
        unlockedApps.clear()
    }
}
