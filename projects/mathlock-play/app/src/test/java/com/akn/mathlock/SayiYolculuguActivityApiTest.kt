package com.akn.mathlock

import android.content.Context
import android.content.SharedPreferences
import com.akn.mathlock.api.ApiClient
import com.akn.mathlock.api.MockApiClient
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.SecurePrefs
import io.mockk.every
import io.mockk.mockkObject
import io.mockk.unmockkAll
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import java.lang.reflect.Field
import java.lang.reflect.Method
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * SayiYolculuguActivity — fetchLevels / uploadLevelProgress API davranış testleri.
 *
 * Sorun geçmişi:
 * 1. Backend auth sadece header kabul ediyordu; eski app versiyonları query param/body token
 *    gönderince 403 alıyordu.
 * 2. child_id mismatch (telefonda kayıtlı child_id, backend'deki cihaz child_id'si farklı)
 *    yüzünden 404 dönüyordu; retry yoktu.
 * 3. uploadLevelProgress 404/hata durumunda callback çağırmıyordu → kullanıcı set bitince
 *    yeni set alamıyordu.
 */
@RunWith(RobolectricTestRunner::class)
class SayiYolculuguActivityApiTest {

    private lateinit var context: Context
    private lateinit var activity: SayiYolculuguActivity
    private lateinit var mockApiClient: MockApiClient

    @Before
    fun setUp() {
        context = RuntimeEnvironment.getApplication()
        mockkObject(SecurePrefs)

        // Fake access token (imzalı format değil, mock auth için yeterli)
        val fakePrefs = context.getSharedPreferences("test_account", Context.MODE_PRIVATE)
        every { SecurePrefs.get(any(), "mathlock_account") } returns fakePrefs
        fakePrefs.edit().putString("access_token", "test-token").apply()

        // Fake PreferenceManager childId
        val prefPrefs = context.getSharedPreferences("mathlock_prefs", Context.MODE_PRIVATE)
        every { SecurePrefs.get(any(), "mathlock_prefs") } returns prefPrefs
        prefPrefs.edit().putInt("active_child_id", 99).apply()

        activity = Robolectric.buildActivity(SayiYolculuguActivity::class.java).create().get()
        mockApiClient = MockApiClient()
        injectApiClient(activity, mockApiClient)
    }

    @After
    fun tearDown() {
        unmockkAll()
        mockApiClient.reset()
    }

    // ─── fetchLevels tests ─────────────────────────────────────────────────

    @Test
    fun fetchLevels_childIdNotFound_retriesWithoutChildId() {
        // İlk istek (child_id=99) 404, ikinci istek (child_id yok) 200
        mockApiClient.enqueue(
            ApiClient.Response(404, JSONObject()),
            ApiClient.Response(200, JSONObject().apply {
                put("set_id", 42)
                put("levels", listOf<Any>())
                put("completed_level_ids", listOf<Any>())
            })
        )

        val result = invokeFetchLevels(activity)

        // İki istek atılmalı
        assertEquals(2, mockApiClient.requests.size)
        assertTrue("First request should contain child_id=99",
            mockApiClient.requests[0].first.contains("child_id=99"))
        assertTrue("Second request should NOT contain child_id",
            !mockApiClient.requests[1].first.contains("child_id"))

        // Sonuç null değil (cache değil, gerçek response)
        assertNotNull(result)
    }

    @Test
    fun fetchLevels_childIdNotFound_resetsLocalChildId() {
        mockApiClient.enqueue(
            ApiClient.Response(404, JSONObject()),
            ApiClient.Response(200, JSONObject().apply {
                put("set_id", 42)
                put("levels", listOf<Any>())
                put("completed_level_ids", listOf<Any>())
            })
        )

        invokeFetchLevels(activity)

        val pm = PreferenceManager(context)
        assertEquals("Local childId should be reset to 0 after 404 retry", 0, pm.activeChildId)
    }

    // ─── uploadLevelProgress tests ─────────────────────────────────────────

    @Test
    fun uploadLevelProgress_childIdNotFound_retriesWithoutChildId() {
        mockApiClient.enqueue(
            ApiClient.Response(404, JSONObject()),
            ApiClient.Response(200, JSONObject().apply {
                put("success", true)
                put("auto_renewal_started", true)
            })
        )

        val latch = CountDownLatch(1)
        var receivedResp: JSONObject? = null

        invokeUploadLevelProgress(activity, listOf(1)) { resp ->
            receivedResp = resp
            latch.countDown()
        }

        assertTrue("Callback should be invoked", latch.await(3, TimeUnit.SECONDS))
        assertNotNull(receivedResp)
        assertTrue("auto_renewal_started should be true",
            receivedResp!!.optBoolean("auto_renewal_started", false))

        // İki POST isteği atılmalı
        val postRequests = mockApiClient.requests.filter { it.first.startsWith("POST") }
        assertEquals(2, postRequests.size)
        assertTrue("First POST should contain child_id=99",
            postRequests[0].second.optInt("child_id", -1) == 99)
        assertFalse("Second POST should NOT contain child_id",
            postRequests[1].second.has("child_id"))
    }

    @Test
    fun uploadLevelProgress_httpError_invokesCallback() {
        mockApiClient.nextResponse = ApiClient.Response(500, JSONObject())

        val latch = CountDownLatch(1)
        var receivedResp: JSONObject? = null

        invokeUploadLevelProgress(activity, listOf(1)) { resp ->
            receivedResp = resp
            latch.countDown()
        }

        assertTrue("Callback should be invoked even on HTTP 500", latch.await(3, TimeUnit.SECONDS))
        assertNotNull(receivedResp)
        assertEquals("error field should indicate http_500", "http_500", receivedResp!!.optString("error"))
        assertFalse("auto_renewal_started should be false on error",
            receivedResp!!.optBoolean("auto_renewal_started", true))
    }

    @Test
    fun uploadLevelProgress_exception_invokesCallback() {
        // Force exception by using a broken apiClient
        val brokenClient = object : ApiClient {
            override fun post(path: String, body: JSONObject) = throw RuntimeException("network error")
            override fun get(path: String) = throw RuntimeException("network error")
            override fun put(path: String, body: JSONObject) = throw RuntimeException("network error")
            override fun delete(path: String, body: JSONObject) = throw RuntimeException("network error")
            override fun setAuthToken(token: String?) {}
        }
        injectApiClient(activity, brokenClient)

        val latch = CountDownLatch(1)
        var receivedResp: JSONObject? = null

        invokeUploadLevelProgress(activity, listOf(1)) { resp ->
            receivedResp = resp
            latch.countDown()
        }

        assertTrue("Callback should be invoked even on exception", latch.await(3, TimeUnit.SECONDS))
        assertNotNull(receivedResp)
        assertEquals("exception", receivedResp!!.optString("error"))
    }

    // ─── Reflection helpers ────────────────────────────────────────────────

    private fun injectApiClient(activity: SayiYolculuguActivity, client: ApiClient) {
        val field: Field = SayiYolculuguActivity::class.java.getDeclaredField("apiClient")
        field.isAccessible = true
        field.set(activity, client)
    }

    private fun invokeFetchLevels(activity: SayiYolculuguActivity): String? {
        val method: Method = SayiYolculuguActivity::class.java.getDeclaredMethod("fetchLevels")
        method.isAccessible = true
        return method.invoke(activity) as? String
    }

    private fun invokeUploadLevelProgress(
        activity: SayiYolculuguActivity,
        newlyCompletedIds: List<Int>,
        onResult: ((JSONObject) -> Unit)?
    ) {
        val method: Method = SayiYolculuguActivity::class.java.getDeclaredMethod(
            "uploadLevelProgress",
            List::class.java,
            Function1::class.java
        )
        method.isAccessible = true
        method.invoke(activity, newlyCompletedIds, onResult)
    }
}
