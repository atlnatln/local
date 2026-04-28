package com.akn.mathlock

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import com.akn.mathlock.databinding.ActivityDisclosureBinding
import com.akn.mathlock.util.PreferenceManager

/**
 * Google Play politikası gereği zorunlu "Prominent Disclosure" ekranı.
 * İlk kurulumda gösterilir. Kullanıcı kabul etmeden uygulamayı kullanamaz.
 *
 * Açıklanan veri kullanımları:
 * - Uygulama listesi (QUERY_ALL_PACKAGES): hangi uygulamaların kilitlenmesi gerektiğini belirlemek için
 * - Kullanım istatistikleri (PACKAGE_USAGE_STATS): ön plandaki uygulamayı tespit etmek için
 * - Overlay (SYSTEM_ALERT_WINDOW): soru ekranını ve geri sayım göstergesini göstermek için
 * - Matematik performans verisi: güvenli bağlantı (HTTPS) üzerinden AI soru kalitesini iyileştirmek için
 */
class DisclosureActivity : BaseActivity() {

    private lateinit var binding: ActivityDisclosureBinding
    private lateinit var prefManager: PreferenceManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDisclosureBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)

        binding.btnAccept.setOnClickListener {
            prefManager.isDisclosureAccepted = true
            prefManager.isFirstRun = false
            finish()
        }

        binding.btnDecline.setOnClickListener {
            Toast.makeText(
                this,
                "MathLock, ebeveyn denetimi için bu izinlere ihtiyaç duyar. Kabul etmeden devam edilemez.",
                Toast.LENGTH_LONG
            ).show()
        }

        binding.btnPrivacyPolicy.setOnClickListener {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://mathlock.com.tr/privacy"))
            startActivity(intent)
        }
    }

    override fun onBackPressed() {
        // Disclosure kabul edilmeden geri basılamaz
        if (!prefManager.isDisclosureAccepted) {
            Toast.makeText(this, "Lütfen veri kullanım bildirimini okuyup kabul edin.", Toast.LENGTH_SHORT).show()
            return
        }
        super.onBackPressed()
    }
}
