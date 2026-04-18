import sqlite3, json
from datetime import datetime, timezone
from pathlib import Path

DB = Path('/home/jccadmin/.openclaw/workspace/structured-memory/memory.db')
now = datetime.now(timezone.utc).isoformat()
conn = sqlite3.connect(DB)

entities = [
    ('system.openclaw', 'system', 'OpenClaw', 'active', 'Personal assistant runtime and gateway', json.dumps({'surface': 'whatsapp'}), 0.95, 'verified', 'Laurynas', now, now, now),
    ('service.wikijs', 'service', 'Wiki.js', 'active', 'Durable operational memory and documentation surface', json.dumps({'url': 'https://wiki.jurys.lt'}), 0.95, 'verified', 'Laurynas', now, now, now),
    ('service.keycloak', 'service', 'Keycloak', 'active', 'OIDC identity provider for the environment', json.dumps({'realm': 'jcc', 'host': 'auth.jurys.lt'}), 0.95, 'verified', 'Laurynas', now, now, now),
    ('service.tailscale', 'service', 'Tailscale', 'active', 'Network exposure layer for OpenClaw web UI', json.dumps({}), 0.9, 'verified', 'Laurynas', now, now, now)
]
conn.executemany('INSERT OR REPLACE INTO entities(id,type,name,status,summary,attributes_json,confidence,validation_state,owner,created_at,updated_at,last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', entities)

relations = [
    ('rel.openclaw.exposed-via.tailscale', 'system.openclaw', 'is_exposed_via', 'service.tailscale', json.dumps({}), 0.95, 'verified', now, now),
    ('rel.wikijs.auth-via.keycloak', 'service.wikijs', 'authenticates_via', 'service.keycloak', json.dumps({}), 0.95, 'verified', now, now)
]
conn.executemany('INSERT OR REPLACE INTO relations(id,from_entity_id,relation_type,to_entity_id,attributes_json,confidence,validation_state,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)', relations)

decisions = [
    ('decision.wikijs-durable-memory', 'Use Wiki.js as durable operational memory', 'Wiki.js should be the durable operational memory surface for infrastructure, runbooks, and architectural knowledge.', 'The environment needed a persistent human-readable source of truth beyond raw chat and daily notes.', 'accepted', 'Improves operational continuity and documentation durability.', 0.95, 'Laurynas', 'accepted', 'Laurynas', now, now, now),
    ('decision.hybrid-memory-stack', 'Adopt a hybrid layered memory architecture', 'Use runtime memory for hot context, daily notes for episodic memory, Wiki.js plus indexed memory for durable semantic memory, and dreaming plus reconcile jobs for reflective maintenance.', 'A single raw chat history is not a durable or controllable memory system.', 'accepted', 'Creates a practical path toward richer agent memory over time.', 0.9, 'Laurynas', 'accepted', 'Laurynas', now, now, now)
]
conn.executemany('INSERT OR REPLACE INTO decisions(id,title,decision_text,context,status,impact,confidence,approved_by,validation_state,owner,created_at,updated_at,last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', decisions)

procedures = [
    ('procedure.nightly-memory-maintenance', 'Nightly memory and wiki maintenance', 'Reconcile memory and wiki nightly at 03:00 Europe/Vilnius.', json.dumps(['OpenClaw running', 'memory-core enabled', 'memory-wiki enabled']), json.dumps(['Review recent memory files', 'Inspect candidate durable updates', 'Lint wiki and memory state', 'Surface only meaningful blockers or results']), json.dumps(['Memory and wiki remain reconciled', 'Contradictions are surfaced']), json.dumps(['Do not store secrets in wiki', 'Do not auto-canonize risky claims']), json.dumps(['Prefer suggestion and validation over silent authority']), 0.9, 'approved', 'Laurynas', now, now, now)
]
conn.executemany('INSERT OR REPLACE INTO procedures(id,name,purpose,preconditions_json,steps_json,expected_outcomes_json,rollback_json,safety_notes_json,confidence,approval_state,owner,created_at,updated_at,last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', procedures)

reflections = [
    ('reflection.layer3-layer4-current-state', 'Layer 3 and 4 are operational but still early-stage.', 'Current durable memory is hybrid and current reflective memory is maintenance-oriented rather than a fully typed procedural engine.', 'Implement a structured SQLite store for typed records and keep Wiki.js as the rendered surface.', json.dumps(['architecture/agent-memory', 'architecture/memory-implementation-map', 'architecture/structured-memory-schema']), 0.88, 'promoted', 'Laurynas', now, now, now)
]
conn.executemany('INSERT OR REPLACE INTO reflections(id,observation,pattern,recommended_action,related_refs_json,confidence,promotion_state,owner,created_at,updated_at,last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)', reflections)

facts = [
    ('fact.openclaw-dreaming-enabled', 'OpenClaw memory-core dreaming is enabled nightly at 03:00 Europe/Vilnius.', 'openclaw', json.dumps(['system.openclaw']), 0.95, 'verified', 'Laurynas', now, now, now)
]
conn.executemany('INSERT OR REPLACE INTO fact_claims(id,claim,domain,subject_refs_json,confidence,validation_state,owner,created_at,updated_at,last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?)', facts)

conn.commit()
conn.close()
print(DB)
