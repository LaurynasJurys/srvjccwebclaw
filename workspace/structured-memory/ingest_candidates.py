import argparse, json, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path

DB = Path('/home/jccadmin/.openclaw/workspace/structured-memory/memory.db')


def now():
    return datetime.now(timezone.utc).isoformat()


def make_id(prefix: str) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:12]}"


def add_evidence(conn, record_type, record_id, evidence):
    ts = now()
    for ref in evidence:
        conn.execute(
            'INSERT INTO evidence_refs(record_type, record_id, source_kind, source_path, source_locator, note, weight, created_at) VALUES (?,?,?,?,?,?,?,?)',
            (
                record_type,
                record_id,
                ref.get('source_kind', 'file'),
                ref.get('source_path'),
                ref.get('source_locator'),
                ref.get('note'),
                ref.get('weight'),
                ts,
            ),
        )


def insert_fact_claim(conn, payload):
    rid = payload.get('id') or make_id('fact')
    ts = now()
    conn.execute(
        'INSERT OR REPLACE INTO fact_claims(id, claim, domain, subject_refs_json, confidence, validation_state, owner, created_at, updated_at, last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
        (
            rid,
            payload['claim'],
            payload.get('domain'),
            json.dumps(payload.get('subject_refs', [])),
            payload.get('confidence', 0.5),
            payload.get('validation_state', 'candidate'),
            payload.get('owner', 'system'),
            payload.get('created_at', ts),
            ts,
            payload.get('last_reviewed_at'),
        ),
    )
    add_evidence(conn, 'fact_claim', rid, payload.get('evidence_refs', []))
    return rid


def insert_reflection(conn, payload):
    rid = payload.get('id') or make_id('reflection')
    ts = now()
    conn.execute(
        'INSERT OR REPLACE INTO reflections(id, observation, pattern, recommended_action, related_refs_json, confidence, promotion_state, owner, created_at, updated_at, last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (
            rid,
            payload['observation'],
            payload.get('pattern'),
            payload.get('recommended_action'),
            json.dumps(payload.get('related_refs', [])),
            payload.get('confidence', 0.5),
            payload.get('promotion_state', 'candidate'),
            payload.get('owner', 'system'),
            payload.get('created_at', ts),
            ts,
            payload.get('last_reviewed_at'),
        ),
    )
    add_evidence(conn, 'reflection', rid, payload.get('evidence_refs', []))
    return rid


def insert_procedure(conn, payload):
    rid = payload.get('id') or make_id('procedure')
    ts = now()
    conn.execute(
        'INSERT OR REPLACE INTO procedures(id, name, purpose, preconditions_json, steps_json, expected_outcomes_json, rollback_json, safety_notes_json, confidence, approval_state, owner, created_at, updated_at, last_reviewed_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (
            rid,
            payload['name'],
            payload.get('purpose'),
            json.dumps(payload.get('preconditions', [])),
            json.dumps(payload.get('steps', [])),
            json.dumps(payload.get('expected_outcomes', [])),
            json.dumps(payload.get('rollback', [])),
            json.dumps(payload.get('safety_notes', [])),
            payload.get('confidence', 0.5),
            payload.get('approval_state', 'draft'),
            payload.get('owner', 'system'),
            payload.get('created_at', ts),
            ts,
            payload.get('last_reviewed_at'),
        ),
    )
    add_evidence(conn, 'procedure', rid, payload.get('evidence_refs', []))
    return rid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('json_file')
    args = ap.parse_args()

    payload = json.loads(Path(args.json_file).read_text())
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys = ON')
    inserted = []

    for item in payload.get('fact_claims', []):
        inserted.append({'type': 'fact_claim', 'id': insert_fact_claim(conn, item)})
    for item in payload.get('reflections', []):
        inserted.append({'type': 'reflection', 'id': insert_reflection(conn, item)})
    for item in payload.get('procedures', []):
        inserted.append({'type': 'procedure', 'id': insert_procedure(conn, item)})

    conn.commit()
    conn.close()
    print(json.dumps({'inserted': inserted}, indent=2))

if __name__ == '__main__':
    main()
