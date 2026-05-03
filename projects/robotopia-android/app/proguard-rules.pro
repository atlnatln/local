# JS Bridge — GameBridge metodları obfuscate olmasın
-keepclassmembers class com.akn.robotopia.MainActivity$GameBridge {
    @android.webkit.JavascriptInterface <methods>;
}

# R8 gereksiz class'ları silmesin
-keepattributes Signature, Exceptions, InnerClasses, EnclosingMethod
