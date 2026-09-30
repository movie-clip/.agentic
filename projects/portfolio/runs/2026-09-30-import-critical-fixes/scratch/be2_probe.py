"""BE-2 probe: FF2026 ledger dates, trade fees, cash roll-forward, unparseable-date skip."""
import sys
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from app.importers import freedom24 as f
snap = f.import_statement(r"C:\projects\investments\portfolio\docs\FF2026.pdf")
es = snap.ledger_entries
print("dates", sorted({str(e.trade_date) for e in es}))
for e in es:
    print(e.entry_type, e.symbol, e.trade_date, "fee", e.fee, "net", e.net_amount, "gross", e.gross_amount)
trades = [e for e in es if e.entry_type in ("BUY", "SELL")]
print("trade dates", [(e.symbol, str(e.trade_date), e.fee) for e in trades])
print("total fee", round(sum(e.fee or 0 for e in es), 2), "FEE entries", sum(e.entry_type == "FEE" for e in es))
cb = snap.cash_balances[0]
print("cash start", cb.starting_cash, "end", cb.ending_cash)
print("rollforward", round(cb.starting_cash + sum(e.net_amount for e in es), 2))
print("statement cash_total", snap.statement_totals.cash_total)

# unparseable trade date -> skipped, others kept
pages = f._extract_text_by_page(r"C:\projects\investments\portfolio\docs\FF2026.pdf")
lines = pages[f._PAGE_TRANSACTIONS].splitlines()
lines[34] = "not-a-date"
pages2 = list(pages); pages2[f._PAGE_TRANSACTIONS] = "\n".join(lines)
out = f._parse_transactions(pages2)
print("bad-date variant:", [(e.symbol, str(e.trade_date)) for e in out])
