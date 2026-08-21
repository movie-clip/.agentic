REPORT 2026-08-21-dynamic-sector-classification/07
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/analytics/overview.py — added UNCLASSIFIED_SECTOR_LABEL constant per plan § Contract
  - services/quant-engine/app/analytics/overview.py — constructs MarketDataService() internally, passes market_data=... into attach_snapshot_metadata; function signature unchanged
  - services/quant-engine/app/analytics/overview.py — aggregation branches on `instrument is not None`; uses `instrument.sector or UNCLASSIFIED_SECTOR_LABEL`; get_sector() else-branch untouched
  - services/quant-engine/app/core/settings.py — added Settings.fmp_profile_cache_ttl_seconds: int, default 2592000 (30 days)
  - services/quant-engine/app/clients/fmp.py — FmpClient sets self.profile_ttl_seconds from the new setting
  - services/quant-engine/app/clients/fmp.py — get_profile() uses ttl_seconds=self.profile_ttl_seconds instead of self.quote_ttl_seconds

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py app/tests/test_fmp_client.py -q
  result:    PASS
  detail:    201 passed, 1 warning (pre-existing unrelated DeprecationWarning on datetime.utcnow)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test-engineer: overview.py now builds its own MarketDataService() — needs the planned _mock_overview_engine_market_data conftest fixture
  - test-engineer: confirmed neither test_analytics.py nor conftest.py currently mocks app.analytics.overview.MarketDataService
  - test-engineer: AC9 needs a regression — unclassified equity lands in distinct "Unclassified" bucket, weight included in totals, never "Other"
  - docs-engineer: exposure-fields.md and financial-methodology.md "Unclassified" write-up still outstanding per 05-technical-plan.md's own contract_notes, unaffected by this ticket
  - exposure_engine.py's _build_current_state_concentration confirmed to already iterate the full overview.sector_allocation list — no code change made there, per DoD instruction

risks:
  - none
