import { config } from "../config.js";

export function meanReversionStrategy({ market, previousSnapshot }) {
  if (!previousSnapshot) return null;

  const prevPrice = Number(previousSnapshot.yes_price || 0);
  if (prevPrice <= 0) return null;

  const move = market.yesPrice - prevPrice;
  if (move <= -(config.priceMoveThreshold * 1.5) && market.yesPrice >= 0.2 && market.yesPrice <= 0.8 && market.spread <= 0.05) {
    return {
      strategy: "MEAN_REVERSION",
      action: "BUY_YES",
      confidence: Math.min(0.85, 0.5 + Math.abs(move)),
      rationale: `Contrarian long: yes price dropped ${(Math.abs(move) * 100).toFixed(1)} pts in one interval`
    };
  }

  if (move >= (config.priceMoveThreshold * 1.5) && market.yesPrice >= 0.2 && market.yesPrice <= 0.8 && market.spread <= 0.05) {
    return {
      strategy: "MEAN_REVERSION",
      action: "BUY_NO",
      confidence: Math.min(0.85, 0.5 + Math.abs(move)),
      rationale: `Contrarian short: yes price jumped ${(Math.abs(move) * 100).toFixed(1)} pts in one interval`
    };
  }

  return null;
}
