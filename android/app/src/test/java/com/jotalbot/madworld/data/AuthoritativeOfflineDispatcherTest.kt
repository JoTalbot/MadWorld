package com.jotalbot.madworld.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test
import java.util.UUID

/** The dispatcher is an allowlist: unknown intents must be rejected, never executed optimistically. */
class AuthoritativeOfflineDispatcherTest {
    private val session = SessionState(UUID.randomUUID(), "rook", "token", "2030-01-01T00:00:00Z")
    // MadWorldApi with an unroutable base URL: the test only checks that dispatch rejects before any network I/O.
    private val dispatcher = AuthoritativeOfflineDispatcher(MadWorldApi("http://127.0.0.1:9"))

    @Test
    fun unknownCommandIsRejected() {
        val ex = assertThrows(ApiException::class.java) {
            dispatcher.dispatch(OfflineCommandQueue.Command("delete_everything", "{}", "k"), session)
        }
        assertEquals("Unsupported offline command: delete_everything", ex.message)
    }

    @Test
    fun malformedPayloadFailsBeforeNetwork() {
        assertThrows(org.json.JSONException::class.java) {
            dispatcher.dispatch(OfflineCommandQueue.Command("create_corporation", """{"code":"X"}""", "k"), session)
        }
    }
}
