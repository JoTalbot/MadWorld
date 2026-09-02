package com.jotalbot.madworld

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import java.util.UUID

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MadWorldApp() }
    }
}

@Composable
private fun MadWorldApp(viewModel: PlayerViewModel = viewModel()) {
    val playerId = remember { UUID.nameUUIDFromBytes("madworld-dev-player".toByteArray()) }
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var bootstrapName by remember { mutableStateOf("Wanderer") }

    LaunchedEffect(playerId) { viewModel.load(playerId) }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            Column(
                modifier = Modifier.fillMaxSize().padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Text("MadWorld", style = MaterialTheme.typography.headlineLarge)
                Text("Persistent wasteland online", modifier = Modifier.padding(top = 8.dp))
                when (val state = uiState) {
                    PlayerUiState.Loading -> CircularProgressIndicator(modifier = Modifier.padding(24.dp))
                    is PlayerUiState.Ready -> {
                        val character = state.state.character
                        Text(character?.name ?: "No character", modifier = Modifier.padding(top = 20.dp))
                        Text("Vehicles: ${state.state.vehicles.size}")
                        state.state.vehicles.firstOrNull()?.let { vehicle ->
                            Text("${vehicle.chassisCode} · fuel ${vehicle.fuel} · durability ${vehicle.durability}")
                        }
                        if (state.offline) Text("Cached state", modifier = Modifier.padding(top = 8.dp))
                    }
                    is PlayerUiState.Error -> {
                        Text(state.message, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 20.dp))
                        Button(onClick = { viewModel.load(playerId) }, modifier = Modifier.padding(top = 12.dp)) { Text("Retry") }
                    }
                }
                if (uiState !is PlayerUiState.Ready) {
                    Button(
                        onClick = { viewModel.bootstrap(playerId, bootstrapName) },
                        modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                    ) { Text("Enter the wasteland") }
                }
            }
        }
    }
}
