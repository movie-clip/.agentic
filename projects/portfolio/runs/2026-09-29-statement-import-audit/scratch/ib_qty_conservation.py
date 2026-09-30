"""Per-symbol quantity conservation using the statement's own Mark-to-Market
Prior/Current Quantity as the external anchor, against the importer's ledger."""
import csv, sys
from collections import defaultdict
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from app.services.statement_importer import import_statement
P = r"C:\projects\investments\portfolio\docs\IB2026.csv"
hdr = {}; mtm = {}; dup = defaultdict(int)
with open(P, encoding="utf-8-sig", newline="") as f:
    for c in csv.reader(f):
        if len(c) < 2: continue
        if c[1] == "Header": hdr[c[0]] = c[2:]; continue
        if c[0] == "Mark-to-Market Performance Summary" and c[1] == "Data":
            r = dict(zip(hdr[c[0]], c[2:]))
            if r["Asset Category"] == "Stocks":
                a = mtm.get(r["Symbol"], (0.0, 0.0)); dup[r["Symbol"]] += 1
                mtm[r["Symbol"]] = (a[0] + float(r["Prior Quantity"].replace(",", "")), a[1] + float(r["Current Quantity"].replace(",", "")))
snap = import_statement(P)
net = defaultdict(float)
for e in snap.ledger_entries:
    if e.entry_type == "BUY": net[e.symbol] += e.quantity
    elif e.entry_type == "SELL": net[e.symbol] -= e.quantity
pos = {p.symbol: p.quantity for p in snap.positions}
viol = []
for s in sorted(set(mtm) | set(net)):
    prior, cur = mtm.get(s, (None, None))
    if prior is None: viol.append((s, "no MTM row")); continue
    gap = prior + net[s] - cur
    if abs(gap) > 1e-9: viol.append((s, prior, net[s], cur, gap))
    if abs(pos.get(s, 0.0) - cur) > 1e-9: viol.append((s, "position qty", pos.get(s), "mtm current", cur))
print("symbols in MTM:", len(mtm), "ledger symbols:", len(net))
print("opening symbols (prior>0):", sum(1 for v in mtm.values() if v[0] > 0))
print("violations:", viol)
print("symbols with >1 MTM row (cross-listed, summed):", [k for k,v in dup.items() if v>1])
