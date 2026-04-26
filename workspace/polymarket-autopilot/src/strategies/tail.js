import { config } from "../config.js";

export function tailStrategy({ market, previousSnapshot }) {
  if (!previousSnapshot) return null;

  const prevPrice = Number(previousSnapshot.yes_price || 0);
  const prevVolume = Number(previousSnapshot.volume || 0);
  if (prevPrice <= 0) return null;

  const priceMove = market.yesPrice - prevPrice;
  const volumeRatio = prevVolume > 0 ? market.volume / prevVolume : 1;

  if (market.yesPrice >= 0.6 && priceMove >= config.priceMoveThreshold && volumeRatio >= config.trendVolumeSpike && market.spread <= 0.04) {
    return {
      strategy: "TAIL",
      action: "BUY_YES",
      confidence: Math.min(0.95, 0.55 + priceMove + Math.min(0.2, (volumeRatio - 1) * 0.1)),
      rationale: `Momentum long: yes price moved ${(priceMove * 100).toFixed(1)} pts with volume ratio ${volumeRatio.toFixed(2)}`
    };
  }

  return null;
}
