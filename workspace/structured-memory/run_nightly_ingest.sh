#!/usr/bin/env bash
set -euo pipefail
cd /home/jccadmin/.openclaw/workspace
python3 structured-memory/ingest_candidates.py structured-memory/nightly_candidates.json
