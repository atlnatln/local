package com.akn.robotopia

import android.content.Context
import androidx.appcompat.app.AppCompatActivity
import com.akn.robotopia.util.LocaleHelper
import com.akn.robotopia.util.LocalePrefs

abstract class BaseActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        val locale = LocalePrefs(newBase).appLocale
        super.attachBaseContext(LocaleHelper.setLocale(newBase, locale))
    }
}
