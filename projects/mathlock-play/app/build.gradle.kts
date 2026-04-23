plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.akn.mathlock"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.akn.mathlock.play"
        minSdk = 26
        targetSdk = 35
        versionCode = 46
        versionName = "1.0.46"
    }

    signingConfigs {
        create("release") {
            storeFile = file("../keystore.jks")
            storePassword = "2001293"
            keyAlias = "mathlock-play"
            keyPassword = "2001293"
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

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit:1.9.0")
}
