import React from 'react';
import '../../styles/immersive.css';

interface LoadingSwimmerProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * LoadingSwimmer - Animated loading state with swimming Paul
 * Shows a swimming fish animation while loading
 */
export const LoadingSwimmer: React.FC<LoadingSwimmerProps> = ({
  text = 'Swimming into the pool...',
  size = 'md',
}) => {
  const sizeMap = {
    sm: { width: 60, container: '80px' },
    md: { width: 120, container: '150px' },
    lg: { width: 180, container: '220px' },
  };

  const { width, container } = sizeMap[size];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '24px',
        padding: '40px',
      }}
    >
      {/* Swimming animation container */}
      <div
        style={{
          position: 'relative',
          width: container,
          height: container,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Ripple effects */}
        <div className="loading-ripple" />
        <div className="loading-ripple" />
        <div className="loading-ripple" />

        {/* Swimming Paul */}
        <div className="loading-swimmer" style={{ width, height: width / 2 }}>
          <svg viewBox="0 0 100 50" fill="currentColor">
            <ellipse cx="45" cy="25" rx="25" ry="12" />
            <polygon points="70,25 90,15 90,35" />
            <polygon points="30,15 35,5 50,15" />
            <polygon points="30,35 35,45 50,35" />
            <circle cx="25" cy="22" r="3" fill="rgba(255,255,255,0.3)" />
          </svg>
        </div>
      </div>

      {/* Loading text */}
      <p
        style={{
          color: '#00d4ff',
          fontSize: size === 'sm' ? '14px' : '16px',
          textAlign: 'center',
          fontWeight: 500,
          textShadow: '0 0 10px rgba(0, 212, 255, 0.5)',
        }}
      >
        {text}
      </p>

      {/* Animated dots */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            style={{
              width: '8px',
              height: '8px',
              background: '#00d4ff',
              borderRadius: '50%',
              animation: `dotPulse 1.4s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes dotPulse {
          0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default LoadingSwimmer;
