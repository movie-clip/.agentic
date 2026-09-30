"""Independent FF2026 value path from the statement's TRUE trade dates (2026-04-07) vs the
importer's grouped date (2025-12-01), frozen prices from golden_market_data.json."""
import json
d = json.load(open(r"C:\projects\investments\portfolio\services\quant-engine\app\scripts\golden_market_data.json"))
px = {}
for e in d["series"]:
    if e["symbol"] in ("VTI","SCHD","VWO") and e["from"] == "2025-12-01":
        px[e["symbol"]] = {r["date"]: r["price"] for r in e["rows"]}
days = sorted(set(px["VTI"]) & set(px["SCHD"]) & set(px["VWO"]))
def path(trade_day, start_day):
    h = {"SCHD": 28, "VTI": 3, "VWO": 4}; cash = 911.23; out = []
    for day in days:
        if day < start_day: continue
        if day >= trade_day and h["SCHD"]:
            h = {"SCHD": 0, "VTI": 9, "VWO": 0}; cash += 857.70 - 2.56 - 1934.56 - 2.12 + 215.78 - 2.08
        if day >= "2026-03-31" and not getattr(path, "d1", None) == (trade_day, start_day, 1): pass
        div = (7.19 - 1.08 if day >= "2026-03-31" else 0) + (2.99 - 0.45 if day >= "2026-04-01" else 0)
        out.append((day, round(sum(h[s] * px[s][day] for s in h) + cash + div, 2)))
    return out
true_p = path("2026-04-07", "2025-12-31")
print("true holdings from first trading day >= 2025-12-31:", true_p[0], "->", true_p[-1], "return %.2f%%" % ((true_p[-1][1] / true_p[0][1] - 1) * 100))
print("statement NAV return (no external flows): %.2f%%" % ((3071.00 / 2900.12 - 1) * 100))
fab = path("2025-12-01", "2025-12-01")
print("importer-dated path (trades on 2025-12-01):", fab[0], "->", fab[-1], "return %.2f%%" % ((fab[-1][1] / fab[0][1] - 1) * 100))
