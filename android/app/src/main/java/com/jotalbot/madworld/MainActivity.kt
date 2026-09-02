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
import androidx.compose.material3.OutlinedTextField
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

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MadWorldApp() }
    }
}

@Composable
private fun MadWorldApp(viewModel: PlayerViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var handle by remember { mutableStateOf("Wanderer") }
    var characterName by remember { mutableStateOf("Wanderer") }

    LaunchedEffect(Unit) { viewModel.load() }

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
                    PlayerUiState.SignedOut -> {
                        OutlinedTextField(value = handle, onValueChange = { handle = it }, label = { Text("Handle") }, singleLine = true)
                        Button(onClick = { viewModel.signIn(handle) }, modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) { Text("Connect") }
                    }
                    is PlayerUiState.Ready -> {
                        val character = state.state.character
                        Text("Pilot: ${state.session.handle}", modifier = Modifier.padding(top = 20.dp))
                        Text(character?.name ?: "No character")
                        Text("Vehicles: ${state.state.vehicles.size}")
                        state.state.vehicles.firstOrNull()?.let { vehicle -> Text("${vehicle.chassisCode} · fuel ${vehicle.fuel} · durability ${vehicle.durability}") }
                        if (state.state.character == null) {
                            OutlinedTextField(value = characterName, onValueChange = { characterName = it }, label = { Text("Character") }, singleLine = true, modifier = Modifier.padding(top = 12.dp))
                            Button(onClick = { viewModel.bootstrap(characterName) }, modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) { Text("Enter the wasteland") }
                        }
                        if (state.offline) Text("Cached state", modifier = Modifier.padding(top = 8.dp))
                    }
                    is PlayerUiState.Error -> {
                        Text(state.message, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 20.dp))
                        Button(onClick = { viewModel.load() }, modifier = Modifier.padding(top = 12.dp)) { Text("Retry") }
                    }
                }
            }
        }
    }
}
