import sqlite3, sys
from pathlib import Path

DB = Path('/home/jccadmin/.openclaw/workspace/structured-memory/memory.db')
query = sys.argv[1] if len(sys.argv) > 1 else "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
rows = conn.execute(query).fetchall()
for row in rows:
    print(dict(row))
conn.close()
