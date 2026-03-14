import React from 'react';
import '../../styles/immersive.css';

interface PoolCardProps {
  title: string;
  description?: string;
  depth?: number;
  fishCount?: number;
  rewardToken?: string;
  onCast?: () => void;
  className?: string;
}

export const PoolCard: React.FC<PoolCardProps> = ({
  title,
  description,
  depth = 50,
  fishCount = 0,
  rewardToken = 'PAUL',
  onCast,
  className = '',
}) => {
  const getDepthLabel = (d: number) => {
    if (d < 30) return '🌊 Shallow Waters';
    if (d < 70) return '🐠 Deep Channel';
    return '🦑 The Abyss';
  };

  const getDepthColor = (d: number) => {
    if (d < 30) return '#00d4ff';
    if (d < 70) return '#3b82f6';
    return '#a855f7';
  };

  return (
    <div className={`pool-card glass-card ${className}`}>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px', color: '#fff' }}>
          {title}
        </h3>
        {description && (
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px' }}>{description}</p>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
        <div className="pool-depth-indicator">
          <span>{getDepthLabel(depth)}</span>
          <div className="depth-bar">
            <div
              className="depth-fill"
              style={{
                width: `${depth}%`,
                background: `linear-gradient(90deg, ${getDepthColor(depth)}, #00d4ff)`,
              }}
            />
          </div>
          <span style={{ fontSize: '12px', minWidth: '40px' }}>{depth}m</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>
          <span>🐟</span>
          <span>{fishCount} Pauls swimming</span>
        </div>
      </div>

      <button className="btn-ocean" onClick={onCast} style={{ width: '100%' }}>
        🎣 Cast into Pool
      </button>
    </div>
  );
};

export default PoolCard;
