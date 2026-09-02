package com.jotalbot.madworld

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.jotalbot.madworld.data.MadWorldApi
import com.jotalbot.madworld.data.PlayerRepository
import com.jotalbot.madworld.data.PlayerState
import com.jotalbot.madworld.data.SessionState
import com.jotalbot.madworld.data.SettlementState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed interface PlayerUiState {
    data object Loading : PlayerUiState
    data object SignedOut : PlayerUiState
    data class Ready(val state: PlayerState, val session: SessionState, val settlement: SettlementState? = null, val offline: Boolean = false, val settlementError: String? = null) : PlayerUiState
    data class Error(val message: String, val cached: PlayerState? = null) : PlayerUiState
}

class PlayerViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = PlayerRepository(application, MadWorldApi(BuildConfig.MADWORLD_API_URL))
    private val _uiState = MutableStateFlow<PlayerUiState>(PlayerUiState.Loading)
    val uiState: StateFlow<PlayerUiState> = _uiState.asStateFlow()

    fun load() {
        val session = repository.session()
        if (session == null) { _uiState.value = PlayerUiState.SignedOut; return }
        val cached = repository.cached(session.playerId)
        val cachedSettlement = repository.cachedSettlement(session.playerId)
        if (cached != null) _uiState.value = PlayerUiState.Ready(cached, session, cachedSettlement, offline = true)
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.refresh(session) }
                .onSuccess { state ->
                    val settlement = runCatching { repository.refreshSettlement(session) }.getOrNull() ?: cachedSettlement
                    _uiState.value = PlayerUiState.Ready(state, session, settlement, offline = false, settlementError = if (settlement == null) "Settlement unavailable" else null)
                }
                .onFailure { error -> if (cached == null) _uiState.value = PlayerUiState.Error(error.message ?: "Unable to load player state") }
        }
    }

    fun refreshSettlement() {
        val state = _uiState.value
        if (state !is PlayerUiState.Ready) return
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.refreshSettlement(state.session) }
                .onSuccess { settlement -> _uiState.value = state.copy(settlement = settlement, settlementError = null, offline = false) }
                .onFailure { error -> _uiState.value = state.copy(settlementError = error.message ?: "Unable to load settlement") }
        }
    }

    fun signIn(handle: String) {
        _uiState.value = PlayerUiState.Loading
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.createSession(handle.trim()) }
                .onSuccess { session ->
                    runCatching { repository.refresh(session) }
                        .onSuccess { playerState ->
                            val settlement = runCatching { repository.refreshSettlement(session) }.getOrNull()
                            _uiState.value = PlayerUiState.Ready(playerState, session, settlement, settlementError = if (settlement == null) "Settlement unavailable" else null)
                        }
                        .onFailure { _uiState.value = PlayerUiState.Error(it.message ?: "Unable to load player state") }
                }
                .onFailure { _uiState.value = PlayerUiState.Error(it.message ?: "Unable to create session") }
        }
    }

    fun bootstrap(characterName: String) {
        val state = _uiState.value
        if (state !is PlayerUiState.Ready) return
        _uiState.value = PlayerUiState.Loading
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.bootstrap(state.session, characterName) }
                .onSuccess { playerState ->
                    val settlement = runCatching { repository.refreshSettlement(state.session) }.getOrNull() ?: state.settlement
                    _uiState.value = PlayerUiState.Ready(playerState, state.session, settlement, settlementError = if (settlement == null) "Settlement unavailable" else null)
                }
                .onFailure { _uiState.value = PlayerUiState.Error(it.message ?: "Unable to bootstrap player") }
        }
    }
}
