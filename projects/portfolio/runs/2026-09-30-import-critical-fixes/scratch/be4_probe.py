"""BE-4 scratch probe: legacy Freedom24 cost-basis scrub through analyze-combined. Market data mocked. Not shipped."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from fastapi.testclient import TestClient
from app.api.main import app
from app.services.statement_importer import import_statement, combine_imported_snapshots, scrub_legacy_freedom24_cost_basis
from app.tests import conftest as c

DOCS = Path(r"C:\projects\investments\portfolio\docs")
ib = import_statement(DOCS / "IB2026.csv")
ff = import_statement(DOCS / "FF2026.pdf")
espp = import_statement(DOCS / "ESPP2026.pdf")

mock = MagicMock()
inst = mock.return_value
inst.get_etf_holdings.return_value = ("SPY", c._SPY_MOCK_ETF_HOLDINGS)
inst.get_etf_holdings_for_date.return_value = ("SPY", c._SPY_MOCK_ETF_HOLDINGS)
inst.get_historical_prices.side_effect = c._mock_price_rows
inst.get_historical_prices_for_symbols.side_effect = c._mock_prices_for_symbols
client = TestClient(app)

# legacy shape: what pre-US-46.4 builds stored for FF2026
legacy_ff = ff.model_copy(deep=True)
for p in legacy_ff.positions:
    p.cost_basis = round(p.market_value, 2)
    p.unrealized_pnl = 0.0
print("legacy FF positions:", [(p.symbol, p.cost_basis, p.unrealized_pnl) for p in legacy_ff.positions])
print("fresh  FF positions:", [(p.symbol, p.cost_basis, p.unrealized_pnl) for p in ff.positions])


def call(snaps):
    return client.post("/portfolios/import/analyze-combined", json={"snapshots": [s.model_dump(mode="json") for s in snaps]})


def show(label, r):
    print("==", label, r.status_code)
    if r.status_code != 200:
        print("  detail:", r.json())
        return None
    j = r.json()
    o = j["overview"]
    print("  positions:", [(p["symbol"], p["cost_basis"], p["unrealized_pnl"]) for p in j["snapshot"]["positions"] if p["symbol"] in ("VTI",)] or "(no VTI)")
    print("  overview: total_cost_basis=%r total_unrealized_pnl=%r cost_basis_trust=%r" % (o["total_cost_basis"], o["total_unrealized_pnl"], o["cost_basis_trust"]))
    print("  admission:", j["admission_summary"]["decision"], j["admission_summary"]["trust_level"])
    return j


with patch("app.services.exposure_engine.MarketDataService", mock):
    show("legacy FF2026 (VTI 3018.96 / 0.00)", call([legacy_ff]))
    j_fresh = show("fresh FF2026", call([ff]))
    j_legacy = call([legacy_ff]).json()
    j_fresh = call([ff]).json()
    for j in (j_legacy, j_fresh):
        j["admission_summary"]["provenance"]["generated_at"] = None
    print("legacy-scrubbed response == fresh response:", j_legacy == j_fresh)
    show("IB2026 alone", call([ib]))
    # stored (already combined) multi_broker IB+FF with legacy FF values: over-nulling of IB accepted per D-12
    stored_mixed = combine_imported_snapshots([ib, legacy_ff])
    print("stored IB+legacyFF importer:", stored_mixed.statement.importer,
          "IB VUAA stored:", [(p.cost_basis, p.unrealized_pnl) for p in stored_mixed.positions if p.symbol == "VUAA"])
    j = show("stored combined IB+FF (multi_broker)", call([stored_mixed]))
    print("  VUAA after scrub:", [(p["cost_basis"], p["unrealized_pnl"]) for p in j["snapshot"]["positions"] if p["symbol"] == "VUAA"])
    # IB + ESPP stored combined (no Freedom24) untouched
    ib_espp = combine_imported_snapshots([ib, espp])
    j = show("stored IB+ESPP (no Freedom24)", call([ib_espp]))
    print("  VUAA:", [(p["cost_basis"], p["unrealized_pnl"]) for p in j["snapshot"]["positions"] if p["symbol"] == "VUAA"])

# idempotence + no mutation + identity on fresh
once = scrub_legacy_freedom24_cost_basis(legacy_ff)
twice = scrub_legacy_freedom24_cost_basis(once)
print("idempotent:", once == twice, "| input not mutated:", legacy_ff.positions[0].cost_basis is not None,
      "| fresh FF returned as same object:", scrub_legacy_freedom24_cost_basis(ff) is ff,
      "| IB returned as same object:", scrub_legacy_freedom24_cost_basis(ib) is ib)
