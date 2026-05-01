# Default ProGuard rules for MathLock
-keepattributes *Annotation*

# ── Google Play Billing ──
-keep class com.android.billingclient.api.** { *; }

# ── Biometric ──
-keep class androidx.biometric.** { *; }

# ── JS Bridge — GameBridge metodları obfuscate olmasın ──
-keepclassmembers class com.akn.mathlock.*$GameBridge {
    @android.webkit.JavascriptInterface <methods>;
}
-keepclassmembers class com.akn.mathlock.SayiYolculuguActivity$GameBridge {
    @android.webkit.JavascriptInterface <methods>;
}
-keepclassmembers class com.akn.mathlock.RobotopiaActivity$GameBridge {
    @android.webkit.JavascriptInterface <methods>;
}

# ── MPAndroidChart ──
-keep class com.github.mikephil.charting.** { *; }

# ── JSON serialization ──
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# ── R8 gereksiz class'ları silmesin ──
-keepattributes Signature, Exceptions, InnerClasses, EnclosingMethod
