package com.jotalbot.madworld.data

import android.content.Context
import org.json.JSONObject
import java.util.UUID

class PlayerRepository(context: Context, private val api: MadWorldApi) {
    private val cache = context.getSharedPreferences("player_state", Context.MODE_PRIVATE)
    private val session = context.getSharedPreferences("player_session", Context.MODE_PRIVATE)

    fun session(): SessionState? {
        val playerId = session.getString("player_id", null)?.let(UUID::fromString) ?: return null
        val handle = session.getString("handle", null) ?: return null
        val token = session.getString("token", null) ?: return null
        val expiresAt = session.getString("expires_at", null) ?: return null
        return SessionState(playerId, handle, token, expiresAt)
    }

    fun createSession(handle: String): SessionState = api.createSession(handle).also { value ->
        session.edit().putString("player_id", value.playerId.toString()).putString("handle", value.handle).putString("token", value.token).putString("expires_at", value.expiresAt).apply()
    }

    fun cached(playerId: UUID): PlayerState? = cache.getString(playerId.toString(), null)?.let(::parseCached)
    fun refresh(session: SessionState): PlayerState = api.fetchPlayerState(session.playerId, session.token).also { save(session.playerId, it) }
    fun bootstrap(session: SessionState, characterName: String): PlayerState = api.bootstrap(session.playerId, characterName, session.token).also { save(session.playerId, it) }

    private fun save(playerId: UUID, state: PlayerState) {
        val root = JSONObject()
        state.character?.let { c -> root.put("character", JSONObject().put("id", c.id).put("player_id", c.playerId).put("name", c.name).put("level", c.level).put("version", c.version)) } ?: root.put("character", JSONObject.NULL)
        val vehicles = org.json.JSONArray()
        state.vehicles.forEach { v -> vehicles.put(JSONObject().put("id", v.id).put("owner_id", v.ownerId).put("code", v.code).put("chassis_code", v.chassisCode).put("durability", v.durability).put("fuel", v.fuel).put("state", v.state).put("version", v.version)) }
        root.put("vehicles", vehicles)
        cache.edit().putString(playerId.toString(), root.toString()).apply()
    }

    private fun parseCached(json: String): PlayerState {
        val root = JSONObject(json)
        val character = if (root.isNull("character")) null else root.getJSONObject("character").let { CharacterState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("player_id")), it.getString("name"), it.getInt("level"), it.getInt("version")) }
        val vehicles = buildList {
            val array = root.getJSONArray("vehicles")
            for (index in 0 until array.length()) { val it = array.getJSONObject(index); add(VehicleState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("owner_id")), it.getString("code"), it.getString("chassis_code"), it.getInt("durability"), it.getInt("fuel"), it.getString("state"), it.getInt("version"))) }
        }
        return PlayerState(character, vehicles)
    }
}
