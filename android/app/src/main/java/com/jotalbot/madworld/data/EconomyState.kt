package com.jotalbot.madworld.data

import java.util.UUID

data class EconomyJobState(
    val id: UUID,
    val kind: String,
    val recipeId: UUID,
    val settlementId: UUID,
    val state: String,
    val completesAt: String,
)

data class EconomyFacilityState(
    val code: String,
    val level: Int,
    val efficiencyBps: Int,
)

data class EconomyOverviewState(
    val settlementId: UUID,
    val region: String,
    val warehouseCapacity: Int,
    val warehouseUsed: Int,
    val facilities: List<EconomyFacilityState>,
    val activeJobs: List<EconomyJobState>,
    val contractCount: Int,
    val readyVehicles: Int,
    val marketPricePoints: Int,
    val nextAction: String,
)
