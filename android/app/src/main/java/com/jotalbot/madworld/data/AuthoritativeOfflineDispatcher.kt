package com.jotalbot.madworld.data

import org.json.JSONObject
import java.util.UUID

/**
 * Allowlisted bridge from durable offline intent to server-authoritative APIs.
 * Unknown commands are rejected rather than executed optimistically.
 */
class AuthoritativeOfflineDispatcher(
    private val api: MadWorldApi,
) : OfflineCommandDispatcher {
    override fun dispatch(command: OfflineCommandQueue.Command, session: SessionState) {
        val payload = JSONObject(command.payload)
        when (command.name) {
            "create_corporation" -> api.createCorporation(
                payload.getString("code").trim(),
                payload.getString("name").trim(),
                payload.getInt("tax_bps"),
                session.token,
                command.idempotencyKey,
            )
            "create_manufacturer" -> api.createManufacturer(
                UUID.fromString(payload.getString("corporation_id")),
                payload.getString("brand_name").trim(),
                payload.getInt("quality_rating"),
                session.token,
                command.idempotencyKey,
            )
            "transfer_corporate_wallet" -> api.transferCorporateWallet(
                UUID.fromString(payload.getString("corporation_id")),
                payload.optString("recipient_player_id", "").takeIf { it.isNotBlank() }?.let(UUID::fromString),
                payload.optString("recipient_corporation_id", "").takeIf { it.isNotBlank() }?.let(UUID::fromString),
                payload.getLong("amount"),
                payload.getString("reason"),
                session.token,
                command.idempotencyKey,
            )
            "create_escrow" -> api.createEscrowContract(
                UUID.fromString(payload.getString("corporation_id")),
                payload.getString("contract_type"),
                payload.getLong("amount"),
                payload.optString("counterparty_player_id", "").takeIf { it.isNotBlank() }?.let(UUID::fromString),
                payload.optString("counterparty_corporation_id", "").takeIf { it.isNotBlank() }?.let(UUID::fromString),
                JSONObject(payload.getString("terms")),
                session.token,
                command.idempotencyKey,
            )
            "settle_contract" -> api.settleContract(
                UUID.fromString(payload.getString("contract_id")),
                payload.getString("new_state"),
                session.token,
                command.idempotencyKey,
            )
            "bootstrap_player" -> api.bootstrap(
                session.playerId,
                payload.getString("character_name").trim(),
                session.token,
                command.idempotencyKey,
            )
            else -> throw ApiException("Unsupported offline command: ${command.name}")
        }
    }
}
