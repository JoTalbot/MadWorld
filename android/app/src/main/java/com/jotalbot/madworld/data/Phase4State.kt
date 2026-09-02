package com.jotalbot.madworld.data

import java.util.UUID

data class CorporationState(val id: UUID, val code: String, val name: String, val role: String, val taxBps: Int, val memberCount: Int)
data class DiplomacyState(val targetCorporationId: UUID, val relation: String, val standing: Int, val tradeAllowed: Boolean, val transitAllowed: Boolean)
data class SocialContractState(val id: UUID, val type: String, val state: String, val expiresAt: String?)
data class ManufacturerState(val id: UUID, val brandName: String, val qualityRating: Int, val reputation: Int)
data class Phase4State(val corporation: CorporationState?, val diplomacy: List<DiplomacyState>, val contracts: List<SocialContractState>, val manufacturer: ManufacturerState?, val canManageMembers: Boolean, val canManageWallet: Boolean, val canManageHangar: Boolean, val canDiplomacy: Boolean)
