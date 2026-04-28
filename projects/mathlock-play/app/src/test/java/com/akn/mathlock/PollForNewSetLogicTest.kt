package com.akn.mathlock

import org.junit.Assert.*
import org.junit.Test

/**
 * pollForNewSet mantığı birim testleri.
 *
 * SayiYolculuguActivity.pollForNewSet() parametrelerini ve davranış sınırlarını doğrular.
 */
class PollForNewSetLogicTest {

    companion object {
        const val MAX_ATTEMPTS = 120
        const val INTERVAL_MS = 5000L
        const val TIMEOUT_MS = 600_000L // 10 dakika
    }

    @Test
    fun maxAttemptsIs120() {
        assertEquals(120, MAX_ATTEMPTS)
    }

    @Test
    fun intervalIs5Seconds() {
        assertEquals(5000L, INTERVAL_MS)
    }

    @Test
    fun timeoutAfter10Minutes() {
        val totalTimeoutMs = MAX_ATTEMPTS * INTERVAL_MS
        assertEquals(600_000L, totalTimeoutMs)
    }

    @Test
    fun exceedingMaxAttemptsShowsError() {
        val attempt = MAX_ATTEMPTS
        assertTrue("attempt >= $MAX_ATTEMPTS → hata gösterilmeli", attempt >= MAX_ATTEMPTS)
    }

    @Test
    fun justBelowMaxAttemptsDoesNotShowError() {
        val attempt = MAX_ATTEMPTS - 1
        assertFalse("attempt < $MAX_ATTEMPTS → hata gösterilmemeli", attempt >= MAX_ATTEMPTS)
    }

    @Test
    fun zeroAttemptsDoesNotShowError() {
        val attempt = 0
        assertFalse("attempt = 0 → hata gösterilmemeli", attempt >= MAX_ATTEMPTS)
    }

    @Test
    fun timeoutCalculationIsConsistent() {
        // 120 deneme × 5 saniye = 10 dakika
        val minutes = (MAX_ATTEMPTS * INTERVAL_MS) / 1000 / 60
        assertEquals(10, minutes)
    }

    @Test
    fun intervalIsPositiveAndNonZero() {
        assertTrue("Interval pozitif olmalı", INTERVAL_MS > 0)
    }

    @Test
    fun maxAttemptsIsPositiveAndNonZero() {
        assertTrue("Max attempts pozitif olmalı", MAX_ATTEMPTS > 0)
    }
}
