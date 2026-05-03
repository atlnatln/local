package com.akn.robotopia.util

import android.content.Context
import android.content.SharedPreferences

class LocalePrefs(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("robotopia_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_APP_LOCALE = "app_locale"
    }

    var appLocale: String
        get() = prefs.getString(KEY_APP_LOCALE, java.util.Locale.getDefault().language) ?: "tr"
        set(value) = prefs.edit().putString(KEY_APP_LOCALE, value).apply()
}
