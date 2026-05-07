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
     * MEB müfredatına uygun: her dönemde yalnızca o dönemde öngörülen tipler.
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

    // ─── Okul Öncesi: sayma, toplama, çıkarma, karşılaştırma, örüntü ──────

    private fun generatePreschool(): MathQuestion {
        return when (Random.nextInt(5)) {
            0 -> generateCounting(maxItems = 5)
            1 -> generateAddition(maxA = 5, maxB = 5, resultMax = 10)
            2 -> generateSubtraction(minA = 2, maxA = 5)
            3 -> generateComparison(maxVal = 10)
            else -> generatePattern()
        }
    }

    // ─── 1. Sınıf: toplama, çıkarma, sıralama, eksik_sayı ─────────────────

    private fun generateGrade1(): MathQuestion {
        return when (Random.nextInt(4)) {
            0 -> generateAddition(maxA = 10, maxB = 10, resultMax = 20)
            1 -> generateSubtraction(minA = 2, maxA = 10, noBorrow = true)
            2 -> generateSorting(maxVal = 20, count = 2, mode = "biggest")
            else -> generateMissingNumber(maxA = 5, maxResult = 10)
        }
    }

    // ─── 2. Sınıf: 4 işlem + sıralama + eksik_sayı ────────────────────────

    private fun generateGrade2(): MathQuestion {
        return when (Random.nextInt(6)) {
            0 -> generateAddition(maxA = 50, maxB = 50)
            1 -> generateSubtraction(minA = 10, maxA = 99)
            2 -> generateMultiplication(maxA = 10, maxB = 10, resultMax = 100)
            3 -> generateDivision(maxDivisor = 10, maxResult = 10)
            4 -> generateSorting(maxVal = 100, count = 3, mode = "smallest")
            else -> generateMissingNumber(maxA = 15, maxResult = 50)
        }
    }

    // ─── 3. Sınıf: 4 işlem + sıralama + eksik_sayı + kesir + problem ──────

    private fun generateGrade3(): MathQuestion {
        return when (Random.nextInt(8)) {
            0 -> generateAddition(maxA = 200, maxB = 100)
            1 -> generateSubtraction(minA = 10, maxA = 200)
            2 -> generateMultiplication(maxA = 20, maxB = 9, resultMax = 900)
            3 -> generateDivision(maxDivisor = 9, maxResult = 20)
            4 -> generateSorting(maxVal = 500, count = 4, mode = "smallest")
            5 -> generateMissingNumber(maxA = 30, maxResult = 100)
            6 -> generateFraction(unitFraction = true)
            else -> generateProblem(difficulty = Random.nextInt(1, 4))
        }
    }

    // ─── 4. Sınıf: 4 işlem + sıralama + eksik_sayı + kesir + problem ──────

    private fun generateGrade4(): MathQuestion {
        return when (Random.nextInt(8)) {
            0 -> generateAddition(maxA = 500, maxB = 500)
            1 -> generateSubtraction(minA = 50, maxA = 500)
            2 -> generateMultiplication(maxA = 100, maxB = 50, resultMax = 10000)
            3 -> generateDivision(maxDivisor = 50, maxResult = 100)
            4 -> generateSorting(maxVal = 10000, count = 5, mode = "biggest")
            5 -> generateMissingNumber(maxA = 100, maxResult = 1000)
            6 -> generateFraction(unitFraction = false)
            else -> generateProblem(difficulty = Random.nextInt(2, 6))
        }
    }

    // ─── Parametrik üretim yardımcıları ───────────────────────────────────

    private fun generateAddition(maxA: Int, maxB: Int, resultMax: Int? = null): MathQuestion {
        val a = Random.nextInt(1, maxA + 1)
        val b = Random.nextInt(1, maxB + 1)
        if (resultMax != null && a + b > resultMax) {
            return generateAddition(maxA, maxB, resultMax)
        }
        return MathQuestion("$a + $b = ?", a + b, "toplama")
    }

    private fun generateSubtraction(minA: Int, maxA: Int, noBorrow: Boolean = false): MathQuestion {
        val a = Random.nextInt(minA, maxA + 1)
        val b = if (noBorrow && a >= 10) {
            val maxB = a % 10
            if (maxB >= 1) Random.nextInt(1, maxB + 1) else 1
        } else {
            Random.nextInt(1, a)
        }
        return MathQuestion("$a - $b = ?", a - b, "çıkarma")
    }

    private fun generateMultiplication(maxA: Int, maxB: Int, resultMax: Int? = null): MathQuestion {
        val a = Random.nextInt(2, maxA + 1)
        val b = Random.nextInt(1, maxB + 1)
        if (resultMax != null && a * b > resultMax) {
            return generateMultiplication(maxA, maxB, resultMax)
        }
        return MathQuestion("$a × $b = ?", a * b, "çarpma")
    }

    private fun generateDivision(maxDivisor: Int, maxResult: Int): MathQuestion {
        val b = Random.nextInt(2, maxDivisor + 1)
        val result = Random.nextInt(1, maxResult + 1)
        val a = b * result
        return MathQuestion("$a ÷ $b = ?", result, "bölme")
    }

    private fun generateCounting(maxItems: Int): MathQuestion {
        val items = listOf("🍎", "⭐", "🐱", "🚗", "🌸")
        val labels = listOf("elma", "yıldız", "kedi", "araba", "çiçek")
        val idx = Random.nextInt(items.size)
        val count = Random.nextInt(1, maxItems + 1)
        val emojis = items[idx].repeat(count)
        return MathQuestion("Kaç tane ${labels[idx]} var: $emojis = ?", count, "sayma")
    }

    private fun generatePattern(): MathQuestion {
        val templates = listOf(
            Pair("1, 2, 1, 2, ?", 1),
            Pair("2, 4, 6, ?", 8),
            Pair("1, 3, 5, ?", 7),
        )
        val (text, answer) = templates[Random.nextInt(templates.size)]
        return MathQuestion("$text = ?", answer, "örüntü")
    }

    private fun generateComparison(maxVal: Int): MathQuestion {
        val a = Random.nextInt(1, maxVal + 1)
        var b = Random.nextInt(1, maxVal + 1)
        while (b == a) b = Random.nextInt(1, maxVal + 1)
        return if (Random.nextBoolean()) {
            MathQuestion("Hangisi büyük: $a, $b = ?", maxOf(a, b), "karşılaştırma")
        } else {
            MathQuestion("Hangisi küçük: $a, $b = ?", minOf(a, b), "karşılaştırma")
        }
    }

    private fun generateSorting(maxVal: Int, count: Int, mode: String): MathQuestion {
        val numbers = mutableSetOf<Int>()
        while (numbers.size < count) {
            numbers.add(Random.nextInt(1, maxVal + 1))
        }
        val numsList = numbers.toList()
        val numsStr = numsList.joinToString(", ")
        return if (mode == "biggest") {
            MathQuestion("En büyüğü hangisi: $numsStr = ?", numsList.maxOrNull() ?: 0, "sıralama")
        } else {
            MathQuestion("En küçüğü hangisi: $numsStr = ?", numsList.minOrNull() ?: 0, "sıralama")
        }
    }

    private fun generateMissingNumber(maxA: Int, maxResult: Int): MathQuestion {
        return if (Random.nextBoolean()) {
            val a = Random.nextInt(1, maxA + 1)
            val b = Random.nextInt(a + 1, maxResult + 1)
            MathQuestion("? + $a = $b", b - a, "eksik_sayı")
        } else {
            val a = Random.nextInt(2, maxResult + 1)
            val b = Random.nextInt(1, a)
            MathQuestion("? - $a = $b", a + b, "eksik_sayı")
        }
    }

    private fun generateFraction(unitFraction: Boolean): MathQuestion {
        val denominators = listOf(2, 3, 4, 5, 6, 8, 10)
        val den = if (unitFraction) denominators[Random.nextInt(5)] else denominators[Random.nextInt(denominators.size)]
        val num = if (unitFraction) 1 else Random.nextInt(2, den)
        val multiplier = Random.nextInt(2, 21)
        val a = den * multiplier
        val answer = num * multiplier

        val name = if (num == 1) {
            when (den) {
                2 -> "yarısı"
                3 -> "üçte biri"
                4 -> "çeyreği"
                5 -> "beşte biri"
                6 -> "altıda biri"
                8 -> "sekizde biri"
                10 -> "onda biri"
                else -> "${den}'de biri"
            }
        } else {
            "$num/$den'i"
        }
        return MathQuestion("${a}'nin $name kaçtır = ?", answer, "kesir")
    }

    private fun generateProblem(difficulty: Int): MathQuestion {
        return when (difficulty) {
            1 -> {
                val a = Random.nextInt(10, 51)
                val b = Random.nextInt(5, a)
                if (Random.nextBoolean()) {
                    MathQuestion("Ali'nin $a TL'si var. $b TL harcadı. Kaç TL kaldı = ?", a - b, "problem")
                } else {
                    MathQuestion("Ayşe'nin $a bilyesi var. $b tane daha aldı. Kaç bilyesi oldu = ?", a + b, "problem")
                }
            }
            2 -> {
                val a = Random.nextInt(3, 13)
                val b = Random.nextInt(2, 11)
                if (Random.nextBoolean()) {
                    MathQuestion("$a kutudan her birinde $b kalem var. Toplam kaç kalem var = ?", a * b, "problem")
                } else {
                    val total = a * b
                    MathQuestion("$total elma $b çocuğa eşit paylaştırıldı. Her çocuğa kaç elma düştü = ?", a, "problem")
                }
            }
            else -> {
                if (Random.nextBoolean()) {
                    val a = Random.nextInt(20, 81)
                    val b = Random.nextInt(5, a / 2)
                    val c = Random.nextInt(10, 51)
                    MathQuestion("Ali'nin $a TL'si var. $b TL harcadı, $c TL daha aldı. Kaç TL'si var = ?", a - b + c, "problem")
                } else {
                    val a = Random.nextInt(2, 11)
                    val b = Random.nextInt(5, 21)
                    val c = a * b + Random.nextInt(5, 51)
                    MathQuestion("$a paket aldı, her biri $b TL. $c TL verdi. Para üstü kaç = ?", c - a * b, "problem")
                }
            }
        }
    }
}
