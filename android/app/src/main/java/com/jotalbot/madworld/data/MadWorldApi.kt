package com.jotalbot.madworld.data

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.util.UUID

class MadWorldApi(private val baseUrl: String) {
    fun createSession(handle: String): SessionState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/sessions").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            doOutput = true
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Accept", "application/json")
        }
        try {
            connection.outputStream.use { it.write(JSONObject().put("handle", handle).toString().toByteArray()) }
            val code = connection.responseCode
            if (code !in 200..299) throw ApiException("session request failed: HTTP $code")
            val root = JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
            return SessionState(
                playerId = UUID.fromString(root.getString("player_id")),
                handle = root.getString("handle"),
                token = root.getString("token"),
                expiresAt = root.getString("expires_at"),
            )
        } finally { connection.disconnect() }
    }

    fun fetchPlayerState(playerId: UUID, token: String? = null): PlayerState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/players/$playerId/state").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Accept", "application/json")
            token?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
        try {
            val code = connection.responseCode
            if (code !in 200..299) throw ApiException("state request failed: HTTP $code")
            return parseState(connection.inputStream.bufferedReader().use { it.readText() })
        } finally { connection.disconnect() }
    }

    fun bootstrap(playerId: UUID, characterName: String, token: String? = null, idempotencyKey: UUID = UUID.randomUUID()): PlayerState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/players/bootstrap").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            doOutput = true
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Idempotency-Key", idempotencyKey.toString())
            token?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
        try {
            connection.outputStream.use { it.write(JSONObject().put("player_id", playerId.toString()).put("character_name", characterName).toString().toByteArray()) }
            val code = connection.responseCode
            if (code !in 200..299) throw ApiException("bootstrap request failed: HTTP $code")
            val root = JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
            return PlayerState(parseCharacter(root.getJSONObject("character")), listOf(parseVehicle(root.getJSONObject("vehicle"))))
        } finally { connection.disconnect() }
    }

    private fun parseState(json: String): PlayerState {
        val root = JSONObject(json)
        val character = if (root.isNull("character")) null else parseCharacter(root.getJSONObject("character"))
        val vehicles = buildList {
            val array = root.getJSONArray("vehicles")
            for (index in 0 until array.length()) add(parseVehicle(array.getJSONObject(index)))
        }
        return PlayerState(character, vehicles)
    }

    private fun parseCharacter(json: JSONObject) = CharacterState(UUID.fromString(json.getString("id")), UUID.fromString(json.getString("player_id")), json.getString("name"), json.getInt("level"), json.getInt("version"))
    private fun parseVehicle(json: JSONObject) = VehicleState(UUID.fromString(json.getString("id")), UUID.fromString(json.getString("owner_id")), json.getString("code"), json.getString("chassis_code"), json.getInt("durability"), json.getInt("fuel"), json.getString("state"), json.getInt("version"))
}

data class SessionState(val playerId: UUID, val handle: String, val token: String, val expiresAt: String)
class ApiException(message: String) : RuntimeException(message)
