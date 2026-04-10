package com.akn.mathlock

import com.akn.mathlock.util.QuestionManager
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.json.JSONArray
import org.json.JSONObject

/**
 * QuestionManager'ın kredi sistemi davranışı için birim testler.
 *
 * Context gerektirmeyen saf mantık testleri.
 * Gerçek `QuestionManager` Context ile çalışır ancak
 * iş mantığını ayrı test edilebilir yardımcılarla doğrularız.
 */
class QuestionManagerLogicTest {

    /**
     * QuestionManager'ın döngü mantığını simüle eden minimal sınıf.
     * Gerçek implementasyondaki hesaplama akışını test eder.
     */
    class FakeQuestionSet(private val count: Int) {
        private var index = 0
        var isRepeating = false

        fun nextOrRepeat(): Int? {
            if (count == 0) return null
            if (!isRepeating && index >= count) return null
            if (isRepeating && index >= count) index = 0
            return index++
        }

        fun isSetComplete() = !isRepeating && index >= count
        fun startRepeating() { isRepeating = true; index = 0 }
        fun solvedCount() = index
    }

    @Test
    fun `50 soruda set tamamlanmış sayılır`() {
        val set = FakeQuestionSet(50)
        repeat(50) { assertNotNull(set.nextOrRepeat()) }
        assertTrue("50 soru → isSetComplete = true", set.isSetComplete())
    }

    @Test
    fun `set tamamlanmadan isSetComplete false döner`() {
        val set = FakeQuestionSet(50)
        repeat(49) { set.nextOrRepeat() }
        assertFalse("49/50 → isSetComplete = false", set.isSetComplete())
    }

    @Test
    fun `tekrar modunda sorular sonsuz döngüde tekrar eder`() {
        val set = FakeQuestionSet(50)
        repeat(50) { set.nextOrRepeat() }  // seti bitir
        set.startRepeating()

        // 100 soru daha isteyebilmeliyiz (2 tam döngü)
        repeat(100) {
            val q = set.nextOrRepeat()
            assertNotNull("Tekrar modunda null dönmemeli ($it)", q)
        }
    }

    @Test
    fun `tekrar modunda isSetComplete false kalır`() {
        val set = FakeQuestionSet(50)
        repeat(50) { set.nextOrRepeat() }
        set.startRepeating()
        set.nextOrRepeat()
        assertFalse("Tekrar modu aktifken set complete değil", set.isSetComplete())
    }

    @Test
    fun `boş set null döner`() {
        val set = FakeQuestionSet(0)
        assertNull("Boş set → null", set.nextOrRepeat())
    }
}

/**
 * Kredi sistemi karar mantığı testleri.
 * Gerçek network/billing çağrısı yok — saf iş mantığı.
 */
class CreditSystemLogicTest {

    // Kredi sisteminin çekirdek karar mantığını simüle eder
    private fun shouldUseFreeSet(freeSetUsed: Boolean) = !freeSetUsed
    private fun canUseCredit(balance: Int) = balance > 0
    private fun creditAfterUse(balance: Int) = if (balance > 0) balance - 1 else balance
    private fun creditsFor(productId: String): Int = when (productId) {
        "kredi_1" -> 1
        "kredi_5" -> 5
        "kredi_10" -> 10
        else -> 0
    }

    @Test
    fun `ilk kullanım her zaman ücretsiz olmalı`() {
        assertTrue("Ücretsiz set kullanılmadıysa ücretsiz olmalı", shouldUseFreeSet(false))
    }

    @Test
    fun `ikinci kullanımda ücretsiz set sunulmamalı`() {
        assertFalse("Ücretsiz set zaten kullanıldıysa tekrar ücretsiz olmamalı", shouldUseFreeSet(true))
    }

    @Test
    fun `kredi yokken kredi kullanılamaz`() {
        assertFalse("Balance=0 → use credit false", canUseCredit(0))
    }

    @Test
    fun `kredi varken kullanım başarılı`() {
        assertTrue("Balance=5 → use credit true", canUseCredit(5))
    }

    @Test
    fun `kredi kullanımı bakiyeyi 1 azaltır`() {
        assertEquals("10 - 1 = 9", 9, creditAfterUse(10))
    }

    @Test
    fun `sıfır krediyle kullanım bakiyeyi değiştirmez`() {
        assertEquals("0 korunur", 0, creditAfterUse(0))
    }

    @Test
    fun `kredi_1 paketi 1 kredi verir`() {
        assertEquals(1, creditsFor("kredi_1"))
    }

    @Test
    fun `kredi_5 paketi 5 kredi verir`() {
        assertEquals(5, creditsFor("kredi_5"))
    }

    @Test
    fun `kredi_10 paketi 10 kredi verir`() {
        assertEquals(10, creditsFor("kredi_10"))
    }

    @Test
    fun `geçersiz ürün 0 kredi verir`() {
        assertEquals("Geçersiz ürün → 0", 0, creditsFor("gecersiz_urun"))
    }

    @Test
    fun `10 kredi ile toplam soru sayısı 550 olur`() {
        val freeQuestions = 50
        val creditsPerPurchase = 10
        val questionsPerCredit = 50
        val total = freeQuestions + (creditsPerPurchase * questionsPerCredit)
        assertEquals("50 ücretsiz + 10×50 = 550", 550, total)
    }
}

/**
 * Backend JSON yanıtı parse testleri.
 * Ağ bağlantısı olmadan JSON parsing mantığını doğrular.
 */
class BackendResponseParseTest {

    private fun parseQuestionsFromResponse(json: JSONObject): List<JSONObject>? {
        return try {
            val arr: JSONArray = json.getJSONArray("questions")
            (0 until arr.length()).map { arr.getJSONObject(it) }
        } catch (e: Exception) {
            null
        }
    }

    private fun isPlaceholder(json: JSONObject) = json.optBoolean("placeholder", false)

    @Test
    fun `geçerli soru listesi parse edilir`() {
        val response = JSONObject("""
            {
                "version": 2,
                "questions": [
                    {"id": 1, "type": "toplama", "text": "3+4=?", "answer": 7, "difficulty": 1, "hint": "3 artı 4"},
                    {"id": 2, "type": "çıkarma", "text": "9-5=?", "answer": 4, "difficulty": 1, "hint": "9 eksi 5"}
                ]
            }
        """.trimIndent())
        val questions = parseQuestionsFromResponse(response)
        assertNotNull(questions)
        assertEquals(2, questions!!.size)
        assertEquals(7, questions[0].getInt("answer"))
    }

    @Test
    fun `placeholder yanıt tekrar modunu tetikler`() {
        val response = JSONObject("""{"version": 3, "questions": [], "placeholder": true}""")
        assertTrue("placeholder=true → tekrar moduna geç", isPlaceholder(response))
    }

    @Test
    fun `boş sorular tekrar modunu tetikler`() {
        val response = JSONObject("""{"version": 3, "questions": []}""")
        val questions = parseQuestionsFromResponse(response)
        assertTrue("Boş liste → tekrar moduna geç", questions!!.isEmpty())
    }

    @Test
    fun `is_repeat true ise tekrar modu`() {
        val response = JSONObject("""
            {
                "success": true,
                "credits_remaining": 0,
                "is_repeat": true,
                "questions": {"version": 1, "questions": []}
            }
        """.trimIndent())
        assertTrue(response.optBoolean("is_repeat", false))
    }

    @Test
    fun `credits bilgisi doğru parse edilir`() {
        val response = JSONObject("""
            {"device_token": "abc-123", "credits": 7, "free_set_used": true}
        """.trimIndent())
        assertEquals(7, response.getInt("credits"))
        assertTrue(response.getBoolean("free_set_used"))
    }

    @Test
    fun `verify purchase response başarılı parse edilir`() {
        val response = JSONObject("""
            {"success": true, "credits_added": 10, "total_credits": 10}
        """.trimIndent())
        assertTrue(response.getBoolean("success"))
        assertEquals(10, response.getInt("credits_added"))
        assertEquals(10, response.getInt("total_credits"))
    }

    @Test
    fun `verify purchase başarısız yanıt parse edilir`() {
        val response = JSONObject("""
            {"success": false, "error": "Purchase not found"}
        """.trimIndent())
        assertFalse(response.getBoolean("success"))
        assertEquals("Purchase not found", response.getString("error"))
    }
}
