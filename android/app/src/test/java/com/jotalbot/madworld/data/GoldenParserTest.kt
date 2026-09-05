package com.jotalbot.madworld.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.UUID

/**
 * Backend <-> Android contract: the JSON under src/test/resources/golden/ is produced by the real
 * FastAPI application (backend/scripts/export_android_golden.py). If a parser fails here, the server
 * response shape and the client disagree.
 */
class GoldenParserTest {
    private fun golden(name: String): String =
        checkNotNull(javaClass.classLoader.getResourceAsStream("golden/$name")) { "missing golden/$name" }.bufferedReader().use { it.readText() }

    @Test
    fun playerStateFromBootstrapContainsStarterVehicleAndWallet() {
        val state = MadWorldJson.parseState(golden("player_state.json"))
        assertEquals("Golden", state.character!!.name)
        assertEquals(1, state.vehicles.size)
        with(state.vehicles.single()) { assertEquals("light_runner", chassisCode); assertEquals(25, fuel); assertEquals("active", this.state) }
        assertNotNull(state.wallet); assertEquals(0L, state.wallet!!.balance)
        assertTrue(state.inventory.isEmpty() && state.activeJobs.isEmpty())
    }

    @Test
    fun settlementParsesModulesAndCapabilitiesAndEnforcesOwner() {
        val json = golden("settlement.json")
        val owner = UUID.fromString(org.json.JSONObject(json).getString("owner_id"))
        val settlement = MadWorldJson.parseSettlement(json, owner)
        assertEquals("dust_basin", settlement.region)
        assertEquals(1, settlement.modules["workshop"]); assertEquals(true, settlement.capabilities["market"])
        assertThrows(ApiException::class.java) { MadWorldJson.parseSettlement(json, UUID.randomUUID()) }
    }

    @Test
    fun economyOverviewParsesFacilitiesAndNextAction() {
        val overview = MadWorldJson.parseEconomyOverview(golden("economy_overview.json"))
        assertEquals(listOf("refinery", "workshop"), overview.facilities.map { it.code })
        assertTrue(overview.warehouseCapacity >= 1000)
        assertTrue(overview.nextAction.isNotBlank())
    }

    @Test
    fun territoryParsesSeedRegions() {
        val territory = MadWorldJson.parseTerritory(golden("territory.json"))
        assertEquals(setOf("dust_basin", "iron_ruins", "salt_coast"), territory.regions.map { it.id }.toSet())
        assertTrue(territory.authoritative)
    }

    @Test
    fun worldSimulationParsesFactionsPressuresAndEvents() {
        val world = MadWorldJson.parseWorld(golden("world_simulation.json"))
        assertEquals(3, world.factions.size); assertEquals(9, world.pressures.size); assertEquals(3, world.events.size)
        assertTrue(world.authoritative)
    }

    @Test
    fun sessionAndBootstrapShapesMatchClientExpectations() {
        val session = org.json.JSONObject(golden("session_create.json"))
        for (key in listOf("player_id", "handle", "token", "expires_at")) assertTrue(key, session.has(key))
        val bootstrap = org.json.JSONObject(golden("player_bootstrap.json"))
        assertTrue(bootstrap.has("character") && bootstrap.has("vehicle"))
    }
}
