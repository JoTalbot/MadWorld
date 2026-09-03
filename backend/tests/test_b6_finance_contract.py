from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_b6_migration_contract():
    sql = (ROOT / "migrations/032_b6_finance_provenance.sql").read_text()
    for token in (
        "finance_credit_agreements",
        "finance_collateral",
        "finance_insurance_policies",
        "finance_investments",
        "asset_provenance_history",
        "finance_events",
    ):
        assert token in sql
    assert "outstanding >= 0 AND outstanding <= principal" in sql
    assert "UNIQUE(credit_agreement_id,asset_id)" in sql
    assert "event_key TEXT NOT NULL UNIQUE" in sql


def test_b6_api_contract():
    code = (ROOT / "app/api/phase10_finance_routes.py").read_text()
    for token in (
        '"/credit"',
        '"/credit/{agreement_id}/repay"',
        '"/credit/{agreement_id}/default"',
        '"/credit/{agreement_id}/collateral"',
        '"/insurance"',
        '"/investment"',
        '"/provenance"',
        '"/provenance/{asset_id}"',
    ):
        assert token in code
    assert "require_key" in code and "store_response" in code
    assert "_asset_owned" in code


def test_b6_router_is_registered():
    main = (ROOT / "app/main.py").read_text()
    assert "phase10_finance_router" in main
