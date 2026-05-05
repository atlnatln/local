package com.akn.mathlock.api

import org.json.JSONObject

/**
 * Testlerde kullanılan ApiClient implementasyonu.
 * Çağrıları kaydeder ve yapılandırılmış yanıtları döndürür.
 */
class MockApiClient : ApiClient {

    val requests = mutableListOf<Pair<String, JSONObject>>()
    var nextResponse: ApiClient.Response = ApiClient.Response(200, JSONObject())
    private val responseQueue = mutableListOf<ApiClient.Response>()

    fun enqueue(vararg responses: ApiClient.Response) {
        responseQueue.addAll(responses)
    }

    private fun dequeue(): ApiClient.Response {
        return if (responseQueue.isNotEmpty()) responseQueue.removeAt(0) else nextResponse
    }

    override fun post(path: String, body: JSONObject): ApiClient.Response {
        requests.add("POST $path" to body)
        return dequeue()
    }

    override fun get(path: String): ApiClient.Response {
        requests.add("GET $path" to JSONObject())
        return dequeue()
    }

    override fun put(path: String, body: JSONObject): ApiClient.Response {
        requests.add("PUT $path" to body)
        return dequeue()
    }

    override fun delete(path: String, body: JSONObject): ApiClient.Response {
        requests.add("DELETE $path" to body)
        return dequeue()
    }

    override fun setAuthToken(token: String?) {
        // Test mock'u — auth token saklanmaz
    }

    fun reset() {
        requests.clear()
        responseQueue.clear()
        nextResponse = ApiClient.Response(200, JSONObject())
    }
}
