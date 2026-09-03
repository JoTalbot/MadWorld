import pytest

from app.infrastructure import db


@pytest.mark.parametrize(
    ("configured", "expected"),
    [
        ("postgresql://user:pass@localhost/db", "postgresql+psycopg://user:pass@localhost/db"),
        ("postgres://user:pass@localhost/db", "postgresql+psycopg://user:pass@localhost/db"),
        ("postgresql+psycopg://user:pass@localhost/db", "postgresql+psycopg://user:pass@localhost/db"),
    ],
)
def test_postgresql_urls_use_psycopg(monkeypatch, configured, expected):
    monkeypatch.setenv("MADWORLD_DATABASE_URL", configured)

    captured = {}

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(db, "create_engine", fake_create_engine)

    db.create_engine_from_env()

    assert captured["url"] == expected
    assert captured["kwargs"]["pool_pre_ping"] is True


def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("MADWORLD_DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="MADWORLD_DATABASE_URL is required"):
        db.database_url()
