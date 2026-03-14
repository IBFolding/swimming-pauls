/**
 * Market Demo Data
 * Fallback data when APIs are unavailable
 */
import { PriceData, SentimentData, TrendingKeyword, CandleData, TimeFrame } from './types';

// Generate realistic sparkline data
function generateSparkline(basePrice: number, points: number = 24): number[] {
  const data: number[] = [basePrice];
  let currentPrice = basePrice;
  
  for (let i = 1; i < points; i++) {
    const change = (Math.random() - 0.48) * 0.02; // Slight upward bias
    currentPrice *= (1 + change);
    data.push(currentPrice);
  }
  
  return data;
}

// Generate candlestick data for a timeframe
function generateCandles(timeframe: TimeFrame, count: number = 100): CandleData[] {
  const candles: CandleData[] = [];
  let basePrice = 45000;
  const now = Date.now();
  
  const intervalMap: Record<TimeFrame, number> = {
    '1H': 60 * 1000, // 1 minute
    '1D': 15 * 60 * 1000, // 15 minutes
    '1W': 4 * 60 * 60 * 1000, // 4 hours
    '1M': 24 * 60 * 60 * 1000, // 1 day
    '3M': 24 * 60 * 60 * 1000, // 1 day
    '1Y': 7 * 24 * 60 * 60 * 1000 // 1 week
  };
  
  const interval = intervalMap[timeframe];
  
  for (let i = count; i >= 0; i--) {
    const timestamp = now - (i * interval);
    const volatility = 0.015;
    const change = (Math.random() - 0.48) * volatility;
    
    const open = basePrice;
    const close = basePrice * (1 + change);
    const high = Math.max(open, close) * (1 + Math.random() * 0.008);
    const low = Math.min(open, close) * (1 - Math.random() * 0.008);
    const volume = Math.floor(Math.random() * 1000000) + 500000;
    
    candles.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume
    });
    
    basePrice = close;
  }
  
  return candles;
}

// Demo price data
export const demoPrices: PriceData[] = [
  {
    symbol: 'BTC',
    name: 'Bitcoin',
    price: 67245.32,
    change24h: 1245.50,
    changePercent24h: 1.88,
    volume24h: 28500000000,
    marketCap: 1320000000000,
    sparklineData: generateSparkline(66000, 24),
    type: 'crypto',
    lastUpdated: new Date().toISOString()
  },
  {
    symbol: 'ETH',
    name: 'Ethereum',
    price: 3524.18,
    change24h: -45.22,
    changePercent24h: -1.27,
    volume24h: 15200000000,
    marketCap: 423000000000,
    sparklineData: generateSparkline(3570, 24),
    type: 'crypto',
    lastUpdated: new Date().toISOString()
  },
  {
    symbol: 'SOL',
    name: 'Solana',
    price: 142.85,
    change24h: 8.45,
    changePercent24h: 6.29,
    volume24h: 4200000000,
    marketCap: 64500000000,
    sparklineData: generateSparkline(134, 24),
    type: 'crypto',
    lastUpdated: new Date().toISOString()
  },
  {
    symbol: 'SPY',
    name: 'SPDR S&P 500',
    price: 512.74,
    change24h: 3.21,
    changePercent24h: 0.63,
    volume24h: 52000000,
    marketCap: 450000000000,
    sparklineData: generateSparkline(509, 24),
    type: 'stock',
    lastUpdated: new Date().toISOString()
  },
  {
    symbol: 'QQQ',
    name: 'Invesco QQQ',
    price: 442.18,
    change24h: -1.45,
    changePercent24h: -0.33,
    volume24h: 28000000,
    marketCap: 185000000000,
    sparklineData: generateSparkline(444, 24),
    type: 'stock',
    lastUpdated: new Date().toISOString()
  }
];

// Demo sentiment data
export const demoSentiment: SentimentData = {
  overall: 65,
  label: 'Greed',
  sources: {
    news: 58,
    social: 72,
    onChain: 65
  }
};

// Demo trending keywords
export const demoTrending: TrendingKeyword[] = [
  { word: 'Bitcoin ETF', score: 94, trend: 'up' },
  { word: 'AI Tokens', score: 87, trend: 'up' },
  { word: 'Rate Cuts', score: 76, trend: 'up' },
  { word: 'Solana', score: 72, trend: 'up' },
  { word: 'Meme Coins', score: 68, trend: 'down' },
  { word: 'Halving', score: 64, trend: 'neutral' },
  { word: 'L2 Scaling', score: 58, trend: 'up' },
  { word: 'DeFi Yields', score: 45, trend: 'down' }
];

// Demo candle data for all timeframes
export const demoCandles: Record<TimeFrame, CandleData[]> = {
  '1H': generateCandles('1H', 60),
  '1D': generateCandles('1D', 96),
  '1W': generateCandles('1W', 42),
  '1M': generateCandles('1M', 30),
  '3M': generateCandles('3M', 90),
  '1Y': generateCandles('1Y', 52)
};

// Update demo prices with random small changes
export function updateDemoPrices(prices: PriceData[]): PriceData[] {
  return prices.map(price => {
    const changePercent = (Math.random() - 0.48) * 0.5; // -0.24% to +0.26%
    const newPrice = price.price * (1 + changePercent / 100);
    const priceChange = newPrice - price.price;
    
    // Update sparkline
    const newSparkline = [...price.sparklineData.slice(1), newPrice];
    
    return {
      ...price,
      price: newPrice,
      change24h: price.change24h + priceChange,
      changePercent24h: price.changePercent24h + changePercent,
      sparklineData: newSparkline,
      lastUpdated: new Date().toISOString()
    };
  });
}
