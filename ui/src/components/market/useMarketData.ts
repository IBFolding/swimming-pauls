/**
 * Market Data Hook
 * Manages auto-refreshing market data with 30s interval
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { PriceData, SentimentData, TrendingKeyword, CandleData, TimeFrame } from './types';
import { fetchCryptoPrices, fetchFearGreed, getTrendingKeywords, getCandleData, getLastUpdated } from './api';

interface MarketDataState {
  prices: PriceData[];
  sentiment: SentimentData;
  trending: TrendingKeyword[];
  candles: CandleData[];
  isLoading: boolean;
  lastUpdated: string;
  error: string | null;
}

interface UseMarketDataOptions {
  refreshInterval?: number;
  autoRefresh?: boolean;
  timeframe?: TimeFrame;
}

export function useMarketData(options: UseMarketDataOptions = {}) {
  const {
    refreshInterval = 30000,
    autoRefresh = true,
    timeframe = '1D'
  } = options;

  const [state, setState] = useState<MarketDataState>({
    prices: [],
    sentiment: {
      overall: 50,
      label: 'Neutral',
      sources: { news: 50, social: 50 }
    },
    trending: [],
    candles: [],
    isLoading: true,
    lastUpdated: '--:--:--',
    error: null
  });

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const [prices, sentiment, trending, candles] = await Promise.all([
        fetchCryptoPrices(),
        fetchFearGreed(),
        Promise.resolve(getTrendingKeywords()),
        Promise.resolve(getCandleData(timeframe))
      ]);

      setState({
        prices,
        sentiment,
        trending,
        candles,
        isLoading: false,
        lastUpdated: getLastUpdated(),
        error: null
      });
    } catch (err) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch market data'
      }));
    }
  }, [timeframe]);

  // Initial fetch
  useEffect(() => {
    refresh();
  }, [refresh]);

  // Auto-refresh interval
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(refresh, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval, refresh]);

  // Update candles when timeframe changes
  useEffect(() => {
    setState(prev => ({
      ...prev,
      candles: getCandleData(timeframe)
    }));
  }, [timeframe]);

  return {
    ...state,
    refresh
  };
}

export default useMarketData;
