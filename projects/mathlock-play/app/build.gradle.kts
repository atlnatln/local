import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.gms.google-services")
    id("com.google.firebase.crashlytics")
}

val localProperties = Properties().apply {
    val localFile = rootProject.file("local.properties")
    if (localFile.exists()) {
        load(localFile.inputStream())
    }
}

android {
    namespace = "com.akn.mathlock"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.akn.mathlock.play"
        minSdk = 26
        targetSdk = 35
        versionCode = 75
        versionName = "1.0.75"
    }

    signingConfigs {
        create("release") {
            storeFile = file("../keystore.jks")
            storePassword = localProperties.getProperty("RELEASE_STORE_PASSWORD") ?: ""
            keyAlias = "mathlock-play"
            keyPassword = localProperties.getProperty("RELEASE_KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.biometric:biometric:1.1.0")
    implementation("androidx.recyclerview:recyclerview:1.3.2")
    implementation("androidx.cardview:cardview:1.0.0")
    implementation("androidx.lifecycle:lifecycle-service:2.7.0")

    // Google Play Billing
    implementation("com.android.billingclient:billing:7.1.1")

    // Grafik kütüphanesi (Dashboard)
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")

    // Firebase Crashlytics (Kotlin 1.9 uyumlu explicit version)
    implementation("com.google.firebase:firebase-crashlytics:18.6.4")

    // Encrypted SharedPreferences
    implementation("androidx.security:security-crypto:1.1.0-alpha06")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit:1.9.0")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.json:json:20231013")
}
