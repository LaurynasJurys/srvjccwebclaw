import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

root = Path('/home/jccadmin/.openclaw/workspace')
mem_dir = root / 'memory'
wiki_dir = root / 'wiki-vault'
sm_dir = root / 'structured-memory'

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

updated_at = utcnow()
today = updated_at[:10]

daily_files = sorted([p for p in mem_dir.glob('*.md') if p.is_file()])
latest_daily = daily_files[-1] if daily_files else None

short_term = json.loads((mem_dir / '.dreams' / 'short-term-recall.json').read_text())
recall_entries = short_term.get('entries', {})
latest_recall_at = short_term.get('updatedAt')
recall_days = sorted({d for e in recall_entries.values() for d in e.get('recallDays', [])})

lint_text = (wiki_dir / 'reports' / 'lint.md').read_text()
warning_count = 0
for line in lint_text.splitlines():
    if line.strip().startswith('- Warnings:'):
        try:
            warning_count = int(line.split(':', 1)[1].strip())
        except Exception:
            pass

conn = sqlite3.connect(sm_dir / 'memory.db')
conn.row_factory = sqlite3.Row
existing_bridge = conn.execute("SELECT id FROM fact_claims WHERE id = ?", ('fact.bridge-mode-zero-exported-artifacts-2026-05-04',)).fetchone()
existing_recall = conn.execute("SELECT id FROM reflections WHERE id = ?", ('reflection.no-new-daily-notes-through-2026-05-04',)).fetchone()
conn.close()

fact_claims = [
    {
        'id': 'fact.bridge-mode-zero-exported-artifacts-2026-05-04',
        'claim': 'As of 2026-05-04, wiki_status reports memory-wiki bridge mode enabled with zero exported public memory artifacts.',
        'domain': 'memory-wiki',
        'subject_refs': ['memory-wiki', 'bridge-mode', 'wiki-status'],
        'confidence': 0.94,
        'validation_state': 'verified',
        'owner': 'nightly-maintenance',
        'last_reviewed_at': updated_at,
        'evidence_refs': [
            {
                'source_kind': 'wiki_status',
                'source_path': 'wiki-vault',
                'source_locator': 'status:2026-05-04',
                'note': 'Bridge mode enabled, zero exported artifacts, bridge warning present.',
                'weight': 1.0
            },
            {
                'source_kind': 'memory',
                'source_path': 'memory/2026-04-18.md',
                'source_locator': 'lines 1-7',
                'note': 'Bridge mode and nightly maintenance were enabled on 2026-04-18.',
                'weight': 0.7
            },
            {
                'source_kind': 'wiki',
                'source_path': 'wiki-vault/syntheses/nightly-memory-reconcile-2026-05-03.md',
                'source_locator': 'summary',
                'note': 'Previous nightly synthesis recorded the same unresolved bridge export gap on 2026-05-03.',
                'weight': 0.8
            }
        ]
    }
]

reflections = []
if latest_daily and latest_daily.name == '2026-04-22.md':
    reflections.append(
        {
            'id': 'reflection.no-new-daily-notes-through-2026-05-04',
            'observation': 'No daily memory note newer than 2026-04-22 was present during the 2026-05-04 nightly reconcile, so fresh episodic evidence remains stalled.',
            'pattern': 'Nightly reconcile continues to run against the same late-April daily memory surface instead of receiving newer daily notes.',
            'recommended_action': 'Keep nightly maintenance evidence-first, but avoid promoting new durable user-facing memory from absence alone; gather newer daily notes before widening operational canon.',
            'related_refs': ['memory/2026-04-22.md', 'fact.bridge-mode-zero-exported-artifacts-2026-05-04'],
            'confidence': 0.83,
            'promotion_state': 'candidate',
            'owner': 'nightly-maintenance',
            'last_reviewed_at': updated_at,
            'evidence_refs': [
                {
                    'source_kind': 'memory',
                    'source_path': str(latest_daily.relative_to(root)),
                    'source_locator': 'file-date',
                    'note': 'Latest available daily note in workspace is still 2026-04-22.',
                    'weight': 1.0
                },
                {
                    'source_kind': 'dream',
                    'source_path': 'memory/.dreams/short-term-recall.json',
                    'source_locator': 'updatedAt',
                    'note': f'Short-term recall artifact updated at {latest_recall_at} still points back to older April sources.',
                    'weight': 0.7
                },
                {
                    'source_kind': 'wiki',
                    'source_path': 'wiki-vault/syntheses/nightly-memory-reconcile-2026-05-03.md',
                    'source_locator': 'summary',
                    'note': 'Previous nightly synthesis already noted lack of newer daily memory notes.',
                    'weight': 0.8
                }
            ]
        }
    )

payload = {
    'generatedAt': updated_at,
    'fact_claims': fact_claims,
    'reflections': reflections,
    'procedures': []
}

out_dated = sm_dir / f'nightly_candidates-{today}.json'
out_default = sm_dir / 'nightly_candidates.json'
out_dated.write_text(json.dumps(payload, indent=2) + '\n')
out_default.write_text(json.dumps(payload, indent=2) + '\n')

print(json.dumps({
    'generatedAt': updated_at,
    'wrote': [str(out_dated), str(out_default)],
    'dailyFiles': [p.name for p in daily_files],
    'latestDaily': latest_daily.name if latest_daily else None,
    'shortTermRecallEntries': len(recall_entries),
    'shortTermRecallDays': recall_days,
    'lintWarnings': warning_count,
    'existingBridgeRecord': bool(existing_bridge),
    'existingNoNewDailyReflection': bool(existing_recall)
}, indent=2))
