package com.akn.mathlock.util

import android.content.Context
import android.content.SharedPreferences
import java.security.MessageDigest

class PreferenceManager(context: Context) {

    internal val prefs: SharedPreferences =
        context.getSharedPreferences("mathlock_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_LOCKED_APPS = "locked_apps"
        private const val KEY_PIN_HASH = "pin_hash"
        private const val KEY_PATTERN_HASH = "pattern_hash"
        private const val KEY_SERVICE_ENABLED = "service_enabled"
        private const val KEY_PASS_SCORE = "pass_score"
        private const val KEY_GUESS_MAX = "guess_max"
        private const val KEY_UNLOCK_DURATION = "unlock_duration_minutes"
        private const val KEY_UNLOCK_EXPIRED_ACTION = "unlock_expired_action"
        private const val KEY_FINGERPRINT_ENABLED = "fingerprint_enabled"
        private const val KEY_PIN_ENABLED = "pin_enabled"
        private const val KEY_PATTERN_ENABLED = "pattern_enabled"
        private const val KEY_FIRST_RUN = "first_run"
        private const val KEY_DISCLOSURE_ACCEPTED = "disclosure_accepted"
        private const val KEY_PUZZLE_ENABLED = "challenge_puzzle_enabled"
        private const val KEY_MATH_ENABLED  = "challenge_math_enabled"
        private const val KEY_GUESS_ENABLED  = "challenge_guess_enabled"
        private const val KEY_ROBOTOPIA_ENABLED = "challenge_robotopia_enabled"

        private const val DEFAULT_PASS_SCORE = 3
        private const val DEFAULT_GUESS_MAX = 100

        const val EXPIRE_ACTION_RELOCK = "relock"
        const val EXPIRE_ACTION_CLOSE = "close"
    }

    // --- Kilitli Uygulamalar ---

    fun getLockedApps(): Set<String> {
        return prefs.getStringSet(KEY_LOCKED_APPS, emptySet()) ?: emptySet()
    }

    fun setLockedApps(apps: Set<String>) {
        prefs.edit().putStringSet(KEY_LOCKED_APPS, apps).apply()
    }

    fun isAppLocked(packageName: String): Boolean {
        return getLockedApps().contains(packageName)
    }

    fun toggleAppLock(packageName: String, locked: Boolean) {
        val apps = getLockedApps().toMutableSet()
        if (locked) apps.add(packageName) else apps.remove(packageName)
        setLockedApps(apps)
    }

    // --- PIN ---

    fun setPin(pin: String) {
        prefs.edit().putString(KEY_PIN_HASH, hashString(pin)).apply()
    }

    fun verifyPin(pin: String): Boolean {
        val stored = prefs.getString(KEY_PIN_HASH, null) ?: return false
        return stored == hashString(pin)
    }

    fun hasPin(): Boolean {
        return prefs.getString(KEY_PIN_HASH, null) != null
    }

    // --- Desen ---

    fun setPattern(pattern: String) {
        prefs.edit().putString(KEY_PATTERN_HASH, hashString(pattern)).apply()
    }

    fun verifyPattern(pattern: String): Boolean {
        val stored = prefs.getString(KEY_PATTERN_HASH, null) ?: return false
        return stored == hashString(pattern)
    }

    fun hasPattern(): Boolean {
        return prefs.getString(KEY_PATTERN_HASH, null) != null
    }

    // --- Servis ---

    var isServiceEnabled: Boolean
        get() = prefs.getBoolean(KEY_SERVICE_ENABLED, false)
        set(value) = prefs.edit().putBoolean(KEY_SERVICE_ENABLED, value).apply()

    // --- Matematik Ayarları ---

    var passScore: Int
        get() = prefs.getInt(KEY_PASS_SCORE, DEFAULT_PASS_SCORE)
        set(value) = prefs.edit().putInt(KEY_PASS_SCORE, value).apply()

    var guessMaxNumber: Int
        get() = prefs.getInt(KEY_GUESS_MAX, DEFAULT_GUESS_MAX)
        set(value) = prefs.edit().putInt(KEY_GUESS_MAX, value).apply()

    // 0 = sınırsız, diğerleri dakika cinsinden
    var unlockDurationMinutes: Int
        get() = prefs.getInt(KEY_UNLOCK_DURATION, 0)
        set(value) = prefs.edit().putInt(KEY_UNLOCK_DURATION, value).apply()

    // "relock" veya "close"
    var unlockExpiredAction: String
        get() = prefs.getString(KEY_UNLOCK_EXPIRED_ACTION, EXPIRE_ACTION_RELOCK) ?: EXPIRE_ACTION_RELOCK
        set(value) = prefs.edit().putString(KEY_UNLOCK_EXPIRED_ACTION, value).apply()

    // --- Kimlik Doğrulama Yöntemleri ---

    var isFingerprintEnabled: Boolean
        get() = prefs.getBoolean(KEY_FINGERPRINT_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_FINGERPRINT_ENABLED, value).apply()

    var isPinEnabled: Boolean
        get() = prefs.getBoolean(KEY_PIN_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_PIN_ENABLED, value).apply()

    var isPatternEnabled: Boolean
        get() = prefs.getBoolean(KEY_PATTERN_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_PATTERN_ENABLED, value).apply()

    // --- İlk Çalıştırma ---

    var isFirstRun: Boolean
        get() = prefs.getBoolean(KEY_FIRST_RUN, true)
        set(value) = prefs.edit().putBoolean(KEY_FIRST_RUN, value).apply()

    // --- Veri Kullanım Bildirimi Onayı ---

    var isDisclosureAccepted: Boolean
        get() = prefs.getBoolean(KEY_DISCLOSURE_ACCEPTED, false)
        set(value) = prefs.edit().putBoolean(KEY_DISCLOSURE_ACCEPTED, value).apply()

    // --- Oyun Görünürlük Ayarları (kilit ekranı) ---

    var isMathEnabled: Boolean
        get() = prefs.getBoolean(KEY_MATH_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_MATH_ENABLED, value).apply()

    var isGuessEnabled: Boolean
        get() = prefs.getBoolean(KEY_GUESS_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_GUESS_ENABLED, value).apply()

    var isPuzzleEnabled: Boolean
        get() = prefs.getBoolean(KEY_PUZZLE_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_PUZZLE_ENABLED, value).apply()

    var isRobotopiaEnabled: Boolean
        get() = prefs.getBoolean(KEY_ROBOTOPIA_ENABLED, true)
        set(value) = prefs.edit().putBoolean(KEY_ROBOTOPIA_ENABLED, value).apply()

    // --- Hash Yardımcısı ---

    private fun hashString(input: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }
    }
}
