package com.jotalbot.madworld.data

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.util.UUID

class MadWorldApi(private val baseUrl: String) {
    fun createSession(handle: String): SessionState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/sessions").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply { requestMethod="POST"; doOutput=true; connectTimeout=10_000; readTimeout=10_000; setRequestProperty("Content-Type","application/json"); setRequestProperty("Accept","application/json") }
        try { connection.outputStream.use { it.write(JSONObject().put("handle",handle).toString().toByteArray()) }; if(connection.responseCode !in 200..299) throw ApiException("session request failed: HTTP ${connection.responseCode}"); val root=JSONObject(connection.inputStream.bufferedReader().use{it.readText()}); return SessionState(UUID.fromString(root.getString("player_id")),root.getString("handle"),root.getString("token"),root.getString("expires_at")) } finally { connection.disconnect() }
    }
    fun fetchPlayerState(playerId: UUID, token: String?=null): PlayerState {
        val connection=connection("/api/v1/players/$playerId/state","GET",token)
        try { if(connection.responseCode !in 200..299) throw ApiException("state request failed: HTTP ${connection.responseCode}"); return parseState(connection.inputStream.bufferedReader().use{it.readText()}) } finally { connection.disconnect() }
    }
    fun fetchSettlement(playerId: UUID, token: String): SettlementState {
        val connection=connection("/api/v1/settlement","GET",token)
        try { if(connection.responseCode !in 200..299) throw ApiException("settlement request failed: HTTP ${connection.responseCode}"); val root=JSONObject(connection.inputStream.bufferedReader().use{it.readText()}); if(UUID.fromString(root.getString("owner_id"))!=playerId) throw ApiException("settlement owner mismatch"); val modulesJson=root.getJSONObject("modules"); val capabilitiesJson=root.getJSONObject("capabilities"); val modules=buildMap{modulesJson.keys().forEach{put(it,modulesJson.getInt(it))}}; val capabilities=buildMap{capabilitiesJson.keys().forEach{put(it,capabilitiesJson.getBoolean(it))}}; return SettlementState(UUID.fromString(root.getString("id")),playerId,root.getString("region"),root.getInt("level"),modules,capabilities,root.getInt("version")) } finally { connection.disconnect() }
    }
    fun fetchEconomyOverview(playerId: UUID, token: String): EconomyOverviewState {
        val connection=connection("/api/v1/economy/overview","GET",token)
        try { if(connection.responseCode !in 200..299) throw ApiException("economy overview request failed: HTTP ${connection.responseCode}"); return parseEconomyOverview(connection.inputStream.bufferedReader().use{it.readText()},playerId) } finally { connection.disconnect() }
    }
    fun fetchSocialCapabilities(token: String): List<String> {
        val connection=connection("/api/v1/social/capabilities","GET",token)
        try { if(connection.responseCode !in 200..299) throw ApiException("social capabilities failed: HTTP ${connection.responseCode}"); val array=JSONObject(connection.inputStream.bufferedReader().use{it.readText()}).getJSONArray("systems"); return buildList{for(i in 0 until array.length()) add(array.getString(i))} } finally { connection.disconnect() }
    }
    fun bootstrap(playerId: UUID, characterName: String, token: String?=null, idempotencyKey: UUID=UUID.randomUUID()): PlayerState {
        val connection=connection("/api/v1/players/bootstrap","POST",token); connection.setRequestProperty("Content-Type","application/json"); connection.setRequestProperty("Idempotency-Key",idempotencyKey.toString()); connection.doOutput=true
        try { connection.outputStream.use{it.write(JSONObject().put("player_id",playerId.toString()).put("character_name",characterName).toString().toByteArray())}; if(connection.responseCode !in 200..299) throw ApiException("bootstrap request failed: HTTP ${connection.responseCode}"); return fetchPlayerState(playerId,token) } finally { connection.disconnect() }
    }
    private fun connection(path:String, method:String, token:String?): HttpURLConnection = (URI.create("${baseUrl.trimEnd('/')}$path").toURL().openConnection() as HttpURLConnection).apply { requestMethod=method; connectTimeout=10_000; readTimeout=10_000; setRequestProperty("Accept","application/json"); token?.let{setRequestProperty("Authorization","Bearer $it")} }
    private fun parseEconomyOverview(json:String,playerId:UUID):EconomyOverviewState { val root=JSONObject(json); val settlementId=UUID.fromString(root.getString("settlement_id")); val jobs=buildList{val array=root.getJSONArray("active_jobs");for(index in 0 until array.length()){val item=array.getJSONObject(index);add(EconomyJobState(UUID.fromString(item.getString("id")),item.getString("kind"),UUID.fromString(item.getString("recipe_id")),UUID.fromString(item.getString("settlement_id")),item.getString("state"),item.getString("completes_at")))}}; val facilities=buildList{val array=root.getJSONArray("facilities");for(index in 0 until array.length()){val item=array.getJSONObject(index);add(EconomyFacilityState(item.getString("code"),item.getInt("level"),item.getInt("efficiency_bps")))}}; return EconomyOverviewState(settlementId,root.getString("region"),root.getInt("warehouse_capacity"),root.getInt("warehouse_used"),facilities,jobs,root.getInt("contract_count"),root.getInt("ready_vehicles"),root.getInt("market_price_points"),root.getString("next_action")) }
    private fun parseState(json:String):PlayerState { val root=JSONObject(json); val character=if(root.isNull("character"))null else parseCharacter(root.getJSONObject("character")); val vehicles=buildList{val array=root.getJSONArray("vehicles");for(index in 0 until array.length())add(parseVehicle(array.getJSONObject(index)))}; val wallet=if(root.isNull("wallet"))null else root.getJSONObject("wallet").let{WalletState(UUID.fromString(it.getString("id")),it.getLong("balance"),it.getInt("version"))}; val inventory=buildList{val array=root.getJSONArray("inventory");for(index in 0 until array.length()){val it=array.getJSONObject(index);add(InventoryState(UUID.fromString(it.getString("inventory_id")),UUID.fromString(it.getString("item_definition_id")),it.getLong("quantity"),it.getInt("condition"),it.getInt("version")))}}; val jobs=buildList{val array=root.getJSONArray("active_jobs");for(index in 0 until array.length()){val it=array.getJSONObject(index);add(JobState(UUID.fromString(it.getString("id")),UUID.fromString(it.getString("owner_id")),it.getString("job_type"),it.getString("started_at"),it.getString("completes_at"),it.getString("state"),it.getInt("version")))}}; return PlayerState(character,vehicles,wallet,inventory,jobs) }
    private fun parseCharacter(json:JSONObject)=CharacterState(UUID.fromString(json.getString("id")),UUID.fromString(json.getString("player_id")),json.getString("name"),json.getInt("level"),json.getInt("version"))
    private fun parseVehicle(json:JSONObject)=VehicleState(UUID.fromString(json.getString("id")),UUID.fromString(json.getString("owner_id")),json.getString("code"),json.getString("chassis_code"),json.getInt("durability"),json.getInt("fuel"),json.getString("state"),json.getInt("version"))
}

data class SessionState(val playerId:UUID,val handle:String,val token:String,val expiresAt:String)
class ApiException(message:String):RuntimeException(message)
