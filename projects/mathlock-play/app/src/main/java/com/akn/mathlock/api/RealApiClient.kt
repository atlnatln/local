package com.akn.mathlock.api

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Gerçek HTTP implementasyonu — production'da kullanılır.
 */
class RealApiClient : ApiClient {

    companion object {
        const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        const val TIMEOUT = 8000
    }

    override fun post(path: String, body: JSONObject): ApiClient.Response {
        return execute("POST", path) { conn ->
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.outputStream.bufferedWriter().use { it.write(body.toString()) }
        }
    }

    override fun get(path: String): ApiClient.Response {
        return execute("GET", path)
    }

    override fun put(path: String, body: JSONObject): ApiClient.Response {
        return execute("PUT", path) { conn ->
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.outputStream.bufferedWriter().use { it.write(body.toString()) }
        }
    }

    override fun delete(path: String, body: JSONObject): ApiClient.Response {
        return execute("DELETE", path) { conn ->
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.doOutput = true
            conn.outputStream.bufferedWriter().use { it.write(body.toString()) }
        }
    }

    private inline fun execute(
        method: String,
        path: String,
        configure: (HttpURLConnection) -> Unit = {}
    ): ApiClient.Response {
        val url = URL("$API_BASE$path")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = method
        conn.connectTimeout = TIMEOUT
        conn.readTimeout = TIMEOUT
        configure(conn)

        val code = conn.responseCode
        val text = try {
            if (code in 200..299) {
                conn.inputStream.bufferedReader().readText()
            } else {
                conn.errorStream?.bufferedReader()?.readText() ?: ""
            }
        } catch (_: Exception) {
            ""
        }
        conn.disconnect()

        val json = try {
            JSONObject(text)
        } catch (_: Exception) {
            JSONObject()
        }
        return ApiClient.Response(code, json)
    }
}
