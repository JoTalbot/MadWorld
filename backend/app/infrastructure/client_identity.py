"""Derive abuse-control keys for a request.

Two independent keys are produced:

* ``network`` – the client IP. Behind a reverse proxy the socket peer is the
  proxy, so ``X-Forwarded-For`` is honoured **only** when the peer is in
  ``MADWORLD_TRUSTED_PROXIES`` (comma-separated IPs/CIDRs). Otherwise the header
  is ignored, because it is trivially spoofable.
* ``session`` – a stable hash of the bearer token, when present. This gives one
  per-player budget even when many players share a NAT/proxy IP, and stops one
  player from escaping the limit by rotating IPs.
"""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger("madworld.security")


@dataclass(frozen=True, slots=True)
class ClientIdentity:
    network: str
    session: str | None

    @property
    def keys(self) -> tuple[str, ...]:
        return (f"net:{self.network}",) + ((f"sess:{self.session}",) if self.session else ())


def parse_trusted_proxies(raw: str | None) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    networks = []
    for item in (raw or "").split(","):
        item = item.strip()
        if not item: continue
        try: networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            # A typo in MADWORLD_TRUSTED_PROXIES must not take the API down; the entry is simply not trusted.
            logger.warning("ignoring invalid trusted proxy entry %r", item)
    return networks


def _is_trusted(peer: str, trusted: list[ipaddress.IPv4Network | ipaddress.IPv6Network]) -> bool:
    try: address = ipaddress.ip_address(peer)
    except ValueError: return False
    return any(address in network for network in trusted)


def resolve_client_ip(peer: str | None, forwarded_for: str | None, trusted: list[ipaddress.IPv4Network | ipaddress.IPv6Network]) -> str:
    peer = peer or "unknown"
    if not forwarded_for or not _is_trusted(peer, trusted): return peer
    # Walk right-to-left skipping trusted hops; the first untrusted hop is the client.
    hops = [h.strip() for h in forwarded_for.split(",") if h.strip()]
    for hop in reversed(hops):
        if not _is_trusted(hop, trusted): return hop
    return hops[0] if hops else peer


def session_key(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "): return None
    token = authorization[7:].strip()
    if not token: return None
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:32]


def identify(peer: str | None, forwarded_for: str | None, authorization: str | None, trusted: list[ipaddress.IPv4Network | ipaddress.IPv6Network] | None = None) -> ClientIdentity:
    trusted = parse_trusted_proxies(os.getenv("MADWORLD_TRUSTED_PROXIES")) if trusted is None else trusted
    return ClientIdentity(resolve_client_ip(peer, forwarded_for, trusted), session_key(authorization))
