import sqlite3, json
from pathlib import Path

root = Path('/home/jccadmin/.openclaw/workspace')
db = root / 'structured-memory' / 'memory.db'
now = '2026-04-26T00:00:00Z'

fact_id = 'fact.bridge-mode-zero-exported-artifacts-2026-04-26'
reflection_id = 'reflection.bridge-mode-still-without-exported-artifacts-2026-04-26'

conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = ON')

fact_claim = 'As of 2026-04-26, wiki_status reports memory-wiki bridge mode enabled with zero exported public memory artifacts.'
conn.execute(
    '''INSERT OR REPLACE INTO fact_claims
       (id, claim, domain, subject_refs_json, confidence, validation_state, owner, created_at, updated_at, last_reviewed_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM fact_claims WHERE id = ?), ?), ?, ?)''',
    (fact_id, fact_claim, 'memory-wiki', json.dumps(['memory-wiki', 'bridge-mode', 'wiki-status']), 0.93, 'verified', 'nightly-maintenance', fact_id, now, now, now)
)
conn.execute('DELETE FROM evidence_refs WHERE record_type = ? AND record_id = ?', ('fact_claim', fact_id))
for source_kind, source_path, source_locator, note, weight in [
    ('wiki_status', 'wiki-vault', 'status:2026-04-26', 'Bridge mode enabled, zero exported artifacts, bridge warning present.', 1.0),
    ('memory', 'memory/2026-04-18.md', 'lines 1-5', 'Bridge mode and nightly maintenance were explicitly enabled on 2026-04-18.', 0.7),
    ('wiki', 'wiki-vault/reports/lint.md', 'generated warnings', 'Lint still reflects only standing open questions, no contradiction with bridge gap.', 0.4),
]:
    conn.execute(
        'INSERT INTO evidence_refs(record_type, record_id, source_kind, source_path, source_locator, note, weight, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('fact_claim', fact_id, source_kind, source_path, source_locator, note, weight, now)
    )

obs = 'Bridge-mode wiki reconciliation is still operating without exported public memory artifacts on 2026-04-26, so nightly synthesis remains grounded mostly in daily notes, local dream artifacts, and existing wiki pages.'
pattern = 'Bridge mode remains enabled while wiki status reports zero exported artifacts across consecutive nightly reconciliations from 2026-04-20 through 2026-04-26.'
rec = 'Keep treating bridge-export absence as an operational follow-up, continue evidence-first ingestion from daily notes and explicit wiki pages, and avoid overstating compiled-wiki coverage until exports appear.'
conn.execute(
    '''INSERT OR REPLACE INTO reflections
       (id, observation, pattern, recommended_action, related_refs_json, confidence, promotion_state, owner, created_at, updated_at, last_reviewed_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM reflections WHERE id = ?), ?), ?, ?)''',
    (reflection_id, obs, pattern, rec, json.dumps([fact_id, 'synthesis.nightly-memory-reconcile-2026-04-26']), 0.87, 'candidate', 'nightly-maintenance', reflection_id, now, now, now)
)
conn.execute('DELETE FROM evidence_refs WHERE record_type = ? AND record_id = ?', ('reflection', reflection_id))
for source_kind, source_path, source_locator, note, weight in [
    ('wiki_status', 'wiki-vault', 'status:2026-04-26', 'Zero exported artifacts persists another night.', 1.0),
    ('wiki', 'wiki-vault/syntheses/nightly-memory-reconcile-2026-04-25.md', 'summary', 'Previous nightly synthesis recorded the same unresolved bridge export gap.', 0.8),
    ('memory', 'memory/2026-04-22.md', 'lines 1-4', 'Daily note confirms under-populated wiki artifacts remain a practical memory gap.', 0.7),
]:
    conn.execute(
        'INSERT INTO evidence_refs(record_type, record_id, source_kind, source_path, source_locator, note, weight, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('reflection', reflection_id, source_kind, source_path, source_locator, note, weight, now)
    )

conn.commit()
for q in [
    "SELECT id, claim, updated_at FROM fact_claims WHERE id = 'fact.bridge-mode-zero-exported-artifacts-2026-04-26'",
    "SELECT id, observation, updated_at FROM reflections WHERE id = 'reflection.bridge-mode-still-without-exported-artifacts-2026-04-26'",
    "SELECT record_type, record_id, source_kind, source_path, source_locator, weight FROM evidence_refs WHERE record_id IN ('fact.bridge-mode-zero-exported-artifacts-2026-04-26', 'reflection.bridge-mode-still-without-exported-artifacts-2026-04-26') ORDER BY record_type, id"
]:
    print('QUERY:', q)
    for row in conn.execute(q):
        print(row)
conn.close()
