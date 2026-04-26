import { config } from "./config.js";
import { getDb } from "./db.js";

const db = getDb();
const sinceIso = new Date(Date.now() - config.reportLookbackHours * 3600 * 1000).toISOString();

function fmt(n) {
  return Number(n || 0).toFixed(2);
}

const latestPortfolio = db.prepare(`SELECT * FROM portfolio_snapshots ORDER BY created_at DESC LIMIT 1`).get();
const recentOrders = db.prepare(`
  SELECT * FROM paper_orders WHERE created_at >= ? ORDER BY created_at DESC LIMIT 20
`).all(sinceIso);
const openPositions = db.prepare(`
  SELECT * FROM paper_positions WHERE status = 'OPEN' ORDER BY opened_at DESC LIMIT 10
`).all();
const strategyStats = db.prepare(`
  SELECT strategy,
         COUNT(*) AS trades,
         SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) AS wins,
         SUM(realized_pnl) AS pnl
  FROM paper_positions
  WHERE status = 'CLOSED'
  GROUP BY strategy
  ORDER BY pnl DESC
`).all();

const lines = [];
lines.push(`Polymarket paper trading summary, last ${config.reportLookbackHours}h`);
if (latestPortfolio) {
  lines.push(`Portfolio: total $${fmt(latestPortfolio.total_value)}, cash $${fmt(latestPortfolio.cash)}, unrealized $${fmt(latestPortfolio.unrealized_pnl)}, realized $${fmt(latestPortfolio.realized_pnl)}`);
}

lines.push("");
lines.push("Recent orders:");
if (!recentOrders.length) {
  lines.push("- No entries or exits in the window");
} else {
  for (const order of recentOrders.slice(0, 8)) {
    lines.push(`- ${order.created_at}: ${order.order_type} ${order.side} ${fmt(order.quantity)} @ ${fmt(order.price)} via ${order.strategy}`);
  }
}

lines.push("");
lines.push("Open positions:");
if (!openPositions.length) {
  lines.push("- None");
} else {
  for (const position of openPositions.slice(0, 8)) {
    const markPnl = (Number(position.current_price) - Number(position.entry_price)) * Number(position.quantity);
    lines.push(`- ${position.strategy} ${position.side} on \"${position.question}\": qty ${fmt(position.quantity)}, entry ${fmt(position.entry_price)}, mark ${fmt(position.current_price)}, pnl ${fmt(markPnl)}`);
  }
}

lines.push("");
lines.push("Strategy stats:");
if (!strategyStats.length) {
  lines.push("- No closed trades yet");
} else {
  for (const stat of strategyStats) {
    const winRate = stat.trades ? ((stat.wins / stat.trades) * 100).toFixed(0) : "0";
    lines.push(`- ${stat.strategy}: trades ${stat.trades}, win rate ${winRate}%, pnl $${fmt(stat.pnl)}`);
  }
}

console.log(lines.join("\n"));
