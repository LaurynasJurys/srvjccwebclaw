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

## Argo CD / Kubernetes

This repo now includes a starter Kubernetes layout in `k8s/` for Argo CD.

Expected flow:
- push this app code to its own repo, for example `git@github.com:LaurynasJurys/polymarket-autopilot.git`
- build and publish the container image, for example `ghcr.io/laurynasjurys/polymarket-autopilot:latest`
- let Argo CD sync from `k8s/overlays/prod`

Current manifests include:
- namespace
- configmap
- persistent volume claim for SQLite
- dashboard deployment
- dashboard service
- dashboard ingress
- scan CronJob
- report CronJob

## Good next steps

1. Push this app into its own Git repo
2. Add GitHub Actions to build and publish the image
3. Add Keycloak auth middleware or OIDC-aware upstream auth in front of the dashboard
4. Add multi-snapshot indicators instead of only previous-snapshot comparisons
5. Add market-category exposure caps
6. Add a backtest runner over stored snapshots
7. Add dashboard charts from SQLite
