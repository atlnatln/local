package com.akn.mathlock.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            val prefManager = PreferenceManager(context)
            if (prefManager.isServiceEnabled) {
                AppLockService.start(context)
            }
        }
    }
}
