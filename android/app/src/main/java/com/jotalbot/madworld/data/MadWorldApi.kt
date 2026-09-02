package com.jotalbot.madworld.data

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.util.UUID

class MadWorldApi(private val baseUrl: String) {
    fun fetchPlayerState(playerId: UUID): PlayerState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/players/$playerId/state").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Accept", "application/json")
        }
        try {
            val code = connection.responseCode
            if (code !in 200..299) throw ApiException("state request failed: HTTP $code")
            return parseState(connection.inputStream.bufferedReader().use { it.readText() })
        } finally {
            connection.disconnect()
        }
    }

    fun bootstrap(playerId: UUID, characterName: String, idempotencyKey: UUID = UUID.randomUUID()): PlayerState {
        val url = URI.create("${baseUrl.trimEnd('/')}/api/v1/players/bootstrap").toURL()
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            doOutput = true
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Idempotency-Key", idempotencyKey.toString())
        }
        try {
            connection.outputStream.use {
                it.write(JSONObject().put("player_id", playerId.toString()).put("character_name", characterName).toString().toByteArray())
            }
            val code = connection.responseCode
            if (code !in 200..299) throw ApiException("bootstrap request failed: HTTP $code")
            val root = JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
            return PlayerState(
                character = parseCharacter(root.getJSONObject("character")),
                vehicles = listOf(parseVehicle(root.getJSONObject("vehicle"))),
            )
        } finally {
            connection.disconnect()
        }
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

    private fun parseCharacter(json: JSONObject) = CharacterState(
        id = UUID.fromString(json.getString("id")),
        playerId = UUID.fromString(json.getString("player_id")),
        name = json.getString("name"),
        level = json.getInt("level"),
        version = json.getInt("version"),
    )

    private fun parseVehicle(json: JSONObject) = VehicleState(
        id = UUID.fromString(json.getString("id")),
        ownerId = UUID.fromString(json.getString("owner_id")),
        code = json.getString("code"),
        chassisCode = json.getString("chassis_code"),
        durability = json.getInt("durability"),
        fuel = json.getInt("fuel"),
        state = json.getString("state"),
        version = json.getInt("version"),
    )
}

class ApiException(message: String) : RuntimeException(message)
