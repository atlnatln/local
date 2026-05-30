package com.akn.mathlock

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.ErrorReporter
import com.akn.mathlock.util.PreferenceManager
import com.akn.mathlock.util.QuestionManager
import com.google.android.material.button.MaterialButton
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class ChildProfilesActivity : BaseActivity() {

    companion object {
        private const val TAG = "ChildProfiles"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val TIMEOUT = 8000

    }

    private fun getPeriodLabel(period: String): String = when (period) {
        "okul_oncesi" -> getString(R.string.period_okul_oncesi_age)
        "sinif_1" -> getString(R.string.period_sinif_1_age)
        "sinif_2" -> getString(R.string.period_sinif_2_age)
        "sinif_3" -> getString(R.string.period_sinif_3_age)
        "sinif_4" -> getString(R.string.period_sinif_4_age)
        else -> period
    }

    private fun getPeriodKeys(): List<String> =
        listOf("okul_oncesi", "sinif_1", "sinif_2", "sinif_3", "sinif_4")

    private fun getPeriodLabels(): List<String> = listOf(
        getString(R.string.period_okul_oncesi_age),
        getString(R.string.period_sinif_1_age),
        getString(R.string.period_sinif_2_age),
        getString(R.string.period_sinif_3_age),
        getString(R.string.period_sinif_4_age)
    )

    private lateinit var prefManager: PreferenceManager
    private lateinit var accountManager: AccountManager
    private lateinit var profilesContainer: LinearLayout
    private lateinit var btnAddChild: MaterialButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_child_profiles)

        prefManager = PreferenceManager(this)
        accountManager = AccountManager(this)
        profilesContainer = findViewById(R.id.profilesContainer)
        btnAddChild = findViewById(R.id.btnAddChild)

        findViewById<View>(R.id.btnBack).setOnClickListener { finish() }
        btnAddChild.setOnClickListener { showAddChildDialog() }

        loadProfiles()
    }

    private fun loadProfiles() {
        var accessToken = accountManager.getAccessToken()
        if (accessToken.isNullOrBlank()) {
            accessToken = accountManager.getOrRegister()
        }
        if (accessToken.isNullOrBlank()) return
        val deviceToken = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/?device_token=$deviceToken")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
                conn.setRequestProperty("Authorization", "Device $accessToken")
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                if (code in 200..299) {
                    val response = JSONObject(conn.inputStream.bufferedReader().readText())
                    conn.disconnect()
                    val children = response.getJSONArray("children")
                    runOnUiThread { renderProfiles(children) }
                } else {
                    conn.disconnect()
                    runOnUiThread { Toast.makeText(this, getString(R.string.profiles_load_failed), Toast.LENGTH_SHORT).show() }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Profil yükleme hatası: ${e.message}")
                ErrorReporter.report(
                    category = "profile",
                    message = "Load profiles failed: ${e.message}",
                    throwable = e
                )
                runOnUiThread { Toast.makeText(this, getString(R.string.connection_error), Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun renderProfiles(children: JSONArray) {
        profilesContainer.removeAllViews()
        for (i in 0 until children.length()) {
            val child = children.getJSONObject(i)
            val view = LayoutInflater.from(this).inflate(R.layout.item_child_profile, profilesContainer, false)

            val tvName = view.findViewById<TextView>(R.id.tvChildName)
            val tvPeriod = view.findViewById<TextView>(R.id.tvEducationPeriod)
            val tvBadge = view.findViewById<TextView>(R.id.tvActiveBadge)
            val btnActive = view.findViewById<MaterialButton>(R.id.btnSetActive)
            val btnEdit = view.findViewById<MaterialButton>(R.id.btnEdit)
            val btnDelete = view.findViewById<MaterialButton>(R.id.btnDelete)
            val btnReport = view.findViewById<MaterialButton>(R.id.btnReport)

            val childId = child.getInt("id")
            val name = child.getString("name")
            val period = child.getString("education_period")
            val isActive = child.getBoolean("is_active")

            tvName.text = name
            tvPeriod.text = getString(R.string.period_label_with_icon, getPeriodLabel(period))

            if (isActive) {
                tvBadge.visibility = View.VISIBLE
                btnActive.visibility = View.GONE
                // Yerel tercihleri güncelle
                prefManager.activeChildId = childId
                prefManager.activeChildName = name
                prefManager.activeEducationPeriod = period
            } else {
                tvBadge.visibility = View.GONE
                btnActive.visibility = View.VISIBLE
            }

            btnActive.setOnClickListener { setActiveChild(childId) }
            btnEdit.setOnClickListener { showEditDialog(childId, name, period) }
            btnDelete.setOnClickListener { confirmDelete(childId, name, children.length()) }
            btnReport.setOnClickListener {
                val intent = android.content.Intent(this, PerformanceReportActivity::class.java)
                intent.putExtra("child_name", name)
                startActivity(intent)
            }

            profilesContainer.addView(view)
        }
    }

    private fun showAddChildDialog() {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_child_edit, null)
        val etName = dialogView.findViewById<EditText>(R.id.etChildName)
        val dropdown = dialogView.findViewById<AutoCompleteTextView>(R.id.spinnerPeriod)
        val periodKeys = getPeriodKeys()
        val periodLabels = getPeriodLabels()

        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, periodLabels)
        dropdown.setAdapter(adapter)
        dropdown.setText(periodLabels[2], false) // sinif_2 default

        AlertDialog.Builder(this)
            .setTitle(getString(R.string.dialog_add_child_title))
            .setView(dialogView)
            .setPositiveButton(getString(R.string.btn_add)) { _, _ ->
                val name = etName.text.toString().trim()
                if (name.isEmpty()) {
                    Toast.makeText(this, getString(R.string.name_empty_error), Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                val selectedIndex = periodLabels.indexOf(dropdown.text.toString()).coerceAtLeast(0)
                createChild(name, periodKeys[selectedIndex])
            }
            .setNegativeButton("İptal", null)
            .show()
    }

    private fun showEditDialog(childId: Int, currentName: String, currentPeriod: String) {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_child_edit, null)
        val etName = dialogView.findViewById<EditText>(R.id.etChildName)
        etName.setText(currentName)
        val dropdown = dialogView.findViewById<AutoCompleteTextView>(R.id.spinnerPeriod)
        val periodKeys = getPeriodKeys()
        val periodLabels = getPeriodLabels()

        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, periodLabels)
        dropdown.setAdapter(adapter)
        val currentIndex = periodKeys.indexOf(currentPeriod).coerceAtLeast(0)
        dropdown.setText(periodLabels[currentIndex], false)

        AlertDialog.Builder(this)
            .setTitle(getString(R.string.dialog_edit_profile_title))
            .setView(dialogView)
            .setPositiveButton(getString(R.string.btn_save)) { _, _ ->
                val name = etName.text.toString().trim()
                if (name.isEmpty()) {
                    Toast.makeText(this, getString(R.string.name_empty_error), Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                val selectedIndex = periodLabels.indexOf(dropdown.text.toString()).coerceAtLeast(0)
                updateChild(childId, name, periodKeys[selectedIndex])
            }
            .setNegativeButton("İptal", null)
            .show()
    }

    private fun confirmDelete(childId: Int, name: String, totalCount: Int) {
        if (totalCount <= 1) {
            Toast.makeText(this, getString(R.string.cannot_delete_last_profile), Toast.LENGTH_SHORT).show()
            return
        }
        AlertDialog.Builder(this)
            .setTitle(getString(R.string.dialog_delete_profile_title))
            .setMessage(getString(R.string.delete_profile_confirm, name))
            .setPositiveButton(getString(R.string.btn_delete)) { _, _ -> deleteChild(childId) }
            .setNegativeButton("İptal", null)
            .show()
    }

    private fun createChild(name: String, period: String) {
        var accessToken = accountManager.getAccessToken()
        if (accessToken.isNullOrBlank()) {
            accessToken = accountManager.getOrRegister()
        }
        if (accessToken.isNullOrBlank()) return
        val deviceToken = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Authorization", "Device $accessToken")
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val body = JSONObject().apply {
                    put("device_token", deviceToken)
                    put("name", name)
                    put("education_period", period)
                }
                conn.outputStream.bufferedWriter().use { it.write(body.toString()) }

                val code = conn.responseCode
                val responseText = if (code in 200..299) {
                    conn.inputStream.bufferedReader().readText()
                } else {
                    conn.errorStream?.bufferedReader()?.readText() ?: ""
                }
                conn.disconnect()

                runOnUiThread {
                    if (code in 200..299) {
                        Toast.makeText(this, getString(R.string.profile_added), Toast.LENGTH_SHORT).show()
                        loadProfiles()
                    } else {
                        val errMsg = try { JSONObject(responseText).optString("error", getString(R.string.error)) } catch (_: Exception) { getString(R.string.error) }
                        Toast.makeText(this, errMsg, Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Profil ekleme hatası: ${e.message}")
                ErrorReporter.report(
                    category = "profile",
                    message = "Create child failed: ${e.message}",
                    throwable = e
                )
                runOnUiThread { Toast.makeText(this, getString(R.string.connection_error), Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun setActiveChild(childId: Int) {
        updateChild(childId, null, null, setActive = true)
        // Çocuk değişince soruları arka planda yeniden indir
        Thread {
            val authToken = accountManager.getAccessToken()
            if (authToken != null) {
                val qm = QuestionManager(this)
                qm.sync(authToken)
                Log.d(TAG, "Aktif çocuk değişti (id=$childId), sorular yeniden indirildi: ${qm.totalCount()}")
            }
        }.start()
        setResult(RESULT_OK) // SettingsActivity'ye "yenile" sinyali
    }

    private fun updateChild(childId: Int, name: String? = null, period: String? = null, setActive: Boolean = false) {
        var accessToken = accountManager.getAccessToken()
        if (accessToken.isNullOrBlank()) {
            accessToken = accountManager.getOrRegister()
        }
        if (accessToken.isNullOrBlank()) return
        val deviceToken = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/detail/?device_token=$deviceToken&child_id=$childId")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "PUT"
                conn.setRequestProperty("Authorization", "Device $accessToken")
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val body = JSONObject()
                if (name != null) body.put("name", name)
                if (period != null) body.put("education_period", period)
                if (setActive) body.put("set_active", true)
                conn.outputStream.bufferedWriter().use { it.write(body.toString()) }

                val code = conn.responseCode
                conn.disconnect()

                runOnUiThread {
                    if (code in 200..299) {
                        loadProfiles()
                    } else {
                        Toast.makeText(this, getString(R.string.update_failed), Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Güncelleme hatası: ${e.message}")
                ErrorReporter.report(
                    category = "profile",
                    message = "Update child failed: ${e.message}",
                    throwable = e
                )
                runOnUiThread { Toast.makeText(this, getString(R.string.connection_error), Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun deleteChild(childId: Int) {
        var accessToken = accountManager.getAccessToken()
        if (accessToken.isNullOrBlank()) {
            accessToken = accountManager.getOrRegister()
        }
        if (accessToken.isNullOrBlank()) return
        val deviceToken = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/detail/?device_token=$deviceToken&child_id=$childId")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "DELETE"
                conn.setRequestProperty("Authorization", "Device $accessToken")
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                conn.disconnect()

                runOnUiThread {
                    if (code in 200..299) {
                        Toast.makeText(this, getString(R.string.profile_deleted), Toast.LENGTH_SHORT).show()
                        loadProfiles()
                    } else {
                        Toast.makeText(this, getString(R.string.delete_failed), Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Silme hatası: ${e.message}")
                ErrorReporter.report(
                    category = "profile",
                    message = "Delete child failed: ${e.message}",
                    throwable = e
                )
                runOnUiThread { Toast.makeText(this, getString(R.string.connection_error), Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }
}
