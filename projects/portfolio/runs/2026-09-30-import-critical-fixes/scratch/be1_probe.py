"""BE-1 scratch probe: analyze-combined on real fixtures (market data mocked). Not shipped."""
import json, sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from fastapi.testclient import TestClient
from app.api.main import app
from app.services.statement_importer import import_statement
from app.tests import conftest as c

IB = Path(r"C:\projects\investments\portfolio\docs\IB2026.csv")
ESPP = Path(r"C:\projects\investments\portfolio\docs\ESPP2026.pdf")
ib = import_statement(IB)
espp = import_statement(ESPP)

mock = MagicMock()
inst = mock.return_value
inst.get_etf_holdings.return_value = ("SPY", c._SPY_MOCK_ETF_HOLDINGS)
inst.get_etf_holdings_for_date.return_value = ("SPY", c._SPY_MOCK_ETF_HOLDINGS)
inst.get_historical_prices.side_effect = c._mock_price_rows
inst.get_historical_prices_for_symbols.side_effect = c._mock_prices_for_symbols
client = TestClient(app)

def call(snaps, carried=None):
    body = {"snapshots": [s.model_dump(mode="json") for s in snaps]}
    if carried:
        body["carried_admissions"] = carried
    return client.post("/portfolios/import/analyze-combined", json=body)

def summarize(label, r):
    print("==", label, r.status_code)
    if r.status_code != 200:
        print("  detail:", r.json()); return None
    j = r.json()
    pos = j["snapshot"]["positions"]
    mv = round(sum(p["market_value"] for p in pos), 2)
    vuaa = [p for p in pos if p["symbol"] == "VUAA"]
    cash = {b["currency"]: b["ending_cash"] for b in j["snapshot"]["cash_balances"]}
    a = j["admission_summary"]
    print("  positions", len(pos), "rawMV", mv, "VUAA", [(p["quantity"], p["market_value"]) for p in vuaa], "cash", cash)
    print("  account_id", j["snapshot"]["statement"]["account_id"], "constituent_snapshots", len(j["constituent_snapshots"]))
    print("  admission", a["decision"], a["trust_level"], "rollup:", None if a["rollup"] is None else
          [(k["origin"], k["decision"], k["trust_level"]) for k in a["rollup"]["constituents"]],
          None if a["rollup"] is None else (a["rollup"]["combined_snapshot_decision"], a["rollup"]["combined_snapshot_trust_level"]))
    return j

with patch("app.services.exposure_engine.MarketDataService", mock):
    single = summarize("IB alone", call([ib]))
    summarize("ESPP alone", call([espp]))
    summarize("IB + IB", call([ib, ib]))
    ibespp = summarize("IB + ESPP", call([ib, espp]))
    j3 = summarize("IB + ESPP + IB", call([ib, espp, ib]))
    # IB unchanged in [IB, ESPP, IB] vs [IB, ESPP]
    p2 = {(p["symbol"], p["currency"]): p["quantity"] for p in ibespp["snapshot"]["positions"]}
    p3 = {(p["symbol"], p["currency"]): p["quantity"] for p in j3["snapshot"]["positions"]}
    print("[IB,ESPP,IB] positions == [IB,ESPP] positions:", p2 == p3)
    # chained input refusal
    combined = ibespp["snapshot"]
    r = client.post("/portfolios/import/analyze-combined", json={"snapshots": [combined, ib.model_dump(mode="json")]})
    print("== chained (IB+ESPP) + IB:", r.status_code, r.json())
    # legacy doubled snapshot
    doubled = json.loads(json.dumps(combined)); doubled["statement"]["account_id"] = "I09548809 + U8516450 + U8516450"
    r = client.post("/portfolios/import/analyze-combined", json={"snapshots": [doubled]})
    print("== legacy doubled single:", r.status_code, r.json())
    # combined + disjoint single OK? (combined IB+ESPP, no third) -> single combined input passes
    r = client.post("/portfolios/import/analyze-combined", json={"snapshots": [combined]})
    print("== stored combined alone:", r.status_code)
    # carried admissions
    carried = [single["admission_summary"]]
    espp_j = client.post("/portfolios/import/analyze-combined", json={"snapshots": [espp.model_dump(mode="json")]}).json()
    r = call([espp], carried=[single["admission_summary"]])
    print("== ESPP + carried IB admission:", r.status_code)
    if r.status_code == 200:
        a = r.json()["admission_summary"]; print("  ", a["decision"], a["trust_level"], [(k["origin"], k["decision"]) for k in a["rollup"]["constituents"]])
    # empty snapshots -> 422
    print("== empty:", client.post("/portfolios/import/analyze-combined", json={"snapshots": []}).status_code)
    # single equals from_snapshot
    from app.services.import_engine import build_import_bootstrap_from_snapshot, build_combined_import_bootstrap
    a = build_import_bootstrap_from_snapshot(ib, "SPY", {}).model_dump(mode="json")
    b = build_combined_import_bootstrap([ib], "SPY", {}).model_dump(mode="json")
    for x in (a, b):
        x["admission_summary"]["provenance"]["generated_at"] = None
    print("single input equals from_snapshot:", a == b)

# upload/analyze path (paths)
from app.services.import_engine import build_import_bootstrap
with patch("app.services.exposure_engine.MarketDataService", mock):
    r = build_import_bootstrap([str(IB), str(ESPP)], "SPY", {})
    print("path analyze [IB, ESPP]:", r.admission_summary.decision, r.admission_summary.trust_level,
          "constituent_snapshots", len(r.constituent_snapshots), [s.statement.importer for s in r.constituent_snapshots])
    r1 = build_import_bootstrap(str(IB), "SPY", {})
    print("path analyze [IB]:", r1.admission_summary.decision, len(r1.constituent_snapshots), r1.admission_summary.rollup)
    try:
        build_import_bootstrap([], "SPY", {})
    except ValueError as e:
        print("empty paths ->", e)
