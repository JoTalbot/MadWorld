package com.jotalbot.madworld.data

import android.content.Context
import org.json.JSONObject
import java.util.UUID

class PlayerRepository(
    context: Context,
    private val api: MadWorldApi,
) {
    private val cache = context.getSharedPreferences("player_state", Context.MODE_PRIVATE)

    fun cached(playerId: UUID): PlayerState? = cache.getString(playerId.toString(), null)?.let(::parseCached)

    fun refresh(playerId: UUID): PlayerState = api.fetchPlayerState(playerId).also { save(playerId, it) }

    fun bootstrap(playerId: UUID, characterName: String): PlayerState = api.bootstrap(playerId, characterName).also { save(playerId, it) }

    private fun save(playerId: UUID, state: PlayerState) {
        val root = JSONObject()
        state.character?.let { character ->
            root.put("character", JSONObject().put("id", character.id).put("player_id", character.playerId).put("name", character.name).put("level", character.level).put("version", character.version))
        } ?: root.put("character", JSONObject.NULL)
        val vehicles = org.json.JSONArray()
        state.vehicles.forEach { vehicle ->
            vehicles.put(JSONObject().put("id", vehicle.id).put("owner_id", vehicle.ownerId).put("code", vehicle.code).put("chassis_code", vehicle.chassisCode).put("durability", vehicle.durability).put("fuel", vehicle.fuel).put("state", vehicle.state).put("version", vehicle.version))
        }
        root.put("vehicles", vehicles)
        cache.edit().putString(playerId.toString(), root.toString()).apply()
    }

    private fun parseCached(json: String): PlayerState {
        val root = JSONObject(json)
        val character = if (root.isNull("character")) null else root.getJSONObject("character").let {
            CharacterState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("player_id")), it.getString("name"), it.getInt("level"), it.getInt("version"))
        }
        val vehicles = buildList {
            val array = root.getJSONArray("vehicles")
            for (index in 0 until array.length()) {
                val it = array.getJSONObject(index)
                add(VehicleState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("owner_id")), it.getString("code"), it.getString("chassis_code"), it.getInt("durability"), it.getInt("fuel"), it.getString("state"), it.getInt("version")))
            }
        }
        return PlayerState(character, vehicles)
    }
}
