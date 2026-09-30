"""F1: expected FF2026 Dashboard values once trades/fee carry their true statement dates.

Runs the PRODUCTION dashboard-history engine (network off, enrichment stubbed) on:
  A  the snapshot exactly as imported today (should reproduce the committed golden, -1.20%)
  B  F1 only: BUY/SELL and the period FEE re-dated to 2026-04-07 (the PDF's trade date)
  C  F1 + F7: as B, with the duplicate period FEE row dropped (fees stay on the trade rows)
Frozen prices are served from golden_market_data.json; windows other than the captured one are
served by slicing the captured 2025-12-01..2026-04-11 series (same rows, filtered by date).
Also an independent path (own arithmetic, no app code) over the statement period and the replay window.
"""
import socket, sys, json, copy
from datetime import date
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError("net off"))
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
import app.services.instrument_enrichment as ie
ie.enrich_imported_instruments = lambda s, m: s
from app.services.statement_importer import import_statements
from app.services.dashboard_history_engine import run_imported_dashboard_history
from app.scripts.frozen_market_data import FrozenMarketData, FrozenMarketDataMiss, _series_key


class SlicingFrozen(FrozenMarketData):
    def _lookup(self, symbol, from_date, to_date):
        try:
            return super()._lookup(symbol, from_date, to_date)
        except FrozenMarketDataMiss:
            sym = _series_key(symbol, from_date, to_date)[0]
            cands = [(k, v) for k, v in self._series.items() if k[0] == sym and k[1] <= from_date and k[2] >= to_date]
            if not cands:
                raise
            _, rows = cands[0]
            self.misses.append((symbol, from_date, to_date))
            return [dict(r) for r in rows if from_date <= r["date"] <= to_date]


def run(snap, label):
    md = SlicingFrozen.from_file()
    md.misses = []
    h = run_imported_dashboard_history(snap, "SPY", market_data=md)
    ds = h.daily_states
    print(f"===== {label}")
    print("  window", ds[0].date if ds else None, "->", ds[-1].date if ds else None, "states", len(ds),
          "sliced windows", sorted(set((m[1], m[2]) for m in md.misses)))
    if ds:
        print("  first state TPV %.2f MV %.2f | last TPV %.2f recon_adj %s" % (
            ds[0].total_portfolio_value, ds[0].total_market_value, ds[-1].total_portfolio_value,
            getattr(ds[-1], "reconciliation_adjustment", None)))
    rm = h.range_metrics or {}
    for k in ("1M", "3M", "YTD", "1Y", "All"):
        m = rm.get(k)
        if not m:
            continue
        s = m.summary
        print(f"  {k:4s} start {m.window_start_date} start_value {s.start_value} end_value {s.end_value} "
              f"TWR {s.time_weighted_return_pct} MWR {s.money_weighted_return_pct} bench {s.benchmark_return_pct} "
              f"excess {s.excess_return_pct} net_contrib {s.net_contributions} gain {s.investment_gain} "
              f"trust {m.portfolio_return_trust} dd {m.max_drawdown_pct}")
        print("        monthly", [(x.month, None if x.return_pct is None else round(x.return_pct, 4)) for x in m.monthly_returns])
    rmd = h.run_metadata
    for attr in ("replay_cash_anchor", "unpriced_replay_symbols", "trade_price_anchored_symbols", "statement_anchored_symbols"):
        if hasattr(rmd, attr):
            print("  ", attr, getattr(rmd, attr))
    print("  return basis", rmd.return_basis_contract)
    print("  section_trust", rmd.section_trust)
    return h


ff = import_statements([r"C:\projects\investments\portfolio\docs\FF2026.pdf"])
print("imported ledger:", [(e.entry_type, str(e.trade_date), e.symbol, e.net_amount, e.fee) for e in ff.ledger_entries])
run(ff, "A current import (expect golden -1.20% on 3M)")

TRUE_TRADE_DATE = date(2026, 4, 7)  # PDF Transactions 'Trade date' column (all three); Commissions rows dated 2026-04-07
b = copy.deepcopy(ff)
b.ledger_entries = [e.model_copy(update={"trade_date": TRUE_TRADE_DATE}) if e.entry_type in ("BUY", "SELL", "FEE") else e
                    for e in b.ledger_entries]
run(b, "B F1 only (true dates, FEE row kept -> still double-counts 6.76)")
c = copy.deepcopy(b)
c.ledger_entries = [e for e in c.ledger_entries if e.entry_type != "FEE"]
run(c, "C F1 + F7 (true dates, single fee charge)")

d = json.load(open(r"C:\projects\investments\portfolio\services\quant-engine\app\scripts\golden_market_data.json"))
px = {e["symbol"]: {r["date"]: r["price"] for r in e["rows"]} for e in d["series"]
      if e["symbol"] in ("VTI", "SCHD", "VWO") and e["from"] == "2025-12-01"}
spy = {r["date"]: (r.get("adjClose") or r["price"]) for e in d["series"]
       if e["symbol"] == "SPY" and e["from"] == "2025-12-01" for r in e["rows"]}


def value(day):
    h = {"SCHD": 28, "VTI": 3, "VWO": 4}
    cash = 911.23
    if day >= "2026-03-31":
        cash += 7.19 - 1.08
    if day >= "2026-04-01":
        cash += 2.99 - 0.45
    if day >= "2026-04-07":
        h = {"SCHD": 0, "VTI": 9, "VWO": 0}
        cash += 857.70 + 215.78 - 1934.56 - 6.76
    return sum(h[s] * px[s][day] for s in h) + cash


print("===== independent path (statement holdings/cash, frozen closes, no external flows -> TWR = value ratio)")
print("  VTI frozen close 2026-04-10 %.4f vs statement price 335.44 ; value 04-10 %.2f vs statement end NAV 3071.00" % (
    px["VTI"]["2026-04-10"], value("2026-04-10")))
for start in ("2025-12-31", "2026-01-09", "2026-01-12", "2026-03-31"):
    if start not in px["VTI"]:
        print("  no price", start)
        continue
    s0 = value(start)
    s1 = value("2026-04-10")
    print(f"  {start} -> 2026-04-10: start {s0:.2f} end {s1:.2f} return {(s1 / s0 - 1) * 100:.4f}%  "
          f"SPY {(spy['2026-04-10'] / spy[start] - 1) * 100:.4f}%")
print("  statement NAV return 2025-12-31 -> 2026-04-11: %.4f%%" % ((3071.00 / 2900.12 - 1) * 100))
print("  cash identity: 911.23 - 861.08 - 6.76 + 8.65 = %.2f (statement 52.04)" % (911.23 - 861.08 - 6.76 + 8.65))
