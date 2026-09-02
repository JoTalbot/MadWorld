package com.jotalbot.madworld.data

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.util.UUID

class MadWorldApi(private val baseUrl: String) {
    fun createSession(handle: String): SessionState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/sessions").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"; doOutput = true; connectTimeout = 10_000; readTimeout = 10_000
            setRequestProperty("Content-Type", "application/json"); setRequestProperty("Accept", "application/json")
        }
        try {
            connection.outputStream.use { it.write(JSONObject().put("handle", handle).toString().toByteArray()) }
            if (connection.responseCode !in 200..299) throw ApiException("session request failed: HTTP ${connection.responseCode}")
            val root = JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
            return SessionState(UUID.fromString(root.getString("player_id")), root.getString("handle"), root.getString("token"), root.getString("expires_at"))
        } finally { connection.disconnect() }
    }

    fun fetchPlayerState(playerId: UUID, token: String? = null): PlayerState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/players/$playerId/state").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"; connectTimeout = 10_000; readTimeout = 10_000; setRequestProperty("Accept", "application/json")
            token?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
        try {
            if (connection.responseCode !in 200..299) throw ApiException("state request failed: HTTP ${connection.responseCode}")
            return parseState(connection.inputStream.bufferedReader().use { it.readText() })
        } finally { connection.disconnect() }
    }

    fun fetchSettlement(playerId: UUID, token: String): SettlementState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/settlement").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"; connectTimeout = 10_000; readTimeout = 10_000
            setRequestProperty("Accept", "application/json"); setRequestProperty("Authorization", "Bearer $token")
        }
        try {
            if (connection.responseCode !in 200..299) throw ApiException("settlement request failed: HTTP ${connection.responseCode}")
            val root = JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
            if (UUID.fromString(root.getString("owner_id")) != playerId) throw ApiException("settlement owner mismatch")
            val modulesJson = root.getJSONObject("modules")
            val capabilitiesJson = root.getJSONObject("capabilities")
            val modules = buildMap { modulesJson.keys().forEach { key -> put(key, modulesJson.getInt(key)) } }
            val capabilities = buildMap { capabilitiesJson.keys().forEach { key -> put(key, capabilitiesJson.getBoolean(key)) } }
            return SettlementState(UUID.fromString(root.getString("id")), playerId, root.getString("region"), root.getInt("level"), modules, capabilities, root.getInt("version"))
        } finally { connection.disconnect() }
    }

    fun bootstrap(playerId: UUID, characterName: String, token: String? = null, idempotencyKey: UUID = UUID.randomUUID()): PlayerState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/players/bootstrap").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"; doOutput = true; connectTimeout = 10_000; readTimeout = 10_000
            setRequestProperty("Content-Type", "application/json"); setRequestProperty("Accept", "application/json")
            setRequestProperty("Idempotency-Key", idempotencyKey.toString()); token?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
        try {
            connection.outputStream.use { it.write(JSONObject().put("player_id", playerId.toString()).put("character_name", characterName).toString().toByteArray()) }
            if (connection.responseCode !in 200..299) throw ApiException("bootstrap request failed: HTTP ${connection.responseCode}")
            return fetchPlayerState(playerId, token)
        } finally { connection.disconnect() }
    }

    private fun parseState(json: String): PlayerState {
        val root = JSONObject(json)
        val character = if (root.isNull("character")) null else parseCharacter(root.getJSONObject("character"))
        val vehicles = buildList { val array = root.getJSONArray("vehicles"); for (index in 0 until array.length()) add(parseVehicle(array.getJSONObject(index))) }
        val wallet = if (root.isNull("wallet")) null else root.getJSONObject("wallet").let { WalletState(UUID.fromString(it.getString("id")), it.getLong("balance"), it.getInt("version")) }
        val inventory = buildList { val array = root.getJSONArray("inventory"); for (index in 0 until array.length()) { val it = array.getJSONObject(index); add(InventoryState(UUID.fromString(it.getString("inventory_id")), UUID.fromString(it.getString("item_definition_id")), it.getLong("quantity"), it.getInt("condition"), it.getInt("version"))) } }
        val jobs = buildList { val array = root.getJSONArray("active_jobs"); for (index in 0 until array.length()) { val it = array.getJSONObject(index); add(JobState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("owner_id")), it.getString("job_type"), it.getString("started_at"), it.getString("completes_at"), it.getString("state"), it.getInt("version"))) } }
        return PlayerState(character, vehicles, wallet, inventory, jobs)
    }

    private fun parseCharacter(json: JSONObject) = CharacterState(UUID.fromString(json.getString("id")), UUID.fromString(json.getString("player_id")), json.getString("name"), json.getInt("level"), json.getInt("version"))
    private fun parseVehicle(json: JSONObject) = VehicleState(UUID.fromString(json.getString("id")), UUID.fromString(json.getString("owner_id")), json.getString("code"), json.getString("chassis_code"), json.getInt("durability"), json.getInt("fuel"), json.getString("state"), json.getInt("version"))
}

data class SessionState(val playerId: UUID, val handle: String, val token: String, val expiresAt: String)
class ApiException(message: String) : RuntimeException(message)
