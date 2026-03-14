import React from 'react';
import '../../styles/immersive.css';

/**
 * SwimmingPauls - Animated silhouette swimmers
 * Paul silhouettes swimming across the screen periodically
 */
export const SwimmingPauls: React.FC = () => {
  // Generate random positions for swimming pauls
  const pauls = Array.from({ length: 5 }, (_, i) => ({
    id: i,
    top: `${15 + Math.random() * 60}%`,
    delay: `${Math.random() * 30}s`,
    duration: `${25 + Math.random() * 20}s`,
    reverse: Math.random() > 0.5,
    scale: 0.7 + Math.random() * 0.5,
  }));

  const PaulSilhouette: React.FC<{ className?: string }> = ({ className }) => (
    <svg
      viewBox="0 0 100 50"
      className={className}
      style={{ filter: 'drop-shadow(0 0 8px rgba(0, 212, 255, 0.4))' }}
    >
      {/* Fish-like swimmer silhouette */}
      <ellipse cx="45" cy="25" rx="25" ry="12" />
      <polygon points="70,25 90,15 90,35" />
      <polygon points="30,15 35,5 50,15" />
      <polygon points="30,35 35,45 50,35" />
      <circle cx="25" cy="22" r="3" fill="rgba(255,255,255,0.3)" />
    </svg>
  );

  return (
    <div className="swimming-pauls-container" style={{ 
      position: 'fixed', 
      inset: 0, 
      pointerEvents: 'none', 
      zIndex: 1,
      overflow: 'hidden'
    }}>
      {pauls.map((paul) => (
        <div
          key={paul.id}
          className={`swimming-paul ${paul.reverse ? 'reverse' : ''}`}
          style={{
            top: paul.top,
            animationDelay: paul.delay,
            animationDuration: paul.duration,
            transform: `scale(${paul.scale})`,
            opacity: 0.1 + Math.random() * 0.1,
          }}
        >
          <PaulSilhouette />
        </div>
      ))}
    </div>
  );
};

export default SwimmingPauls;
