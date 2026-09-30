"""F3: is the backend path idempotent under re-adding the same statement?
Dashboard history on IB2026 alone vs combine(IB2026, IB2026), frozen prices, network off."""
import socket, sys
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError("net off"))
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
import app.services.instrument_enrichment as ie
ie.enrich_imported_instruments = lambda s, m: s
from app.services.statement_importer import import_statement, combine_imported_snapshots
from app.services.dashboard_history_engine import run_imported_dashboard_history
from app.scripts.frozen_market_data import FrozenMarketData

D = r"C:\projects\investments\portfolio\docs"
ib = import_statement(D + r"\IB2026.csv")
both = combine_imported_snapshots([ib, import_statement(D + r"\IB2026.csv")])
out = {}
for label, s in (("IB2026", ib), ("IB2026+IB2026", both)):
    h = run_imported_dashboard_history(s, "SPY", market_data=FrozenMarketData.from_file())
    m = h.range_metrics["3M"].summary
    a = h.range_metrics["All"].summary
    out[label] = (len(h.daily_states), m.start_value, m.end_value, m.time_weighted_return_pct, m.money_weighted_return_pct,
                  a.time_weighted_return_pct, a.money_weighted_return_pct, a.net_contributions)
    print(label, "states", out[label][0], "3M start/end", m.start_value, m.end_value, "3M TWR", m.time_weighted_return_pct,
          "MWR", m.money_weighted_return_pct, "| All TWR", a.time_weighted_return_pct, "MWR", a.money_weighted_return_pct,
          "net_contrib", a.net_contributions, "trust", h.range_metrics["All"].portfolio_return_trust)
print("identical:", out["IB2026"] == out["IB2026+IB2026"])
