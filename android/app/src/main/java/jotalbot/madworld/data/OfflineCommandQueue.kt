package com.jotalbot.madworld.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

/** Durable client-side queue for commands that are safe to retry after reconnect.
 * The server remains authoritative: queued entries carry only command intent and
 * an idempotency key, never an authoritative result or balance.
 */
class OfflineCommandQueue(context: Context) {
    data class Command(
        val name: String,
        val payload: String,
        val idempotencyKey: String,
    )

    private val prefs = context.getSharedPreferences("madworld_offline_commands", Context.MODE_PRIVATE)

    fun enqueue(command: Command) {
        val items = read().toMutableList()
        if (items.none { it.idempotencyKey == command.idempotencyKey }) {
            items.add(command)
            write(items)
        }
    }

    fun peek(): List<Command> = read()

    fun remove(idempotencyKey: String) {
        write(read().filterNot { it.idempotencyKey == idempotencyKey })
    }

    fun clear() {
        prefs.edit().remove("queue").apply()
    }

    private fun read(): List<Command> {
        val raw = prefs.getString("queue", null) ?: return emptyList()
        return runCatching {
            val array = JSONArray(raw)
            buildList {
                for (i in 0 until array.length()) {
                    val item = array.getJSONObject(i)
                    add(
                        Command(
                            name = item.getString("name"),
                            payload = item.getString("payload"),
                            idempotencyKey = item.getString("idempotencyKey"),
                        ),
                    )
                }
            }
        }.getOrDefault(emptyList())
    }

    private fun write(items: List<Command>) {
        val array = JSONArray()
        items.forEach { command ->
            array.put(
                JSONObject()
                    .put("name", command.name)
                    .put("payload", command.payload)
                    .put("idempotencyKey", command.idempotencyKey),
            )
        }
        prefs.edit().putString("queue", array.toString()).apply()
    }
}
