package com.jotalbot.madworld.data

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class B7StateGuardTest {
    @Test
    fun rejectsOlderSnapshot() {
        val guard = StaleStateGuard()
        assertTrue(guard.accept("player", 4))
        assertTrue(guard.accept("player", 4))
        assertTrue(guard.accept("player", 7))
        assertFalse(guard.accept("player", 6))
    }

    @Test
    fun tracksVersionsIndependently() {
        val guard = StaleStateGuard()
        assertTrue(guard.accept("economy", 9))
        assertTrue(guard.accept("territory", 2))
        assertFalse(guard.accept("economy", 8))
        assertTrue(guard.accept("territory", 3))
    }
}
