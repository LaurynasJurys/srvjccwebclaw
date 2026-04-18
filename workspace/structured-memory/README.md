# Structured memory SQLite store

This directory contains the first real implementation of typed layer 3 and layer 4 memory.

## Files
- `memory.db` - SQLite database
- `init_sqlite_memory.py` - creates schema
- `seed_sqlite_memory.py` - seeds initial known entities, decisions, procedures, reflections, and facts
- `query_memory.py` - quick query helper

## Record families
- `entities`
- `relations`
- `decisions`
- `fact_claims`
- `procedures`
- `heuristics`
- `reflections`
- `policy_rules`
- `evidence_refs`

## Design intent
- SQLite is the typed durable store for structured memory.
- Wiki.js remains the human-readable operational surface.
- Daily notes and existing memory files remain evidence and episodic memory.
- High-impact records should still be validated before becoming canonical.

## Initialize
```bash
python3 structured-memory/init_sqlite_memory.py
python3 structured-memory/seed_sqlite_memory.py
```

## Example query
```bash
python3 structured-memory/query_memory.py "SELECT id, name, type FROM entities ORDER BY id"
```
