import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

root = Path('/home/jccadmin/.openclaw/workspace')
db = root / 'structured-memory' / 'memory.db'
recall = json.loads((root / 'memory' / '.dreams' / 'short-term-recall.json').read_text())
updated_at = recall.get('updatedAt')
entries = recall.get('entries', {})
keys = sorted(entries.keys())
newest_spans = []
for k in keys:
    e = entries[k]
    newest_spans.append({
        'path': e.get('path'),
        'startLine': e.get('startLine'),
        'endLine': e.get('endLine'),
        'lastRecalledAt': e.get('lastRecalledAt'),
        'recallCount': e.get('recallCount'),
    })
newest_spans = sorted(newest_spans, key=lambda x: x.get('lastRecalledAt') or '', reverse=True)[:5]

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
counts = {}
for table in ['fact_claims','reflections','procedures','evidence_refs']:
    counts[table] = conn.execute(f'SELECT COUNT(*) c FROM {table}').fetchone()['c']
recent = [dict(r) for r in conn.execute("SELECT id, claim, updated_at FROM fact_claims ORDER BY updated_at DESC LIMIT 5")]
conn.close()

payload = {
  'generatedAt': datetime.now(timezone.utc).isoformat(),
  'fact_claims': [
    {
      'id': 'fact.bridge-mode-zero-exported-artifacts-2026-04-30',
      'claim': 'As of 2026-04-30, wiki_status reports memory-wiki bridge mode enabled with zero exported public memory artifacts.',
      'domain': 'memory-wiki',
      'subject_refs': ['memory-wiki', 'bridge-mode', 'wiki-status'],
      'confidence': 0.94,
      'validation_state': 'verified',
      'owner': 'nightly-maintenance',
      'last_reviewed_at': '2026-04-30T00:00:00Z',
      'evidence_refs': [
        {
          'source_kind': 'wiki_status',
          'source_path': 'wiki-vault',
          'source_locator': 'status:2026-04-30',
          'note': 'Bridge mode enabled, zero exported artifacts, bridge warning present.',
          'weight': 1.0
        },
        {
          'source_kind': 'memory',
          'source_path': 'memory/2026-04-18.md',
          'source_locator': 'lines 1-5',
          'note': 'Bridge mode and nightly maintenance were explicitly enabled on 2026-04-18.',
          'weight': 0.7
        },
        {
          'source_kind': 'wiki',
          'source_path': 'wiki-vault/syntheses/nightly-memory-reconcile-2026-04-29.md',
          'source_locator': 'summary',
          'note': 'Previous nightly synthesis recorded the same unresolved bridge export gap on 2026-04-29.',
          'weight': 0.8
        }
      ]
    }
  ],
  'reflections': [
    {
      'id': 'reflection.bridge-mode-still-without-exported-artifacts-2026-04-30',
      'observation': 'Bridge-mode wiki reconciliation is still operating without exported public memory artifacts on 2026-04-30, so nightly synthesis remains grounded mostly in daily notes, local dream artifacts, and existing wiki pages.',
      'pattern': 'Bridge mode remains enabled while wiki status reports zero exported artifacts across consecutive nightly reconciliations from 2026-04-20 through 2026-04-30.',
      'recommended_action': 'Keep treating bridge-export absence as an operational follow-up, continue evidence-first ingestion from daily notes and explicit wiki pages, and avoid overstating compiled-wiki coverage until exports appear.',
      'related_refs': ['fact.bridge-mode-zero-exported-artifacts-2026-04-30', 'synthesis.nightly-memory-reconcile-2026-04-29'],
      'confidence': 0.88,
      'promotion_state': 'candidate',
      'owner': 'nightly-maintenance',
      'last_reviewed_at': '2026-04-30T00:00:00Z',
      'evidence_refs': [
        {
          'source_kind': 'wiki_status',
          'source_path': 'wiki-vault',
          'source_locator': 'status:2026-04-30',
          'note': 'Zero exported artifacts persists another night.',
          'weight': 1.0
        },
        {
          'source_kind': 'wiki',
          'source_path': 'wiki-vault/syntheses/nightly-memory-reconcile-2026-04-29.md',
          'source_locator': 'summary',
          'note': 'Previous nightly synthesis recorded the same unresolved bridge export gap.',
          'weight': 0.8
        },
        {
          'source_kind': 'memory',
          'source_path': 'memory/2026-04-22.md',
          'source_locator': 'lines 1-4',
          'note': 'Daily note confirms under-populated wiki artifacts remain a practical memory gap.',
          'weight': 0.7
        }
      ]
    },
    {
      'id': 'reflection.no-new-episodic-evidence-since-2026-04-22',
      'observation': 'No new daily memory note was found after 2026-04-22 during the 2026-04-30 maintenance run.',
      'pattern': 'Recent nightly reconciles are reprocessing the same episodic evidence set, with dream recall traces reinforcing retrieval of older April notes rather than surfacing new source material.',
      'recommended_action': 'Treat the current memory state as stable but stale, avoid promoting new durable claims from recall traces alone, and wait for fresh daily notes or explicit new workspace artifacts before expanding operational canon.',
      'related_refs': ['synthesis.nightly-memory-reconcile-2026-04-29'],
      'confidence': 0.83,
      'promotion_state': 'candidate',
      'owner': 'nightly-maintenance',
      'last_reviewed_at': '2026-04-30T00:00:00Z',
      'evidence_refs': [
        {
          'source_kind': 'memory',
          'source_path': 'memory/2026-04-22.md',
          'source_locator': 'full note',
          'note': 'Newest daily memory note present in workspace.',
          'weight': 0.9
        },
        {
          'source_kind': 'dream-recall',
          'source_path': 'memory/.dreams/short-term-recall.json',
          'source_locator': f'updatedAt:{updated_at}',
          'note': 'Recall spans continue to reference April 17-22 notes rather than newer memory files.',
          'weight': 0.7
        },
        {
          'source_kind': 'wiki',
          'source_path': 'wiki-vault/syntheses/nightly-memory-reconcile-2026-04-29.md',
          'source_locator': 'summary',
          'note': 'Previous nightly synthesis already noted the lack of newer substantive episodic evidence.',
          'weight': 0.8
        }
      ]
    }
  ],
  'procedures': []
}

out = root / 'structured-memory' / 'nightly_candidates-2026-04-30.json'
out.write_text(json.dumps(payload, indent=2) + '\n')
print(json.dumps({'wrote': str(out), 'db_counts_before': counts, 'recent_fact_claims': recent, 'top_recall_spans': newest_spans}, indent=2))
