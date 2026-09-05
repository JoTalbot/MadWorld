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
            val r=JSONObject(c.inputStream.bufferedReader().use{it.readText()})
            val s=r.getJSONObject("simulation")
            val factions=buildList{val a=r.getJSONArray("factions");for(i in 0 until a.length()){val x=a.getJSONObject(i);add(WorldFactionState(x.getString("id"),x.getString("name"),x.getString("doctrine"),x.getInt("aggression_bps"),x.getInt("logistics_bps")))}}
            val pressures=buildList{val a=r.getJSONArray("pressures");for(i in 0 until a.length()){val x=a.getJSONObject(i);add(WorldPressureState(x.getString("region_id"),x.getString("resource_type"),x.getInt("pressure_bps"),x.getInt("trend_bps"),x.getLong("available_quantity"),x.getLong("target_quantity")))}}
            val events=buildList{val a=r.getJSONArray("events");for(i in 0 until a.length()){val x=a.getJSONObject(i);add(WorldEventState(x.getString("id"),x.getLong("tick"),if(x.isNull("region_id"))null else x.getString("region_id"),if(x.isNull("faction_id"))null else x.getString("faction_id"),x.getString("event_type"),x.getInt("severity"),x.getString("state")))}}
            val missions=buildList{val a=r.getJSONArray("missions");for(i in 0 until a.length()){val x=a.getJSONObject(i);add(WorldMissionState(x.getString("id"),x.getString("region_id"),x.getString("mission_type"),x.getString("title"),x.getLong("reward_credits"),x.getInt("risk_bps"),x.getString("state")))}}
            val discoveries=buildList{val a=r.getJSONArray("discoveries");for(i in 0 until a.length()){val x=a.getJSONObject(i);add(WorldDiscoveryState(x.getString("id"),x.getString("region_id"),x.getString("resource_type"),x.getLong("quantity"),x.getString("state")))}}
            val disasters=buildList{val a=r.getJSONArray("disasters");for(i in 0 until a.length()){val x=a.getJSONObject(i);add(WorldDisasterState(x.getString("id"),x.getString("region_id"),x.getString("disaster_type"),x.getInt("severity"),x.getInt("hazard_bps"),x.getInt("travel_risk_bps"),x.getInt("extraction_modifier_bps")))}}
            return WorldState(s.getInt("season"),s.getLong("tick"),r.getBoolean("authoritative"),factions,pressures,events,missions,discoveries,disasters)
        }finally{c.disconnect()}
    }
}
