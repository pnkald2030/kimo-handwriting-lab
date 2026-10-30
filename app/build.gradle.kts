plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.kimo.handwriting"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.kimo.handwriting"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }
}
