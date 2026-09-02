package com.jotalbot.madworld.data

import java.util.UUID

data class CharacterState(
    val id: UUID,
    val playerId: UUID,
    val name: String,
    val level: Int,
    val version: Int,
)

data class VehicleState(
    val id: UUID,
    val ownerId: UUID,
    val code: String,
    val chassisCode: String,
    val durability: Int,
    val fuel: Int,
    val state: String,
    val version: Int,
)

data class PlayerState(
    val character: CharacterState?,
    val vehicles: List<VehicleState>,
)
