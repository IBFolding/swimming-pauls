/**
 * Price Ticker Component
 * Displays crypto and stock prices with 24h changes and sparklines
 */
import React from 'react';
import { PriceData } from './types';
import { Sparkline } from './Sparkline';

interface PriceTickerProps {
  prices: PriceData[];
  lastUpdated: string;
  isLoading?: boolean;
  onRefresh?: () => void;
}

const formatPrice = (price: number): string => {
  if (price >= 1000) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
  return price.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4
  });
};

const formatChange = (change: number, percent: number): string => {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)} (${sign}${percent.toFixed(2)}%)`;
};

const formatVolume = (volume: number): string => {
  if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
  if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
  if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
  return `$${volume.toFixed(0)}`;
};

const AssetCard: React.FC<{ asset: PriceData }> = ({ asset }) => {
  const isPositive = asset.changePercent24h >= 0;

  return (
    <div className="asset-card" style={{
      background: 'rgba(255,255,255,0.05)',
      borderRadius: '12px',
      padding: '16px',
      border: '1px solid rgba(255,255,255,0.1)',
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'pointer',
      minWidth: '220px'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)';
      e.currentTarget.style.boxShadow = '0 4px 20px rgba(233, 69, 96, 0.15)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = 'none';
    }}
    >
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '12px'
      }}>
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{
              fontSize: '1.3em',
              fontWeight: 'bold',
              color: '#fff'
            }}>
              {asset.symbol}
            </span>
            <span style={{
              fontSize: '0.75em',
              color: 'rgba(255,255,255,0.5)',
              padding: '2px 8px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '4px'
            }}>
              {asset.type === 'crypto' ? 'Crypto' : 'Stock'}
            </span>
          </div>
          <div style={{
            fontSize: '0.85em',
            color: 'rgba(255,255,255,0.6)',
            marginTop: '2px'
          }}>
            {asset.name}
          </div>
        </div>
        <div style={{
          textAlign: 'right'
        }}>
          <div style={{
            fontSize: '1.4em',
            fontWeight: 'bold',
            color: '#fff'
          }}>
            ${formatPrice(asset.price)}
          </div>
          <div style={{
            fontSize: '0.9em',
            color: isPositive ? '#4ade80' : '#ef4444',
            fontWeight: '500'
          }}>
            {formatChange(asset.change24h, asset.changePercent24h)}
          </div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginTop: '8px'
      }}>
        <div style={{
          fontSize: '0.75em',
          color: 'rgba(255,255,255,0.4)'
        }}>
          Vol: {formatVolume(asset.volume24h || 0)}
        </div>
        <Sparkline
          data={asset.sparklineData}
          width={100}
          height={30}
          isPositive={isPositive}
        />
      </div>
    </div>
  );
};

export const PriceTicker: React.FC<PriceTickerProps> = ({
  prices,
  lastUpdated,
  isLoading = false,
  onRefresh
}) => {
  const cryptoAssets = prices.filter(p => p.type === 'crypto');
  const stockAssets = prices.filter(p => p.type === 'stock');

  return (
    <div className="price-ticker" style={{
      background: 'rgba(0,0,0,0.2)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(255,255,255,0.1)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <div>
          <h2 style={{
            margin: 0,
            color: '#e94560',
            fontSize: '1.3em',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span>📊</span> Live Prices
          </h2>
          <div style={{
            fontSize: '0.8em',
            color: 'rgba(255,255,255,0.4)',
            marginTop: '4px'
          }}>
            Last updated: {lastUpdated}
            {isLoading && <span style={{ marginLeft: '8px' }}>⟳</span>}
          </div>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          style={{
            padding: '8px 16px',
            background: 'linear-gradient(135deg, #e94560 0%, #ff6b6b 100%)',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.6 : 1,
            fontSize: '0.85em',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!isLoading) {
              e.currentTarget.style.transform = 'scale(1.05)';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          {isLoading ? '⟳ Refreshing...' : '↻ Refresh'}
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3 style={{
          fontSize: '0.9em',
          color: 'rgba(255,255,255,0.6)',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span>🪙</span> Cryptocurrency
        </h3>
        <div style={{
          display: 'flex',
          gap: '12px',
          overflowX: 'auto',
          paddingBottom: '8px',
          scrollbarWidth: 'thin',
          scrollbarColor: '#e94560 rgba(255,255,255,0.1)'
        }}>
          {cryptoAssets.map(asset => (
            <AssetCard key={asset.symbol} asset={asset} />
          ))}
        </div>
      </div>

      <div>
        <h3 style={{
          fontSize: '0.9em',
          color: 'rgba(255,255,255,0.6)',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span>📈</span> Stock Indices
        </h3>
        <div style={{
          display: 'flex',
          gap: '12px',
          overflowX: 'auto',
          paddingBottom: '8px'
        }}>
          {stockAssets.map(asset => (
            <AssetCard key={asset.symbol} asset={asset} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default PriceTicker;
