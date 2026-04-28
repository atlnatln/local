package com.akn.mathlock.util

import android.content.Context
import java.util.Locale

object LocaleHelper {
    fun setLocale(context: Context, language: String): Context {
        val locale = Locale(language)
        Locale.setDefault(locale)
        val config = context.resources.configuration
        config.setLocale(locale)
        return context.createConfigurationContext(config)
    }

    fun getLocale(context: Context): String {
        return PreferenceManager(context).appLocale
    }
}
