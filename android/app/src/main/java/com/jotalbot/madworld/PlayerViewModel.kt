package com.jotalbot.madworld

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.jotalbot.madworld.data.MadWorldApi
import com.jotalbot.madworld.data.PlayerRepository
import com.jotalbot.madworld.data.PlayerState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID

sealed interface PlayerUiState {
    data object Loading : PlayerUiState
    data class Ready(val state: PlayerState, val offline: Boolean = false) : PlayerUiState
    data class Error(val message: String, val cached: PlayerState? = null) : PlayerUiState
}

class PlayerViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = PlayerRepository(application, MadWorldApi(BuildConfig.MADWORLD_API_URL))
    private val _uiState = MutableStateFlow<PlayerUiState>(PlayerUiState.Loading)
    val uiState: StateFlow<PlayerUiState> = _uiState.asStateFlow()

    fun load(playerId: UUID) {
        val cached = repository.cached(playerId)
        if (cached != null) _uiState.value = PlayerUiState.Ready(cached, offline = true)
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.refresh(playerId) }
                .onSuccess { _uiState.value = PlayerUiState.Ready(it) }
                .onFailure { error ->
                    if (cached == null) _uiState.value = PlayerUiState.Error(error.message ?: "Unable to load player state")
                }
        }
    }

    fun bootstrap(playerId: UUID, characterName: String) {
        _uiState.value = PlayerUiState.Loading
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { repository.bootstrap(playerId, characterName) }
                .onSuccess { _uiState.value = PlayerUiState.Ready(it) }
                .onFailure { _uiState.value = PlayerUiState.Error(it.message ?: "Unable to bootstrap player") }
        }
    }
}
