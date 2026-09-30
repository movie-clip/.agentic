"""Run Freedom24 and ESPP importers network-free and dump output for comparison
with hand-read pdftotext extractions (ff.txt / espp.txt)."""
import socket, sys, json
def _blocked(*a, **k): raise OSError("network disabled for audit")
socket.socket.connect = _blocked; socket.create_connection = _blocked
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
import app.services.instrument_enrichment as ie
ie.enrich_imported_instruments = lambda snapshot, md: snapshot  # vendor enrichment off
from app.services.statement_importer import import_statement
from app.services.import_admission import build_import_admission_summary
for name in ("FF2026.pdf", "ESPP2026.pdf"):
    s = import_statement(rf"C:\projects\investments\portfolio\docs\{name}")
    print("=====", name, s.statement.importer, s.statement.account_id, s.statement.base_currency, s.statement.statement_period)
    print("totals:", s.statement_totals.model_dump())
    for p in s.positions: print("pos:", p.model_dump(mode="json"))
    for c in s.cash_balances: print("cash:", c.model_dump())
    for e in s.ledger_entries: print("led:", e.entry_type, e.trade_date, e.symbol, e.quantity, e.price, e.gross_amount, e.net_amount, e.fee, e.tax, e.currency, e.source_section)
    for i in s.instruments: print("ins:", i.model_dump())
    a = build_import_admission_summary(s)
    print("admission:", a.decision, a.trust_level, [(c.check_id, c.status, c.delta) for c in a.checks])
