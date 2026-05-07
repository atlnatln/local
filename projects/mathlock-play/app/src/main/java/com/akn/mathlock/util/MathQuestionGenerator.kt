package com.akn.mathlock.util

import kotlin.random.Random

data class MathQuestion(
    val text: String,
    val answer: Int,
    val operationType: String
)

object MathQuestionGenerator {

    /**
     * Çocuğun eğitim dönemine göre yaş uygun matematik sorusu üretir.
     */
    fun generate(educationPeriod: String = "sinif_2"): MathQuestion {
        return when (educationPeriod) {
            "okul_oncesi" -> generatePreschool()
            "sinif_1" -> generateGrade1()
            "sinif_2" -> generateGrade2()
            "sinif_3" -> generateGrade3()
            "sinif_4" -> generateGrade4()
            else -> generateGrade2()
        }
    }

    // ─── Okul Öncesi: sadece basit toplama / çıkarma (1-5 arası) ──────────

    private fun generatePreschool(): MathQuestion {
        return when (Random.nextInt(2)) {
            0 -> {
                val a = Random.nextInt(1, 6)   // 1-5
                val b = Random.nextInt(1, 6)   // 1-5  → sonuç max 10
                MathQuestion("$a + $b = ?", a + b, "toplama")
            }
            else -> {
                val a = Random.nextInt(2, 6)   // 2-5
                val b = Random.nextInt(1, a)   // sonuç pozitif ve küçük
                MathQuestion("$a - $b = ?", a - b, "çıkarma")
            }
        }
    }

    // ─── 1. Sınıf: toplama / çıkarma (1-10 arası), nadiren basit çarpma ────

    private fun generateGrade1(): MathQuestion {
        return when (Random.nextInt(2)) {
            0 -> {
                val a = Random.nextInt(1, 11)  // 1-10
                val b = Random.nextInt(1, 11)  // 1-10  → sonuç max 20
                MathQuestion("$a + $b = ?", a + b, "toplama")
            }
            else -> {
                val a = Random.nextInt(2, 11)  // 2-10
                val b = Random.nextInt(1, a)   // sonuç pozitif
                MathQuestion("$a - $b = ?", a - b, "çıkarma")
            }
        }
    }

    // ─── 2. Sınıf: mevcut varsayılan seviye ───────────────────────────────

    private fun generateGrade2(): MathQuestion {
        return when (Random.nextInt(4)) {
            0 -> generateAddition(maxA = 50, maxB = 50)
            1 -> generateSubtraction(minA = 10, maxA = 99)
            2 -> generateMultiplication(maxA = 10, maxB = 10)
            else -> generateDivision(maxDivisor = 10, maxResult = 10)
        }
    }

    // ─── 3. Sınıf: biraz daha zor ─────────────────────────────────────────

    private fun generateGrade3(): MathQuestion {
        return when (Random.nextInt(5)) {
            0 -> generateAddition(maxA = 100, maxB = 100)
            1 -> generateSubtraction(minA = 10, maxA = 200)
            2 -> generateMultiplication(maxA = 12, maxB = 12)
            3 -> generateDivision(maxDivisor = 12, maxResult = 12)
            else -> generateSquare(max = 15)
        }
    }

    // ─── 4. Sınıf: en zor seviye ──────────────────────────────────────────

    private fun generateGrade4(): MathQuestion {
        return when (Random.nextInt(5)) {
            0 -> generateAddition(maxA = 500, maxB = 500)
            1 -> generateSubtraction(minA = 50, maxA = 500)
            2 -> generateMultiplication(maxA = 15, maxB = 15)
            3 -> generateDivision(maxDivisor = 15, maxResult = 15)
            else -> generateSquare(max = 20)
        }
    }

    // ─── Parametrik üretim yardımcıları ───────────────────────────────────

    private fun generateAddition(maxA: Int, maxB: Int): MathQuestion {
        val a = Random.nextInt(1, maxA + 1)
        val b = Random.nextInt(1, maxB + 1)
        return MathQuestion("$a + $b = ?", a + b, "toplama")
    }

    private fun generateSubtraction(minA: Int, maxA: Int): MathQuestion {
        val a = Random.nextInt(minA, maxA + 1)
        val b = Random.nextInt(1, a)     // sonuç her zaman pozitif
        return MathQuestion("$a - $b = ?", a - b, "çıkarma")
    }

    private fun generateMultiplication(maxA: Int, maxB: Int): MathQuestion {
        val a = Random.nextInt(2, maxA + 1)
        val b = Random.nextInt(1, maxB + 1)
        return MathQuestion("$a × $b = ?", a * b, "çarpma")
    }

    private fun generateDivision(maxDivisor: Int, maxResult: Int): MathQuestion {
        val b = Random.nextInt(2, maxDivisor + 1)
        val result = Random.nextInt(1, maxResult + 1)
        val a = b * result
        return MathQuestion("$a ÷ $b = ?", result, "bölme")
    }

    private fun generateSquare(max: Int): MathQuestion {
        val a = Random.nextInt(1, max + 1)
        return MathQuestion("$a² = ?  ($a × $a)", a * a, "kare")
    }
}
