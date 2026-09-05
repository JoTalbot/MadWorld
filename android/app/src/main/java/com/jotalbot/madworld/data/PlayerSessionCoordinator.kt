package com.jotalbot.madworld.data

import java.util.UUID

/**
 * Pure-Kotlin orchestration of the sign-in / load / bootstrap flows.
 *
 * The view model only adds coroutine dispatch and StateFlow publication on top of
 * this class, so the reconnect semantics (cached-first, drain offline queue, refresh
 * again, degrade individual panels instead of the whole screen) are unit-testable.
 */
class PlayerSessionCoordinator(
    private val api: MadWorldApiClient,
    private val world: WorldApiClient,
    private val repository: PlayerRepository,
    private val drainer: OfflineQueueDrainer,
    private val notifications: NotificationCenter,
    private val staleGuard: StaleStateGuard = StaleStateGuard(),
) {
    data class Snapshot(
        val state: PlayerState,
        val session: SessionState,
        val settlement: SettlementState?,
        val economy: EconomyOverviewState?,
        val territory: TerritoryState?,
        val world: WorldState?,
    ) {
        val settlementError: String? get() = if (settlement == null) "Settlement unavailable" else null
        val economyError: String? get() = if (economy == null) "Economy unavailable" else null
        val territoryError: String? get() = if (territory == null) "Territory unavailable" else null
        val worldError: String? get() = if (world == null) "World unavailable" else null
    }

    sealed interface LoadOutcome {
        data object SignedOut : LoadOutcome
        data class Cached(val state: PlayerState, val session: SessionState, val settlement: SettlementState?) : LoadOutcome
        data class Live(val snapshot: Snapshot) : LoadOutcome
        data class Failed(val message: String, val hadCache: Boolean) : LoadOutcome
    }

    fun acceptSettlement(current: SettlementState?, candidate: SettlementState?): SettlementState? =
        if (candidate == null) current
        else if (staleGuard.accept("settlement:${candidate.id}", candidate.version.toLong())) candidate
        else current

    fun drainQueuedCommands(session: SessionState): OfflineQueueDrainer.DrainResult {
        val result = drainer.drain(session)
        if (result.delivered > 0) notifications.publish("Offline commands synchronized", "${result.delivered} queued command(s) delivered.", "info")
        if (result.remaining > 0) notifications.publish("Offline queue paused", "${result.remaining} command(s) remain queued after a failed authoritative request.", "warning")
        return result
    }

    /** Cached snapshot (if any) for immediate display; null when signed out. */
    fun cachedOutcome(): LoadOutcome {
        val session = repository.session() ?: return LoadOutcome.SignedOut
        val cached = repository.cached(session.playerId) ?: return LoadOutcome.Failed("no cache", hadCache = false)
        return LoadOutcome.Cached(cached, session, repository.cachedSettlement(session.playerId))
    }

    /** Authoritative refresh: first refresh proves connectivity, then queued intent is drained, then state is re-read. */
    fun loadLive(session: SessionState, cachedSettlement: SettlementState?, hadCache: Boolean): LoadOutcome =
        runCatching { repository.refresh(session) }.fold(
            onSuccess = { initial ->
                drainQueuedCommands(session)
                val state = runCatching { repository.refresh(session) }.getOrDefault(initial)
                LoadOutcome.Live(snapshotFor(session, state, cachedSettlement))
            },
            onFailure = { LoadOutcome.Failed(it.message ?: "Unable to load player state", hadCache) },
        )

    fun signIn(handle: String): LoadOutcome =
        runCatching { repository.createSession(handle.trim()) }.fold(
            onSuccess = { session -> loadLive(session, cachedSettlement = null, hadCache = false) },
            onFailure = { LoadOutcome.Failed(it.message ?: "Unable to create session", hadCache = false) },
        )

    fun bootstrap(session: SessionState, characterName: String, previous: Snapshot?): LoadOutcome =
        runCatching { repository.bootstrap(session, characterName) }.fold(
            onSuccess = { state ->
                val fresh = snapshotFor(session, state, previous?.settlement)
                LoadOutcome.Live(
                    fresh.copy(
                        settlement = fresh.settlement ?: previous?.settlement,
                        economy = fresh.economy ?: previous?.economy,
                        territory = fresh.territory ?: previous?.territory,
                        world = fresh.world ?: previous?.world,
                    ),
                )
            },
            onFailure = { LoadOutcome.Failed(it.message ?: "Unable to bootstrap player", hadCache = previous != null) },
        )

    fun createCorporation(session: SessionState, code: String, name: String, taxBps: Int): Result<UUID> =
        runCatching { api.createCorporation(code.trim(), name.trim(), taxBps, session.token) }

    private fun snapshotFor(session: SessionState, state: PlayerState, cachedSettlement: SettlementState?): Snapshot = Snapshot(
        state = state,
        session = session,
        settlement = acceptSettlement(cachedSettlement, runCatching { repository.refreshSettlement(session) }.getOrNull()),
        economy = runCatching { repository.refreshEconomy(session) }.getOrNull(),
        territory = runCatching { api.fetchTerritory(session.token) }.getOrNull(),
        world = runCatching { world.fetch(session.token) }.getOrNull(),
    )
}
