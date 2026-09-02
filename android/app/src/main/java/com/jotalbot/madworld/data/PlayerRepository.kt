package com.jotalbot.madworld.data

import android.content.Context
import org.json.JSONObject
import java.util.UUID

class PlayerRepository(context: Context, private val api: MadWorldApi) {
    private val cache = context.getSharedPreferences("player_state", Context.MODE_PRIVATE)
    private val session = context.getSharedPreferences("player_session", Context.MODE_PRIVATE)
    private val settlementCache = context.getSharedPreferences("settlement_state", Context.MODE_PRIVATE)

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
    fun cachedSettlement(playerId: UUID): SettlementState? = settlementCache.getString(playerId.toString(), null)?.let(::parseSettlement)
    fun refresh(session: SessionState): PlayerState = api.fetchPlayerState(session.playerId, session.token).also { save(session.playerId, it) }
    fun refreshSettlement(session: SessionState): SettlementState = api.fetchSettlement(session.playerId, session.token).also { saveSettlement(session.playerId, it) }
    fun bootstrap(session: SessionState, characterName: String): PlayerState = api.bootstrap(session.playerId, characterName, session.token).also { save(session.playerId, it) }

    private fun saveSettlement(playerId: UUID, state: SettlementState) {
        val modules = JSONObject(); state.modules.forEach { (key, value) -> modules.put(key, value) }
        val capabilities = JSONObject(); state.capabilities.forEach { (key, value) -> capabilities.put(key, value) }
        settlementCache.edit().putString(playerId.toString(), JSONObject().put("id", state.id).put("owner_id", state.ownerId).put("region", state.region).put("level", state.level).put("modules", modules).put("capabilities", capabilities).put("version", state.version).toString()).apply()
    }

    private fun save(playerId: UUID, state: PlayerState) {
        val root = JSONObject()
        state.character?.let { c -> root.put("character", JSONObject().put("id", c.id).put("player_id", c.playerId).put("name", c.name).put("level", c.level).put("version", c.version)) } ?: root.put("character", JSONObject.NULL)
        val vehicles = org.json.JSONArray(); state.vehicles.forEach { v -> vehicles.put(JSONObject().put("id", v.id).put("owner_id", v.ownerId).put("code", v.code).put("chassis_code", v.chassisCode).put("durability", v.durability).put("fuel", v.fuel).put("state", v.state).put("version", v.version)) }; root.put("vehicles", vehicles)
        state.wallet?.let { w -> root.put("wallet", JSONObject().put("id", w.id).put("balance", w.balance).put("version", w.version)) } ?: root.put("wallet", JSONObject.NULL)
        val inventory = org.json.JSONArray(); state.inventory.forEach { i -> inventory.put(JSONObject().put("inventory_id", i.inventoryId).put("item_definition_id", i.itemDefinitionId).put("quantity", i.quantity).put("condition", i.condition).put("version", i.version)) }; root.put("inventory", inventory)
        val jobs = org.json.JSONArray(); state.activeJobs.forEach { j -> jobs.put(JSONObject().put("id", j.id).put("owner_id", j.ownerId).put("job_type", j.jobType).put("started_at", j.startedAt).put("completes_at", j.completesAt).put("state", j.state).put("version", j.version)) }; root.put("active_jobs", jobs)
        cache.edit().putString(playerId.toString(), root.toString()).apply()
    }

    private fun parseSettlement(json: String): SettlementState {
        val root = JSONObject(json)
        val modulesJson = root.getJSONObject("modules")
        val capabilitiesJson = root.getJSONObject("capabilities")
        val modules = buildMap { modulesJson.keys().forEach { key -> put(key, modulesJson.getInt(key)) } }
        val capabilities = buildMap { capabilitiesJson.keys().forEach { key -> put(key, capabilitiesJson.getBoolean(key)) } }
        return SettlementState(UUID.fromString(root.getString("id")), UUID.fromString(root.getString("owner_id")), root.getString("region"), root.getInt("level"), modules, capabilities, root.getInt("version"))
    }

    private fun parseCached(json: String): PlayerState {
        val root = JSONObject(json)
        val character = if (root.isNull("character")) null else root.getJSONObject("character").let { CharacterState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("player_id")), it.getString("name"), it.getInt("level"), it.getInt("version")) }
        val vehicles = buildList { val array = root.getJSONArray("vehicles"); for (index in 0 until array.length()) { val it = array.getJSONObject(index); add(VehicleState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("owner_id")), it.getString("code"), it.getString("chassis_code"), it.getInt("durability"), it.getInt("fuel"), it.getString("state"), it.getInt("version"))) } }
        val wallet = if (root.isNull("wallet")) null else root.getJSONObject("wallet").let { WalletState(UUID.fromString(it.getString("id")), it.getLong("balance"), it.getInt("version")) }
        val inventory = buildList { val array = root.getJSONArray("inventory"); for (index in 0 until array.length()) { val it = array.getJSONObject(index); add(InventoryState(UUID.fromString(it.getString("inventory_id")), UUID.fromString(it.getString("item_definition_id")), it.getLong("quantity"), it.getInt("condition"), it.getInt("version"))) } }
        val jobs = buildList { val array = root.getJSONArray("active_jobs"); for (index in 0 until array.length()) { val it = array.getJSONObject(index); add(JobState(UUID.fromString(it.getString("id")), UUID.fromString(it.getString("owner_id")), it.getString("job_type"), it.getString("started_at"), it.getString("completes_at"), it.getString("state"), it.getInt("version"))) } }
        return PlayerState(character, vehicles, wallet, inventory, jobs)
    }
}
