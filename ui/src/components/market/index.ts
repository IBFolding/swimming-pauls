/**
 * Market Components Index
 * Barrel export for all market dashboard components
 */

// Main dashboard
export { MarketDashboard } from './MarketDashboard';
export { default } from './MarketDashboard';

// Individual components
export { PriceTicker } from './PriceTicker';
export { SentimentPanel } from './SentimentPanel';
export { ChartSection } from './ChartSection';
export { Sparkline } from './Sparkline';

// Hooks
export { useMarketData } from './useMarketData';

// Types
export type {
  PriceData,
  SentimentData,
  TrendingKeyword,
  CandleData,
  TimeFrame,
  TechnicalIndicators,
  PriceTickerProps,
  SentimentPanelProps,
  ChartSectionProps,
} from './types';

// API utilities
export {
  fetchCryptoPrices,
  fetchFearGreed,
  getTrendingKeywords,
  getCandleData,
  getLastUpdated,
  getApiStatus,
} from './api';

// Demo data
export {
  demoPrices,
  demoSentiment,
  demoTrending,
  demoCandles,
  updateDemoPrices,
} from './demoData';
