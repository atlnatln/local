package com.akn.mathlock.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.akn.mathlock.service.AppLockService
import com.akn.mathlock.util.PreferenceManager

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val trigger = when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED -> "BOOT"
            Intent.ACTION_MY_PACKAGE_REPLACED -> "OTA_UPDATE"
            else -> return
        }
        val prefManager = PreferenceManager(context)
        if (prefManager.isServiceEnabled) {
            android.util.Log.d("BootReceiver", "Servis başlatılıyor (tetikleyen: $trigger)")
            AppLockService.start(context)
        }
    }
}
