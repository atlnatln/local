package com.akn.mathlock

import android.content.Context
import android.content.SharedPreferences
import com.akn.mathlock.api.ApiClient
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.SecurePrefs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.mockkObject
import io.mockk.mockkStatic
import io.mockk.Runs
import io.mockk.unmockkAll
import io.mockk.verify
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * AccountManager birim testleri — token expiry ve re-register davranışı.
 */
class AccountManagerTest {

    private lateinit var context: Context
    private lateinit var mockPrefs: SharedPreferences
    private lateinit var mockEditor: SharedPreferences.Editor
    private lateinit var mockApi: ApiClient

    @Before
    fun setUp() {
        mockkStatic(android.util.Log::class)
        every { android.util.Log.d(any(), any()) } returns 0
        every { android.util.Log.w(any(), any<String>()) } returns 0
        every { android.util.Log.w(any(), any<Throwable>()) } returns 0
        every { android.util.Log.w(any(), any<String>(), any()) } returns 0
        every { android.util.Log.e(any(), any<String>()) } returns 0
        every { android.util.Log.e(any(), any<String>(), any()) } returns 0

        mockkObject(SecurePrefs)
        context = mockk(relaxed = true)
        mockPrefs = mockk(relaxed = true)
        mockEditor = mockk(relaxed = true)
        mockApi = mockk(relaxed = true)

        every { SecurePrefs.get(any(), any()) } returns mockPrefs
        every { mockPrefs.edit() } returns mockEditor
        every { mockEditor.putString(any(), any()) } returns mockEditor
        every { mockEditor.putInt(any(), any()) } returns mockEditor
        every { mockEditor.putBoolean(any(), any()) } returns mockEditor
        every { mockEditor.remove(any()) } returns mockEditor
        every { mockEditor.apply() } just Runs
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `getOrRefreshToken - token yoksa getOrRegister cagrilir`() {
        every { mockPrefs.getString("access_token", null) } returns null
        every { mockApi.post("/register/", any()) } returns ApiClient.Response(
            200,
            JSONObject().apply {
                put("device_token", "dev123")
                put("access_token", "acc123")
                put("credits", 0)
                put("free_set_used", false)
            }
        )

        val am = AccountManager(context, mockApi)
        val token = am.getOrRefreshToken()

        assertEquals("acc123", token)
        verify { mockApi.post("/register/", any()) }
    }

    @Test
    fun `getOrRefreshToken - token gecerliyse ayni token doner`() {
        every { mockPrefs.getString("access_token", null) } returns "valid_token"
        every { mockApi.get("/credits/") } returns ApiClient.Response(
            200,
            JSONObject().apply { put("credits", 5) }
        )

        val am = AccountManager(context, mockApi)
        val token = am.getOrRefreshToken()

        assertEquals("valid_token", token)
    }

    @Test
    fun `getOrRefreshToken - 403 alinca token silinir ve re-register yapilir`() {
        // 1. init bloğunda getAccessToken() çağrılır
        // 2. getOrRefreshToken() içindeki getAccessToken() (existing değerini alır)
        // 3. getOrRegister() içindeki getAccessToken() (remove sonrası)
        every { mockPrefs.getString("access_token", null) } returnsMany listOf("expired_token", "expired_token", null)
        every { mockApi.get("/credits/") } returns ApiClient.Response(
            403,
            JSONObject().apply { put("error", "Token expired") }
        )
        every { mockApi.post("/register/", any()) } returns ApiClient.Response(
            200,
            JSONObject().apply {
                put("device_token", "dev_new")
                put("access_token", "acc_new")
                put("credits", 0)
                put("free_set_used", false)
            }
        )

        val am = AccountManager(context, mockApi)
        val token = am.getOrRefreshToken()

        assertEquals("acc_new", token)
        verify { mockEditor.remove("access_token") }
        verify { mockApi.setAuthToken(null) }
        verify { mockApi.post("/register/", any()) }
    }

    @Test
    fun `getOrRefreshToken - offline durumda mevcut token korunur`() {
        every { mockPrefs.getString("access_token", null) } returns "offline_token"
        every { mockApi.get("/credits/") } throws java.net.UnknownHostException("No internet")

        val am = AccountManager(context, mockApi)
        val token = am.getOrRefreshToken()

        assertEquals("offline_token", token)
    }

    @Test
    fun `getRawDeviceToken - kayitli device_token doner`() {
        every { mockPrefs.getString("access_token", null) } returns "acc_token"
        every { mockPrefs.getString("device_token", null) } returns "raw_dev_token"

        val am = AccountManager(context, mockApi)
        assertEquals("raw_dev_token", am.getRawDeviceToken())
    }

    @Test
    fun `getDeviceToken - kayitli device_token doner`() {
        every { mockPrefs.getString("access_token", null) } returns "acc_token"
        every { mockPrefs.getString("device_token", null) } returns "dev_token"

        val am = AccountManager(context, mockApi)
        assertEquals("dev_token", am.getDeviceToken())
    }
}
