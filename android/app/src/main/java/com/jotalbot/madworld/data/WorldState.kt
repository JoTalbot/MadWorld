package com.jotalbot.madworld.data

data class WorldState(
    val season: Int,
    val tick: Long,
    val authoritative: Boolean,
    val factions: List<WorldFactionState>,
    val pressures: List<WorldPressureState>,
    val events: List<WorldEventState>,
    val missions: List<WorldMissionState>,
    val discoveries: List<WorldDiscoveryState>,
    val disasters: List<WorldDisasterState>
)
data class WorldFactionState(val id:String,val name:String,val doctrine:String,val aggressionBps:Int,val logisticsBps:Int)
data class WorldPressureState(val regionId:String,val resourceType:String,val pressureBps:Int,val trendBps:Int,val availableQuantity:Long,val targetQuantity:Long)
data class WorldEventState(val id:String,val tick:Long,val regionId:String?,val factionId:String?,val eventType:String,val severity:Int,val state:String)
data class WorldMissionState(val id:String,val regionId:String,val missionType:String,val title:String,val rewardCredits:Long,val riskBps:Int,val state:String)
data class WorldDiscoveryState(val id:String,val regionId:String,val resourceType:String,val quantity:Long,val state:String)
data class WorldDisasterState(val id:String,val regionId:String,val disasterType:String,val severity:Int,val hazardBps:Int,val travelRiskBps:Int,val extractionModifierBps:Int)
