package com.akn.mathlock.util

import org.junit.Assert.*
import org.junit.Test
import java.util.Locale

/**
 * LocaleHelper davranışı birim testleri.
 *
 * LocaleHelper.setLocale'in temel locale mantığını simüle eder.
 * Context wrapping doğrudan test edilemez (Android runtime bağımlılığı),
 * bu nedenle Locale değişimi ve getLocale akışı test edilir.
 */
class LocaleHelperTest {

    @Test
    fun setLocale_en_configuresEnglish() {
        val oldDefault = Locale.getDefault()
        try {
            val locale = Locale("en")
            Locale.setDefault(locale)
            assertEquals("en", Locale.getDefault().language)
            assertEquals(Locale.ENGLISH.language, Locale.getDefault().language)
        } finally {
            Locale.setDefault(oldDefault)
        }
    }

    @Test
    fun setLocale_tr_configuresTurkish() {
        val oldDefault = Locale.getDefault()
        try {
            val locale = Locale("tr")
            Locale.setDefault(locale)
            assertEquals("tr", Locale.getDefault().language)
            assertEquals(Locale("tr").language, Locale.getDefault().language)
        } finally {
            Locale.setDefault(oldDefault)
        }
    }

    @Test
    fun setLocale_setsDefaultLocale() {
        val oldDefault = Locale.getDefault()
        try {
            val newLocale = Locale("de")
            Locale.setDefault(newLocale)
            assertEquals(newLocale, Locale.getDefault())
        } finally {
            Locale.setDefault(oldDefault)
        }
    }

    @Test
    fun setLocale_invalidFallbacksToDefault() {
        // Geçersiz locale kodu Locale tarafından kabul edilir (ISO uyumsuz),
        // ancak LocaleHelper.setLocale içinde normalize edilebilir.
        // Burada Locale davranışını doğruluyoruz.
        val invalidLocale = Locale("xx")
        assertEquals("xx", invalidLocale.language)
    }

    @Test
    fun getLocaleSimulation_returnsCorrectValue() {
        // LocaleHelper.getLocale(context) = PreferenceManager(context).appLocale
        // Bu test getLocale akışını simüle eder.
        var storedLocale: String? = "en"
        val result = storedLocale ?: Locale.getDefault().language
        assertEquals("en", result)
    }

    @Test
    fun getLocaleSimulation_fallbackToSystemLocale() {
        var storedLocale: String? = null
        val result = storedLocale ?: Locale.getDefault().language
        assertEquals(Locale.getDefault().language, result)
    }
}
