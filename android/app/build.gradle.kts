plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.jotalbot.madworld"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.jotalbot.madworld"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"

        // Dev/emulator fallback remains available, but production must inject a real HTTPS URL.
        val apiUrl = providers.gradleProperty("MADWORLD_API_URL")
            .orElse(providers.environmentVariable("MADWORLD_API_URL"))
            .orElse("http://10.0.2.2:8000")
            .get()
        buildConfigField("String", "MADWORLD_API_URL", "\"${apiUrl.replace("\\", "\\\\").replace("\"", "\\\"")}\"")

        // Android 9+ blocks cleartext HTTP by default. Keep it enabled only for
        // explicitly configured debug builds so a physical phone can reach a
        // development server on the local network without weakening production.
        manifestPlaceholders["madworldAllowCleartext"] = false
    }

    buildTypes {
        debug {
            manifestPlaceholders["madworldAllowCleartext"] = true
        }
        release {
            manifestPlaceholders["madworldAllowCleartext"] = false
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.02.00")
    implementation(composeBom)
    androidTestImplementation(composeBom)
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    debugImplementation("androidx.compose.ui:ui-tooling")
    testImplementation("junit:junit:4.13.2")
}
