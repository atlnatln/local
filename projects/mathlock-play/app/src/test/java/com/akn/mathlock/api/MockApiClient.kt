package com.akn.mathlock.api

import org.json.JSONObject

/**
 * Testlerde kullanılan ApiClient implementasyonu.
 * Çağrıları kaydeder ve yapılandırılmış yanıtları döndürür.
 */
class MockApiClient : ApiClient {

    val requests = mutableListOf<Pair<String, JSONObject>>()
    var nextResponse: ApiClient.Response = ApiClient.Response(200, JSONObject())

    override fun post(path: String, body: JSONObject): ApiClient.Response {
        requests.add("POST $path" to body)
        return nextResponse
    }

    override fun get(path: String): ApiClient.Response {
        requests.add("GET $path" to JSONObject())
        return nextResponse
    }

    override fun put(path: String, body: JSONObject): ApiClient.Response {
        requests.add("PUT $path" to body)
        return nextResponse
    }

    override fun delete(path: String, body: JSONObject): ApiClient.Response {
        requests.add("DELETE $path" to body)
        return nextResponse
    }

    fun reset() {
        requests.clear()
        nextResponse = ApiClient.Response(200, JSONObject())
    }
}
