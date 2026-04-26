# OpenClaw cron wiring

Suggested jobs:

## 1. Scan every 15 minutes

Use an isolated cron job that runs:

```bash
cd /home/jccadmin/.openclaw/workspace/polymarket-autopilot && npm run scan
```

## 2. Morning report at 08:00 UTC

Run:

```bash
cd /home/jccadmin/.openclaw/workspace/polymarket-autopilot && npm run report
```

Then send the output to Laurynas on WhatsApp or to Discord if you switch surfaces.

## Notes

- v1 uses public market data only.
- No authenticated trading keys are needed.
- This is paper trading only.
- If you want stricter behavior, raise liquidity/volume thresholds and lower max position fraction.
