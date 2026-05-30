package com.akn.mathlock

import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
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

class StatsDashboardActivity : BaseActivity() {

    companion object {
        private const val TAG = "StatsDashboard"
        private const val API_BASE = "https://mathlock.com.tr/api/mathlock"
        private const val TIMEOUT = 10000

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
        setContentView(R.layout.activity_stats_dashboard)

        childName = intent.getStringExtra("child_name") ?: getString(R.string.default_child_name)

        findViewById<View>(R.id.btnBack).setOnClickListener { finish() }
        findViewById<TextView>(R.id.tvTitle).text = getString(R.string.stats_title, childName)

        loadStats()
    }

    private fun loadStats() {
        val am = AccountManager(this)
        val accessToken = am.getOrRegister() ?: return
        val deviceToken = am.getDeviceToken() ?: return
        Thread {
            try {
                val url = URL("$API_BASE/children/stats-history/?device_token=$deviceToken&child_name=${java.net.URLEncoder.encode(childName, "UTF-8")}")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
                conn.setRequestProperty("Authorization", "Device $accessToken")
                conn.connectTimeout = TIMEOUT
                conn.readTimeout = TIMEOUT

                val code = conn.responseCode
                if (code in 200..299) {
                    val data = JSONObject(conn.inputStream.bufferedReader().readText())
                    conn.disconnect()
                    runOnUiThread { renderStats(data) }
                } else {
                    conn.disconnect()
                    runOnUiThread { Toast.makeText(this, getString(R.string.stats_load_failed), Toast.LENGTH_SHORT).show() }
                }
            } catch (e: Exception) {
                Log.w(TAG, "İstatistik hatası: ${e.message}")
                runOnUiThread { Toast.makeText(this, getString(R.string.connection_error), Toast.LENGTH_SHORT).show() }
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

        val dataSet = BarDataSet(entries, getString(R.string.chart_label_solved)).apply {
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
            labels.add(getTypeLabel(tip))

            val color = when {
                accuracy >= 85 -> Color.parseColor("#4CAF50")
                accuracy >= 60 -> Color.parseColor("#FF9800")
                accuracy >= 40 -> Color.parseColor("#FF5722")
                else -> Color.parseColor("#F44336")
            }
            colors.add(color)
        }

        val dataSet = BarDataSet(entries, getString(R.string.chart_label_accuracy)).apply {
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
