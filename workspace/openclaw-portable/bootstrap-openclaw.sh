#!/usr/bin/env bash
set -euo pipefail

STATE_DIR=${STATE_DIR:-/home/jccadmin/.openclaw}
WORKSPACE_DIR=${WORKSPACE_DIR:-$STATE_DIR/workspace}
TEMPLATE_JSON=${TEMPLATE_JSON:-$WORKSPACE_DIR/openclaw-portable/openclaw.template.json}
ENV_FILE=${ENV_FILE:-$STATE_DIR/.env}
SYSTEMD_ENV_FILE=${SYSTEMD_ENV_FILE:-$STATE_DIR/gateway.systemd.env}
TARGET_JSON=${TARGET_JSON:-$STATE_DIR/openclaw.json}
SERVICE_NAME=${SERVICE_NAME:-openclaw-gateway}

mkdir -p "$STATE_DIR" "$WORKSPACE_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  echo "Start from $WORKSPACE_DIR/openclaw-portable/openclaw.env.example and source secrets from Vault." >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

: "${OPENCLAW_GATEWAY_PASSWORD:?OPENCLAW_GATEWAY_PASSWORD is required}"
: "${OPENCLAW_ALLOWED_ORIGIN:?OPENCLAW_ALLOWED_ORIGIN is required}"
: "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"

python3 - <<'PY' > "$TARGET_JSON"
import os, json
from pathlib import Path
p = Path(os.environ['TEMPLATE_JSON'])
raw = p.read_text()
for key in ['OPENCLAW_GATEWAY_PASSWORD', 'OPENCLAW_ALLOWED_ORIGIN']:
    raw = raw.replace('${'+key+'}', os.environ[key])
print(raw)
PY

install -m 600 "$ENV_FILE" "$SYSTEMD_ENV_FILE"

if command -v systemctl >/dev/null 2>&1; then
  systemctl daemon-reload || true
  systemctl enable "$SERVICE_NAME" || true
  systemctl restart "$SERVICE_NAME"
fi

echo "Bootstrap complete. Validate with: openclaw health && openclaw status"
