import sqlite3
from pathlib import Path

ROOT = Path('/home/jccadmin/.openclaw/workspace/structured-memory')
DB = ROOT / 'memory.db'
ROOT.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
conn.execute('PRAGMA foreign_keys = ON')

schema = '''
CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT,
  summary TEXT,
  attributes_json TEXT NOT NULL DEFAULT '{}',
  confidence REAL,
  validation_state TEXT NOT NULL DEFAULT 'verified',
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS entity_aliases (
  entity_id TEXT NOT NULL,
  alias TEXT NOT NULL,
  PRIMARY KEY (entity_id, alias),
  FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relations (
  id TEXT PRIMARY KEY,
  from_entity_id TEXT NOT NULL,
  relation_type TEXT NOT NULL,
  to_entity_id TEXT NOT NULL,
  attributes_json TEXT NOT NULL DEFAULT '{}',
  confidence REAL,
  validation_state TEXT NOT NULL DEFAULT 'verified',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (from_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
  FOREIGN KEY (to_entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS decisions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  decision_text TEXT NOT NULL,
  context TEXT,
  status TEXT NOT NULL,
  impact TEXT,
  confidence REAL,
  approved_by TEXT,
  validation_state TEXT NOT NULL DEFAULT 'accepted',
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS fact_claims (
  id TEXT PRIMARY KEY,
  claim TEXT NOT NULL,
  domain TEXT,
  subject_refs_json TEXT NOT NULL DEFAULT '[]',
  confidence REAL,
  validation_state TEXT NOT NULL DEFAULT 'candidate',
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS procedures (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  purpose TEXT,
  preconditions_json TEXT NOT NULL DEFAULT '[]',
  steps_json TEXT NOT NULL DEFAULT '[]',
  expected_outcomes_json TEXT NOT NULL DEFAULT '[]',
  rollback_json TEXT NOT NULL DEFAULT '[]',
  safety_notes_json TEXT NOT NULL DEFAULT '[]',
  confidence REAL,
  approval_state TEXT NOT NULL DEFAULT 'draft',
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS heuristics (
  id TEXT PRIMARY KEY,
  statement TEXT NOT NULL,
  scope TEXT,
  trigger_conditions_json TEXT NOT NULL DEFAULT '[]',
  exceptions_json TEXT NOT NULL DEFAULT '[]',
  confidence REAL,
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS reflections (
  id TEXT PRIMARY KEY,
  observation TEXT NOT NULL,
  pattern TEXT,
  recommended_action TEXT,
  related_refs_json TEXT NOT NULL DEFAULT '[]',
  confidence REAL,
  promotion_state TEXT NOT NULL DEFAULT 'candidate',
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS policy_rules (
  id TEXT PRIMARY KEY,
  rule_text TEXT NOT NULL,
  scope TEXT,
  priority TEXT,
  exceptions_json TEXT NOT NULL DEFAULT '[]',
  confidence REAL,
  approved_by TEXT,
  validation_state TEXT NOT NULL DEFAULT 'candidate',
  owner TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS evidence_refs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  record_type TEXT NOT NULL,
  record_id TEXT NOT NULL,
  source_kind TEXT NOT NULL,
  source_path TEXT,
  source_locator TEXT,
  note TEXT,
  weight REAL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_relations_from ON relations(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_to ON relations(to_entity_id);
CREATE INDEX IF NOT EXISTS idx_evidence_record ON evidence_refs(record_type, record_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_fact_claims_state ON fact_claims(validation_state);
CREATE INDEX IF NOT EXISTS idx_procedures_state ON procedures(approval_state);
CREATE INDEX IF NOT EXISTS idx_reflections_state ON reflections(promotion_state);
'''

conn.executescript(schema)
conn.execute("INSERT OR REPLACE INTO schema_meta(key, value) VALUES (?, ?)", ('schema_version', '1'))
conn.execute("INSERT OR REPLACE INTO schema_meta(key, value) VALUES (?, ?)", ('store_purpose', 'Layer 3 and 4 structured memory store'))
conn.commit()
conn.close()
print(DB)
