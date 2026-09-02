package com.jotalbot.madworld.data

import java.util.UUID

data class VehicleModuleState(val id: UUID, val code: String, val slotType: String, val mass: Int, val armor: Int, val power: Int)
data class WeaponState(val id: UUID, val code: String, val damage: Int, val damageType: String, val rangeM: Int, val cooldownSeconds: Int)
data class Phase3State(
    val vehicleId: UUID,
    val componentConditions: Map<String, Int>,
    val fittedModules: Map<Int, String>,
    val weapons: List<WeaponState>,
    val canFight: Boolean,
    val canSalvage: Boolean,
    val canRecover: Boolean,
    val convoyMember: Boolean,
)
