package com.akn.mathlock.api

import org.json.JSONObject

/**
 * MathLock backend API'si için soyut client.
 * Test edilebilirlik için interface olarak tanımlanmıştır.
 */
interface ApiClient {

    data class Response(
        val statusCode: Int,
        val body: JSONObject
    )

    /** Auth token'ı ayarla (Authorization: Device <token> header'ı için) */
    fun setAuthToken(token: String?)

    /** POST isteği gönder */
    fun post(path: String, body: JSONObject): Response

    /** GET isteği gönder */
    fun get(path: String): Response

    /** PUT isteği gönder */
    fun put(path: String, body: JSONObject): Response

    /** DELETE isteği gönder */
    fun delete(path: String, body: JSONObject): Response
}
