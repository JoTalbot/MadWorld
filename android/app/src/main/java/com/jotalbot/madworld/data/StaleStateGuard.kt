package com.jotalbot.madworld.data

/** Small client-side guard for versioned domain snapshots. */
class StaleStateGuard {
    private val versions = mutableMapOf<String, Long>()

    @Synchronized
    fun accept(key: String, version: Long): Boolean {
        val previous = versions[key]
        if (previous != null && version < previous) return false
        versions[key] = version
        return true
    }

    @Synchronized
    fun version(key: String): Long? = versions[key]

    @Synchronized
    fun clear() = versions.clear()
}
