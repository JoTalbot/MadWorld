package com.jotalbot.madworld.data

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI

class WorldRepository(private val baseUrl:String):WorldApiClient{
    override fun fetch(token:String):WorldState{
        val c=(URI.create("${baseUrl.trimEnd('/')}/api/v1/world-simulation").toURL().openConnection() as HttpURLConnection).apply{
            requestMethod="GET"; connectTimeout=10_000; readTimeout=10_000
            setRequestProperty("Accept","application/json"); setRequestProperty("Authorization","Bearer $token")
        }
        try{
            if(c.responseCode !in 200..299) throw ApiException("world simulation request failed: HTTP ${c.responseCode}")
            return MadWorldJson.parseWorld(c.inputStream.bufferedReader().use{it.readText()})
        }finally{c.disconnect()}
    }
}
