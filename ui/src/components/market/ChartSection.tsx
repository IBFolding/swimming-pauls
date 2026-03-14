/**
 * Chart Section Component
 * Candlestick charts with timeframe selector and technical indicators
 */
import React, { useState } from 'react';
import { CandleData, TimeFrame, TechnicalIndicators } from './types';

interface ChartSectionProps {
  symbol?: string;
  candles: CandleData[];
  defaultTimeframe?: TimeFrame;
  showIndicators?: boolean;
}

const TIMEFRAMES: { value: TimeFrame; label: string }[] = [
  { value: '1H', label: '1H' },
  { value: '1D', label: '1D' },
  { value: '1W', label: '1W' },
  { value: '1M', label: '1M' },
];

// Calculate simple moving average
function calculateSMA(data: number[], period: number): (number | null)[] {
  const result: (number | null)[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / period);
    }
  }
  return result;
}

// Calculate RSI
function calculateRSI(closes: number[], period: number = 14): (number | null)[] {
  const result: (number | null)[] = [];
  let gains = 0;
  let losses = 0;
  
  for (let i = 0; i < closes.length; i++) {
    if (i === 0) {
      result.push(null);
      continue;
    }
    
    const change = closes[i] - closes[i - 1];
    if (i < period) {
      result.push(null);
    } else if (i === period) {
      // Initial average
      for (let j = 1; j <= period; j++) {
        const c = closes[j] - closes[j - 1];
        if (c > 0) gains += c;
        else losses += Math.abs(c);
      }
      const rs = gains / losses;
      result.push(100 - (100 / (1 + rs)));
    } else {
      const change = closes[i] - closes[i - 1];
      const gain = change > 0 ? change : 0;
      const loss = change < 0 ? Math.abs(change) : 0;
      gains = (gains * (period - 1) + gain) / period;
      losses = (losses * (period - 1) + loss) / period;
      const rs = gains / losses;
      result.push(100 - (100 / (1 + rs)));
    }
  }
  return result;
}

const CandlestickChart: React.FC<{
  candles: CandleData[];
  timeframe: TimeFrame;
  indicators: TechnicalIndicators;
}> = ({ candles, indicators }) => {
  const width = 800;
  const height = 400;
  const padding = { top: 20, right: 60, bottom: 40, left: 10 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate min/max for scaling
  const prices = candles.flatMap(c => [c.high, c.low]);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice || 1;

  // Scale functions
  const xScale = (index: number) => 
    padding.left + (index / (candles.length - 1)) * chartWidth;
  const yScale = (price: number) => 
    padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;

  // Calculate technical indicators
  const closes = candles.map(c => c.close);
  const ma20 = indicators.ma20 ? calculateSMA(closes, 20) : [];
  const ma50 = indicators.ma50 ? calculateSMA(closes, 50) : [];
  const rsi = indicators.rsi ? calculateRSI(closes) : [];

  const candleWidth = Math.max(2, (chartWidth / candles.length) * 0.7);

  return (
    <svg
      width="100%"
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{ overflow: 'visible' }}
    >
      <defs>
        <linearGradient id="bullGradient" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#4ade80" />
          <stop offset="100%" stopColor="#22c55e" />
        </linearGradient>
        <linearGradient id="bearGradient" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#ef4444" />
          <stop offset="100%" stopColor="#dc2626" />
        </linearGradient>
      </defs>

      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map(t => (
        <g key={t}>
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={padding.top + chartHeight * t}
            y2={padding.top + chartHeight * t}
            stroke="rgba(255,255,255,0.05)"
            strokeDasharray="4,4"
          />
          <text
            x={width - padding.right + 8}
            y={padding.top + chartHeight * t + 4}
            fill="rgba(255,255,255,0.4)"
            fontSize="10"
          >
            {(maxPrice - priceRange * t).toFixed(
              maxPrice > 1000 ? 0 : maxPrice > 100 ? 2 : 4
            )}
          </text>
        </g>
      ))}

      {/* MA20 Line */}
      {indicators.ma20 && ma20.some(v => v !== null) && (
        <polyline
          points={ma20
            .map((v, i) => v !== null ? `${xScale(i)},${yScale(v)}` : '')
            .filter(Boolean)
            .join(' ')}
          fill="none"
          stroke="#fbbf24"
          strokeWidth={1.5}
          opacity={0.8}
        />
      )}

      {/* MA50 Line */}
      {indicators.ma50 && ma50.some(v => v !== null) && (
        <polyline
          points={ma50
            .map((v, i) => v !== null ? `${xScale(i)},${yScale(v)}` : '')
            .filter(Boolean)
            .join(' ')}
          fill="none"
          stroke="#a855f7"
          strokeWidth={1.5}
          opacity={0.8}
        />
      )}

      {/* Candles */}
      {candles.map((candle, i) => {
        const isBullish = candle.close >= candle.open;
        const color = isBullish ? '#4ade80' : '#ef4444';
        const x = xScale(i);
        const yOpen = yScale(candle.open);
        const yClose = yScale(candle.close);
        const yHigh = yScale(candle.high);
        const yLow = yScale(candle.low);

        return (
          <g key={candle.timestamp}>
            {/* Wick */}
            <line
              x1={x}
              x2={x}
              y1={yHigh}
              y2={yLow}
              stroke={color}
              strokeWidth={1}
            />
            
            {/* Body */}
            <rect
              x={x - candleWidth / 2}
              y={Math.min(yOpen, yClose)}
              width={candleWidth}
              height={Math.max(2, Math.abs(yClose - yOpen))}
              fill={color}
              rx={1}
            />
          </g>
        );
      })}

      {/* Legend */}
      <g transform={`translate(${padding.left + 10}, ${padding.top})`}>
        {indicators.ma20 && (
          <g>
            <line x1={0} x2={15} y1={0} y2={0} stroke="#fbbf24" strokeWidth={2} />
            <text x={20} y={4} fill="rgba(255,255,255,0.6)" fontSize="10">MA20</text>
          </g>
        )}
        {indicators.ma50 && (
          <g transform="translate(60, 0)">
            <line x1={0} x2={15} y1={0} y2={0} stroke="#a855f7" strokeWidth={2} />
            <text x={20} y={4} fill="rgba(255,255,255,0.6)" fontSize="10">MA50</text>
          </g>
        )}
      </g>

      {/* RSI Panel */}
      {indicators.rsi && rsi.some(v => v !== null) && (
        <g transform={`translate(0, ${height - 60})`}>
          <rect
            x={padding.left}
            y={0}
            width={chartWidth}
            height={50}
            fill="rgba(0,0,0,0.3)"
            rx={4}
          />
          <text
            x={padding.left + 5}
            y={12}
            fill="rgba(255,255,255,0.5)"
            fontSize="9"
          >
            RSI
          </text>
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={25}
            y2={25}
            stroke="rgba(255,255,255,0.1)"
          />
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={40}
            y2={40}
            stroke="rgba(255,255,255,0.1)"
          />
          <polyline
            points={rsi
              .map((v, i) => v !== null ? `${xScale(i)},${45 - (v / 100) * 40}` : '')
              .filter(Boolean)
              .join(' ')}
            fill="none"
            stroke="#3b82f6"
            strokeWidth={1}
          />
        </g>
      )}
    </svg>
  );
};

export const ChartSection: React.FC<ChartSectionProps> = ({
  symbol = 'BTC',
  candles,
  defaultTimeframe = '1D',
  showIndicators = true
}) => {
  const [timeframe, setTimeframe] = useState<TimeFrame>(defaultTimeframe);
  const [indicators, setIndicators] = useState<TechnicalIndicators>({
    ma20: true,
    ma50: false,
    ma200: false,
    rsi: false,
    macd: false,
    bollinger: false
  });

  const toggleIndicator = (key: keyof TechnicalIndicators) => {
    setIndicators(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div style={{
      background: 'rgba(0,0,0,0.2)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(255,255,255,0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '16px'
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
            <span>📈</span> {symbol}/USD
          </h2>
        </div>

        {/* Timeframe Selector */}
        <div style={{
          display: 'flex',
          gap: '4px',
          background: 'rgba(0,0,0,0.3)',
          padding: '4px',
          borderRadius: '8px'
        }}>
          {TIMEFRAMES.map(tf => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              style={{
                padding: '6px 14px',
                border: 'none',
                borderRadius: '6px',
                background: timeframe === tf.value
                  ? 'linear-gradient(135deg, #e94560 0%, #ff6b6b 100%)'
                  : 'transparent',
                color: '#fff',
                fontSize: '0.85em',
                fontWeight: timeframe === tf.value ? '600' : '400',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Indicators Toggle */}
      {showIndicators && (
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '16px',
          flexWrap: 'wrap'
        }}>
          {[
            { key: 'ma20', label: 'MA20', color: '#fbbf24' },
            { key: 'ma50', label: 'MA50', color: '#a855f7' },
            { key: 'rsi', label: 'RSI', color: '#3b82f6' },
          ].map(ind => (
            <button
              key={ind.key}
              onClick={() => toggleIndicator(ind.key as keyof TechnicalIndicators)}
              style={{
                padding: '4px 12px',
                border: `1px solid ${indicators[ind.key as keyof TechnicalIndicators] ? ind.color : 'rgba(255,255,255,0.2)'}`,
                borderRadius: '4px',
                background: indicators[ind.key as keyof TechnicalIndicators]
                  ? `${ind.color}20`
                  : 'transparent',
                color: indicators[ind.key as keyof TechnicalIndicators] ? ind.color : 'rgba(255,255,255,0.5)',
                fontSize: '0.75em',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {indicators[ind.key as keyof TechnicalIndicators] ? '●' : '○'} {ind.label}
            </button>
          ))}
        </div>
      )}

      {/* Chart */}
      <div style={{
        background: 'rgba(0,0,0,0.2)',
        borderRadius: '12px',
        padding: '16px',
        overflow: 'hidden'
      }}>
        <CandlestickChart
          candles={candles}
          timeframe={timeframe}
          indicators={indicators}
        />
      </div>
    </div>
  );
};

export default ChartSection;
