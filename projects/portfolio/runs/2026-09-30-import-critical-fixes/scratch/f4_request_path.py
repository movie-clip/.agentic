"""F4 second fabrication site: the request-path snapshot builder (used by /engines/exposure/run and
stress/drawdown/distribution/drift) sets cost_basis = market_value and unrealized_pnl = 0 for every
position. Build the request the desktop would send for the IB2026 snapshot and show the overview it yields."""
import socket, sys
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError("net off"))
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
import app.services.instrument_enrichment as ie
ie.enrich_imported_instruments = lambda s, m: s
from app.services.statement_importer import import_statement
from app.services.portfolio_snapshot_builder import build_imported_snapshot_from_request
from app.schemas.imports import SnapshotAnalysisRequest, SnapshotAnalysisPosition, SnapshotAnalysisCashBalance
from app.analytics.overview import build_portfolio_overview
from app.scripts.frozen_market_data import FrozenMarketData

ib = import_statement(r"C:\projects\investments\portfolio\docs\IB2026.csv")
req = SnapshotAnalysisRequest(
    base_currency="USD", statement_period=ib.statement.statement_period, importer="interactive_brokers",
    positions=[SnapshotAnalysisPosition(symbol=p.symbol, market_value=p.market_value, quantity=p.quantity, currency=p.currency) for p in ib.positions],
    cash_balances=[SnapshotAnalysisCashBalance(currency=b.currency, amount=b.ending_cash or 0) for b in ib.cash_balances],
)
snap = build_imported_snapshot_from_request(req)
md = FrozenMarketData.from_file()
ov_req = build_portfolio_overview(snap, market_data=md)
ov_imp = build_portfolio_overview(ib, market_data=md)
print("statement-path overview: total_mv", ov_imp.total_market_value, "total_cost_basis", ov_imp.total_cost_basis, "total_unrealized_pnl", ov_imp.total_unrealized_pnl)
print("request-path overview:   total_mv", ov_req.total_market_value, "total_cost_basis", ov_req.total_cost_basis, "total_unrealized_pnl", ov_req.total_unrealized_pnl,
      "(no fx_rates in request -> unconverted sum)")
print("request-path top uPnL", [(t["symbol"], t["unrealized_pnl"]) for t in ov_req.top_positions][:4])
