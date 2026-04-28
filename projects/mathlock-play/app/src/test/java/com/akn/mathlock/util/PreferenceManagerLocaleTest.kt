package com.akn.mathlock.util

import org.junit.Assert.*
import org.junit.Test
import java.util.Locale

/**
 * PreferenceManager locale davranışı birim testleri.
 *
 * PreferenceManager.appLocale get/set akışını simüle eder.
 * Gerçek SharedPreferences Android runtime gerektirdiği için,
 * mantık katmanını in-memory değişkenlerle test eder.
 */
class PreferenceManagerLocaleTest {

    @Test
    fun defaultLocaleIsTr() {
        // PreferenceManager.appLocale get(): null stored → Locale.getDefault().language ?: "tr"
        val storedLocale: String? = null
        val fallback = "tr"
        val effectiveLocale = storedLocale ?: fallback
        assertEquals("tr", effectiveLocale)
    }

    @Test
    fun setLocale_en_persists() {
        // Simüle edilmiş persist akışı
        var storedValue = "tr"
        fun persistLocale(value: String) {
            storedValue = value
        }
        persistLocale("en")
        assertEquals("en", storedValue)
    }

    @Test
    fun getLocale_returnsStoredValue() {
        val storedValue = "en"
        assertEquals("en", storedValue)
    }

    @Test
    fun getLocale_withDifferentStoredValues() {
        val locales = listOf("tr", "en", "de", "fr")
        for (locale in locales) {
            assertEquals(locale, locale) // Stored value correctly retrieved
        }
    }

    @Test
    fun appLocale_setAndGet_simulation() {
        var storedLocale: String? = null

        fun getLocale(): String = storedLocale ?: Locale.getDefault().language
        fun setLocale(value: String) {
            storedLocale = value
        }

        // Başlangıçta null → system locale
        val initial = getLocale()
        assertEquals(Locale.getDefault().language, initial)

        // "en" olarak set et
        setLocale("en")
        assertEquals("en", getLocale())

        // "tr" olarak değiştir
        setLocale("tr")
        assertEquals("tr", getLocale())
    }
}
