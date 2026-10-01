"""BE-3 scratch probe: cost basis / unrealized P&L unavailable. Market data mocked. Not shipped."""
import json, sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from fastapi.testclient import TestClient
from app.api.main import app
from app.services.statement_importer import import_statement, combine_imported_snapshots
from app.services import portfolio_snapshot_builder as psb
from app.tests import conftest as c
from app.domain.ledger import reconstruct_position_lots

DOCS = Path(r"C:\projects\investments\portfolio\docs")


def make_mock():
    mock = MagicMock()
    inst = mock.return_value
    inst.get_etf_holdings.return_value = ("SPY", c._SPY_MOCK_ETF_HOLDINGS)
    inst.get_etf_holdings_for_date.return_value = ("SPY", c._SPY_MOCK_ETF_HOLDINGS)
    inst.get_historical_prices.side_effect = c._mock_price_rows
    inst.get_historical_prices_for_symbols.side_effect = c._mock_prices_for_symbols
    return mock


mock = make_mock()
patch_targets = [
    "app.services.market_data.MarketDataService",
    "app.analytics.overview.MarketDataService",
    "app.services.dashboard_history_engine.MarketDataService",
    "app.services.drawdown_engine.MarketDataService",
    "app.services.stress_engine.MarketDataService",
    "app.services.distribution_engine.MarketDataService",
    "app.services.exposure_engine.MarketDataService",
]
patches = [patch(t, mock) for t in patch_targets]
for p in patches:
    p.start()

from app.analytics.overview import build_portfolio_overview

ib = import_statement(DOCS / "IB2026.csv")
ff = import_statement(DOCS / "FF2026.pdf")


def ov(label, snap):
    o = build_portfolio_overview(snap)
    print(f"== overview {label}: total_market_value={o.total_market_value} total_cost_basis={o.total_cost_basis} "
          f"total_unrealized_pnl={o.total_unrealized_pnl} cost_basis_trust={o.cost_basis_trust}")
    return o

print("== IB positions null cost basis:", sum(p.cost_basis is None for p in ib.positions), "of", len(ib.positions))
ov("IB2026", ib)
o = ov("FF2026", ff)
vti = [p for p in ff.positions if p.symbol == "VTI"][0]
print("   FF VTI cost_basis", vti.cost_basis, "unrealized_pnl", vti.unrealized_pnl, "market_value", vti.market_value)
print("   FF top_positions", o.top_positions)
comb = combine_imported_snapshots([ib, ff])
ov("IB2026+FF2026", comb)
cvti = [p for p in comb.positions if p.symbol == "VTI"]
print("   combined VTI cost_basis", [p.cost_basis for p in cvti])

ib2 = ib.model_copy(deep=True)
ib2.statement.account_id = "OTHER"
ib2.statements = [ib2.statement]
both = combine_imported_snapshots([ib, ib2])
print("== merge IB(A)+IB(B) VUAA (cost_basis, upnl)", [(p.cost_basis, p.unrealized_pnl) for p in both.positions if p.symbol == "VUAA"],
      " single IB VUAA", [(p.cost_basis, p.unrealized_pnl) for p in ib.positions if p.symbol == "VUAA"])
ibnull = ib2.model_copy(deep=True)
for p in ibnull.positions:
    p.cost_basis = None
    p.unrealized_pnl = None
mixed = combine_imported_snapshots([ib, ibnull])
print("== merge stated + null VUAA", [(p.cost_basis, p.unrealized_pnl) for p in mixed.positions if p.symbol == "VUAA"])

lots = reconstruct_position_lots(ff)
flat = list(lots.values()) if isinstance(lots, dict) else list(lots)
flat = [l for v in flat for l in (v if isinstance(v, list) else [v])]
for l in flat:
    if l.symbol == "VTI":
        print("== FF VTI lot", l.source, l.original_quantity, "unit_cost", l.unit_cost,
              "remaining_cost_basis", l.remaining_cost_basis, "estimated", l.cost_basis_is_estimated)

from app.schemas.portfolio_engine import PortfolioEngineRequest
req_body = {
    "base_currency": "USD",
    "positions": [{"symbol": p.symbol, "quantity": p.quantity, "market_value": p.market_value, "currency": p.currency} for p in ib.positions],
    "cash_balances": [],
}
req = PortfolioEngineRequest.model_validate(req_body)
snap = psb.build_imported_snapshot_from_request(req)
print("== builder: cost_basis set", {p.cost_basis for p in snap.positions}, "unrealized set", {p.unrealized_pnl for p in snap.positions})
ov("request-path IB", snap)

client = TestClient(app)


def dump(r):
    assert r.status_code == 200, (r.status_code, r.text[:300])
    return json.dumps(r.json(), sort_keys=True)


def with_costs(snap, mode):
    s = snap.model_copy(deep=True)
    for p in s.positions:
        if mode == "null":
            p.cost_basis, p.unrealized_pnl = None, None
        elif mode == "fabricated":
            p.cost_basis, p.unrealized_pnl = p.market_value, 0.0
    return s


for label, base in (("IB2026", ib), ("FF2026", ff)):
    outs = {m: dump(client.post("/engines/dashboard-history/run-imported", json=with_costs(base, m).model_dump(mode="json")))
            for m in ("as_imported", "null", "fabricated")}
    print(f"== dashboard-history {label}: as_imported==null {outs['as_imported'] == outs['null']} ; "
          f"null==fabricated {outs['null'] == outs['fabricated']} ; len={len(outs['null'])}")

orig = psb.build_imported_snapshot_from_request


def old_builder(request):
    s = orig(request)
    for p in s.positions:
        p.cost_basis, p.unrealized_pnl = p.market_value, 0.0
    return s


mods = [m for m in list(sys.modules.values()) if getattr(m, "build_imported_snapshot_from_request", None) is orig]
print("== modules holding builder:", sorted(m.__name__ for m in mods))
body = {"benchmark_symbol": "SPY", "base_currency": "USD", "imported_at": "2026-04-11T00:00:00",
        "positions": req_body["positions"], "cash_balances": []}
routes = ["/engines/drawdown/run", "/engines/stress/run", "/engines/distribution/run", "/engines/exposure/run"]
new = {r: dump(client.post(r, json=body)) for r in routes}
for m in mods:
    m.build_imported_snapshot_from_request = old_builder
old = {r: dump(client.post(r, json=body)) for r in routes}
for m in mods:
    m.build_imported_snapshot_from_request = orig
for r in routes:
    same = new[r] == old[r]
    print(f"== {r}: null-basis output == fabricated-basis output: {same}")
    if not same:
        jn, jo = json.loads(new[r]), json.loads(old[r])
        for k in jn:
            if jn[k] != jo[k]:
                print("     differs at top-level key:", k)
        if "overview" in jn:
            print("     new overview cost:", jn["overview"]["total_cost_basis"], jn["overview"]["total_unrealized_pnl"], jn["overview"]["cost_basis_trust"])
            print("     old overview cost:", jo["overview"]["total_cost_basis"], jo["overview"]["total_unrealized_pnl"], jo["overview"]["cost_basis_trust"])

for p in patches:
    p.stop()
