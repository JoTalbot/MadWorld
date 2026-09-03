package com.jotalbot.madworld.data

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

/** Local/in-app notification foundation. Server push delivery belongs to B9. */
class NotificationCenter(context: Context) {
    data class Notification(
        val id: String,
        val title: String,
        val body: String,
        val severity: String = "info",
        val createdAt: Long = System.currentTimeMillis(),
        val read: Boolean = false,
    )

    private val prefs = context.getSharedPreferences("madworld_notifications", Context.MODE_PRIVATE)
    private val _items = MutableStateFlow(read())
    val items: StateFlow<List<Notification>> = _items.asStateFlow()

    fun publish(title: String, body: String, severity: String = "info") {
        val item = Notification(UUID.randomUUID().toString(), title, body, severity)
        persist((_items.value + item).takeLast(50))
    }

    fun markRead(id: String) {
        persist(_items.value.map { if (it.id == id) it.copy(read = true) else it })
    }

    fun markAllRead() = persist(_items.value.map { it.copy(read = true) })

    private fun persist(items: List<Notification>) {
        val array = JSONArray()
        items.forEach {
            array.put(JSONObject().put("id", it.id).put("title", it.title).put("body", it.body)
                .put("severity", it.severity).put("createdAt", it.createdAt).put("read", it.read))
        }
        prefs.edit().putString("items", array.toString()).apply()
        _items.value = items
    }

    private fun read(): List<Notification> = runCatching {
        val array = JSONArray(prefs.getString("items", "[]"))
        buildList {
            for (i in 0 until array.length()) {
                val x = array.getJSONObject(i)
                add(Notification(x.getString("id"), x.getString("title"), x.getString("body"), x.getString("severity"), x.getLong("createdAt"), x.getBoolean("read")))
            }
        }
    }.getOrDefault(emptyList())
}
