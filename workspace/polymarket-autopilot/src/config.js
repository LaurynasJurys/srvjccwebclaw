import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

export const config = {
  rootDir,
  dataDir: path.join(rootDir, "data"),
  dbPath: process.env.POLYMARKET_DB_PATH || path.join(rootDir, "data", "paper_trading.db"),
  marketsUrl: process.env.POLYMARKET_MARKETS_URL || "https://gamma-api.polymarket.com/markets",
  maxMarkets: Number(process.env.POLYMARKET_MAX_MARKETS || 25),
  minLiquidity: Number(process.env.POLYMARKET_MIN_LIQUIDITY || 50000),
  minVolume: Number(process.env.POLYMARKET_MIN_VOLUME || 10000),
  maxPositionFraction: Number(process.env.POLYMARKET_MAX_POSITION_FRACTION || 0.02),
  maxHoldingHours: Number(process.env.POLYMARKET_MAX_HOLDING_HOURS || 24),
  startingCash: Number(process.env.POLYMARKET_STARTING_CASH || 10000),
  priceMoveThreshold: Number(process.env.POLYMARKET_PRICE_MOVE_THRESHOLD || 0.03),
  trendVolumeSpike: Number(process.env.POLYMARKET_TREND_VOLUME_SPIKE || 1.2),
  reportLookbackHours: Number(process.env.POLYMARKET_REPORT_LOOKBACK_HOURS || 24)
};
