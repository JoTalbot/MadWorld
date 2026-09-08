plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

fun envOrProperty(name: String): String? = providers.gradleProperty(name).orElse(providers.environmentVariable(name)).orNull
fun escaped(value: String): String = value.replace("\\", "\\\\").replace("\"", "\\\"")

android {
    namespace = "com.jotalbot.madworld"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.jotalbot.madworld"
        minSdk = 26
        targetSdk = 35
        versionCode = 2
        versionName = "0.1.1"
        manifestPlaceholders["madworldAllowCleartext"] = false
    }

    buildTypes {
        debug {
            val apiUrl = envOrProperty("MADWORLD_API_URL") ?: "https://api.autosklo.org.ua"
            buildConfigField("String", "MADWORLD_API_URL", "\"${escaped(apiUrl)}\"")
            manifestPlaceholders["madworldAllowCleartext"] = apiUrl.startsWith("http://")
        }
        release {
            val apiUrl = envOrProperty("MADWORLD_API_URL")
            buildConfigField("String", "MADWORLD_API_URL", "\"${escaped(apiUrl ?: "")}\"")
            manifestPlaceholders["madworldAllowCleartext"] = false
            // The release artifact is intended for direct device testing/distribution.
            // Use the standard Android debug keystore so it is installable without
            // storing a production signing key in the repository or CI logs.
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    buildFeatures { compose = true; buildConfig = true }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
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
    testImplementation("org.json:json:20240303")
}

gradle.taskGraph.whenReady {
    val releaseScheduled = allTasks.any { it.project == project && it.name.contains("Release") && !it.name.contains("UnitTest") }
    if (releaseScheduled) {
        val apiUrl = envOrProperty("MADWORLD_API_URL") ?: throw GradleException("MADWORLD_API_URL is required for release builds")
        require(apiUrl.startsWith("https://")) { "MADWORLD_API_URL must use HTTPS for release builds" }
    }
}
