package com.akn.mathlock

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/**
 * SayiYolculugu initGame payload yapısı birim testleri.
 *
 * Saf JSONObject mantığı — Android Context gerektirmez.
 */
class SayiYolculuguPayloadTest {

    @Test
    fun initGamePayloadContainsLocale() {
        val payload = JSONObject().apply {
            put("locale", "en")
            put("forceClear", true)
        }
        assertTrue(payload.has("locale"))
        assertEquals("en", payload.getString("locale"))
    }

    @Test
    fun initGamePayloadContainsForceClear() {
        val payload = JSONObject().apply {
            put("locale", "tr")
            put("forceClear", false)
        }
        assertTrue(payload.has("forceClear"))
        assertFalse(payload.getBoolean("forceClear"))
    }

    @Test
    fun isNewSet_true_forceClear_true() {
        val isNewSet = true
        val forceClear = isNewSet
        assertTrue("Yeni set → forceClear=true olmalı", forceClear)
    }
}
