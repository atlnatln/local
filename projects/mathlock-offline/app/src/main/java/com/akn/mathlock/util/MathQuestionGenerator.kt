package com.akn.mathlock.util

import kotlin.random.Random

data class MathQuestion(
    val text: String,
    val answer: Int,
    val operationType: String
)

object MathQuestionGenerator {

    /**
     * 2. sınıf seviyesinde rastgele matematik sorusu üretir.
     * Toplama, çıkarma, çarpma tablosu, bölme
     */
    fun generate(): MathQuestion {
        return when (Random.nextInt(5)) {
            0 -> generateAddition()
            1 -> generateSubtraction()
            2 -> generateMultiplication()
            3 -> generateDivision()
            else -> generateSquare()
        }
    }

    /** Toplama: iki sayının toplamı (max 100) */
    private fun generateAddition(): MathQuestion {
        val a = Random.nextInt(1, 51)   // 1-50
        val b = Random.nextInt(1, 51)   // 1-50
        return MathQuestion(
            text = "$a + $b = ?",
            answer = a + b,
            operationType = "toplama"
        )
    }

    /** Çıkarma: sonuç her zaman pozitif (2. sınıf seviyesi) */
    private fun generateSubtraction(): MathQuestion {
        val a = Random.nextInt(10, 100)  // 10-99
        val b = Random.nextInt(1, a)     // 1 ile a-1 arası (sonuç pozitif)
        return MathQuestion(
            text = "$a - $b = ?",
            answer = a - b,
            operationType = "çıkarma"
        )
    }

    /** Çarpma tablosu: 1-10 arası çarpma */
    private fun generateMultiplication(): MathQuestion {
        val a = Random.nextInt(2, 11)  // 2-10
        val b = Random.nextInt(1, 11)  // 1-10
        return MathQuestion(
            text = "$a × $b = ?",
            answer = a * b,
            operationType = "çarpma"
        )
    }

    /** Bölme: tam bölünebilen sayılar (2. sınıf seviyesi) */
    private fun generateDivision(): MathQuestion {
        val b = Random.nextInt(2, 11)   // bölen: 2-10
        val result = Random.nextInt(1, 11) // sonuç: 1-10
        val a = b * result                // bölünen = bölen × sonuç (tam bölünür)
        return MathQuestion(
            text = "$a ÷ $b = ?",
            answer = result,
            operationType = "bölme"
        )
    }

    /** Kare alma: 1-12 arası bir sayının karesi (v1.1 ile eklendi) */
    private fun generateSquare(): MathQuestion {
        val a = Random.nextInt(1, 13)  // 1-12
        return MathQuestion(
            text = "$a² = ?  ($a × $a)",
            answer = a * a,
            operationType = "kare"
        )
    }
}
