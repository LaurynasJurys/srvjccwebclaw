import { getDb, nowIso } from "./db.js";
import { fetchMarkets } from "./polymarket.js";
import { tailStrategy } from "./strategies/tail.js";
import { meanReversionStrategy } from "./strategies/meanReversion.js";
import { hasOpenPositionForMarket, openPosition, refreshPortfolioSnapshot, updateAndClosePositions } from "./portfolio.js";

const db = getDb();
const strategies = [tailStrategy, meanReversionStrategy];

function getPreviousSnapshot(marketId) {
  return db.prepare(`
    SELECT * FROM market_snapshots WHERE market_id = ? ORDER BY created_at DESC LIMIT 1
  `).get(marketId);
}

function upsertMarket(market) {
  db.prepare(`
    INSERT INTO markets (
      market_id, question, slug, active, end_date, liquidity, volume, outcome_yes_token_id, outcome_no_token_id, last_seen_at
    ) VALUES (
      @market_id, @question, @slug, @active, @end_date, @liquidity, @volume, @outcome_yes_token_id, @outcome_no_token_id, @last_seen_at
    )
    ON CONFLICT(market_id) DO UPDATE SET
      question = excluded.question,
      slug = excluded.slug,
      active = excluded.active,
      end_date = excluded.end_date,
      liquidity = excluded.liquidity,
      volume = excluded.volume,
      outcome_yes_token_id = excluded.outcome_yes_token_id,
      outcome_no_token_id = excluded.outcome_no_token_id,
      last_seen_at = excluded.last_seen_at
  `).run({
    market_id: market.marketId,
    question: market.question,
    slug: market.slug,
    active: market.active ? 1 : 0,
    end_date: market.endDate,
    liquidity: market.liquidity,
    volume: market.volume,
    outcome_yes_token_id: market.outcomeYesTokenId,
    outcome_no_token_id: market.outcomeNoTokenId,
    last_seen_at: nowIso()
  });
}

function insertSnapshot(market) {
  db.prepare(`
    INSERT INTO market_snapshots (
      market_id, yes_price, no_price, best_bid, best_ask, spread, volume, liquidity, raw_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    market.marketId,
    market.yesPrice,
    market.noPrice,
    market.bestBid,
    market.bestAsk,
    market.spread,
    market.volume,
    market.liquidity,
    JSON.stringify(market.raw),
    nowIso()
  );
}

function logStrategyRun(signal, market) {
  db.prepare(`
    INSERT INTO strategy_runs (strategy, market_id, action, confidence, rationale, raw_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(signal.strategy, market.marketId, signal.action, signal.confidence, signal.rationale, JSON.stringify({ signal, market }), nowIso());
}

async function main() {
  const markets = await fetchMarkets();
  const marketsById = new Map();
  let opened = 0;

  for (const market of markets) {
    marketsById.set(market.marketId, market);
    const previousSnapshot = getPreviousSnapshot(market.marketId);
    upsertMarket(market);
    insertSnapshot(market);

    if (hasOpenPositionForMarket(market.marketId)) continue;

    for (const strategy of strategies) {
      const signal = strategy({ market, previousSnapshot });
      if (!signal) continue;
      logStrategyRun(signal, market);
      const positionId = openPosition({ market, signal });
      if (positionId) {
        opened += 1;
        break;
      }
    }
  }

  const closed = updateAndClosePositions(marketsById);
  refreshPortfolioSnapshot(marketsById);

  console.log(JSON.stringify({ scanned: markets.length, opened, closed }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
