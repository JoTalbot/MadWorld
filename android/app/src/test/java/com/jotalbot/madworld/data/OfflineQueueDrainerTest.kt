package com.jotalbot.madworld.data

import org.junit.Assert.assertEquals
import org.junit.Test
import java.util.UUID

class OfflineQueueDrainerTest {
    private val session = SessionState(UUID.randomUUID(), "rook", "token", "2030-01-01T00:00:00Z")
    private fun cmd(key: String) = OfflineCommandQueue.Command("bootstrap_player", "{}", key)

    @Test
    fun drainsInOrderAndRemovesOnlyDeliveredCommands() {
        val queue = OfflineCommandQueue(InMemoryKeyValueStore())
        listOf("a", "b", "c").forEach { queue.enqueue(cmd(it)) }
        val delivered = mutableListOf<String>()
        val result = OfflineQueueDrainer(queue) { command, _ -> delivered += command.idempotencyKey }.drain(session)
        assertEquals(listOf("a", "b", "c"), delivered)
        assertEquals(OfflineQueueDrainer.DrainResult(delivered = 3, remaining = 0), result)
        assertEquals(0, queue.peek().size)
    }

    @Test
    fun failureStopsDrainAndKeepsFailedAndLaterCommandsQueued() {
        val queue = OfflineCommandQueue(InMemoryKeyValueStore())
        listOf("a", "b", "c").forEach { queue.enqueue(cmd(it)) }
        val result = OfflineQueueDrainer(queue) { command, _ ->
            if (command.idempotencyKey == "b") throw ApiException("HTTP 503")
        }.drain(session)
        assertEquals(OfflineQueueDrainer.DrainResult(delivered = 1, remaining = 2), result)
        assertEquals(listOf("b", "c"), queue.peek().map { it.idempotencyKey })
    }

    @Test
    fun retryAfterFailureResumesFromFailedCommandWithSameIdempotencyKey() {
        val queue = OfflineCommandQueue(InMemoryKeyValueStore())
        listOf("a", "b").forEach { queue.enqueue(cmd(it)) }
        var failOnce = true
        val seen = mutableListOf<String>()
        val drainer = OfflineQueueDrainer(queue) { command, _ ->
            seen += command.idempotencyKey
            if (command.idempotencyKey == "b" && failOnce) { failOnce = false; throw ApiException("offline") }
        }
        drainer.drain(session)
        drainer.drain(session)
        assertEquals(listOf("a", "b", "b"), seen)
        assertEquals(0, queue.peek().size)
    }

    @Test
    fun emptyQueueIsNoop() {
        val result = OfflineQueueDrainer(OfflineCommandQueue(InMemoryKeyValueStore())) { _, _ -> error("must not dispatch") }.drain(session)
        assertEquals(OfflineQueueDrainer.DrainResult(0, 0), result)
    }
}
