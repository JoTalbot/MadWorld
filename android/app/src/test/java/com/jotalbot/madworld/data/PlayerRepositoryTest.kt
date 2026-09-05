package com.jotalbot.madworld.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class PlayerRepositoryTest {
    private val api = FakeMadWorldApi()
    private val cache = InMemoryKeyValueStore()
    private val session = InMemoryKeyValueStore()
    private val settlements = InMemoryKeyValueStore()
    private val repo = PlayerRepository(api, cache, session, settlements)

    @Test
    fun sessionRoundTripsThroughStorage() {
        assertNull(repo.session())
        val created = repo.createSession("rook")
        assertEquals(created, repo.session())
        assertEquals(created, PlayerRepository(api, cache, session, settlements).session())
        repo.clearSession()
        assertNull(repo.session())
    }

    @Test
    fun refreshCachesPlayerStateAndSettlementLosslessly() {
        val s = repo.createSession("rook")
        val live = repo.refresh(s)
        val settlement = repo.refreshSettlement(s)
        assertEquals(live, repo.cached(s.playerId))
        assertEquals(settlement, repo.cachedSettlement(s.playerId))
        assertEquals(live, PlayerRepository(api, cache, session, settlements).cached(s.playerId))
    }

    @Test
    fun partialSessionIsTreatedAsSignedOut() {
        session.put("player_id", java.util.UUID.randomUUID().toString()); session.put("handle", "x")
        assertNull(repo.session())
    }

    @Test
    fun corruptCacheYieldsNullInsteadOfCrash() {
        val s = repo.createSession("rook")
        cache.put(s.playerId.toString(), "{broken"); settlements.put(s.playerId.toString(), "[]")
        assertNull(repo.cached(s.playerId)); assertNull(repo.cachedSettlement(s.playerId))
    }
}
