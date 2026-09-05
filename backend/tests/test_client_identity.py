from ipaddress import ip_network

from app.infrastructure.client_identity import identify, parse_trusted_proxies, resolve_client_ip, session_key

TRUSTED = [ip_network("10.0.0.0/8"), ip_network("127.0.0.1/32")]


def test_forwarded_for_is_ignored_from_untrusted_peer() -> None:
    assert resolve_client_ip("203.0.113.9", "1.2.3.4", TRUSTED) == "203.0.113.9"


def test_forwarded_for_walks_past_trusted_hops() -> None:
    assert resolve_client_ip("10.0.0.5", "198.51.100.7, 10.0.0.2", TRUSTED) == "198.51.100.7"
    assert resolve_client_ip("10.0.0.5", "198.51.100.7", TRUSTED) == "198.51.100.7"


def test_all_hops_trusted_falls_back_to_leftmost() -> None:
    assert resolve_client_ip("10.0.0.5", "10.0.0.1, 10.0.0.2", TRUSTED) == "10.0.0.1"


def test_no_header_or_no_trusted_proxies_uses_peer() -> None:
    assert resolve_client_ip("10.0.0.5", None, TRUSTED) == "10.0.0.5"
    assert resolve_client_ip("10.0.0.5", "198.51.100.7", []) == "10.0.0.5"
    assert resolve_client_ip(None, None, []) == "unknown"


def test_session_key_is_hashed_and_only_for_bearer() -> None:
    assert session_key(None) is None and session_key("Basic abc") is None and session_key("Bearer   ") is None
    key = session_key("Bearer secret-token")
    assert key and "secret" not in key and key == session_key("Bearer secret-token") and len(key) == 32


def test_identity_keys_include_session_when_present() -> None:
    ident = identify("203.0.113.9", None, "Bearer t", trusted=[])
    assert ident.keys[0] == "net:203.0.113.9" and ident.keys[1].startswith("sess:") and len(ident.keys) == 2
    assert identify("203.0.113.9", None, None, trusted=[]).keys == ("net:203.0.113.9",)


def test_parse_trusted_proxies_accepts_ips_and_cidrs() -> None:
    nets = parse_trusted_proxies(" 10.0.0.0/8, 192.0.2.1 ,, ")
    assert [str(n) for n in nets] == ["10.0.0.0/8", "192.0.2.1/32"]


def test_invalid_trusted_proxy_entries_are_ignored_not_fatal() -> None:
    assert [str(n) for n in parse_trusted_proxies("garbage, 10.0.0.0/8")] == ["10.0.0.0/8"]
