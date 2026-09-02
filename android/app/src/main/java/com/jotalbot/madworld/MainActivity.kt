package com.jotalbot.madworld

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
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
                modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text("MadWorld", style = MaterialTheme.typography.headlineLarge)
                Text("Persistent wasteland online")
                when (val state = uiState) {
                    PlayerUiState.Loading -> CircularProgressIndicator(modifier = Modifier.padding(24.dp))
                    PlayerUiState.SignedOut -> {
                        OutlinedTextField(value = handle, onValueChange = { handle = it }, label = { Text("Handle") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                        Button(onClick = { viewModel.signIn(handle) }, modifier = Modifier.fillMaxWidth()) { Text("Connect") }
                    }
                    is PlayerUiState.Ready -> {
                        Text("Pilot: ${state.session.handle}", style = MaterialTheme.typography.titleLarge)
                        state.state.character?.let { Text("${it.name} · level ${it.level}") }
                        state.state.vehicles.firstOrNull()?.let { vehicle -> Text("Vehicle: ${vehicle.chassisCode} · fuel ${vehicle.fuel} · durability ${vehicle.durability}") }
                        if (state.state.character == null) {
                            OutlinedTextField(value = characterName, onValueChange = { characterName = it }, label = { Text("Character") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                            Button(onClick = { viewModel.bootstrap(characterName) }, modifier = Modifier.fillMaxWidth()) { Text("Enter the wasteland") }
                        }
                        SettlementPanel(state, onRefresh = viewModel::refreshSettlement)
                        if (state.offline) Text("Cached state", color = MaterialTheme.colorScheme.secondary)
                    }
                    is PlayerUiState.Error -> {
                        Text(state.message, color = MaterialTheme.colorScheme.error)
                        Button(onClick = { viewModel.load() }) { Text("Retry") }
                    }
                }
            }
        }
    }
}

@Composable
private fun SettlementPanel(state: PlayerUiState.Ready, onRefresh: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Settlement", style = MaterialTheme.typography.titleLarge)
            val settlement = state.settlement
            if (settlement == null) {
                Text(state.settlementError ?: "Loading settlement…", color = MaterialTheme.colorScheme.error)
            } else {
                Text("Region: ${settlement.region}")
                Text("Level: ${settlement.level} · version ${settlement.version}")
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    CapabilityButton("Garage", settlement.capabilities["garage"] == true)
                    CapabilityButton("Warehouse", settlement.capabilities["warehouse"] == true)
                }
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    CapabilityButton("Workshop", settlement.capabilities["workshop"] == true)
                    CapabilityButton("Contracts", settlement.capabilities["contracts"] == true)
                    CapabilityButton("Market", settlement.capabilities["market"] == true)
                }
                if (settlement.modules.isNotEmpty()) {
                    Text("Modules")
                    settlement.modules.toSortedMap().forEach { (name, level) -> Text("$name: $level") }
                }
            }
            OutlinedButton(onClick = onRefresh, modifier = Modifier.fillMaxWidth()) { Text("Refresh settlement") }
        }
    }
}

@Composable
private fun RowScope.CapabilityButton(label: String, enabled: Boolean) {
    OutlinedButton(onClick = {}, enabled = enabled, modifier = Modifier.weight(1f)) { Text(label) }
}
