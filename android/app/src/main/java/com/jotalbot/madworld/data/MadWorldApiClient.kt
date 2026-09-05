package com.jotalbot.madworld.data

import org.json.JSONObject
import java.util.UUID

/** Authoritative server API surface used by repositories, dispatcher and view model. */
interface MadWorldApiClient {
    fun createSession(handle: String): SessionState
    fun fetchPlayerState(playerId: UUID, token: String? = null): PlayerState
    fun fetchSettlement(playerId: UUID, token: String): SettlementState
    fun fetchEconomyOverview(playerId: UUID, token: String): EconomyOverviewState
    fun fetchSocialCapabilities(token: String): List<String>
    fun fetchCorporationOverview(corporationId: UUID, token: String): CorporationState
    fun fetchCorporateWallet(corporationId: UUID, token: String): Long
    fun createCorporation(code: String, name: String, taxBps: Int, token: String, idempotencyKey: String = UUID.randomUUID().toString()): UUID
    fun createManufacturer(corporationId: UUID, brandName: String, quality: Int, token: String, idempotencyKey: String = UUID.randomUUID().toString()): UUID
    fun transferCorporateWallet(corporationId: UUID, recipientPlayerId: UUID?, recipientCorporationId: UUID?, amount: Long, reason: String, token: String, idempotencyKey: String = UUID.randomUUID().toString())
    fun createEscrowContract(corporationId: UUID, contractType: String, amount: Long, counterpartyPlayerId: UUID?, counterpartyCorporationId: UUID?, terms: JSONObject, token: String, idempotencyKey: String = UUID.randomUUID().toString()): UUID
    fun settleContract(contractId: UUID, newState: String, token: String, idempotencyKey: String = UUID.randomUUID().toString())
    fun fetchTerritory(token: String): TerritoryState
    fun bootstrap(playerId: UUID, characterName: String, token: String? = null, idempotencyKey: String = UUID.randomUUID().toString()): PlayerState
}

/** World simulation read API, separated so it can be faked independently. */
fun interface WorldApiClient {
    fun fetch(token: String): WorldState
}
