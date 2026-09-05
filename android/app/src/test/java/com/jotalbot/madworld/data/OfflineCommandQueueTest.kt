package com.jotalbot.madworld.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class OfflineCommandQueueTest {
    private fun cmd(key: String, name: String = "bootstrap_player") =
        OfflineCommandQueue.Command(name, """{"character_name":"Rook $key"}""", key)

    @Test
    fun enqueuePreservesFifoOrderAndPersistsAcrossInstances() {
        val store = InMemoryKeyValueStore()
        val queue = OfflineCommandQueue(store)
        queue.enqueue(cmd("k1")); queue.enqueue(cmd("k2")); queue.enqueue(cmd("k3"))
        assertEquals(listOf("k1", "k2", "k3"), queue.peek().map { it.idempotencyKey })
        // A fresh instance over the same storage sees the same durable queue.
        assertEquals(queue.peek(), OfflineCommandQueue(store).peek())
    }

    @Test
    fun duplicateIdempotencyKeyIsIgnored() {
        val queue = OfflineCommandQueue(InMemoryKeyValueStore())
        queue.enqueue(cmd("same")); queue.enqueue(cmd("same", name = "create_corporation"))
        assertEquals(1, queue.peek().size)
        assertEquals("bootstrap_player", queue.peek().single().name)
    }

    @Test
    fun removeAndClear() {
        val queue = OfflineCommandQueue(InMemoryKeyValueStore())
        queue.enqueue(cmd("a")); queue.enqueue(cmd("b"))
        queue.remove("a")
        assertEquals(listOf("b"), queue.peek().map { it.idempotencyKey })
        queue.remove("missing")
        assertEquals(1, queue.peek().size)
        queue.clear()
        assertTrue(queue.peek().isEmpty())
    }

    @Test
    fun corruptStorageDegradesToEmptyQueueInsteadOfCrashing() {
        val store = InMemoryKeyValueStore().apply { put("queue", "{not json") }
        val queue = OfflineCommandQueue(store)
        assertTrue(queue.peek().isEmpty())
        queue.enqueue(cmd("recovered"))
        assertEquals(listOf("recovered"), queue.peek().map { it.idempotencyKey })
    }

    @Test
    fun payloadRoundTripsVerbatim() {
        val queue = OfflineCommandQueue(InMemoryKeyValueStore())
        val payload = """{"code":"RÄV","name":"Quote \" and \\ backslash","tax_bps":250}"""
        queue.enqueue(OfflineCommandQueue.Command("create_corporation", payload, "p1"))
        assertEquals(payload, queue.peek().single().payload)
    }
}
