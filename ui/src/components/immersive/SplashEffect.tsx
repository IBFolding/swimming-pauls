import React, { useEffect, useState, useCallback } from 'react';
import '../../styles/immersive.css';

interface SplashParticle {
  id: number;
  x: number;
  y: number;
  tx: number;
  ty: number;
}

interface SplashEffectProps {
  children: React.ReactNode;
  splashOnClick?: boolean;
}

/**
 * SplashEffect - Creates water splash animation on interactions
 * Triggers splash particles when casting pools or clicking
 */
export const SplashEffect: React.FC<SplashEffectProps> = ({
  children,
  splashOnClick = true,
}) => {
  const [particles, setParticles] = useState<SplashParticle[]>([]);
  const [containerRef, setContainerRef] = useState<HTMLDivElement | null>(null);

  const createSplash = useCallback((x: number, y: number) => {
    const particleCount = 12;
    const newParticles: SplashParticle[] = Array.from({ length: particleCount }, (_, i) => {
      const angle = (i / particleCount) * Math.PI * 2;
      const velocity = 50 + Math.random() * 50;
      return {
        id: Date.now() + i,
        x,
        y,
        tx: Math.cos(angle) * velocity,
        ty: Math.sin(angle) * velocity - 30, // Slightly upward bias
      };
    });

    setParticles((prev) => [...prev, ...newParticles]);

    // Remove particles after animation
    setTimeout(() => {
      setParticles((prev) => prev.filter((p) => !newParticles.find((np) => np.id === p.id)));
    }, 600);
  }, []);

  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      if (splashOnClick) {
        const rect = (e.target as HTMLElement).getBoundingClientRect();
        createSplash(
          e.clientX - rect.left,
          e.clientY - rect.top
        );
      }
    },
    [splashOnClick, createSplash]
  );

  // Global splash function exposed for other components
  useEffect(() => {
    (window as any).triggerSplash = createSplash;
    return () => {
      delete (window as any).triggerSplash;
    };
  }, [createSplash]);

  return (
    <div
      ref={setContainerRef}
      onClick={handleClick}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      {children}

      {/* Splash particles */}
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="splash-particle"
          style={{
            left: particle.x,
            top: particle.y,
            '--tx': `${particle.tx}px`,
            '--ty': `${particle.ty}px`,
          } as React.CSSProperties}
        />
      ))}
    </div>
  );
};

/**
 * Trigger a splash at specific coordinates (can be called from outside)
 */
export const triggerSplash = (x: number, y: number) => {
  if (typeof window !== 'undefined' && (window as any).triggerSplash) {
    (window as any).triggerSplash(x, y);
  }
};

export default SplashEffect;
