"""Independent re-derivation of docs/IB2026.csv broker truth.

Anchor: the raw statement itself. Does NOT import app.importers or statement_truths.
Own reader: csv.reader, positional header tracking per section, written from the
IBKR Activity Statement layout observed in the file.
"""
import csv, json, sys
from collections import defaultdict, Counter
from decimal import Decimal as D

PATH = r"C:\projects\investments\portfolio\docs\IB2026.csv"

def num(s):
    s = (s or "").replace(",", "").strip()
    return D(s)

rows = []
hdr = {}
with open(PATH, encoding="utf-8-sig", newline="") as f:
    for c in csv.reader(f):
        if len(c) < 2: continue
        sec, rt = c[0], c[1]
        if rt == "Header":
            hdr[sec] = c[2:]; continue
        rows.append((sec, rt, dict(zip(hdr.get(sec, []), c[2:])), c))

out = {}
kv = lambda sec: {r["Field Name"]: r["Field Value"] for s, t, r, _ in rows if s == sec and t == "Data" and "Field Name" in r}
chg = kv("Change in NAV")
out["change_in_nav"] = {k: str(num(v)) for k, v in chg.items()}
nav = {}
for s, t, r, c in rows:
    if s == "Net Asset Value" and t == "Data":
        if "Asset Class" in r: nav[r["Asset Class"].strip()] = str(num(r["Current Total"]))
        else: nav["TWR"] = c[2]
out["nav"] = nav

# Open positions + implied FX
pos = []
tot = [r for s, t, r, _ in rows if s == "Open Positions" and t == "Total"]
for s, t, r, _ in rows:
    if s == "Open Positions" and t == "Data" and r["DataDiscriminator"] == "Summary":
        pos.append({k: r[k] for k in ("Asset Category","Currency","Symbol","Quantity","Mult","Cost Price","Cost Basis","Close Price","Value","Unrealized P/L")})
fx = {}
for a, b in zip(tot, tot[1:]):
    if a["Currency"] != "USD" and b["Currency"] == "USD":
        fx[a["Currency"]] = num(b["Value"]) / num(a["Value"])
        fx[a["Currency"]+"_cost"] = num(b["Cost Basis"]) / num(a["Cost Basis"])
fx["USD"] = D(1)
out["implied_fx"] = {k: f"{v:.10f}" for k, v in fx.items()}
base_mv = sum(num(p["Value"]) * fx[p["Currency"]] for p in pos)
raw_mv = sum(num(p["Value"]) for p in pos)
base_cb = sum(num(p["Cost Basis"]) * fx[p["Currency"]] for p in pos)
out["positions"] = pos
out["position_count"] = len(pos)
out["positions_by_ccy"] = dict(Counter(p["Currency"] for p in pos))
out["mv_base"] = f"{base_mv:.6f}"; out["mv_raw_mixed"] = f"{raw_mv:.6f}"; out["cost_basis_base"] = f"{base_cb:.6f}"
# internal consistency qty*close == value ; value-cost == upnl
out["pos_checks"] = [
    {"sym": p["Symbol"], "qty_x_close_minus_value": f"{num(p['Quantity'])*num(p['Close Price'])-num(p['Value']):.6f}",
     "value_minus_cost_minus_upnl": f"{num(p['Value'])-num(p['Cost Basis'])-num(p['Unrealized P/L']):.6f}"} for p in pos]

# Cash report
cash = defaultdict(dict)
for s, t, r, _ in rows:
    if s == "Cash Report" and t == "Data":
        cash[r["Currency"]][r["Currency Summary"]] = str(num(r["Total"]))
out["cash_report"] = cash

# Trades
stock_tr = []; fx_tr = []; other_tr = Counter()
for s, t, r, c in rows:
    if s != "Trades" or t != "Data": continue
    if r.get("DataDiscriminator") != "Order": other_tr[r.get("DataDiscriminator")] += 1; continue
    if r["Asset Category"] == "Stocks": stock_tr.append(r)
    elif r["Asset Category"] == "Forex": fx_tr.append(r)
    else: other_tr[r["Asset Category"]] += 1
def trsum(tr, comm):
    agg = defaultdict(lambda: {"n":0,"buy":0,"sell":0,"zero":0,"proceeds":D(0),"comm":D(0)})
    for r in tr:
        a = agg[r["Currency"]]; q = num(r["Quantity"]); a["n"] += 1
        if q > 0: a["buy"] += 1
        elif q < 0: a["sell"] += 1
        else: a["zero"] += 1
        a["proceeds"] += num(r["Proceeds"]); a["comm"] += num(r[comm])
    return {k: {kk: str(vv) for kk, vv in v.items()} for k, v in agg.items()}
out["stock_trades"] = trsum(stock_tr, "Comm/Fee")
out["stock_trade_counts"] = {"BUY": sum(num(r["Quantity"])>0 for r in stock_tr), "SELL": sum(num(r["Quantity"])<0 for r in stock_tr)}
out["forex_trades"] = trsum(fx_tr, "Comm in USD")
out["forex_trade_count"] = len(fx_tr)
out["forex_comm_usd"] = str(sum(num(r["Comm in USD"]) for r in fx_tr))
out["trade_rows_skipped_other"] = dict(other_tr)
# Forex cash effect per currency: each pair BASE.QUOTE, qty in BASE ccy (+ = buy base), proceeds in QUOTE ccy
fxcash = defaultdict(D)
for r in fx_tr:
    b, qccy = r["Symbol"].split(".")
    fxcash[b] += num(r["Quantity"]); fxcash[qccy] += num(r["Proceeds"])
    fxcash["USD"] += num(r["Comm in USD"])
out["forex_cash_effect_by_ccy"] = {k: str(v) for k, v in fxcash.items()}

# Cash flow sections
def cf(sec):
    xs = [r for s, t, r, _ in rows if s == sec and t == "Data" and len(r.get("Currency","")) == 3 and r["Currency"].isupper()]
    return xs
flows = {}
for sec in ("Dividends","Withholding Tax","Interest","Fees","Deposits & Withdrawals"):
    xs = cf(sec)
    flows[sec] = {"n": len(xs), "signed": str(sum(num(r["Amount"]) for r in xs)), "abs": str(sum(abs(num(r["Amount"])) for r in xs)),
                  "positive_rows": sum(num(r["Amount"])>0 for r in xs), "negative_rows": sum(num(r["Amount"])<0 for r in xs)}
out["cash_flows"] = flows

# Cash roll-forward per currency from ledger-like components
roll = {}
for ccy in ("USD","EUR","GBP"):
    st = num(cash[ccy]["Starting Cash"])
    stk = sum(num(r["Proceeds"]) + num(r["Comm/Fee"]) for r in stock_tr if r["Currency"] == ccy)
    cfx = D(0)
    for sec in ("Dividends","Withholding Tax","Interest","Fees","Deposits & Withdrawals"):
        cfx += sum(num(r["Amount"]) for r in cf(sec) if r["Currency"] == ccy)
    end_stock_only = st + stk + cfx
    end_with_fx = end_stock_only + fxcash.get(ccy, D(0))
    roll[ccy] = {"starting": str(st), "stock_trades_net": str(stk), "cashflows": str(cfx),
                 "ending_without_forex": f"{end_stock_only:.6f}", "ending_with_forex": f"{end_with_fx:.6f}",
                 "statement_ending": cash[ccy]["Ending Cash"]}
out["cash_rollforward"] = roll

ca = [c for s, t, r, c in rows if s == "Corporate Actions"]
out["corporate_actions"] = ca
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ("nav","implied_fx","position_count","positions_by_ccy","mv_base","mv_raw_mixed","cost_basis_base","stock_trade_counts","stock_trades","forex_trade_count","forex_comm_usd","forex_cash_effect_by_ccy","trade_rows_skipped_other","cash_flows","cash_rollforward","corporate_actions")}, indent=1, default=str))
bad = [p for p in out["pos_checks"] if abs(D(p["qty_x_close_minus_value"]))>D("0.01") or abs(D(p["value_minus_cost_minus_upnl"]))>D("0.01")]
print("pos internal inconsistencies:", bad)
