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

        private val PERIOD_LABELS = linkedMapOf(
            "okul_oncesi" to "Okul Öncesi (5-6 yaş)",
            "sinif_1" to "1. Sınıf (6-7 yaş)",
            "sinif_2" to "2. Sınıf (7-8 yaş)",
            "sinif_3" to "3. Sınıf (8-9 yaş)",
            "sinif_4" to "4. Sınıf (9-10 yaş)"
        )
    }

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
        val token = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/?device_token=$token")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
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
                    runOnUiThread { Toast.makeText(this, "Profiller yüklenemedi", Toast.LENGTH_SHORT).show() }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Profil yükleme hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, "Bağlantı hatası", Toast.LENGTH_SHORT).show() }
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
            tvPeriod.text = "📚 ${PERIOD_LABELS[period] ?: period}"

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
        val periodKeys = PERIOD_LABELS.keys.toList()
        val periodLabels = PERIOD_LABELS.values.toList()

        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, periodLabels)
        dropdown.setAdapter(adapter)
        dropdown.setText(periodLabels[2], false) // sinif_2 default

        AlertDialog.Builder(this)
            .setTitle("Yeni Çocuk Ekle")
            .setView(dialogView)
            .setPositiveButton("Ekle") { _, _ ->
                val name = etName.text.toString().trim()
                if (name.isEmpty()) {
                    Toast.makeText(this, "İsim boş olamaz", Toast.LENGTH_SHORT).show()
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
        val periodKeys = PERIOD_LABELS.keys.toList()
        val periodLabels = PERIOD_LABELS.values.toList()

        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, periodLabels)
        dropdown.setAdapter(adapter)
        val currentIndex = periodKeys.indexOf(currentPeriod).coerceAtLeast(0)
        dropdown.setText(periodLabels[currentIndex], false)

        AlertDialog.Builder(this)
            .setTitle("Profili Düzenle")
            .setView(dialogView)
            .setPositiveButton("Kaydet") { _, _ ->
                val name = etName.text.toString().trim()
                if (name.isEmpty()) {
                    Toast.makeText(this, "İsim boş olamaz", Toast.LENGTH_SHORT).show()
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
            Toast.makeText(this, "Son profil silinemez", Toast.LENGTH_SHORT).show()
            return
        }
        AlertDialog.Builder(this)
            .setTitle("Profili Sil")
            .setMessage("\"$name\" profilini silmek istediğinize emin misiniz?")
            .setPositiveButton("Sil") { _, _ -> deleteChild(childId) }
            .setNegativeButton("İptal", null)
            .show()
    }

    private fun createChild(name: String, period: String) {
        val token = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val body = JSONObject().apply {
                    put("device_token", token)
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
                        Toast.makeText(this, "Profil eklendi", Toast.LENGTH_SHORT).show()
                        loadProfiles()
                    } else {
                        val errMsg = try { JSONObject(responseText).optString("error", "Hata") } catch (_: Exception) { "Hata" }
                        Toast.makeText(this, errMsg, Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Profil ekleme hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, "Bağlantı hatası", Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun setActiveChild(childId: Int) {
        updateChild(childId, null, null, setActive = true)
        // Çocuk değişince soruları arka planda yeniden indir
        Thread {
            val token = accountManager.getDeviceToken()
            if (token != null) {
                val qm = QuestionManager(this)
                qm.sync(token)
                Log.d(TAG, "Aktif çocuk değişti (id=$childId), sorular yeniden indirildi: ${qm.totalCount()}")
            }
        }.start()
        setResult(RESULT_OK) // SettingsActivity'ye "yenile" sinyali
    }

    private fun updateChild(childId: Int, name: String? = null, period: String? = null, setActive: Boolean = false) {
        val token = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/detail/?device_token=$token&child_id=$childId")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "PUT"
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
                        Toast.makeText(this, "Güncelleme başarısız", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Güncelleme hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, "Bağlantı hatası", Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun deleteChild(childId: Int) {
        val token = accountManager.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/detail/?device_token=$token&child_id=$childId")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "DELETE"
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                conn.disconnect()

                runOnUiThread {
                    if (code in 200..299) {
                        Toast.makeText(this, "Profil silindi", Toast.LENGTH_SHORT).show()
                        loadProfiles()
                    } else {
                        Toast.makeText(this, "Silme başarısız", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Silme hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, "Bağlantı hatası", Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }
}
