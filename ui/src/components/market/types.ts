/**
 * Market Data Types
 * TypeScript interfaces for market data components
 */

// Price data types
export interface PriceData {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h?: number;
  marketCap?: number;
  sparklineData: number[];
  type: 'crypto' | 'stock';
  lastUpdated: string;
}

export interface PriceTickerProps {
  assets?: PriceData[];
  refreshInterval?: number;
  onRefresh?: () => void;
}

// Sentiment types
export interface SentimentData {
  overall: number; // -100 to 100
  label: 'Extreme Fear' | 'Fear' | 'Neutral' | 'Greed' | 'Extreme Greed';
  sources: {
    news: number;
    social: number;
    onChain?: number;
  };
}

export interface TrendingKeyword {
  word: string;
  score: number;
  trend: 'up' | 'down' | 'neutral';
}

export interface SentimentPanelProps {
  sentiment?: SentimentData;
  trending?: TrendingKeyword[];
  refreshInterval?: number;
}

// Chart types
export type TimeFrame = '1H' | '1D' | '1W' | '1M' | '3M' | '1Y';

export interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartSectionProps {
  symbol?: string;
  defaultTimeframe?: TimeFrame;
  showIndicators?: boolean;
}

export interface TechnicalIndicators {
  ma20: boolean;
  ma50: boolean;
  ma200: boolean;
  rsi: boolean;
  macd: boolean;
  bollinger: boolean;
}

// API Response types
export interface CoinGeckoPrice {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_24h: number;
  price_change_percentage_24h: number;
  market_cap: number;
  total_volume: number;
  sparkline_in_7d?: {
    price: number[];
  };
  last_updated: string;
}

export interface FearGreedData {
  value: number;
  value_classification: string;
  timestamp: string;
  time_until_update: string;
}

// Demo data
export interface DemoDataSet {
  prices: PriceData[];
  sentiment: SentimentData;
  trending: TrendingKeyword[];
  candles: Record<TimeFrame, CandleData[]>;
}
