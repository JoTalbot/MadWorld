package com.jotalbot.madworld.data

import org.json.JSONObject
import java.util.UUID

/** Scriptable fake of the authoritative API. Every call is recorded; failures are injected per method name. */
class FakeMadWorldApi : MadWorldApiClient, WorldApiClient {
    val calls = mutableListOf<String>()
    val failures = mutableMapOf<String, Int>() // method -> remaining failures
    var playerId: UUID = UUID.randomUUID()
    var stateVersion = 1
    var settlementVersion = 1

    fun failNext(method: String, times: Int = 1) { failures[method] = times }

    private fun <T> call(method: String, produce: () -> T): T {
        calls += method
        val remaining = failures[method] ?: 0
        if (remaining > 0) { failures[method] = remaining - 1; throw ApiException("$method failed") }
        return produce()
    }

    fun playerState(name: String = "Rook") = PlayerState(
        character = CharacterState(UUID.nameUUIDFromBytes("c".toByteArray()), playerId, name, 1, stateVersion),
        vehicles = listOf(VehicleState(UUID.nameUUIDFromBytes("v".toByteArray()), playerId, "starter", "light_runner", 100, 25, "active", stateVersion)),
        wallet = WalletState(UUID.nameUUIDFromBytes("w".toByteArray()), 40, stateVersion),
    )

    fun settlement(version: Int = settlementVersion) = SettlementState(UUID.nameUUIDFromBytes("s".toByteArray()), playerId, "dust_basin", 1, mapOf("workshop" to 1), mapOf("craft" to true), version)

    override fun createSession(handle: String) = call("createSession") { SessionState(playerId, handle, "tok-$handle", "2030-01-01T00:00:00Z") }
    override fun fetchPlayerState(playerId: UUID, token: String?) = call("fetchPlayerState") { playerState() }
    override fun fetchSettlement(playerId: UUID, token: String) = call("fetchSettlement") { settlement() }
    override fun fetchEconomyOverview(playerId: UUID, token: String) = call("fetchEconomyOverview") {
        EconomyOverviewState(settlement().id, "dust_basin", 100, 10, emptyList(), emptyList(), 0, 1, 0, "gather")
    }
    override fun fetchSocialCapabilities(token: String) = call("fetchSocialCapabilities") { emptyList<String>() }
    override fun fetchCorporationOverview(corporationId: UUID, token: String) = call("fetchCorporationOverview") { CorporationState(corporationId, "RST", "Rust", "leader", 100, 1) }
    override fun fetchCorporateWallet(corporationId: UUID, token: String) = call("fetchCorporateWallet") { 500L }
    override fun createCorporation(code: String, name: String, taxBps: Int, token: String, idempotencyKey: String) = call("createCorporation") { UUID.randomUUID() }
    override fun createManufacturer(corporationId: UUID, brandName: String, quality: Int, token: String, idempotencyKey: String) = call("createManufacturer") { UUID.randomUUID() }
    override fun transferCorporateWallet(corporationId: UUID, recipientPlayerId: UUID?, recipientCorporationId: UUID?, amount: Long, reason: String, token: String, idempotencyKey: String) = call("transferCorporateWallet") { }
    override fun createEscrowContract(corporationId: UUID, contractType: String, amount: Long, counterpartyPlayerId: UUID?, counterpartyCorporationId: UUID?, terms: JSONObject, token: String, idempotencyKey: String) = call("createEscrowContract") { UUID.randomUUID() }
    override fun settleContract(contractId: UUID, newState: String, token: String, idempotencyKey: String) = call("settleContract") { }
    override fun fetchTerritory(token: String) = call("fetchTerritory") { TerritoryState(emptyList(), emptyList(), emptyList(), emptyList()) }
    override fun bootstrap(playerId: UUID, characterName: String, token: String?, idempotencyKey: String) = call("bootstrap") { playerState(characterName) }
    override fun fetch(token: String) = call("fetchWorld") { WorldState(1, 7, true, emptyList(), emptyList(), emptyList(), emptyList(), emptyList(), emptyList()) }
}
