package com.akn.mathlock

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import com.akn.mathlock.util.AccountManager
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class PerformanceReportActivity : BaseActivity() {

    companion object {
        private const val TAG = "PerfReport"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val TIMEOUT = 10000

        private val CATEGORY_COLORS = mapOf(
            "USTA" to "#4CAF50",
            "GÜVENLİ" to "#8BC34A",
            "GELİŞEN" to "#FF9800",
            "ZORLU" to "#FF5722",
            "KRİTİK" to "#F44336"
        )

    }

    private fun getPeriodLabel(period: String): String = when (period) {
        "okul_oncesi" -> getString(R.string.period_okul_oncesi)
        "sinif_1" -> getString(R.string.period_sinif_1)
        "sinif_2" -> getString(R.string.period_sinif_2)
        "sinif_3" -> getString(R.string.period_sinif_3)
        "sinif_4" -> getString(R.string.period_sinif_4)
        else -> period
    }

    private fun getTypeLabel(type: String): String = when (type) {
        "toplama" -> getString(R.string.type_toplama)
        "çıkarma" -> getString(R.string.type_cikarma)
        "çarpma" -> getString(R.string.type_carpma)
        "bölme" -> getString(R.string.type_bolme)
        "sıralama" -> getString(R.string.type_siralama)
        "eksik_sayı" -> getString(R.string.type_eksik_sayi)
        "karşılaştırma" -> getString(R.string.type_karsilastirma)
        "sayma" -> getString(R.string.type_sayma)
        "kesir" -> getString(R.string.type_kesir)
        "problem" -> getString(R.string.type_problem)
        "örüntü" -> getString(R.string.type_oruntu)
        "zaman" -> getString(R.string.type_zaman)
        "para" -> getString(R.string.type_para)
        "ondalik" -> getString(R.string.type_ondalik)
        "geometri" -> getString(R.string.type_geometri)
        else -> type
    }

    private var childName: String = "Çocuk"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_performance_report)

        childName = intent.getStringExtra("child_name") ?: getString(R.string.default_child_name)

        findViewById<View>(R.id.btnBack).setOnClickListener { finish() }
        findViewById<TextView>(R.id.tvTitle).text = getString(R.string.report_title, childName)

        findViewById<MaterialButton>(R.id.btnDashboard).setOnClickListener {
            val intent = Intent(this, StatsDashboardActivity::class.java)
            intent.putExtra("child_name", childName)
            startActivity(intent)
        }

        loadReport()
    }

    private fun loadReport() {
        val am = AccountManager(this)
        val accessToken = am.getOrRegister() ?: return
        val deviceToken = am.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/report/?device_token=$deviceToken&child_name=${java.net.URLEncoder.encode(childName, "UTF-8")}")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
                conn.setRequestProperty("Authorization", "Device $accessToken")
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                if (code in 200..299) {
                    val data = JSONObject(conn.inputStream.bufferedReader().readText())
                    conn.disconnect()
                    runOnUiThread { renderReport(data) }
                } else {
                    conn.disconnect()
                    runOnUiThread { Toast.makeText(this, getString(R.string.report_load_failed), Toast.LENGTH_SHORT).show() }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Rapor hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, getString(R.string.connection_error), Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun renderReport(data: JSONObject) {
        val child = data.getJSONObject("child")

        // Çocuk bilgileri
        findViewById<TextView>(R.id.tvChildName).text = child.getString("name")
        val period = child.getString("education_period")
        findViewById<TextView>(R.id.tvPeriod).text = getString(R.string.period_label_with_icon, getPeriodLabel(period))
        findViewById<TextView>(R.id.tvAccuracy).text = "%${child.getDouble("accuracy").toInt()}"
        findViewById<TextView>(R.id.tvTotalSolved).text = "${child.getInt("total_shown")}"
        findViewById<TextView>(R.id.tvSetsCompleted).text = "${child.getInt("sets_completed")}"

        val totalMinutes = child.getInt("total_time_seconds") / 60
        findViewById<TextView>(R.id.tvTotalTime).text = "$totalMinutes"

        // Konu bazlı performans
        val byType = data.getJSONObject("by_type")
        val container = findViewById<LinearLayout>(R.id.containerByType)
        container.removeAllViews()

        val keys = byType.keys()
        while (keys.hasNext()) {
            val tip = keys.next()
            val tipData = byType.getJSONObject(tip)
            addTypeCard(container, tip, tipData)
        }

        // AI Raporu (weekly_report)
        val weeklyReport = data.optJSONObject("weekly_report")
        if (weeklyReport != null && weeklyReport.length() > 0) {
            // Güçlü yanlar
            val strengths = weeklyReport.optJSONArray("strengths")
            if (strengths != null && strengths.length() > 0) {
                val sb = StringBuilder()
                for (i in 0 until strengths.length()) {
                    sb.append("• ${strengths.getString(i)}\n")
                }
                findViewById<TextView>(R.id.tvStrengths).text = sb.toString().trimEnd()
                findViewById<MaterialCardView>(R.id.cardStrengths).visibility = View.VISIBLE
            }

            // Gelişim alanları
            val improvements = weeklyReport.optJSONArray("improvementAreas")
            if (improvements != null && improvements.length() > 0) {
                val sb = StringBuilder()
                for (i in 0 until improvements.length()) {
                    sb.append("• ${improvements.getString(i)}\n")
                }
                findViewById<TextView>(R.id.tvImprovements).text = sb.toString().trimEnd()
                findViewById<MaterialCardView>(R.id.cardImprovements).visibility = View.VISIBLE
            }

            // Öneri
            val recommendation = weeklyReport.optString("recommendation", "")
            if (recommendation.isNotEmpty()) {
                findViewById<TextView>(R.id.tvRecommendation).text = recommendation
                findViewById<MaterialCardView>(R.id.cardRecommendation).visibility = View.VISIBLE
            }
        }
    }

    private fun addTypeCard(container: LinearLayout, tip: String, data: JSONObject) {
        val card = MaterialCardView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 8.dpToPx() }
            radius = 12f.dpToPxF()
            cardElevation = 1f.dpToPxF()
        }

        val inner = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(14.dpToPx(), 12.dpToPx(), 14.dpToPx(), 12.dpToPx())
            gravity = android.view.Gravity.CENTER_VERTICAL
        }

        val category = data.getString("category")
        val accuracy = data.getDouble("accuracy")
        val shown = data.getInt("shown")
        val correct = data.getInt("correct")
        val avgTime = data.getDouble("avgTime")
        val label = getTypeLabel(tip)

        // Kategori badge
        val badge = TextView(this).apply {
            text = category
            textSize = 10f
            setTextColor(Color.WHITE)
            val color = Color.parseColor(CATEGORY_COLORS[category] ?: "#757575")
            setBackgroundColor(color)
            setPadding(8.dpToPx(), 4.dpToPx(), 8.dpToPx(), 4.dpToPx())
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { marginEnd = 10.dpToPx() }
        }

        // Konu adı + detay
        val info = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }

        val tvLabel = TextView(this).apply {
            text = label
            textSize = 15f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }

        val tvDetail = TextView(this).apply {
            text = getString(R.string.type_card_detail, correct, shown, accuracy.toInt(), avgTime)
            textSize = 12f
            setTextColor(Color.parseColor("#757575"))
        }

        info.addView(tvLabel)
        info.addView(tvDetail)
        inner.addView(badge)
        inner.addView(info)
        card.addView(inner)
        container.addView(card)
    }

    private fun Int.dpToPx(): Int = (this * resources.displayMetrics.density).toInt()
    private fun Float.dpToPxF(): Float = this * resources.displayMetrics.density
}
