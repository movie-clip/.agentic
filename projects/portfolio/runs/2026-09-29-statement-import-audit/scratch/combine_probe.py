"""Backend multi-statement merge probes: same statement twice; IB + ESPP (None cash); ledger dedupe within one statement."""
import socket, sys
from collections import Counter
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError("net off"))
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
import app.services.instrument_enrichment as ie
ie.enrich_imported_instruments = lambda s, m: s
from app.services.statement_importer import import_statement, combine_imported_snapshots
from app.domain.ledger import classify_opening_state
D = r"C:\projects\investments\portfolio\docs"
ib = import_statement(D + r"\IB2026.csv")
ib2 = import_statement(D + r"\IB2026.csv")
c = combine_imported_snapshots([ib, ib2])
t = c.statement_totals
print("IB+IB: positions", len(c.positions), "VUAA qty", [p.quantity for p in c.positions if p.symbol == "VUAA"],
      "ledger", len(c.ledger_entries), "vs single", len(ib.ledger_entries))
print("  totals dividends", t.dividends_total, "deposits", t.deposits_total, "commissions", t.commissions_total, "twr", t.time_weighted_return_pct, "stock", t.stock_total, "start_nav", t.starting_nav, "end_nav", t.ending_nav)
# within-statement duplicate rows under the dedupe key
key = lambda e: (e.entry_type, e.trade_date, e.symbol, e.description, e.quantity, e.price, e.gross_amount, e.net_amount, e.fee, e.tax, e.currency, e.source_section)
dups = [k for k, n in Counter(key(e) for e in ib.ledger_entries).items() if n > 1]
print("IB2026 within-statement key collisions:", len(dups), dups[:3])
es = import_statement(D + r"\ESPP2026.pdf")
ce = combine_imported_snapshots([ib, es])
print("IB+ESPP cash:", [(b.currency, b.starting_cash, b.ending_cash) for b in ce.cash_balances])
print("ESPP alone cash:", [(b.currency, b.starting_cash, b.ending_cash) for b in es.cash_balances])
try:
    print("opening state IB+ESPP:", classify_opening_state(ce))
    print("opening state ESPP:", classify_opening_state(es))
except Exception as ex: print("classify err", ex)
print("IB+ESPP totals start_nav", ce.statement_totals.starting_nav, "end_nav", ce.statement_totals.ending_nav, "twr", ce.statement_totals.time_weighted_return_pct)
