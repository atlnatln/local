package com.akn.mathlock.util

import android.app.Activity
import android.util.Log
import com.android.billingclient.api.*
import com.android.billingclient.api.BillingClient.BillingResponseCode

class BillingHelper(
    private val activity: Activity,
    private val listener: BillingListener
) : PurchasesUpdatedListener {

    interface BillingListener {
        fun onProductDetailsReady(details: Map<String, ProductDetails>)
        fun onPurchaseSuccess(purchase: Purchase)
        fun onPurchaseError(message: String)
        fun onBillingReady()
        fun onBillingUnavailable(message: String)
    }

    private var billingClient: BillingClient? = null
    private val productDetailsMap = mutableMapOf<String, ProductDetails>()

    companion object {
        private const val TAG = "BillingHelper"
        val PRODUCT_IDS = listOf("kredi_1", "kredi_3", "kredi_5")
    }

    fun connect() {
        val pendingParams = PendingPurchasesParams.newBuilder()
            .enableOneTimeProducts()
            .build()

        billingClient = BillingClient.newBuilder(activity)
            .setListener(this)
            .enablePendingPurchases(pendingParams)
            .build()

        billingClient?.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    Log.d(TAG, "BillingClient connected")
                    listener.onBillingReady()
                    queryPurchases() // Önceki consume edilmemiş satın almaları kontrol et
                    queryProducts()
                } else {
                    Log.e(TAG, "BillingClient setup failed: ${result.debugMessage}")
                    listener.onBillingUnavailable("Faturalandırma servisi başlatılamadı")
                }
            }

            override fun onBillingServiceDisconnected() {
                Log.w(TAG, "BillingClient disconnected")
            }
        })
    }

    fun disconnect() {
        billingClient?.endConnection()
        billingClient = null
    }

    private fun queryPurchases() {
        val client = billingClient ?: return
        val params = QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.INAPP)
            .build()

        client.queryPurchasesAsync(params) { result, purchasesList ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK && purchasesList != null) {
                for (purchase in purchasesList) {
                    if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
                        Log.d(TAG, "Önceki satın alma bulundu: ${purchase.products.firstOrNull()}")
                        handlePurchase(purchase)
                    }
                }
            }
        }
    }

    private fun queryProducts() {
        val productList = PRODUCT_IDS.map { productId ->
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(productId)
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        }

        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(productList)
            .build()

        billingClient?.queryProductDetailsAsync(params) { result, detailsList ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK && detailsList != null) {
                productDetailsMap.clear()
                for (details in detailsList) {
                    productDetailsMap[details.productId] = details
                }
                Log.d(TAG, "Products loaded: ${productDetailsMap.keys}")
                activity.runOnUiThread {
                    listener.onProductDetailsReady(productDetailsMap.toMap())
                }
            } else {
                Log.e(TAG, "queryProductDetails failed: ${result.debugMessage}")
            }
        }
    }

    fun launchPurchase(productId: String) {
        val client = billingClient
        if (client == null || !client.isReady) {
            listener.onPurchaseError("Faturalandırma servisi hazır değil")
            return
        }

        val productDetails = productDetailsMap[productId]
        if (productDetails == null) {
            listener.onPurchaseError("Ürün bulunamadı: $productId")
            return
        }

        val productDetailsParams = BillingFlowParams.ProductDetailsParams.newBuilder()
            .setProductDetails(productDetails)
            .build()

        val billingFlowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(productDetailsParams))
            .build()

        val result = client.launchBillingFlow(activity, billingFlowParams)
        if (result.responseCode != BillingClient.BillingResponseCode.OK) {
            Log.e(TAG, "launchBillingFlow failed: ${result.debugMessage}")
            listener.onPurchaseError("Satın alma başlatılamadı")
        }
    }

    override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
        when (result.responseCode) {
            BillingClient.BillingResponseCode.OK -> {
                if (purchases != null) {
                    for (purchase in purchases) {
                        handlePurchase(purchase)
                    }
                }
            }
            BillingClient.BillingResponseCode.USER_CANCELED -> {
                Log.d(TAG, "User canceled purchase")
                activity.runOnUiThread {
                    listener.onPurchaseError("Satın alma iptal edildi")
                }
            }
            else -> {
                Log.e(TAG, "Purchase error: ${result.responseCode} - ${result.debugMessage}")
                activity.runOnUiThread {
                    listener.onPurchaseError("Satın alma hatası: ${result.debugMessage}")
                }
            }
        }
    }

    private fun handlePurchase(purchase: Purchase) {
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            // Satın alma başarılı — önce backend'e gönder, sonra consume et
            activity.runOnUiThread {
                listener.onPurchaseSuccess(purchase)
            }
        }
    }

    fun consumePurchase(purchase: Purchase) {
        val consumeParams = ConsumeParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()

        billingClient?.consumeAsync(consumeParams) { result, _ ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                Log.d(TAG, "Purchase consumed successfully")
            } else {
                Log.e(TAG, "Consume failed: ${result.debugMessage}")
            }
        }
    }

    fun getFormattedPrice(productId: String): String? {
        val details = productDetailsMap[productId] ?: return null
        return details.oneTimePurchaseOfferDetails?.formattedPrice
    }

    fun isReady(): Boolean = billingClient?.isReady == true
}
