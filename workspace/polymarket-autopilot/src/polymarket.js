import { config } from "./config.js";

function toNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeMarket(raw) {
  const outcomes = Array.isArray(raw.outcomes) ? raw.outcomes : [];
  const tokenIds = Array.isArray(raw.clobTokenIds) ? raw.clobTokenIds : [];
  const yesIndex = outcomes.findIndex((o) => String(o).toLowerCase() === "yes");
  const noIndex = outcomes.findIndex((o) => String(o).toLowerCase() === "no");

  const yesPrice = toNumber(raw.outcomePrices?.[yesIndex] ?? raw.lastTradePrice ?? raw.price, 0);
  const noPrice = noIndex >= 0 ? toNumber(raw.outcomePrices?.[noIndex], Math.max(0, 1 - yesPrice)) : Math.max(0, 1 - yesPrice);

  return {
    marketId: String(raw.id ?? raw.conditionId ?? raw.slug),
    question: raw.question ?? raw.title ?? raw.slug ?? "Unknown market",
    slug: raw.slug ?? null,
    active: Boolean(raw.active ?? raw.enable_order_book ?? true),
    endDate: raw.endDate ?? raw.end_date_iso ?? null,
    liquidity: toNumber(raw.liquidity ?? raw.liquidityNum ?? raw.liquidityClob, 0),
    volume: toNumber(raw.volume ?? raw.volumeNum ?? raw.volumeClob, 0),
    yesPrice,
    noPrice,
    bestBid: toNumber(raw.bestBid ?? yesPrice - 0.01, yesPrice),
    bestAsk: toNumber(raw.bestAsk ?? yesPrice + 0.01, yesPrice),
    spread: Math.max(0, toNumber(raw.bestAsk ?? yesPrice) - toNumber(raw.bestBid ?? yesPrice)),
    outcomeYesTokenId: yesIndex >= 0 ? String(tokenIds[yesIndex] ?? "") : null,
    outcomeNoTokenId: noIndex >= 0 ? String(tokenIds[noIndex] ?? "") : null,
    raw
  };
}

export async function fetchMarkets() {
  const url = new URL(config.marketsUrl);
  url.searchParams.set("closed", "false");
  url.searchParams.set("limit", String(config.maxMarkets));

  const response = await fetch(url, {
    headers: {
      "accept": "application/json",
      "user-agent": "openclaw-polymarket-autopilot/0.1"
    }
  });

  if (!response.ok) {
    throw new Error(`Polymarket fetch failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error("Unexpected Polymarket response shape");
  }

  return data.map(normalizeMarket).filter((m) => m.active && m.liquidity >= config.minLiquidity && m.volume >= config.minVolume);
}
