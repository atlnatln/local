package com.akn.mathlock.util

import android.util.Log
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * Backend kredi API'si için basit HTTP client.
 * useCredit() → 1 kredi kullan veya ilk ücretsiz seti etkinleştir,
 *               backend AI ile yeni soru seti üretir.
 */
class CreditApiClient {

    companion object {
        private const val TAG = "CreditApiClient"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val CONNECT_TIMEOUT = 8000
        private const val READ_TIMEOUT = 120000 // AI üretim uzun sürebilir
    }

    data class UseCreditResult(
        val success: Boolean,
        val creditsRemaining: Int,
        val isFree: Boolean,
        val questionsGenerated: Int,
        val setVersion: Int,
        val error: String? = null
    )

    /**
     * 1 kredi kullan (veya ilk ücretsiz set).
     * IO thread'den çağır.
     */
    fun useCredit(
        deviceToken: String,
        childName: String,
        statsJson: String? = null
    ): UseCreditResult {
        return try {
            val url = URL("$API_BASE/credits/use/")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.connectTimeout = CONNECT_TIMEOUT
            conn.readTimeout = READ_TIMEOUT

            val body = JSONObject().apply {
                put("device_token", deviceToken)
                put("child_name", childName)
                if (!statsJson.isNullOrBlank()) {
                    put("stats", JSONObject(statsJson))
                }
            }
            OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(body.toString()) }

            val code = conn.responseCode
            val responseText = try {
                conn.inputStream.bufferedReader().use { it.readText() }
            } catch (e: Exception) {
                conn.errorStream?.bufferedReader()?.use { it.readText() } ?: ""
            }
            conn.disconnect()

            if (code in 200..299) {
                val json = JSONObject(responseText)
                UseCreditResult(
                    success = json.optBoolean("success", false),
                    creditsRemaining = json.optInt("credits_remaining", 0),
                    isFree = json.optBoolean("is_free", false),
                    questionsGenerated = json.optInt("questions_generated", 0),
                    setVersion = json.optInt("set_version", 0)
                )
            } else {
                val err = try { JSONObject(responseText).optString("error", "HTTP $code") } catch (_: Exception) { "HTTP $code" }
                Log.w(TAG, "useCredit başarısız: $err")
                UseCreditResult(success = false, creditsRemaining = 0, isFree = false, questionsGenerated = 0, setVersion = 0, error = err)
            }
        } catch (e: Exception) {
            Log.w(TAG, "useCredit hatası: ${e.message}")
            UseCreditResult(success = false, creditsRemaining = 0, isFree = false, questionsGenerated = 0, setVersion = 0, error = e.message)
        }
    }
}
