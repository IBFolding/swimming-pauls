import React, { useState } from 'react';
import {
  OceanBackground,
  BubbleParticles,
  SwimmingPauls,
  AudioPlayer,
  GlassCard,
  LoadingSwimmer,
  SplashEffect,
  PoolCard,
  triggerSplash,
} from './components/immersive';
import './styles/immersive.css';

/**
 * ImmersiveDemo - Example page showing all immersive UI components
 * This demonstrates how to use the Swimming Pauls atmospheric UI
 */
const ImmersiveDemo: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [castCount, setCastCount] = useState(0);

  const handleCast = (e: React.MouseEvent) => {
    // Trigger splash effect at click position
    const rect = (e.target as HTMLElement).getBoundingClientRect();
    triggerSplash(rect.left + rect.width / 2, rect.top + rect.height / 2);
    
    setCastCount(prev => prev + 1);
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  return (
    <div style={{ minHeight: '100vh', position: 'relative' }}>
      {/* Background Layers */}
      <OceanBackground />
      <BubbleParticles />
      <SwimmingPauls />

      {/* Main Content */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '40px 20px',
        }}
      >
        {/* Header */}
        <GlassCard className="text-center" style={{ marginBottom: '32px', padding: '32px' }}>
          <h1 className="text-shimmer" style={{ fontSize: '48px', marginBottom: '16px' }}>
            🐟 Swimming Pauls
          </h1>
          <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.8)' }}>
            Dive into the immersive fishing experience
          </p>
        </GlassCard>

        {/* Audio Player */}
        <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'center' }}>
          <AudioPlayer
            trackUrl="/swimming-paul.mp3"
            trackName="Swimming Paul"
            artistName="The Deep End"
          />
        </div>

        {/* Pool Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
            marginBottom: '32px',
          }}
        >
          <SplashEffect>
            <PoolCard
              title="Shallow Reef"
              description="Perfect for beginners. Small rewards but frequent catches."
              depth={25}
              fishCount={42}
              onCast={handleCast}
            />
          </SplashEffect>

          <SplashEffect>
            <PoolCard
              title="Midnight Trench"
              description="The sweet spot for experienced anglers."
              depth={65}
              fishCount={128}
              onCast={handleCast}
            />
          </SplashEffect>

          <SplashEffect>
            <PoolCard
              title="Abyssal Depths"
              description="Legendary Pauls lurk here. High risk, high reward."
              depth={95}
              fishCount={7}
              onCast={handleCast}
            />
          </SplashEffect>
        </div>

        {/* Stats Card */}
        <GlassCard style={{ padding: '24px', marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: '24px' }}>
            <div style={{ textAlign: 'center' }}>
              <div className="text-gradient" style={{ fontSize: '36px', fontWeight: 'bold' }}>
                {castCount}
              </div>
              <div style={{ color: 'rgba(255,255,255,0.7)' }}>Total Casts</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="text-gradient" style={{ fontSize: '36px', fontWeight: 'bold' }}>
                🏆
              </div>
              <div style={{ color: 'rgba(255,255,255,0.7)' }}>Best Catch</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="text-gradient" style={{ fontSize: '36px', fontWeight: 'bold' }}>
                1,234
              </div>
              <div style={{ color: 'rgba(255,255,255,0.7)' }}>PAUL Earned</div>
            </div>
          </div>
        </GlassCard>

        {/* Loading Demo */}
        {isLoading && (
          <GlassCard style={{ padding: '40px', textAlign: 'center' }}>
            <LoadingSwimmer text="Reeling in your catch..." />
          </GlassCard>
        )}

        {/* Instructions */}
        <GlassCard style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '16px', color: '#00d4ff' }}>🎮 How to Play</h3>
          <ul style={{ color: 'rgba(255,255,255,0.8)', lineHeight: '1.8', paddingLeft: '20px' }}>
            <li>Click "Cast into Pool" to start fishing</li>
            <li>Deeper pools have rarer Pauls but take longer</li>
            <li>Listen to the Swimming Paul track while you fish</li>
            <li>Watch for the splash effects when you cast!</li>
          </ul>
        </GlassCard>
      </div>
    </div>
  );
};

export default ImmersiveDemo;
