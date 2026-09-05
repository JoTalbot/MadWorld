package com.jotalbot.madworld.data

import com.jotalbot.madworld.data.PlayerSessionCoordinator.LoadOutcome
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class PlayerSessionCoordinatorTest {
    private val api = FakeMadWorldApi()
    private val repo = PlayerRepository(api, InMemoryKeyValueStore(), InMemoryKeyValueStore(), InMemoryKeyValueStore())
    private val queue = OfflineCommandQueue(InMemoryKeyValueStore())
    private val notifications = NotificationCenter(InMemoryKeyValueStore()) { 0L }
    private val dispatched = mutableListOf<String>()
    private val coordinator = PlayerSessionCoordinator(
        api, api, repo,
        OfflineQueueDrainer(queue) { c, _ -> dispatched += c.idempotencyKey; if (c.name == "explode") throw ApiException("boom") },
        notifications,
    )

    @Test
    fun signInLoadsEverythingAndDrainsQueueBetweenTwoStateReads() {
        queue.enqueue(OfflineCommandQueue.Command("bootstrap_player", "{}", "q1"))
        val outcome = coordinator.signIn("  rook ") as LoadOutcome.Live
        assertEquals("rook", outcome.snapshot.session.handle)
        assertEquals(listOf("q1"), dispatched)
        // connectivity probe -> drain -> authoritative re-read
        assertEquals(listOf("createSession", "fetchPlayerState", "fetchPlayerState"), api.calls.take(3))
        assertNotNull(outcome.snapshot.settlement); assertNotNull(outcome.snapshot.economy); assertNotNull(outcome.snapshot.world)
        assertNull(outcome.snapshot.settlementError)
        assertEquals(listOf("Offline commands synchronized"), notifications.items.value.map { it.title })
    }

    @Test
    fun secondaryPanelFailuresDegradeIndividuallyNotTheWholeScreen() {
        api.failNext("fetchSettlement"); api.failNext("fetchWorld")
        val outcome = coordinator.signIn("rook") as LoadOutcome.Live
        assertNull(outcome.snapshot.settlement); assertEquals("Settlement unavailable", outcome.snapshot.settlementError)
        assertNull(outcome.snapshot.world); assertEquals("World unavailable", outcome.snapshot.worldError)
        assertNotNull(outcome.snapshot.economy); assertNull(outcome.snapshot.economyError)
    }

    @Test
    fun primaryStateFailureIsReportedWithCacheAwareness() {
        val session = repo.createSession("rook")
        api.failNext("fetchPlayerState")
        val noCache = coordinator.loadLive(session, null, hadCache = false) as LoadOutcome.Failed
        assertEquals("fetchPlayerState failed", noCache.message); assertTrue(!noCache.hadCache)
        api.failNext("fetchPlayerState")
        val withCache = coordinator.loadLive(session, null, hadCache = true) as LoadOutcome.Failed
        assertTrue(withCache.hadCache)
    }

    @Test
    fun failedDrainKeepsIntentQueuedAndWarns() {
        queue.enqueue(OfflineCommandQueue.Command("explode", "{}", "bad")); queue.enqueue(OfflineCommandQueue.Command("bootstrap_player", "{}", "later"))
        coordinator.signIn("rook")
        assertEquals(listOf("bad", "later"), queue.peek().map { it.idempotencyKey })
        assertEquals(listOf("Offline queue paused"), notifications.items.value.map { it.title })
    }

    @Test
    fun staleSettlementSnapshotIsRejected() {
        val session = repo.createSession("rook")
        api.settlementVersion = 5
        val first = coordinator.loadLive(session, null, hadCache = false) as LoadOutcome.Live
        assertEquals(5, first.snapshot.settlement!!.version)
        api.settlementVersion = 3
        val second = coordinator.loadLive(session, first.snapshot.settlement, hadCache = true) as LoadOutcome.Live
        assertEquals(5, second.snapshot.settlement!!.version)
    }

    @Test
    fun bootstrapKeepsPreviousPanelsWhenRefreshFails() {
        val session = repo.createSession("rook")
        val before = (coordinator.loadLive(session, null, hadCache = false) as LoadOutcome.Live).snapshot
        api.failNext("fetchEconomyOverview"); api.failNext("fetchTerritory")
        val after = (coordinator.bootstrap(session, "Dust", before) as LoadOutcome.Live).snapshot
        assertEquals("Dust", after.state.character!!.name)
        assertEquals(before.economy, after.economy); assertEquals(before.territory, after.territory)
    }

    @Test
    fun createSessionFailureIsSurfaced() {
        api.failNext("createSession")
        assertEquals("createSession failed", (coordinator.signIn("rook") as LoadOutcome.Failed).message)
    }
}
