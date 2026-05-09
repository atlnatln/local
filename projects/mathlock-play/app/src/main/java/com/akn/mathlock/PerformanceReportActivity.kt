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

        private val PERIOD_LABELS = mapOf(
            "okul_oncesi" to "Okul Öncesi",
            "sinif_1" to "1. Sınıf",
            "sinif_2" to "2. Sınıf",
            "sinif_3" to "3. Sınıf",
            "sinif_4" to "4. Sınıf"
        )

        private val TYPE_LABELS = mapOf(
            "toplama" to "Toplama",
            "çıkarma" to "Çıkarma",
            "çarpma" to "Çarpma",
            "bölme" to "Bölme",
            "sıralama" to "Sıralama",
            "eksik_sayı" to "Eksik Sayı",
            "karşılaştırma" to "Karşılaştırma",
            "sayma" to "Sayma",
            "kesir" to "Kesir",
            "problem" to "Problem",
            "örüntü" to "Örüntü",
            "zaman" to "Zaman",
            "para" to "Para",
            "ondalik" to "Ondalık",
            "geometri" to "Geometri"
        )

        private val CATEGORY_COLORS = mapOf(
            "USTA" to "#4CAF50",
            "GÜVENLİ" to "#8BC34A",
            "GELİŞEN" to "#FF9800",
            "ZORLU" to "#FF5722",
            "KRİTİK" to "#F44336"
        )
    }

    private var childName: String = "Çocuk"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_performance_report)

        childName = intent.getStringExtra("child_name") ?: "Çocuk"

        findViewById<View>(R.id.btnBack).setOnClickListener { finish() }
        findViewById<TextView>(R.id.tvTitle).text = "$childName — Rapor"

        findViewById<MaterialButton>(R.id.btnDashboard).setOnClickListener {
            val intent = Intent(this, StatsDashboardActivity::class.java)
            intent.putExtra("child_name", childName)
            startActivity(intent)
        }

        loadReport()
    }

    private fun loadReport() {
        val am = AccountManager(this)
        am.getOrRegister() // ensure registered
        val deviceToken = am.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/report/?device_token=$deviceToken&child_name=${java.net.URLEncoder.encode(childName, "UTF-8")}")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                if (code in 200..299) {
                    val data = JSONObject(conn.inputStream.bufferedReader().readText())
                    conn.disconnect()
                    runOnUiThread { renderReport(data) }
                } else {
                    conn.disconnect()
                    runOnUiThread { Toast.makeText(this, "Rapor yüklenemedi", Toast.LENGTH_SHORT).show() }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Rapor hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, "Bağlantı hatası", Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun renderReport(data: JSONObject) {
        val child = data.getJSONObject("child")

        // Çocuk bilgileri
        findViewById<TextView>(R.id.tvChildName).text = child.getString("name")
        val period = child.getString("education_period")
        findViewById<TextView>(R.id.tvPeriod).text = "📚 ${PERIOD_LABELS[period] ?: period}"
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
        val label = TYPE_LABELS[tip] ?: tip

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
            text = "$correct/$shown doğru • %${accuracy.toInt()} • ${avgTime}s"
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
