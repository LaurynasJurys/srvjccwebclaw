#!/usr/bin/env bash
set -euo pipefail

REPO="/home/jccadmin/.openclaw"
LOCK="$REPO/.sync.lock"
LOGDIR="$REPO/logs"
LOGFILE="$LOGDIR/git-sync.log"
TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

mkdir -p "$LOGDIR"

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$TS] sync skipped, lock busy" >> "$LOGFILE"
  exit 0
fi

log() {
  echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*" >> "$LOGFILE"
}

cd "$REPO"
branch="$(git rev-parse --abbrev-ref HEAD)"

if ! git fetch origin "$branch" >> "$LOGFILE" 2>&1; then
  log "fetch failed"
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  log "local changes detected, creating auto-sync commit before pull"
  git add -A
  if ! git diff --cached --quiet; then
    if ! git commit -m "Auto-sync $(date -u +'%Y-%m-%d %H:%M:%S UTC')" >> "$LOGFILE" 2>&1; then
      log "commit failed"
      exit 1
    fi
  fi
fi

if ! git pull --rebase --autostash origin "$branch" >> "$LOGFILE" 2>&1; then
  log "pull/rebase failed, manual resolution required"
  git rebase --abort >> "$LOGFILE" 2>&1 || true
  exit 1
fi

if ! git push origin "$branch" >> "$LOGFILE" 2>&1; then
  log "push failed"
  exit 1
fi

log "sync ok"
