package com.akn.mathlock

import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.akn.mathlock.util.AccountManager
import com.github.mikephil.charting.charts.BarChart
import com.github.mikephil.charting.charts.HorizontalBarChart
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.BarData
import com.github.mikephil.charting.data.BarDataSet
import com.github.mikephil.charting.data.BarEntry
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class StatsDashboardActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "StatsDashboard"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val TIMEOUT = 10000

        private val TYPE_LABELS = mapOf(
            "toplama" to "Toplama",
            "cikarma" to "Çıkarma",
            "carpma" to "Çarpma",
            "bolme" to "Bölme",
            "siralama" to "Sıralama",
            "eksik_sayi" to "Eksik Sayı",
            "karsilastirma" to "Karşılaştırma",
            "sayma" to "Sayma",
            "kesir_giris" to "Kesir",
            "zaman" to "Zaman",
            "para" to "Para",
            "ondalik" to "Ondalık",
            "geometri" to "Geometri"
        )
    }

    private var childName: String = "Çocuk"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_stats_dashboard)

        childName = intent.getStringExtra("child_name") ?: "Çocuk"

        findViewById<View>(R.id.btnBack).setOnClickListener { finish() }
        findViewById<TextView>(R.id.tvTitle).text = "$childName — İstatistik"

        loadStats()
    }

    private fun loadStats() {
        val token = AccountManager(this).getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/stats-history/?device_token=$token&child_name=${java.net.URLEncoder.encode(childName, "UTF-8")}")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                if (code in 200..299) {
                    val data = JSONObject(conn.inputStream.bufferedReader().readText())
                    conn.disconnect()
                    runOnUiThread { renderStats(data) }
                } else {
                    conn.disconnect()
                    runOnUiThread { Toast.makeText(this, "İstatistikler yüklenemedi", Toast.LENGTH_SHORT).show() }
                }
            } catch (e: Exception) {
                Log.w(TAG, "İstatistik hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, "Bağlantı hatası", Toast.LENGTH_SHORT).show() }
            }
        }.start()
    }

    private fun renderStats(data: JSONObject) {
        // Özet kartları
        findViewById<TextView>(R.id.tvStreak).text = "${data.getInt("streak_days")}"
        findViewById<TextView>(R.id.tvAccuracy).text = "%${data.getDouble("accuracy").toInt()}"
        findViewById<TextView>(R.id.tvTotalTime).text = "${data.getDouble("total_time_minutes").toInt()}"

        // Günlük çözüm grafiği
        val dailyStats = data.optJSONObject("daily") ?: JSONObject()
        setupDailyChart(dailyStats)

        // Konu bazlı başarı grafiği
        val byType = data.optJSONObject("by_type") ?: JSONObject()
        setupByTypeChart(byType)
    }

    private fun setupDailyChart(dailyStats: JSONObject) {
        val chart = findViewById<BarChart>(R.id.chartDaily)
        val entries = mutableListOf<BarEntry>()
        val labels = mutableListOf<String>()
        val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.US)
        val labelFormat = SimpleDateFormat("dd/MM", Locale.US)

        val cal = Calendar.getInstance()
        cal.add(Calendar.DAY_OF_YEAR, -13) // Son 14 gün

        for (i in 0 until 14) {
            val dateStr = dateFormat.format(cal.time)
            val dayData = dailyStats.optJSONObject(dateStr)
            val solved = dayData?.optInt("solved", 0) ?: 0
            entries.add(BarEntry(i.toFloat(), solved.toFloat()))
            labels.add(labelFormat.format(cal.time))
            cal.add(Calendar.DAY_OF_YEAR, 1)
        }

        val dataSet = BarDataSet(entries, "Çözülen Soru").apply {
            color = Color.parseColor("#4CAF50")
            valueTextSize = 10f
            valueTextColor = Color.parseColor("#212121")
        }

        chart.apply {
            this.data = BarData(dataSet)
            description.isEnabled = false
            legend.isEnabled = false
            setFitBars(true)

            xAxis.apply {
                position = XAxis.XAxisPosition.BOTTOM
                valueFormatter = IndexAxisValueFormatter(labels)
                granularity = 1f
                setDrawGridLines(false)
                textSize = 9f
                labelRotationAngle = -45f
            }

            axisLeft.apply {
                axisMinimum = 0f
                granularity = 1f
                textSize = 10f
            }

            axisRight.isEnabled = false
            animateY(600)
            invalidate()
        }
    }

    private fun setupByTypeChart(byType: JSONObject) {
        val chart = findViewById<HorizontalBarChart>(R.id.chartByType)
        val entries = mutableListOf<BarEntry>()
        val labels = mutableListOf<String>()
        val colors = mutableListOf<Int>()

        val keys = byType.keys().asSequence().toList()
        if (keys.isEmpty()) {
            chart.visibility = View.GONE
            return
        }

        keys.forEachIndexed { index, tip ->
            val tipData = byType.getJSONObject(tip)
            val accuracy = tipData.getDouble("accuracy").toFloat()
            entries.add(BarEntry(index.toFloat(), accuracy))
            labels.add(TYPE_LABELS[tip] ?: tip)

            val color = when {
                accuracy >= 85 -> Color.parseColor("#4CAF50")
                accuracy >= 60 -> Color.parseColor("#FF9800")
                accuracy >= 40 -> Color.parseColor("#FF5722")
                else -> Color.parseColor("#F44336")
            }
            colors.add(color)
        }

        val dataSet = BarDataSet(entries, "Başarı %").apply {
            this.colors = colors
            valueTextSize = 11f
            valueTextColor = Color.parseColor("#212121")
        }

        chart.apply {
            this.data = BarData(dataSet)
            description.isEnabled = false
            legend.isEnabled = false
            setFitBars(true)

            xAxis.apply {
                position = XAxis.XAxisPosition.BOTTOM
                valueFormatter = IndexAxisValueFormatter(labels)
                granularity = 1f
                setDrawGridLines(false)
                textSize = 11f
            }

            axisLeft.apply {
                axisMinimum = 0f
                axisMaximum = 100f
                granularity = 20f
                textSize = 10f
            }

            axisRight.isEnabled = false
            animateX(600)
            invalidate()
        }
    }
}
