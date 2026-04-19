package com.akn.mathlock.util

import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID

/**
 * Cihaz kaydı ve email hesabını yönetir.
 *
 * - İlk açılışta otomatik olarak VPS'e cihaz kaydeder ve device_token alır.
 * - Kredi satın almak için email kaydı gerekir: registerEmail().
 * - device_token ve email SharedPreferences'da kalıcı tutulur.
 */
class AccountManager(private val context: Context) {

    companion object {
        private const val TAG = "AccountManager"
        private const val PREFS_NAME = "mathlock_account"
        private const val KEY_DEVICE_TOKEN = "device_token"
        private const val KEY_INSTALLATION_ID = "installation_id"
        private const val KEY_EMAIL = "registered_email"
        private const val KEY_CREDITS = "cached_credits"
        private const val KEY_FREE_USED = "free_set_used"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val TIMEOUT = 8000
    }

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    /** Kayıtlı device_token (null = henüz kayıt yok). */
    fun getDeviceToken(): String? = prefs.getString(KEY_DEVICE_TOKEN, null)

    /** Kayıtlı email (null = kayıt yok). */
    fun getEmail(): String? = prefs.getString(KEY_EMAIL, null)

    /** Email kaydı var mı? */
    fun hasEmail(): Boolean = !prefs.getString(KEY_EMAIL, null).isNullOrBlank()

    /** Yerel olarak önbelleğe alınan kredi sayısı. */
    fun getCachedCredits(): Int = prefs.getInt(KEY_CREDITS, 0)

    /** Ücretsiz set kullanıldı mı? */
    fun isFreeSetUsed(): Boolean = prefs.getBoolean(KEY_FREE_USED, false)

    /**
     * Cihazı VPS'e kaydet ve device_token al.
     * Daha önce kaydedildiyse mevcut token'ı döndürür.
     * IO thread'den çağır.
     * @return device_token veya null (ağ hatası)
     */
    fun getOrRegister(): String? {
        val existing = getDeviceToken()
        if (!existing.isNullOrBlank()) return existing

        val installationId = getOrCreateInstallationId()
        return try {
            val url = URL("$API_BASE/register/")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.connectTimeout = TIMEOUT
            conn.readTimeout = TIMEOUT

            val body = JSONObject().apply { put("installation_id", installationId) }
            conn.outputStream.bufferedWriter().use { it.write(body.toString()) }

            val code = conn.responseCode
            if (code in 200..299) {
                val response = JSONObject(conn.inputStream.bufferedReader().readText())
                conn.disconnect()
                val token = response.getString("device_token")
                val credits = response.optInt("credits", 0)
                val freeUsed = response.optBoolean("free_set_used", false)
                prefs.edit()
                    .putString(KEY_DEVICE_TOKEN, token)
                    .putInt(KEY_CREDITS, credits)
                    .putBoolean(KEY_FREE_USED, freeUsed)
                    .apply()
                // Çocuk profil bilgisini kaydet
                val children = response.optJSONArray("children")
                if (children != null && children.length() > 0) {
                    val prefManager = PreferenceManager(context)
                    for (i in 0 until children.length()) {
                        val c = children.getJSONObject(i)
                        if (c.optBoolean("is_active", false)) {
                            prefManager.activeChildName = c.optString("name", "Çocuk")
                            prefManager.activeEducationPeriod = c.optString("education_period", "sinif_2")
                            break
                        }
                    }
                }
                Log.d(TAG, "Cihaz kaydedildi: token=${token.take(8)}...")
                token
            } else {
                conn.disconnect()
                Log.w(TAG, "Cihaz kaydı başarısız: $code")
                null
            }
        } catch (e: Exception) {
            Log.w(TAG, "Cihaz kaydı hatası: ${e.message}")
            null
        }
    }

    /**
     * Email adresini cihaza bağla.
     * IO thread'den çağır.
     * @return true: başarılı, false: hata
     * @throws IllegalArgumentException geçersiz email
     */
    fun registerEmail(email: String): RegisterEmailResult {
        val token = getDeviceToken()
            ?: return RegisterEmailResult.Error("Önce cihaz kaydı yapılmalı")

        return try {
            val url = URL("$API_BASE/auth/register-email/")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.connectTimeout = TIMEOUT
            conn.readTimeout = TIMEOUT

            val body = JSONObject().apply {
                put("device_token", token)
                put("email", email.trim().lowercase())
            }
            conn.outputStream.bufferedWriter().use { it.write(body.toString()) }

            val code = conn.responseCode
            val responseText = if (code in 200..299) {
                conn.inputStream.bufferedReader().readText()
            } else {
                conn.errorStream?.bufferedReader()?.readText() ?: ""
            }
            conn.disconnect()

            if (code in 200..299) {
                val response = try { JSONObject(responseText) } catch (_: Exception) { JSONObject() }
                val recovered = response.optBoolean("recovered", false)
                val credits = response.optInt("credits", -1)
                prefs.edit().apply {
                    putString(KEY_EMAIL, email.trim().lowercase())
                    if (credits >= 0) putInt(KEY_CREDITS, credits)
                }.apply()
                Log.d(TAG, "Email kaydedildi: $email, recovered=$recovered, credits=$credits")
                if (recovered) RegisterEmailResult.Recovered(credits)
                else RegisterEmailResult.Success
            } else {
                val error = try {
                    JSONObject(responseText).optString("error", "Kayıt başarısız")
                } catch (_: Exception) { "Kayıt başarısız" }
                Log.w(TAG, "Email kaydı başarısız ($code): $error")
                RegisterEmailResult.Error(error)
            }
        } catch (e: Exception) {
            Log.w(TAG, "Email kaydı hatası: ${e.message}")
            RegisterEmailResult.Error("Bağlantı hatası")
        }
    }

    /**
     * Kredi bakiyesini VPS'ten güncelle.
     * IO thread'den çağır.
     */
    fun refreshCredits(): Int {
        val token = getDeviceToken() ?: return getCachedCredits()
        return try {
            val url = URL("$API_BASE/credits/?device_token=$token")
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = TIMEOUT
            conn.readTimeout = TIMEOUT
            if (conn.responseCode in 200..299) {
                val data = JSONObject(conn.inputStream.bufferedReader().readText())
                conn.disconnect()
                val credits = data.optInt("credits", 0)
                val freeUsed = data.optBoolean("free_set_used", false)
                prefs.edit()
                    .putInt(KEY_CREDITS, credits)
                    .putBoolean(KEY_FREE_USED, freeUsed)
                    .apply()
                credits
            } else {
                conn.disconnect()
                getCachedCredits()
            }
        } catch (e: Exception) {
            getCachedCredits()
        }
    }

    private fun getOrCreateInstallationId(): String {
        val stored = prefs.getString(KEY_INSTALLATION_ID, null)
        if (!stored.isNullOrBlank()) return stored
        val id = UUID.randomUUID().toString()
        prefs.edit().putString(KEY_INSTALLATION_ID, id).apply()
        return id
    }

    sealed class RegisterEmailResult {
        object Success : RegisterEmailResult()
        data class Recovered(val credits: Int) : RegisterEmailResult()
        data class Error(val message: String) : RegisterEmailResult()
    }
}
