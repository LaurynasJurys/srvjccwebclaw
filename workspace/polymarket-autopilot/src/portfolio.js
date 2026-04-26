import { config } from "./config.js";
import { getDb, getLatestPortfolio, nowIso, savePortfolioSnapshot } from "./db.js";

const db = getDb();

export function getOpenPositions() {
  return db.prepare(`SELECT * FROM paper_positions WHERE status = 'OPEN' ORDER BY opened_at ASC`).all();
}

export function hasOpenPositionForMarket(marketId) {
  const row = db.prepare(`SELECT id FROM paper_positions WHERE market_id = ? AND status = 'OPEN' LIMIT 1`).get(marketId);
  return Boolean(row);
}

export function computePositionSize(price) {
  const portfolio = getLatestPortfolio();
  const maxNotional = portfolio.total_value * config.maxPositionFraction;
  if (price <= 0) return 0;
  return Number((maxNotional / price).toFixed(4));
}

export function openPosition({ market, signal }) {
  const side = signal.action === 'BUY_NO' ? 'NO' : 'YES';
  const fillPrice = side === 'YES' ? market.bestAsk : Math.max(0.01, 1 - market.bestBid);
  const quantity = computePositionSize(fillPrice);
  const notional = Number((quantity * fillPrice).toFixed(4));
  if (quantity <= 0 || notional <= 0) return null;

  const portfolio = getLatestPortfolio();
  if (portfolio.cash < notional) return null;

  const openedAt = nowIso();
  const tx = db.transaction(() => {
    const positionResult = db.prepare(`
      INSERT INTO paper_positions (
        market_id, question, strategy, side, quantity, entry_price, current_price, status, entry_reason, opened_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
    `).run(market.marketId, market.question, signal.strategy, side, quantity, fillPrice, fillPrice, signal.rationale, openedAt);

    db.prepare(`
      INSERT INTO paper_orders (
        position_id, market_id, strategy, side, order_type, quantity, price, notional, status, rationale, created_at
      ) VALUES (?, ?, ?, ?, 'ENTRY', ?, ?, ?, 'FILLED', ?, ?)
    `).run(positionResult.lastInsertRowid, market.marketId, signal.strategy, side, quantity, fillPrice, notional, signal.rationale, openedAt);

    savePortfolioSnapshot({
      cash: Number((portfolio.cash - notional).toFixed(4)),
      position_value: portfolio.position_value,
      total_value: portfolio.total_value,
      realized_pnl: portfolio.realized_pnl,
      unrealized_pnl: portfolio.unrealized_pnl,
      open_positions: getOpenPositions().length + 1,
      created_at: openedAt
    });

    return positionResult.lastInsertRowid;
  });

  return tx();
}

export function updateAndClosePositions(marketsById) {
  const openPositions = getOpenPositions();
  const now = Date.now();
  let closedCount = 0;

  for (const position of openPositions) {
    const market = marketsById.get(position.market_id);
    if (!market) continue;

    const currentPrice = position.side === 'YES' ? market.bestBid : Math.max(0.01, 1 - market.bestAsk);
    db.prepare(`UPDATE paper_positions SET current_price = ? WHERE id = ?`).run(currentPrice, position.id);

    const ageHours = (now - Date.parse(position.opened_at)) / 36e5;
    const pnl = Number(((currentPrice - position.entry_price) * position.quantity).toFixed(4));
    const shouldClose = ageHours >= config.maxHoldingHours || pnl >= position.entry_price * position.quantity * 0.1 || pnl <= -(position.entry_price * position.quantity * 0.08);

    if (!shouldClose) continue;

    const closedAt = nowIso();
    const notional = Number((currentPrice * position.quantity).toFixed(4));
    const portfolio = getLatestPortfolio();

    db.transaction(() => {
      db.prepare(`
        UPDATE paper_positions
        SET status = 'CLOSED', closed_at = ?, exit_price = ?, realized_pnl = ?, current_price = ?
        WHERE id = ?
      `).run(closedAt, currentPrice, pnl, currentPrice, position.id);

      db.prepare(`
        INSERT INTO paper_orders (
          position_id, market_id, strategy, side, order_type, quantity, price, notional, status, rationale, created_at
        ) VALUES (?, ?, ?, ?, 'EXIT', ?, ?, ?, 'FILLED', ?, ?)
      `).run(position.id, position.market_id, position.strategy, position.side, position.quantity, currentPrice, notional, `Auto exit after ${ageHours.toFixed(1)}h, pnl ${pnl.toFixed(2)}`, closedAt);

      savePortfolioSnapshot({
        cash: Number((portfolio.cash + notional).toFixed(4)),
        position_value: portfolio.position_value,
        total_value: portfolio.total_value,
        realized_pnl: Number((portfolio.realized_pnl + pnl).toFixed(4)),
        unrealized_pnl: portfolio.unrealized_pnl,
        open_positions: Math.max(0, getOpenPositions().length - 1),
        created_at: closedAt
      });
    })();

    closedCount += 1;
  }

  refreshPortfolioSnapshot(marketsById);
  return closedCount;
}

export function refreshPortfolioSnapshot(marketsById) {
  const openPositions = getOpenPositions();
  const portfolio = getLatestPortfolio();
  let positionValue = 0;
  let unrealizedPnl = 0;

  for (const position of openPositions) {
    const market = marketsById.get(position.market_id);
    const mark = market ? (position.side === 'YES' ? market.bestBid : Math.max(0.01, 1 - market.bestAsk)) : position.current_price;
    positionValue += mark * position.quantity;
    unrealizedPnl += (mark - position.entry_price) * position.quantity;
  }

  savePortfolioSnapshot({
    cash: portfolio.cash,
    position_value: Number(positionValue.toFixed(4)),
    total_value: Number((portfolio.cash + positionValue).toFixed(4)),
    realized_pnl: portfolio.realized_pnl,
    unrealized_pnl: Number(unrealizedPnl.toFixed(4)),
    open_positions: openPositions.length,
    created_at: nowIso()
  });
}
