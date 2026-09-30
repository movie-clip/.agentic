// Runs the production desktop overlay on the real IB2026 importer output, added onto itself
// (same account, same period) and onto an ESPP snapshot, to measure what Exposure receives.
import { readFileSync } from 'node:fs'
import { buildPortfolioSnapshotFromAnalysis, overlayImportedSnapshot } from 'C:/projects/investments/portfolio/apps/desktop/src/features/portfolio/portfolioSnapshot.ts'
const snap = JSON.parse(readFileSync(process.argv[2], 'utf8'))
const analysis: any = { snapshot: snap, overview: { sector_allocation: [], sector_position_breakdown: {} }, risk_summary: { benchmark_symbol: 'SPY' } }
const a = buildPortfolioSnapshotFromAnalysis(analysis, ['IB2026.csv'])
const twice = overlayImportedSnapshot(a, buildPortfolioSnapshotFromAnalysis(analysis, ['IB2026.csv']))
const sum = (s: any) => s.positions.reduce((t: number, p: any) => t + p.marketValue, 0)
const vuaa = (s: any) => s.positions.find((p: any) => p.symbol === 'VUAA')
console.log('single: positions', a.positions.length, 'raw MV', sum(a).toFixed(2), 'VUAA qty', vuaa(a).quantity, 'cash', JSON.stringify(a.cashBalances))
console.log('same statement added again: positions', twice.positions.length, 'raw MV', sum(twice).toFixed(2), 'VUAA qty', vuaa(twice).quantity, 'cash', JSON.stringify(twice.cashBalances))
