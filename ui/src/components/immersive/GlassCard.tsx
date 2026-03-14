import React from 'react';
import '../../styles/immersive.css';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: 'lift' | 'glow' | 'both';
  onClick?: () => void;
}

/**
 * GlassCard - Glassmorphism card component
 * Features: Blur background, border highlight, hover effects
 */
export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  style,
  hoverEffect = 'lift',
  onClick,
}) => {
  const hoverClasses = {
    lift: 'card-hover-lift',
    glow: 'card-hover-glow',
    both: 'card-hover-lift card-hover-glow',
    none: '',
  };

  return (
    <div
      className={`glass-card ${hoverClasses[hoverEffect]} ${className}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default', ...style }}
    >
      {children}
    </div>
  );
};

export default GlassCard;
sCard;
