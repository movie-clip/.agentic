"""Run the production importer on docs/IB2026.csv and diff against rederived.json."""
import json, sys
from collections import Counter, defaultdict
from decimal import Decimal as D
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from app.services.statement_importer import import_statement

ref = json.load(open(sys.argv[1]))
snap = import_statement(r"C:\projects\investments\portfolio\docs\IB2026.csv")
mism = []
def cmp(label, exp, act, tol=1e-6):
    if exp is None or act is None:
        if exp != act: mism.append((label, exp, act))
        return
    if abs(float(exp) - float(act)) > tol: mism.append((label, float(exp), float(act), float(act) - float(exp)))

print("statement:", snap.statement.importer, snap.statement.account_id, snap.statement.base_currency, snap.statement.statement_period, snap.statement.detected_format)
by = {p.symbol: p for p in snap.positions}
print("positions:", len(snap.positions), Counter(p.currency for p in snap.positions))
for p in ref["positions"]:
    q = by.get(p["Symbol"])
    if q is None: mism.append(("missing position", p["Symbol"])); continue
    if q.currency != p["Currency"]: mism.append(("ccy", p["Symbol"], p["Currency"], q.currency))
    for rk, qk in (("Quantity","quantity"),("Cost Basis","cost_basis"),("Close Price","close_price"),("Value","market_value"),("Unrealized P/L","unrealized_pnl")):
        cmp(f"{p['Symbol']}.{qk}", p[rk], getattr(q, qk))
    if str(q.as_of_date) != "2026-08-28": mism.append(("as_of", p["Symbol"], str(q.as_of_date)))
extra = set(by) - {p["Symbol"] for p in ref["positions"]}
if extra: mism.append(("extra positions", extra))

t = snap.statement_totals
cn = ref["change_in_nav"]
for f, a in {"Starting Value":"starting_nav","Ending Value":"ending_nav","Dividends":"dividends_total","Withholding Tax":"withholding_tax_total","Interest":"interest_total","Other Fees":"other_fees_total","Commissions":"commissions_total","Deposits & Withdrawals":"deposits_total"}.items():
    cmp(f"totals.{a} (vs |ChangeInNAV|)", abs(float(cn[f])), getattr(t, a))
cmp("totals.cash_total", ref["nav"]["Cash"], t.cash_total)
cmp("totals.stock_total", ref["nav"]["Stock"], t.stock_total)
cmp("totals.twr", ref["nav"]["TWR"].rstrip("%"), t.time_weighted_return_pct)
print("fx_rates:", t.fx_rates)
for c in ("EUR","GBP"):
    cmp(f"fx.{c}USD", ref["implied_fx"][c], t.fx_rates.get(c+"USD"), 1e-9)
print("all totals fields:", t.model_dump())

cb = {c.currency: c for c in snap.cash_balances}
print("cash:", {k: (v.starting_cash, v.ending_cash, v.ending_settled_cash) for k, v in cb.items()})
for ccy, d in ref["cash_report"].items():
    if ccy == "Base Currency Summary": continue
    for rk, qk in (("Starting Cash","starting_cash"),("Ending Cash","ending_cash"),("Ending Settled Cash","ending_settled_cash")):
        cmp(f"cash.{ccy}.{qk}", d[rk], getattr(cb[ccy], qk))

L = snap.ledger_entries
print("ledger counts:", dict(Counter(e.entry_type for e in L)))
agg = defaultdict(lambda: defaultdict(float))
for e in L:
    a = agg[(e.entry_type, e.currency)]
    a["n"] += 1; a["gross"] += e.gross_amount or 0; a["net"] += e.net_amount or 0; a["fee"] += e.fee or 0; a["tax"] += e.tax or 0
for k in sorted(agg): print(" ", k, {kk: round(v, 6) for kk, v in agg[k].items()})
# per-ccy ledger cash roll-forward using net_amount
for ccy in ("USD","EUR","GBP"):
    st = cb[ccy].starting_cash
    net = sum((e.net_amount or 0) for e in L if e.currency == ccy)
    print(f"ledger rollforward {ccy}: start {st} + sum(net) {net:.6f} = {st+net:.6f} vs statement ending {cb[ccy].ending_cash} gap {st+net-cb[ccy].ending_cash:.6f}")
fees_base = sum((e.fee or 0) * t.fx_rates.get(f"{e.currency}USD", 1.0) for e in L if e.entry_type in ("BUY","SELL"))
print(f"ledger trade commissions in base (static fx): {fees_base:.4f} vs statement commissions_total {t.commissions_total}")
wt_tax = sum(e.tax for e in L if e.entry_type == "WITHHOLDING_TAX"); wt_net = sum(e.net_amount for e in L if e.entry_type == "WITHHOLDING_TAX")
print(f"withholding: sum(tax field)={wt_tax:.2f} sum(net)={wt_net:.2f} statement={t.withholding_tax_total}")
print("zero-qty trades:", [e for e in L if e.entry_type in ('BUY','SELL') and not e.quantity])
print("LQQ ledger:", [(e.entry_type, str(e.trade_date), e.quantity, e.price, e.currency) for e in L if e.symbol == "LQQ"])
print("LQQ position:", by.get("LQQ"))
print("instruments:", len(snap.instruments), "with currency:", sum(1 for i in snap.instruments if getattr(i, 'currency', None)))
print("MISMATCHES:", len(mism))
for m in mism: print("  ", m)
json.dump(snap.model_dump(mode="json"), open(sys.argv[2], "w"), indent=1)
