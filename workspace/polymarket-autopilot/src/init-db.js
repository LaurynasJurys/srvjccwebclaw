import fs from "node:fs";
import { config } from "./config.js";
import { getDb, getLatestPortfolio } from "./db.js";

fs.mkdirSync(config.dataDir, { recursive: true });
const db = getDb();

db.exec(`
CREATE TABLE IF NOT EXISTS markets (
  market_id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  slug TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  end_date TEXT,
  liquidity REAL,
  volume REAL,
  outcome_yes_token_id TEXT,
  outcome_no_token_id TEXT,
  last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS market_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  market_id TEXT NOT NULL,
  yes_price REAL,
  no_price REAL,
  best_bid REAL,
  best_ask REAL,
  spread REAL,
  volume REAL,
  liquidity REAL,
  raw_json TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (market_id) REFERENCES markets(market_id)
);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_market_time ON market_snapshots (market_id, created_at DESC);

CREATE TABLE IF NOT EXISTS strategy_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  strategy TEXT NOT NULL,
  market_id TEXT NOT NULL,
  action TEXT NOT NULL,
  confidence REAL,
  rationale TEXT,
  raw_json TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_strategy_runs_time ON strategy_runs (created_at DESC);

CREATE TABLE IF NOT EXISTS paper_positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  market_id TEXT NOT NULL,
  question TEXT NOT NULL,
  strategy TEXT NOT NULL,
  side TEXT NOT NULL,
  quantity REAL NOT NULL,
  entry_price REAL NOT NULL,
  current_price REAL NOT NULL,
  status TEXT NOT NULL,
  entry_reason TEXT,
  opened_at TEXT NOT NULL,
  closed_at TEXT,
  exit_price REAL,
  realized_pnl REAL DEFAULT 0,
  notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_positions_status ON paper_positions (status, opened_at DESC);

CREATE TABLE IF NOT EXISTS paper_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  position_id INTEGER,
  market_id TEXT NOT NULL,
  strategy TEXT NOT NULL,
  side TEXT NOT NULL,
  order_type TEXT NOT NULL,
  quantity REAL NOT NULL,
  price REAL NOT NULL,
  notional REAL NOT NULL,
  status TEXT NOT NULL,
  rationale TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (position_id) REFERENCES paper_positions(id)
);
CREATE INDEX IF NOT EXISTS idx_orders_time ON paper_orders (created_at DESC);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cash REAL NOT NULL,
  position_value REAL NOT NULL,
  total_value REAL NOT NULL,
  realized_pnl REAL NOT NULL,
  unrealized_pnl REAL NOT NULL,
  open_positions INTEGER NOT NULL,
  created_at TEXT NOT NULL
);
`);

const portfolio = getLatestPortfolio();
console.log(`Database ready at ${config.dbPath}`);
console.log(`Portfolio cash: ${portfolio.cash}`);
