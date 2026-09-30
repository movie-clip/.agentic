"""F2 / F3 / F4 probes on the committed statements (network off, enrichment stubbed).

F3: backend combine (the methodology's merge rule) for IB2026 + IB2026 — the expected Exposure inputs.
F2: admission per constituent vs admission recomputed on the combined snapshot, for several pairs;
    weakest-link = min over constituents (and the combined recompute).
F4: which published numbers consume cost_basis / unrealized_pnl, and what they are today for FF2026,
    IB2026, and IB2026 + FF2026 (cross-account combine), with FF's cost basis fabricated vs removed.
"""
import socket, sys
from collections import defaultdict
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError("net off"))
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
import app.services.instrument_enrichment as ie
ie.enrich_imported_instruments = lambda s, m: s
from app.services.statement_importer import import_statement, combine_imported_snapshots
from app.services.import_admission import build_import_admission_summary
from app.analytics.currency import convert_to_base, snapshot_fx_context

D = r"C:\projects\investments\portfolio\docs"
ib = import_statement(D + r"\IB2026.csv")
ib_again = import_statement(D + r"\IB2026.csv")
ff = import_statement(D + r"\FF2026.pdf")
es = import_statement(D + r"\ESPP2026.pdf")

RANK = {"verified": 3, "degraded": 2, "withheld": 1, "unavailable": 0}
DRANK = {"admitted": 2, "degraded": 1, "withheld": 0}


def base_mv(s):
    base, fx = snapshot_fx_context(s)
    return round(sum(convert_to_base(p.market_value, p.currency, base, fx)[0] for p in s.positions), 2)


def raw_mv(s):
    return round(sum(p.market_value for p in s.positions), 2)


def pos_summary(s):
    q = defaultdict(float)
    for p in s.positions:
        q[(p.symbol, p.currency)] += p.quantity
    return q


print("===== F3 backend combine IB2026 + IB2026 (same account", ib.statement.account_id, ")")
c = combine_imported_snapshots([ib, ib_again])
print("  single: positions", len(ib.positions), "raw MV", raw_mv(ib), "base MV", base_mv(ib),
      "cash", [(b.currency, b.ending_cash) for b in ib.cash_balances])
print("  combined: positions", len(c.positions), "raw MV", raw_mv(c), "base MV", base_mv(c),
      "cash", [(b.currency, b.ending_cash) for b in c.cash_balances])
qa, qc = pos_summary(ib), pos_summary(c)
diff = {k: (qa.get(k), qc.get(k)) for k in set(qa) | set(qc) if abs((qa.get(k) or 0) - (qc.get(k) or 0)) > 1e-9}
print("  per-(symbol,ccy) quantity differences single vs combined:", diff or "none")
print("  VUAA", [(p.quantity, p.market_value, p.currency) for p in c.positions if p.symbol == "VUAA"])
dup_symbols = [sym for sym, n in defaultdict(int, {}).items()]
by_sym = defaultdict(set)
for p in ib.positions:
    by_sym[p.symbol].add(p.currency)
print("  IB2026 symbols held in >1 currency (desktop normalize dedups by symbol only):",
      {s: sorted(v) for s, v in by_sym.items() if len(v) > 1} or "none")
print("  combined totals (F10, not in scope): stock", c.statement_totals.stock_total, "cash", c.statement_totals.cash_total,
      "ending_nav", c.statement_totals.ending_nav, "twr", c.statement_totals.time_weighted_return_pct)

print("===== F2 admission: constituents vs combined recompute vs weakest-link")
single = {"IB2026": ib, "FF2026": ff, "ESPP2026": es}
adm = {k: build_import_admission_summary(v) for k, v in single.items()}
for k, a in adm.items():
    print(f"  {k:9s} decision {a.decision:9s} trust {a.trust_level:9s} checks",
          [(ch.check_id.split('_')[0] + '/' + ch.check_id.split('_')[-1], ch.status, ch.delta) for ch in a.checks])
pairs = [("IB2026", "IB2026"), ("IB2026", "ESPP2026"), ("ESPP2026", "IB2026"), ("IB2026", "FF2026"), ("FF2026", "ESPP2026")]
for left, right in pairs:
    snaps = [single[left], import_statement(D + ("\\" + right + (".csv" if right == "IB2026" else ".pdf")))]
    try:
        comb = combine_imported_snapshots(snaps)
    except ValueError as ex:
        print(f"  {left}+{right}: combine refused: {ex}")
        continue
    ca = build_import_admission_summary(comb)
    wl_trust = min((adm[left].trust_level, adm[right].trust_level), key=lambda t: RANK[t])
    wl_dec = min((adm[left].decision, adm[right].decision), key=lambda d: DRANK[d])
    last_added = adm[right]
    print(f"  {left}+{right}: shown today (added file) {last_added.decision}/{last_added.trust_level} | "
          f"combined recompute {ca.decision}/{ca.trust_level} | weakest-link {wl_dec}/{wl_trust} | "
          f"min(all) {min((wl_trust, ca.trust_level), key=lambda t: RANK[t])}")
    print("      combined checks", [(ch.check_id, ch.status, ch.delta) for ch in ca.checks])
    print("      combined base MV", base_mv(comb), "raw MV", raw_mv(comb), "share of base MV by account:",
          {s.statement.account_id: round(base_mv(s) / base_mv(comb) * 100, 1) for s in snaps if base_mv(comb)})

print("===== F4 cost basis consumers")
from app.analytics.overview import build_portfolio_overview
from app.scripts.frozen_market_data import FrozenMarketData
md = FrozenMarketData.from_file()
for name, s in (("FF2026", ff), ("IB2026", ib), ("ESPP2026", es)):
    print(f"  {name} positions:", [(p.symbol, p.quantity, p.close_price, p.market_value, p.cost_basis, p.unrealized_pnl) for p in s.positions][:4], "...")
    try:
        ov = build_portfolio_overview(s, market_data=md)
        print(f"     overview total_cost_basis {ov.total_cost_basis} total_unrealized_pnl {ov.total_unrealized_pnl} "
              f"total_mv {ov.total_market_value} top_positions uPnL {[(t['symbol'], t['unrealized_pnl']) for t in ov.top_positions][:3]}")
    except Exception as ex:  # frozen fixture may miss profiles for some paths
        print("     overview error", type(ex).__name__, ex)
ibff = combine_imported_snapshots([ib, ff])
try:
    ov = build_portfolio_overview(ibff, market_data=md)
    print(f"  IB2026+FF2026 overview total_cost_basis {ov.total_cost_basis} total_unrealized_pnl {ov.total_unrealized_pnl} total_mv {ov.total_market_value}")
except Exception as ex:
    print("  IB+FF overview error", type(ex).__name__, ex)
ib_known_upnl = sum(convert_to_base(p.unrealized_pnl, p.currency, *snapshot_fx_context(ib))[0] for p in ib.positions)
print("  IB-only unrealized (base) %.2f ; FF VTI unrealized true value = unknown (statement states none)" % ib_known_upnl)
print("  FF VTI fabricated cost 9 x 335.44 =", round(9 * 335.44, 2), "; lower bound on cost from in-period buy: 6 x 322.426 + fee 2.12 =",
      round(6 * 322.426 + 2.12, 2), "(3 opening shares' cost is not stated anywhere in the PDF)")
from app.domain.ledger import reconstruct_position_lots
print("  reconstruct_position_lots(FF) (no production caller):",
      [(l.symbol, l.source, l.original_quantity, l.unit_cost, l.remaining_cost_basis, l.cost_basis_is_estimated) for l in reconstruct_position_lots(ff)])
