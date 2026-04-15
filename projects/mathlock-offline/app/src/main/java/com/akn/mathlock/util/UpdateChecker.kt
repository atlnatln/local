package com.akn.mathlock.util

import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

data class UpdateInfo(
    val versionCode: Int,
    val versionName: String,
    val apkUrl: String,
    val releaseNotes: String
)

/**
 * VPS sunucusundaki version.json dosyasını kontrol ederek yeni sürüm varsa
 * APK'yı indirir ve kurulumu başlatır.
 *
 * Sunucu URL: http://89.252.152.222/mathlock/dist/version.json
 * APK URL:    http://89.252.152.222/mathlock/dist/mathlock-latest.apk
 */
class UpdateChecker(private val context: Context) {

    companion object {
        private const val TAG = "UpdateChecker"
        const val VERSION_URL = "http://89.252.152.222/mathlock/dist/version.json"
        private const val CONNECT_TIMEOUT_MS = 5_000
        private const val READ_TIMEOUT_MS = 10_000
        private const val DOWNLOAD_TIMEOUT_MS = 120_000
    }

    private val executor: ExecutorService = Executors.newSingleThreadExecutor()

    /**
     * Offline mod: güncelleme kontrolü devre dışı.
     */
    fun checkForUpdate(onUpdateAvailable: (UpdateInfo) -> Unit) {
        Log.d(TAG, "Offline mod: güncelleme kontrolü atlandı")
    }

    /**
     * APK'yı cache dizinine indirir ve kurulum niyetini başlatır.
     * Tüm callback'ler arka plan thread'inden çağırılır.
     */
    fun downloadAndInstall(
        apkUrl: String,
        onProgress: (percent: Int) -> Unit,
        onComplete: () -> Unit,
        onError: (message: String) -> Unit
    ) {
        executor.execute {
            try {
                val updateDir = File(context.cacheDir, "updates")
                updateDir.mkdirs()
                val apkFile = File(updateDir, "mathlock_update.apk")

                val conn = URL(apkUrl).openConnection() as HttpURLConnection
                conn.connectTimeout = CONNECT_TIMEOUT_MS
                conn.readTimeout = DOWNLOAD_TIMEOUT_MS
                conn.connect()

                if (conn.responseCode != HttpURLConnection.HTTP_OK) {
                    onError("Sunucu yanıt kodu: ${conn.responseCode}")
                    conn.disconnect()
                    return@execute
                }

                val total = conn.contentLength
                var downloaded = 0

                conn.inputStream.use { input ->
                    FileOutputStream(apkFile).use { output ->
                        val buffer = ByteArray(8192)
                        var bytes: Int
                        while (input.read(buffer).also { bytes = it } != -1) {
                            output.write(buffer, 0, bytes)
                            downloaded += bytes
                            if (total > 0) {
                                onProgress(downloaded * 100 / total)
                            }
                        }
                    }
                }
                conn.disconnect()

                onComplete()
                installApk(apkFile)
            } catch (e: Exception) {
                Log.e(TAG, "APK indirme hatası", e)
                onError(e.message ?: "İndirme hatası")
            }
        }
    }

    private fun fetchVersionInfo(): UpdateInfo? {
        val conn = URL(VERSION_URL).openConnection() as HttpURLConnection
        conn.connectTimeout = CONNECT_TIMEOUT_MS
        conn.readTimeout = READ_TIMEOUT_MS
        conn.requestMethod = "GET"
        return try {
            if (conn.responseCode != HttpURLConnection.HTTP_OK) return null
            val json = conn.inputStream.bufferedReader().readText()
            val obj = JSONObject(json)
            UpdateInfo(
                versionCode = obj.getInt("versionCode"),
                versionName = obj.getString("versionName"),
                apkUrl = obj.getString("apkUrl"),
                releaseNotes = obj.optString("releaseNotes", "")
            )
        } catch (e: Exception) {
            Log.w(TAG, "version.json parse hatası: ${e.message}")
            null
        } finally {
            conn.disconnect()
        }
    }

    @Suppress("DEPRECATION")
    private fun getCurrentVersionCode(): Int {
        return try {
            val pi = context.packageManager.getPackageInfo(context.packageName, 0)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                pi.longVersionCode.toInt()
            } else {
                pi.versionCode
            }
        } catch (e: Exception) {
            0
        }
    }

    private fun installApk(apkFile: File) {
        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.provider",
            apkFile
        )
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(intent)
    }
}
