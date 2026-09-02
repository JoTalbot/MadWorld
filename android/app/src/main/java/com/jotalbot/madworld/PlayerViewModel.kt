package com.jotalbot.madworld

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.jotalbot.madworld.data.MadWorldApi
import com.jotalbot.madworld.data.PlayerRepository
import com.jotalbot.madworld.data.PlayerState
import com.jotalbot.madworld.data.SessionState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed interface PlayerUiState {
    data object Loading : PlayerUiState
    data object SignedOut : PlayerUiState
    data class Ready(val state: PlayerState, val session: SessionState, val offline: Boolean = false) : PlayerUiState
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
        if (cached != null) _uiState.value = PlayerUiState.Ready(cached, session, offline = true)
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.refresh(session) }
                .onSuccess { _uiState.value = PlayerUiState.Ready(it, session) }
                .onFailure { error -> if (cached == null) _uiState.value = PlayerUiState.Error(error.message ?: "Unable to load player state") }
        }
    }

    fun signIn(handle: String) {
        _uiState.value = PlayerUiState.Loading
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.createSession(handle.trim()) }
                .onSuccess { session ->
                    runCatching { repository.refresh(session) }
                        .onSuccess { _uiState.value = PlayerUiState.Ready(it, session) }
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
                .onSuccess { _uiState.value = PlayerUiState.Ready(it, state.session) }
                .onFailure { _uiState.value = PlayerUiState.Error(it.message ?: "Unable to bootstrap player") }
        }
    }
}
