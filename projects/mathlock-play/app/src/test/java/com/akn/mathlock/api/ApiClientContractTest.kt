package com.akn.mathlock.api

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * ApiClient interface contract testleri.
 * MockApiClient kullanarak tüm HTTP method'larının doğru kaydedildiğini doğrular.
 */
class ApiClientContractTest {

    private lateinit var mock: MockApiClient

    @Before
    fun setUp() {
        mock = MockApiClient()
    }

    @Test
    fun `post records path and body`() {
        mock.nextResponse = ApiClient.Response(201, JSONObject().put("id", 1))
        val body = JSONObject().put("name", "Ali")

        val resp = mock.post("/register/", body)

        assertEquals(201, resp.statusCode)
        assertEquals(1, resp.body.getInt("id"))
        assertEquals(1, mock.requests.size)
        assertEquals("POST /register/", mock.requests[0].first)
        assertEquals("Ali", mock.requests[0].second.getString("name"))
    }

    @Test
    fun `get records path`() {
        mock.nextResponse = ApiClient.Response(200, JSONObject().put("credits", 5))

        val resp = mock.get("/credits/?device_token=abc")

        assertEquals(200, resp.statusCode)
        assertEquals(5, resp.body.getInt("credits"))
        assertEquals(1, mock.requests.size)
        assertEquals("GET /credits/?device_token=abc", mock.requests[0].first)
    }

    @Test
    fun `put records path and body`() {
        mock.nextResponse = ApiClient.Response(200, JSONObject().put("success", true))
        val body = JSONObject().put("new_name", "Veli")

        val resp = mock.put("/children/detail/", body)

        assertTrue(resp.body.getBoolean("success"))
        assertEquals("PUT /children/detail/", mock.requests[0].first)
    }

    @Test
    fun `delete records path and body`() {
        mock.nextResponse = ApiClient.Response(200, JSONObject().put("success", true))
        val body = JSONObject().put("child_id", 2)

        val resp = mock.delete("/children/detail/", body)

        assertTrue(resp.body.getBoolean("success"))
        assertEquals("DELETE /children/detail/", mock.requests[0].first)
    }

    @Test
    fun `reset clears requests`() {
        mock.post("/x/", JSONObject())
        assertEquals(1, mock.requests.size)

        mock.reset()

        assertEquals(0, mock.requests.size)
        assertEquals(200, mock.nextResponse.statusCode)
    }

    @Test
    fun `multiple requests are recorded in order`() {
        mock.post("/a/", JSONObject().put("k", 1))
        mock.get("/b/")
        mock.put("/c/", JSONObject().put("k", 2))

        assertEquals(3, mock.requests.size)
        assertEquals("POST /a/", mock.requests[0].first)
        assertEquals("GET /b/", mock.requests[1].first)
        assertEquals("PUT /c/", mock.requests[2].first)
    }
}
