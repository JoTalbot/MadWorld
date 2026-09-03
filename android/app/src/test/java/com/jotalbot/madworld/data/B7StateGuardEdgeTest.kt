package com.jotalbot.madworld.data

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class B7StateGuardEdgeTest {
    @Test
    fun acceptsEqualVersionAsIdempotentSnapshot() {
        val guard = StaleStateGuard()

        assertTrue(guard.accept("settlement", 12))
        assertTrue(guard.accept("settlement", 12))
    }

    @Test
    fun rejectsOlderSnapshotAfterNewerVersion() {
        val guard = StaleStateGuard()

        assertTrue(guard.accept("territory", 20))
        assertFalse(guard.accept("territory", 19))
        assertFalse(guard.accept("territory", 1))
    }
}
