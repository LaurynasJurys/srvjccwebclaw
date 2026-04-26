# Polymarket Autopilot v1

A local SQLite-backed Polymarket paper trading prototype for OpenClaw.

## What it does

- Fetches active Polymarket markets from the public API
- Stores market snapshots in SQLite
- Runs simple signal generation for:
  - TAIL momentum
  - mean reversion
- Simulates paper entries and exits
- Tracks portfolio snapshots
- Prints a daily-style summary report

## Quick start

```bash
cd polymarket-autopilot
npm install
npm run init-db
npm run scan
npm run report
```

## Files

- `src/init-db.js` initializes schema
- `src/polymarket.js` fetches and normalizes market data
- `src/scan.js` stores snapshots and executes strategies
- `src/report.js` prints a human-readable report
- `src/portfolio.js` manages position sizing, exits, and portfolio snapshots

## Important limits

- Public data only, no real trading
- No news ingestion yet
- No historical backtester yet
- Fill logic is conservative but still simplified
- Strategy logic is intentionally basic for v1

## Good next steps

1. Add multi-snapshot indicators instead of only previous-snapshot comparisons
2. Add market-category exposure caps
3. Add a backtest runner over stored snapshots
4. Add message delivery automation for reports
5. Add dashboard charts from SQLite
