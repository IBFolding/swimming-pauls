/**
 * Market Data API
 * Fetches live market data from free APIs with fallback to demo data
 */
import { PriceData, SentimentData, TrendingKeyword, CandleData, TimeFrame, CoinGeckoPrice, FearGreedData } from './types';
import { demoPrices, demoSentiment, demoTrending, demoCandles, updateDemoPrices } from './demoData';

// API Configuration
const COINGECKO_API = 'https://api.coingecko.com/api/v3';
const FEAR_GREED_API = 'https://api.alternative.me/fng/';

// Cache configuration
let priceCache: PriceData[] | null = null;
let sentimentCache: SentimentData | null = null;
let lastPriceFetch = 0;
let lastSentimentFetch = 0;
const CACHE_DURATION = 30000; // 30 seconds

// Track API availability
let apiAvailable = {
  coingecko: true,
  fearGreed: true
};

/**
 * Fetch crypto prices from CoinGecko
 */
export async function fetchCryptoPrices(): Promise<PriceData[]> {
  // Return cached data if fresh
  if (priceCache && Date.now() - lastPriceFetch < CACHE_DURATION) {
    return priceCache;
  }
  
  try {
    const response = await fetch(
      `${COINGECKO_API}/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana&order=market_cap_desc&sparkline=true&price_change_percentage=24h`,
      { 
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      }
    );
    
    if (!response.ok) {
      throw new Error(`CoinGecko API error: ${response.status}`);
    }
    
    const data: CoinGeckoPrice[] = await response.json();
    
    const cryptoPrices: PriceData[] = data.map(coin => ({
      symbol: coin.symbol.toUpperCase(),
      name: coin.name,
      price: coin.current_price,
      change24h: coin.price_change_24h || 0,
      changePercent24h: coin.price_change_percentage_24h || 0,
      volume24h: coin.total_volume,
      marketCap: coin.market_cap,
      sparklineData: coin.sparkline_in_7d?.price.slice(-24) || [],
      type: 'crypto',
      lastUpdated: coin.last_updated
    }));
    
    // Fetch stock prices (mock for now - would need separate API)
    const stockPrices = demoPrices.filter(p => p.type === 'stock');
    
    priceCache = [...cryptoPrices, ...stockPrices];
    lastPriceFetch = Date.now();
    apiAvailable.coingecko = true;
    
    return priceCache;
    
  } catch (error) {
    console.warn('CoinGecko API failed, using demo data:', error);
    apiAvailable.coingecko = false;
    
    // Return updated demo data
    priceCache = updateDemoPrices(demoPrices);
    lastPriceFetch = Date.now();
    return priceCache;
  }
}

/**
 * Fetch Fear & Greed Index
 */
export async function fetchFearGreed(): Promise<SentimentData> {
  // Return cached data if fresh
  if (sentimentCache && Date.now() - lastSentimentFetch < CACHE_DURATION) {
    return sentimentCache;
  }
  
  try {
    const response = await fetch(`${FEAR_GREED_API}?limit=1`);
    
    if (!response.ok) {
      throw new Error(`Fear & Greed API error: ${response.status}`);
    }
    
    const data = await response.json();
    const fg: FearGreedData = data.data[0];
    
    const value = parseInt(fg.value);
    let label: SentimentData['label'] = 'Neutral';
    
    if (value <= 20) label = 'Extreme Fear';
    else if (value <= 40) label = 'Fear';
    else if (value <= 60) label = 'Neutral';
    else if (value <= 80) label = 'Greed';
    else label = 'Extreme Greed';
    
    sentimentCache = {
      overall: value,
      label,
      sources: {
        news: Math.round(value * (0.9 + Math.random() * 0.2)),
        social: Math.round(value * (0.9 + Math.random() * 0.2)),
        onChain: Math.round(value * (0.9 + Math.random() * 0.2))
      }
    };
    
    lastSentimentFetch = Date.now();
    apiAvailable.fearGreed = true;
    
    return sentimentCache;
    
  } catch (error) {
    console.warn('Fear & Greed API failed, using demo data:', error);
    apiAvailable.fearGreed = false;
    
    // Vary the demo sentiment slightly
    const variation = Math.floor(Math.random() * 10) - 5;
    const newValue = Math.max(0, Math.min(100, demoSentiment.overall + variation));
    
    sentimentCache = {
      ...demoSentiment,
      overall: newValue
    };
    
    lastSentimentFetch = Date.now();
    return sentimentCache;
  }
}

/**
 * Get trending keywords (simulated - would need social API)
 */
export function getTrendingKeywords(): TrendingKeyword[] {
  // Shuffle and slightly vary scores
  return demoTrending.map(k => ({
    ...k,
    score: Math.max(0, Math.min(100, k.score + Math.floor(Math.random() * 10) - 5))
  })).sort((a, b) => b.score - a.score);
}

/**
 * Get candle data for chart
 */
export function getCandleData(timeframe: TimeFrame): CandleData[] {
  // In a real implementation, this would fetch from an API
  // For now, return demo data
  return demoCandles[timeframe] || demoCandles['1D'];
}

/**
 * Get last updated timestamp
 */
export function getLastUpdated(): string {
  return new Date().toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * Check API status
 */
export function getApiStatus() {
  return { ...apiAvailable };
}
