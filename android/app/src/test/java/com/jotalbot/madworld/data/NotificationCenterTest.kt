package com.jotalbot.madworld.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class NotificationCenterTest {
    @Test
    fun publishPersistsAndRestoresAcrossInstances() {
        val store = InMemoryKeyValueStore()
        var now = 1_000L
        val center = NotificationCenter(store) { now }
        center.publish("Queued", "bootstrap will sync", "info"); now += 5
        center.publish("Paused", "1 command remains", "warning")
        val restored = NotificationCenter(store).items.value
        assertEquals(listOf("Queued", "Paused"), restored.map { it.title })
        assertEquals(listOf(1_000L, 1_005L), restored.map { it.createdAt })
        assertEquals("warning", restored[1].severity)
        assertEquals(2, NotificationCenter(store).unreadCount())
    }

    @Test
    fun markReadIsTargetedAndMarkAllReadClearsUnread() {
        val center = NotificationCenter(InMemoryKeyValueStore()) { 0L }
        center.publish("a", "x"); center.publish("b", "y")
        val first = center.items.value.first().id
        center.markRead(first)
        assertEquals(listOf(true, false), center.items.value.map { it.read })
        center.markAllRead()
        assertEquals(0, center.unreadCount())
    }

    @Test
    fun historyIsBoundedToMostRecentItems() {
        val center = NotificationCenter(InMemoryKeyValueStore()) { 0L }
        repeat(NotificationCenter.MAX_ITEMS + 10) { center.publish("n$it", "body") }
        assertEquals(NotificationCenter.MAX_ITEMS, center.items.value.size)
        assertEquals("n10", center.items.value.first().title)
    }

    @Test
    fun corruptStorageStartsEmpty() {
        val store = InMemoryKeyValueStore().apply { put("items", "garbage") }
        assertTrue(NotificationCenter(store).items.value.isEmpty())
    }
}
