/**
 * Market Dashboard
 * Main container component for all market data
 */
import React, { useState } from 'react';
import { PriceTicker } from './PriceTicker';
import { SentimentPanel } from './SentimentPanel';
import { ChartSection } from './ChartSection';
import { useMarketData } from './useMarketData';
import { TimeFrame } from './types';

interface MarketDashboardProps {
  className?: string;
}

export const MarketDashboard: React.FC<MarketDashboardProps> = ({ className }) => {
  const [timeframe, setTimeframe] = useState<TimeFrame>('1D');
  
  const {
    prices,
    sentiment,
    trending,
    candles,
    isLoading,
    lastUpdated,
    error,
    refresh
  } = useMarketData({
    refreshInterval: 30000,
    autoRefresh: true,
    timeframe
  });

  return (
    <div className={`market-dashboard ${className || ''}`} style={{
      width: '100%',
      maxWidth: '1400px',
      margin: '0 auto',
      padding: '20px'
    }}>
      {/* Header */}
      <header style={{
        marginBottom: '24px',
        paddingBottom: '20px',
        borderBottom: '2px solid #e94560'
      }}>
        <h1 style={{
          margin: 0,
          fontSize: '2em',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span>🐟📊</span>
          Swimming Pauls Market Data
        </h1>
        
        <p style={{
          margin: '8px 0 0 0',
          color: 'rgba(255,255,255,0.6)',
          fontSize: '0.95em'
        }}>
          Real-time crypto & stock data • Auto-refresh every 30s
        </p>
      </header>

      {/* Error Message */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#ef4444'
        }}>
          <span>⚠️</span>
          {error}
          <button
            onClick={refresh}
            style={{
              marginLeft: 'auto',
              padding: '4px 12px',
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '4px',
              color: '#ef4444',
              cursor: 'pointer',
              fontSize: '0.85em'
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Price Ticker */}
      <section style={{ marginBottom: '24px' }}>
        <PriceTicker
          prices={prices}
          lastUpdated={lastUpdated}
          isLoading={isLoading}
          onRefresh={refresh}
        />
      </section>

      {/* Sentiment Panel */}
      <section style={{ marginBottom: '24px' }}>
        <SentimentPanel
          sentiment={sentiment}
          trending={trending}
          isLoading={isLoading}
        />
      </section>

      {/* Chart Section */}
      <section>
        <ChartSection
          symbol={prices[0]?.symbol || 'BTC'}
          candles={candles}
          defaultTimeframe={timeframe}
          showIndicators={true}
        />
      </section>

      {/* Footer */}
      <footer style={{
        marginTop: '40px',
        paddingTop: '20px',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{
          fontSize: '0.8em',
          color: 'rgba(255,255,255,0.4)'
        }}>
          Data from CoinGecko • Fear & Greed from alternative.me
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.8em',
          color: 'rgba(255,255,255,0.4)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isLoading ? '#fbbf24' : '#4ade80',
            animation: isLoading ? 'pulse 1s infinite' : 'none'
          }} />
          {isLoading ? 'Updating...' : 'Live'}
        </div>
      </footer>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default MarketDashboard;
