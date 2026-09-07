package com.jotalbot.madworld

import android.app.Application
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions

class MadWorldApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.MADWORLD_FIREBASE_API_KEY.isBlank() || BuildConfig.MADWORLD_FIREBASE_APP_ID.isBlank() || BuildConfig.MADWORLD_FIREBASE_PROJECT_ID.isBlank() || BuildConfig.MADWORLD_FIREBASE_SENDER_ID.isBlank()) return
        if (FirebaseApp.getApps(this).isNotEmpty()) return
        val options = FirebaseOptions.Builder()
            .setApiKey(BuildConfig.MADWORLD_FIREBASE_API_KEY)
            .setApplicationId(BuildConfig.MADWORLD_FIREBASE_APP_ID)
            .setProjectId(BuildConfig.MADWORLD_FIREBASE_PROJECT_ID)
            .setGcmSenderId(BuildConfig.MADWORLD_FIREBASE_SENDER_ID)
            .build()
        FirebaseApp.initializeApp(this, options)
    }
}
