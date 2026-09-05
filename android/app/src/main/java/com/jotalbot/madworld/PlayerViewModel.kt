package com.jotalbot.madworld

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.jotalbot.madworld.data.*
import com.jotalbot.madworld.data.PlayerSessionCoordinator.LoadOutcome
import com.jotalbot.madworld.data.PlayerSessionCoordinator.Snapshot
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.util.UUID

sealed interface PlayerUiState {
    data object Loading : PlayerUiState
    data object SignedOut : PlayerUiState
    data class Ready(
        val state: PlayerState,
        val session: SessionState,
        val settlement: SettlementState? = null,
        val economy: EconomyOverviewState? = null,
        val corporation: CorporationState? = null,
        val socialWalletBalance: Long? = null,
        val territory: TerritoryState? = null,
        val world: WorldState? = null,
        val offline: Boolean = false,
        val settlementError: String? = null,
        val economyError: String? = null,
        val socialError: String? = null,
        val territoryError: String? = null,
        val worldError: String? = null,
    ) : PlayerUiState

    data class Error(val message: String, val cached: PlayerState? = null) : PlayerUiState
}

class PlayerViewModel(application: Application) : AndroidViewModel(application) {
    private val api: MadWorldApiClient = MadWorldApi(BuildConfig.MADWORLD_API_URL)
    private val worldApi: WorldApiClient = WorldRepository(BuildConfig.MADWORLD_API_URL)
    private val repository = PlayerRepository(application, api)
    private val offlineQueue = OfflineCommandQueue(application)
    private val notifications = NotificationCenter(application)
    private val coordinator = PlayerSessionCoordinator(
        api, worldApi, repository,
        OfflineQueueDrainer(offlineQueue, AuthoritativeOfflineDispatcher(api)),
        notifications,
    )
    private val _uiState = MutableStateFlow<PlayerUiState>(PlayerUiState.Loading)
    val uiState: StateFlow<PlayerUiState> = _uiState.asStateFlow()

    private fun Snapshot.toReady(previous: PlayerUiState.Ready? = null) = PlayerUiState.Ready(
        state, session, settlement, economy,
        corporation = previous?.corporation, socialWalletBalance = previous?.socialWalletBalance,
        territory = territory, world = world, offline = false,
        settlementError = settlementError, economyError = economyError, territoryError = territoryError, worldError = worldError,
    )

    fun enqueueOfflineCommand(name: String, payload: JSONObject, idempotencyKey: String = UUID.randomUUID().toString()) {
        offlineQueue.enqueue(OfflineCommandQueue.Command(name, payload.toString(), idempotencyKey))
        notifications.publish("Command queued", "$name will be synchronized after reconnect.", "info")
    }

    fun load() {
        val session = repository.session()
        if (session == null) { _uiState.value = PlayerUiState.SignedOut; return }
        val cached = repository.cached(session.playerId)
        val cachedSettlement = repository.cachedSettlement(session.playerId)
        if (cached != null) _uiState.value = PlayerUiState.Ready(cached, session, cachedSettlement, offline = true)
        viewModelScope.launch(Dispatchers.IO) {
            when (val outcome = coordinator.loadLive(session, cachedSettlement, hadCache = cached != null)) {
                is LoadOutcome.Live -> _uiState.value = outcome.snapshot.toReady()
                is LoadOutcome.Failed -> if (!outcome.hadCache) _uiState.value = PlayerUiState.Error(outcome.message)
                else -> Unit
            }
        }
    }

    fun signIn(handle: String) {
        _uiState.value = PlayerUiState.Loading
        viewModelScope.launch(Dispatchers.IO) {
            when (val outcome = coordinator.signIn(handle)) {
                is LoadOutcome.Live -> _uiState.value = outcome.snapshot.toReady()
                is LoadOutcome.Failed -> _uiState.value = PlayerUiState.Error(outcome.message)
                else -> Unit
            }
        }
    }

    fun bootstrap(characterName: String) {
        val x = _uiState.value as? PlayerUiState.Ready ?: return
        _uiState.value = PlayerUiState.Loading
        viewModelScope.launch(Dispatchers.IO) {
            val previous = Snapshot(x.state, x.session, x.settlement, x.economy, x.territory, x.world)
            when (val outcome = coordinator.bootstrap(x.session, characterName, previous)) {
                is LoadOutcome.Live -> _uiState.value = outcome.snapshot.toReady(x)
                is LoadOutcome.Failed -> _uiState.value = PlayerUiState.Error(outcome.message)
                else -> Unit
            }
        }
    }

    private inline fun updateReady(crossinline block: suspend (PlayerUiState.Ready) -> PlayerUiState.Ready) {
        val x = _uiState.value as? PlayerUiState.Ready ?: return
        viewModelScope.launch(Dispatchers.IO) { _uiState.value = block(x) }
    }

    fun refreshSettlement() = updateReady { x ->
        runCatching { repository.refreshSettlement(x.session) }.fold(
            { x.copy(settlement = coordinator.acceptSettlement(x.settlement, it), settlementError = null, offline = false) },
            { x.copy(settlementError = it.message ?: "Unable to load settlement") },
        )
    }

    fun refreshEconomy() = updateReady { x ->
        runCatching { repository.refreshEconomy(x.session) }.fold(
            { x.copy(economy = it, economyError = null, offline = false) },
            { x.copy(economyError = it.message ?: "Unable to load economy") },
        )
    }

    fun refreshTerritory() = updateReady { x ->
        runCatching { api.fetchTerritory(x.session.token) }.fold(
            { x.copy(territory = it, territoryError = null, offline = false) },
            { x.copy(territoryError = it.message ?: "Unable to load territory") },
        )
    }

    fun refreshWorld() = updateReady { x ->
        runCatching { worldApi.fetch(x.session.token) }.fold(
            { x.copy(world = it, worldError = null, offline = false) },
            { x.copy(worldError = it.message ?: "Unable to load world") },
        )
    }

    fun refreshCorporation(corporationId: UUID) = updateReady { x ->
        runCatching { api.fetchCorporationOverview(corporationId, x.session.token) }.fold(
            { x.copy(corporation = it, socialError = null) },
            { x.copy(socialError = it.message ?: "Unable to load corporation") },
        )
    }

    fun refreshCorporateWallet(corporationId: UUID) = updateReady { x ->
        runCatching { api.fetchCorporateWallet(corporationId, x.session.token) }.fold(
            { x.copy(socialWalletBalance = it, socialError = null) },
            { x.copy(socialError = it.message ?: "Unable to load corporate wallet") },
        )
    }

    fun createCorporation(code: String, name: String, taxBps: Int) {
        val x = _uiState.value as? PlayerUiState.Ready ?: return
        viewModelScope.launch(Dispatchers.IO) {
            coordinator.createCorporation(x.session, code, name, taxBps).fold(
                { refreshCorporation(it); refreshCorporateWallet(it) },
                { _uiState.value = x.copy(socialError = it.message ?: "Unable to create corporation") },
            )
        }
    }

    fun createManufacturer(brand: String, quality: Int) {
        val x = _uiState.value as? PlayerUiState.Ready ?: return
        val corporation = x.corporation ?: return
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = runCatching { api.createManufacturer(corporation.id, brand.trim(), quality, x.session.token) }.fold(
                { x.copy(socialError = "Manufacturer created") },
                { x.copy(socialError = it.message ?: "Unable to create manufacturer") },
            )
        }
    }
}
