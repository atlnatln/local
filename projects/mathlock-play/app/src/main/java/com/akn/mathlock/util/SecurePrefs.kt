package com.akn.mathlock.util

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * EncryptedSharedPreferences wrapper.
 * All sensitive app data should use this instead of raw getSharedPreferences().
 * Fallback to plain text KALDIRILDI — güvenlik riski (Hata 7 fix).
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
            // Fallback KALDIRILDI — güvenlik riski
            Log.e("SecurePrefs", "Encryption init failed for '$name': ${e.message}")
            throw IllegalStateException(
                "Güvenli depolama başlatılamadı. Lütfen cihaz şifrelemesini kontrol edin.",
                e
            )
        }
    }
}
