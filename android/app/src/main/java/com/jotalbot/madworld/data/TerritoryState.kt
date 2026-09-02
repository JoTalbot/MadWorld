package com.jotalbot.madworld.data

import java.util.UUID

data class TerritoryRegionState(val id:String,val name:String,val security:String,val version:Long)
data class TerritoryControlState(val regionId:String,val targetType:String,val targetId:String,val controllerCorporationId:UUID?,val controlledSince:String?,val version:Long)
data class TerritoryRoadState(val id:UUID,val regionId:String,val fromNode:String,val toNode:String,val controllerCorporationId:UUID?,val travelModifierBps:Int,val riskModifierBps:Int,val version:Long)
data class TerritoryResourceSiteState(val id:UUID,val regionId:String,val resourceType:String,val name:String,val controllerCorporationId:UUID?,val capacity:Long,val remaining:Long,val renewalRate:Long,val extractionLimit:Long,val version:Long)
data class TerritoryState(val regions:List<TerritoryRegionState>,val control:List<TerritoryControlState>,val roads:List<TerritoryRoadState>,val resourceSites:List<TerritoryResourceSiteState>,val authoritative:Boolean=true)
