import Database from "better-sqlite3";
import fs from "node:fs";
import { config } from "./config.js";

fs.mkdirSync(config.dataDir, { recursive: true });

const db = new Database(config.dbPath);
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

export function getDb() {
  return db;
}

export function nowIso() {
  return new Date().toISOString();
}

export function getLatestPortfolio() {
  const row = db.prepare(`SELECT * FROM portfolio_snapshots ORDER BY created_at DESC LIMIT 1`).get();
  if (row) return row;

  const createdAt = nowIso();
  db.prepare(`
    INSERT INTO portfolio_snapshots (cash, position_value, total_value, realized_pnl, unrealized_pnl, open_positions, created_at)
    VALUES (@cash, 0, @cash, 0, 0, 0, @created_at)
  `).run({ cash: config.startingCash, created_at: createdAt });

  return db.prepare(`SELECT * FROM portfolio_snapshots ORDER BY id DESC LIMIT 1`).get();
}

export function savePortfolioSnapshot(snapshot) {
  db.prepare(`
    INSERT INTO portfolio_snapshots (
      cash, position_value, total_value, realized_pnl, unrealized_pnl, open_positions, created_at
    ) VALUES (
      @cash, @position_value, @total_value, @realized_pnl, @unrealized_pnl, @open_positions, @created_at
    )
  `).run(snapshot);
}
