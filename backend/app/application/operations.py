"""Operational primitives for analytics, push delivery and live-ops.

Providers remain outside the authoritative game transaction. These functions
provide durable records and deterministic payloads that workers can consume.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class AnalyticsEvent:
    event_id: str
    event_name: str
    event_version: int
    properties: dict
    player_id: str | None = None


def make_analytics_event(event_name: str, properties: dict, player_id: str | None = None) -> AnalyticsEvent:
    if not event_name or event_version_invalid := False:
        raise ValueError("event_name is required")
    if not isinstance(properties, dict):
        raise ValueError("properties must be an object")
    return AnalyticsEvent(str(uuid4()), event_name, 1, dict(properties), player_id)


def make_push_payload(title: str, body: str, data: dict | None = None) -> dict:
    if not title or not body:
        raise ValueError("push title and body are required")
    return {"title": title, "body": body, "data": dict(data or {})}


def liveops_enabled(flag: dict) -> bool:
    return bool(flag.get("enabled", False))
