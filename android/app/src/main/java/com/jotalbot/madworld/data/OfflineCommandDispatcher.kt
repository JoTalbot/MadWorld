package com.jotalbot.madworld.data

/** Executes one queued command against authoritative server APIs. */
fun interface OfflineCommandDispatcher {
    fun dispatch(command: OfflineCommandQueue.Command, session: SessionState)
}

/**
 * Drains in FIFO order. A failed command remains queued so transient connectivity
 * cannot silently discard player intent. Successful commands are removed only after
 * the authoritative request returns successfully.
 */
class OfflineQueueDrainer(
    private val queue: OfflineCommandQueue,
    private val dispatcher: OfflineCommandDispatcher,
) {
    fun drain(session: SessionState): DrainResult {
        var delivered = 0
        for (command in queue.peek()) {
            try {
                dispatcher.dispatch(command, session)
                queue.remove(command.idempotencyKey)
                delivered++
            } catch (_: Throwable) {
                return DrainResult(delivered, remaining = queue.peek().size)
            }
        }
        return DrainResult(delivered, remaining = 0)
    }

    data class DrainResult(val delivered: Int, val remaining: Int)
}
