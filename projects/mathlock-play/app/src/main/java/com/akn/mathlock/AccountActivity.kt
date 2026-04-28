package com.akn.mathlock

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.inputmethod.InputMethodManager
import com.akn.mathlock.databinding.ActivityAccountBinding
import com.akn.mathlock.util.AccountManager
import com.akn.mathlock.util.BillingHelper
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.snackbar.Snackbar

class AccountActivity : BaseActivity(), BillingHelper.BillingListener {

    private lateinit var binding: ActivityAccountBinding
    private lateinit var accountManager: AccountManager
    private lateinit var billingHelper: BillingHelper
    private var billingReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAccountBinding.inflate(layoutInflater)
        setContentView(binding.root)

        accountManager = AccountManager(this)
        billingHelper = BillingHelper(this, this)

        binding.btnBack.setOnClickListener { finish() }
        binding.btnRegister.setOnClickListener { onRegisterClick() }
        binding.btnChangeEmail.setOnClickListener { showChangeEmailDialog() }

        binding.cardBuy1.setOnClickListener { onBuyCredit(1, "kredi_1") }
        binding.cardBuy3.setOnClickListener { onBuyCredit(3, "kredi_3") }
        binding.cardBuy5.setOnClickListener { onBuyCredit(5, "kredi_5") }

        billingHelper.connect()

        refreshUI()
        refreshFromServer()
    }

    override fun onDestroy() {
        billingHelper.disconnect()
        super.onDestroy()
    }

    companion object {
        private const val TAG = "AccountActivity"
        private const val FREE_TEST_EMAIL = "atalanakin@gmail.com"
    }

    private fun refreshUI() {
        val email = accountManager.getEmail()
        val hasEmail = !email.isNullOrBlank()
        val credits = accountManager.getCachedCredits()
        val freeUsed = accountManager.isFreeSetUsed()
        val token = accountManager.getDeviceToken()

        if (hasEmail) {
            // Kayıtlı kullanıcı
            binding.tvAvatarEmoji.text = "✅"
            binding.tvAccountTitle.text = email
            binding.tvAccountSubtitle.text = "Hesabınız aktif"
            binding.tvAccountSubtitle.setTextColor(getColor(R.color.correct_green))

            binding.cardRegister.visibility = View.GONE
            binding.cardAccountInfo.visibility = View.VISIBLE

            binding.tvEmail.text = email
            binding.tvDeviceId.text = token?.take(12)?.plus("…") ?: "—"
        } else {
            // Kayıtsız kullanıcı
            binding.tvAvatarEmoji.text = "👤"
            binding.tvAccountTitle.text = "Hesap Oluştur"
            binding.tvAccountSubtitle.text = "Email ile kayıt olarak hesabınızı koruyun"
            binding.tvAccountSubtitle.setTextColor(getColor(R.color.on_surface_secondary))

            binding.cardRegister.visibility = View.VISIBLE
            binding.cardAccountInfo.visibility = View.GONE
        }

        // Kredi bilgisi
        binding.tvCredits.text = credits.toString()
        binding.tvCreditDetail.text = "Toplam kullanılan: ${accountManager.getCachedCredits()} kredi"
        binding.tvFreeSetStatus.text = if (freeUsed) {
            "🎁 Ücretsiz set kullanıldı"
        } else {
            "🎁 Ücretsiz: 50 soru + sınırsız sayı oyunu + 12 sayı yolculuğu"
        }

        // Kredi paketleri: email yoksa gizle
        binding.cardPackages.visibility = if (hasEmail) View.VISIBLE else View.GONE
    }

    private fun refreshFromServer() {
        Thread {
            val token = accountManager.getOrRegister()
            if (token != null) {
                accountManager.refreshCredits()
            }
            runOnUiThread { refreshUI() }
        }.start()
    }

    private fun onRegisterClick() {
        val email = binding.etEmail.text.toString().trim()

        if (email.isBlank()) {
            binding.tilEmail.error = "Email adresi gerekli"
            return
        }
        if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            binding.tilEmail.error = "Geçerli bir email girin"
            return
        }
        binding.tilEmail.error = null

        // Klavyeyi kapat
        val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        imm.hideSoftInputFromWindow(binding.etEmail.windowToken, 0)

        binding.btnRegister.isEnabled = false
        binding.btnRegister.text = "Kaydediliyor…"

        Thread {
            val result = accountManager.registerEmail(email)
            runOnUiThread {
                binding.btnRegister.isEnabled = true
                binding.btnRegister.text = "Kayıt Ol"
                when (result) {
                    is AccountManager.RegisterEmailResult.Success -> {
                        Snackbar.make(binding.root, "✅ Hesap oluşturuldu!", Snackbar.LENGTH_LONG).show()
                        refreshUI()
                    }
                    is AccountManager.RegisterEmailResult.Recovered -> {
                        Snackbar.make(binding.root, "✅ Hesabınız yüklendi! (${result.credits} kredi)", Snackbar.LENGTH_LONG).show()
                        refreshUI()
                    }
                    is AccountManager.RegisterEmailResult.Error -> {
                        Snackbar.make(binding.root, "❌ ${result.message}", Snackbar.LENGTH_LONG)
                            .setBackgroundTint(getColor(R.color.wrong_red))
                            .setTextColor(getColor(android.R.color.white))
                            .show()
                    }
                }
            }
        }.start()
    }

    private fun showChangeEmailDialog() {
        val container = android.widget.FrameLayout(this).apply {
            setPadding(64, 16, 64, 0)
        }
        val input = com.google.android.material.textfield.TextInputEditText(this).apply {
            hint = "yeni@email.com"
            inputType = android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS or
                        android.text.InputType.TYPE_CLASS_TEXT
            accountManager.getEmail()?.let { setText(it) }
            setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 16f)
        }
        container.addView(input, android.widget.FrameLayout.LayoutParams(
            android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
            android.widget.FrameLayout.LayoutParams.WRAP_CONTENT
        ))

        val dialog = MaterialAlertDialogBuilder(this)
            .setTitle("Email Değiştir")
            .setView(container)
            .setPositiveButton("Kaydet", null)
            .setNegativeButton("İptal", null)
            .create()

        dialog.setOnShowListener {
            dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val email = input.text.toString().trim()
                if (email.isBlank()) {
                    input.error = "Email adresi boş olamaz"
                    return@setOnClickListener
                }
                if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                    input.error = "Geçerli bir email girin"
                    return@setOnClickListener
                }
                dialog.dismiss()
                registerEmailInBackground(email)
            }
            input.requestFocus()
            val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
            imm.showSoftInput(input, InputMethodManager.SHOW_IMPLICIT)
        }
        dialog.show()
    }

    private fun registerEmailInBackground(email: String) {
        Snackbar.make(binding.root, "Kaydediliyor…", Snackbar.LENGTH_SHORT).show()
        Thread {
            val result = accountManager.registerEmail(email)
            runOnUiThread {
                when (result) {
                    is AccountManager.RegisterEmailResult.Success -> {
                        Snackbar.make(binding.root, "✅ Email güncellendi!", Snackbar.LENGTH_LONG).show()
                        refreshUI()
                    }
                    is AccountManager.RegisterEmailResult.Recovered -> {
                        Snackbar.make(binding.root, "✅ Hesabınız yüklendi! (${result.credits} kredi)", Snackbar.LENGTH_LONG).show()
                        refreshUI()
                    }
                    is AccountManager.RegisterEmailResult.Error -> {
                        Snackbar.make(binding.root, "❌ ${result.message}", Snackbar.LENGTH_LONG)
                            .setBackgroundTint(getColor(R.color.wrong_red))
                            .setTextColor(getColor(android.R.color.white))
                            .show()
                    }
                }
            }
        }.start()
    }

    private fun onBuyCredit(amount: Int, productId: String) {
        val email = accountManager.getEmail()
        if (email.isNullOrBlank()) {
            Snackbar.make(binding.root, "Önce email ile kayıt olun", Snackbar.LENGTH_SHORT).show()
            return
        }

        // TODO: Test bittikten sonra FREE_TEST_EMAIL kontrolünü geri aç
        // if (email == FREE_TEST_EMAIL) {
        //     // Test kullanıcısı: ücretsiz kredi
        //     MaterialAlertDialogBuilder(this)
        //         .setTitle("🎁 Test Hesabı")
        //         .setMessage("$amount kredi test hesabınıza ücretsiz eklenecek.")
        //         .setPositiveButton("Ekle") { _, _ -> purchaseDebugCredits(amount, productId) }
        //         .setNegativeButton("İptal", null)
        //         .show()
        //     return
        // }

        // Gerçek Google Play satın alma
        if (!billingReady) {
            Snackbar.make(binding.root, "Faturalandırma servisi hazırlanıyor…", Snackbar.LENGTH_SHORT).show()
            billingHelper.connect()
            return
        }

        val formattedPrice = billingHelper.getFormattedPrice(productId)
        val priceText = formattedPrice ?: when (amount) {
            1 -> "₺10"
            3 -> "₺25"
            5 -> "₺40"
            else -> "₺?"
        }

        MaterialAlertDialogBuilder(this)
            .setTitle("🛒 $amount Kredi — $priceText")
            .setMessage("Google Play üzerinden $priceText ödeme yaparak $amount kredi satın alacaksınız.")
            .setPositiveButton("Satın Al") { _, _ ->
                billingHelper.launchPurchase(productId)
            }
            .setNegativeButton("İptal", null)
            .show()
    }

    // — BillingHelper.BillingListener callbacks —

    override fun onBillingReady() {
        billingReady = true
        Log.d(TAG, "Billing ready")
    }

    override fun onBillingUnavailable(message: String) {
        billingReady = false
        Log.w(TAG, "Billing unavailable: $message")
    }

    override fun onProductDetailsReady(details: Map<String, ProductDetails>) {
        Log.d(TAG, "Product details ready: ${details.keys}")
        // Fiyatları Google Play'den çekip kartlarda göster — kullanıcı gerçek fiyatı görür
        runOnUiThread {
            details["kredi_1"]?.oneTimePurchaseOfferDetails?.formattedPrice?.let { price ->
                binding.tvPrice1.text = price
            }
            details["kredi_3"]?.oneTimePurchaseOfferDetails?.let { offer ->
                binding.tvPrice3.text = offer.formattedPrice
                // Kredi başı fiyat: micros / 3
                val perUnit = offer.priceAmountMicros / 3_000_000.0
                binding.tvPrice3PerUnit.text = "%.2f/kredi".format(perUnit)
                    .let { priceStr ->
                        val currency = offer.formattedPrice.firstOrNull { !it.isDigit() && it != ',' && it != '.' } ?: '₺'
                        "$currency$priceStr"
                    }
            }
            details["kredi_5"]?.oneTimePurchaseOfferDetails?.let { offer ->
                binding.tvPrice5.text = offer.formattedPrice
                val perUnit = offer.priceAmountMicros / 5_000_000.0
                binding.tvPrice5PerUnit.text = "%.2f/kredi".format(perUnit)
                    .let { priceStr ->
                        val currency = offer.formattedPrice.firstOrNull { !it.isDigit() && it != ',' && it != '.' } ?: '₺'
                        "$currency$priceStr"
                    }
            }
        }
    }

    override fun onPurchaseSuccess(purchase: Purchase) {
        Snackbar.make(binding.root, "Satın alma doğrulanıyor…", Snackbar.LENGTH_SHORT).show()
        verifyAndConsumePurchase(purchase)
    }

    override fun onPurchaseError(message: String) {
        if (message != "Satın alma iptal edildi") {
            Snackbar.make(binding.root, "❌ $message", Snackbar.LENGTH_LONG)
                .setBackgroundTint(getColor(R.color.wrong_red))
                .setTextColor(getColor(android.R.color.white))
                .show()
        }
    }

    private fun verifyAndConsumePurchase(purchase: Purchase) {
        val token = accountManager.getDeviceToken() ?: return

        // İlk satın alınan ürünün product_id'sini al
        val productId = purchase.products.firstOrNull() ?: return

        Thread {
            try {
                val url = java.net.URL("https://mathlock.com.tr/api/mathlock/purchase/verify/")
                val conn = url.openConnection() as java.net.HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.connectTimeout = 15000
                conn.readTimeout = 15000

                val body = org.json.JSONObject().apply {
                    put("device_token", token)
                    put("purchase_token", purchase.purchaseToken)
                    put("product_id", productId)
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
                        // Backend doğruladı — şimdi Google Play'de consume et
                        billingHelper.consumePurchase(purchase)

                        val resp = org.json.JSONObject(responseText)
                        val added = resp.optInt("credits_added", 0)
                        val total = resp.optInt("total_credits", 0)
                        Snackbar.make(binding.root, "✅ $added kredi eklendi! Toplam: $total", Snackbar.LENGTH_LONG).show()
                        refreshUI()
                        // Kredi bilgisini arka planda güncelle
                        Thread { accountManager.refreshCredits(); runOnUiThread { refreshUI() } }.start()
                    } else {
                        val error = try {
                            org.json.JSONObject(responseText).optString("error", "Doğrulama hatası")
                        } catch (_: Exception) { "Doğrulama hatası" }
                        Snackbar.make(binding.root, "❌ $error", Snackbar.LENGTH_LONG)
                            .setBackgroundTint(getColor(R.color.wrong_red))
                            .setTextColor(getColor(android.R.color.white))
                            .show()
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Verify purchase failed", e)
                runOnUiThread {
                    Snackbar.make(binding.root, "❌ Bağlantı hatası", Snackbar.LENGTH_LONG)
                        .setBackgroundTint(getColor(R.color.wrong_red))
                        .setTextColor(getColor(android.R.color.white))
                        .show()
                }
            }
        }.start()
    }

    private fun purchaseDebugCredits(amount: Int, productId: String) {
        val token = accountManager.getDeviceToken() ?: return
        Snackbar.make(binding.root, "Kredi ekleniyor…", Snackbar.LENGTH_SHORT).show()

        Thread {
            try {
                val url = java.net.URL("https://mathlock.com.tr/api/mathlock/purchase/verify/")
                val conn = url.openConnection() as java.net.HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.connectTimeout = 8000
                conn.readTimeout = 8000

                val debugToken = "DEBUG_TEST_TOKEN_${System.currentTimeMillis()}"
                val body = org.json.JSONObject().apply {
                    put("device_token", token)
                    put("purchase_token", debugToken)
                    put("product_id", productId)
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
                        val resp = org.json.JSONObject(responseText)
                        val added = resp.optInt("credits_added", 0)
                        val total = resp.optInt("total_credits", 0)
                        Snackbar.make(binding.root, "✅ $added kredi eklendi! Toplam: $total", Snackbar.LENGTH_LONG).show()
                        accountManager.refreshCredits()
                        refreshUI()
                        refreshFromServer()
                    } else {
                        val error = try {
                            org.json.JSONObject(responseText).optString("error", "Hata oluştu")
                        } catch (_: Exception) { "Hata oluştu" }
                        Snackbar.make(binding.root, "❌ $error", Snackbar.LENGTH_LONG)
                            .setBackgroundTint(getColor(R.color.wrong_red))
                            .setTextColor(getColor(android.R.color.white))
                            .show()
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Snackbar.make(binding.root, "❌ Bağlantı hatası", Snackbar.LENGTH_LONG)
                        .setBackgroundTint(getColor(R.color.wrong_red))
                        .setTextColor(getColor(android.R.color.white))
                        .show()
                }
            }
        }.start()
    }
}
