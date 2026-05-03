package com.akn.mathlock.util

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * EncryptedSharedPreferences wrapper with fallback to regular SharedPreferences.
 * All sensitive app data should use this instead of raw getSharedPreferences().
 */
object SecurePrefs {

    fun get(context: Context, name: String): SharedPreferences {
        return try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()

            EncryptedSharedPreferences.create(
                context,
                name,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            // Fallback: if encryption fails (e.g., corrupted keystore), use regular prefs
            context.getSharedPreferences(name, Context.MODE_PRIVATE)
        }
    }
}
