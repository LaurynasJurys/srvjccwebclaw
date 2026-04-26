import http from "node:http";
import { getDb } from "./db.js";

const db = getDb();
const port = Number(process.env.PORT || 3000);

function fmt(n) {
  return Number(n || 0).toFixed(2);
}

function html({ portfolio, openPositions, recentOrders, strategyStats }) {
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Polymarket Autopilot</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 32px; background: #0b1020; color: #e8ecf1; }
    .cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px; }
    .card { background:#151c33; border-radius:16px; padding:18px; box-shadow: 0 8px 24px rgba(0,0,0,.2); }
    h1,h2 { margin:0 0 12px; }
    table { width:100%; border-collapse: collapse; background:#151c33; border-radius:16px; overflow:hidden; margin-bottom:24px; }
    th, td { padding:12px; border-bottom:1px solid #24304f; text-align:left; font-size:14px; }
    th { color:#98a2b3; }
    .muted { color:#98a2b3; }
  </style>
</head>
<body>
  <h1>Polymarket Autopilot</h1>
  <p class="muted">Paper trading dashboard</p>

  <div class="cards">
    <div class="card"><h2>Total</h2><div>$${fmt(portfolio?.total_value)}</div></div>
    <div class="card"><h2>Cash</h2><div>$${fmt(portfolio?.cash)}</div></div>
    <div class="card"><h2>Realized P&L</h2><div>$${fmt(portfolio?.realized_pnl)}</div></div>
    <div class="card"><h2>Unrealized P&L</h2><div>$${fmt(portfolio?.unrealized_pnl)}</div></div>
  </div>

  <h2>Open Positions</h2>
  <table>
    <tr><th>Strategy</th><th>Market</th><th>Side</th><th>Qty</th><th>Entry</th><th>Mark</th></tr>
    ${(openPositions.length ? openPositions.map((p) => `<tr><td>${p.strategy}</td><td>${p.question}</td><td>${p.side}</td><td>${fmt(p.quantity)}</td><td>${fmt(p.entry_price)}</td><td>${fmt(p.current_price)}</td></tr>`).join("") : `<tr><td colspan="6">No open positions</td></tr>`)}
  </table>

  <h2>Recent Orders</h2>
  <table>
    <tr><th>Time</th><th>Type</th><th>Strategy</th><th>Side</th><th>Qty</th><th>Price</th></tr>
    ${(recentOrders.length ? recentOrders.map((o) => `<tr><td>${o.created_at}</td><td>${o.order_type}</td><td>${o.strategy}</td><td>${o.side}</td><td>${fmt(o.quantity)}</td><td>${fmt(o.price)}</td></tr>`).join("") : `<tr><td colspan="6">No recent orders</td></tr>`)}
  </table>

  <h2>Strategy Stats</h2>
  <table>
    <tr><th>Strategy</th><th>Trades</th><th>Wins</th><th>P&L</th></tr>
    ${(strategyStats.length ? strategyStats.map((s) => `<tr><td>${s.strategy}</td><td>${s.trades}</td><td>${s.wins}</td><td>$${fmt(s.pnl)}</td></tr>`).join("") : `<tr><td colspan="4">No closed trades yet</td></tr>`)}
  </table>
</body>
</html>`;
}

const server = http.createServer((_req, res) => {
  const portfolio = db.prepare(`SELECT * FROM portfolio_snapshots ORDER BY created_at DESC LIMIT 1`).get();
  const openPositions = db.prepare(`SELECT * FROM paper_positions WHERE status = 'OPEN' ORDER BY opened_at DESC LIMIT 20`).all();
  const recentOrders = db.prepare(`SELECT * FROM paper_orders ORDER BY created_at DESC LIMIT 20`).all();
  const strategyStats = db.prepare(`
    SELECT strategy, COUNT(*) AS trades,
           SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) AS wins,
           SUM(realized_pnl) AS pnl
    FROM paper_positions
    WHERE status = 'CLOSED'
    GROUP BY strategy
    ORDER BY pnl DESC
  `).all();

  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(html({ portfolio, openPositions, recentOrders, strategyStats }));
});

server.listen(port, () => {
  console.log(`Dashboard listening on ${port}`);
});
