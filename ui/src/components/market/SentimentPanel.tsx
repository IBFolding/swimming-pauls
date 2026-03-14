/**
 * Sentiment Panel Component
 * Displays Fear & Greed index, sentiment gauges, and trending keywords
 */
import React from 'react';
import { SentimentData, TrendingKeyword } from './types';

interface SentimentPanelProps {
  sentiment: SentimentData;
  trending: TrendingKeyword[];
  isLoading?: boolean;
}

const getSentimentColor = (value: number): string => {
  if (value <= 20) return '#ef4444'; // Extreme Fear - Red
  if (value <= 40) return '#f97316'; // Fear - Orange
  if (value <= 60) return '#fbbf24'; // Neutral - Yellow
  if (value <= 80) return '#4ade80'; // Greed - Green
  return '#10b981'; // Extreme Greed - Emerald
};

const getSentimentEmoji = (label: string): string => {
  switch (label) {
    case 'Extreme Fear': return '😱';
    case 'Fear': return '😨';
    case 'Neutral': return '😐';
    case 'Greed': return '🤑';
    case 'Extreme Greed': return '🚀';
    default: return '😐';
  }
};

interface GaugeProps {
  value: number;
  label: string;
  size?: number;
}

const FearGreedGauge: React.FC<GaugeProps> = ({ value, label, size = 150 }) => {
  const color = getSentimentColor(value);
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference * 0.75; // 75% circle

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '12px'
    }}>
      <div style={{ position: 'relative', width: size, height: size * 0.8 }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          style={{ transform: 'rotate(135deg)', overflow: 'visible' }}
        >
          {/* Background arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
          />
          
          {/* Value arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
            strokeDashoffset={circumference - (value / 100) * circumference * 0.75}
            style={{
              filter: `drop-shadow(0 0 8px ${color}40)`,
              transition: 'stroke-dashoffset 0.5s ease-out'
            }}
          />
        </svg>
        
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -30%)',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '2.5em',
            fontWeight: 'bold',
            color: '#fff',
            lineHeight: 1
          }}>
            {value}
          </div>
          <div style={{
            fontSize: '0.75em',
            color: 'rgba(255,255,255,0.5)',
            marginTop: '4px'
          }}>
            / 100
          </div>
        </div>
      </div>
      
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 16px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '20px',
        border: `1px solid ${color}40`
      }}>
        <span style={{ fontSize: '1.5em' }}>{getSentimentEmoji(label)}</span>
        <span style={{
          color: color,
          fontWeight: 'bold',
          fontSize: '1em'
        }}>
          {label}
        </span>
      </div>
    </div>
  );
};

const MiniGauge: React.FC<{ value: number; label: string }> = ({ value, label }) => {
  const color = getSentimentColor(value);
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '8px',
      padding: '12px',
      background: 'rgba(255,255,255,0.03)',
      borderRadius: '12px',
      minWidth: '80px'
    }}>
      <div style={{
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        background: `conic-gradient(${color} ${value * 3.6}deg, rgba(255,255,255,0.1) 0deg)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '50%',
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{
            fontSize: '0.75em',
            fontWeight: 'bold',
            color: '#fff'
          }}>
            {value}
          </span>
        </div>
      </div>
      <span style={{
        fontSize: '0.75em',
        color: 'rgba(255,255,255,0.6)'
      }}>
        {label}
      </span>
    </div>
  );
};

const TrendingItem: React.FC<{ item: TrendingKeyword; index: number }> = ({ item, index }) => {
  const trendIcon = item.trend === 'up' ? '📈' : item.trend === 'down' ? '📉' : '➡️';
  const trendColor = item.trend === 'up' ? '#4ade80' : item.trend === 'down' ? '#ef4444' : '#fbbf24';
  
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '10px 0',
      borderBottom: index < 5 ? '1px solid rgba(255,255,255,0.05)' : 'none'
    }}>
      <span style={{
        fontSize: '0.8em',
        color: 'rgba(255,255,255,0.3)',
        width: '20px'
      }}>
        #{index + 1}
      </span>
      
      <span style={{
        flex: 1,
        fontSize: '0.9em',
        color: '#fff',
        fontWeight: '500'
      }}>
        {item.word}
      </span>
      
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px'
      }}>
        <span style={{ fontSize: '0.9em' }}>{trendIcon}</span>
        <div style={{
          width: '60px',
          height: '4px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${item.score}%`,
            height: '100%',
            background: trendColor,
            borderRadius: '2px'
          }} />
        </div>
        <span style={{
          fontSize: '0.75em',
          color: 'rgba(255,255,255,0.5)',
          minWidth: '30px',
          textAlign: 'right'
        }}>
          {item.score}
        </span>
      </div>
    </div>
  );
};

export const SentimentPanel: React.FC<SentimentPanelProps> = ({
  sentiment,
  trending,
  isLoading = false
}) => {
  return (
    <div className="sentiment-panel" style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '20px'
    }}>
      {/* Fear & Greed Index */}
      <div style={{
        background: 'rgba(0,0,0,0.2)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <h3 style={{
          margin: '0 0 20px 0',
          color: '#e94560',
          fontSize: '1.1em',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>🎯</span> Fear & Greed Index
        </h3>
        
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          opacity: isLoading ? 0.6 : 1,
          transition: 'opacity 0.3s'
        }}>
          <FearGreedGauge
            value={sentiment.overall}
            label={sentiment.label}
          />
        </div>
        
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '12px',
          marginTop: '20px'
        }}>
          <MiniGauge value={sentiment.sources.news} label="News" />
          <MiniGauge value={sentiment.sources.social} label="Social" />
          {sentiment.sources.onChain !== undefined && (
            <MiniGauge value={sentiment.sources.onChain} label="On-Chain" />
          )}
        </div>
      </div>

      {/* Trending Keywords */}
      <div style={{
        background: 'rgba(0,0,0,0.2)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <h3 style={{
          margin: '0 0 16px 0',
          color: '#e94560',
          fontSize: '1.1em',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>🔥</span> Trending Keywords
        </h3>
        
        <div style={{
          opacity: isLoading ? 0.6 : 1,
          transition: 'opacity 0.3s'
        }}>
          {trending.slice(0, 6).map((item, index) => (
            <TrendingItem key={item.word} item={item} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default SentimentPanel;
