package com.akn.mathlock

import android.content.Context
import android.content.SharedPreferences
import com.akn.mathlock.util.SecurePrefs
import com.akn.mathlock.util.StatsTracker
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkObject
import io.mockk.mockkStatic
import io.mockk.unmockkAll
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.lang.reflect.Method

/**
 * StatsTracker birim testleri — session_id üretimi ve idempotency.
 */
class StatsTrackerTest {

    private lateinit var context: Context
    private lateinit var mockPrefs: SharedPreferences
    private lateinit var mockEditor: SharedPreferences.Editor

    @Before
    fun setUp() {
        mockkStatic(android.util.Log::class)
        every { android.util.Log.d(any(), any()) } returns 0
        every { android.util.Log.w(any(), any<String>()) } returns 0
        every { android.util.Log.w(any(), any<String>(), any()) } returns 0
        every { android.util.Log.e(any(), any<String>()) } returns 0
        every { android.util.Log.e(any(), any<String>(), any()) } returns 0

        mockkObject(SecurePrefs)
        context = mockk(relaxed = true)
        mockPrefs = mockk(relaxed = true)
        mockEditor = mockk(relaxed = true)

        every { SecurePrefs.get(any(), any()) } returns mockPrefs
        every { mockPrefs.edit() } returns mockEditor
        every { mockEditor.putString(any(), any()) } returns mockEditor
        every { mockEditor.putLong(any(), any()) } returns mockEditor
        every { mockEditor.putInt(any(), any()) } returns mockEditor
        every { mockEditor.remove(any()) } returns mockEditor
        every { mockEditor.apply() } returns Unit
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `generateSessionId - ilk cagri yeni session id uretir`() {
        every { mockPrefs.getString("last_session_id", null) } returns null
        every { mockPrefs.getLong("last_session_time", 0) } returns 0L

        val tracker = StatsTracker(context)
        val method = tracker.javaClass.getDeclaredMethod("generateSessionId")
        method.isAccessible = true
        val sessionId = method.invoke(tracker) as String

        assertNotNull(sessionId)
        assertTrue("Session ID bos olmamali", sessionId.isNotBlank())
        assertTrue("Session ID timestamp icermeli", sessionId.contains("-"))
    }

    @Test
    fun `generateSessionId - 5 dakika icinde ayni session id doner`() {
        val existingId = "test-session-123"
        val now = System.currentTimeMillis()
        every { mockPrefs.getString("last_session_id", null) } returns existingId
        every { mockPrefs.getLong("last_session_time", 0) } returns (now - 60_000) // 1 dk önce

        val tracker = StatsTracker(context)
        val method = tracker.javaClass.getDeclaredMethod("generateSessionId")
        method.isAccessible = true
        val sessionId = method.invoke(tracker) as String

        assertEquals(existingId, sessionId)
    }

    @Test
    fun `generateSessionId - 5 dakika gecince yeni session id uretir`() {
        val existingId = "test-session-123"
        val now = System.currentTimeMillis()
        every { mockPrefs.getString("last_session_id", null) } returns existingId
        every { mockPrefs.getLong("last_session_time", 0) } returns (now - 600_000) // 10 dk önce

        val tracker = StatsTracker(context)
        val method = tracker.javaClass.getDeclaredMethod("generateSessionId")
        method.isAccessible = true
        val sessionId = method.invoke(tracker) as String

        assertNotEquals(existingId, sessionId)
    }

    @Test
    fun `buildStatsJson - gecerli json uretir`() {
        val tracker = StatsTracker(context)
        val json = tracker.buildStatsJson(1)

        assertTrue("JSON bos olmamali", json.isNotBlank())
        assertTrue("questionVersion icermeli", json.contains("questionVersion"))
        assertTrue("completedAt icermeli", json.contains("completedAt"))
    }
}
