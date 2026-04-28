package com.akn.mathlock

import android.content.Context
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.util.LocaleHelper
import com.akn.mathlock.util.PreferenceManager

abstract class BaseActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        val locale = PreferenceManager(newBase).appLocale
        super.attachBaseContext(LocaleHelper.setLocale(newBase, locale))
    }
}
