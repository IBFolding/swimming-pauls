import React from 'react';
import { 
  useCurrentFrame, 
  useVideoConfig, 
  spring,
  interpolate,
  AbsoluteFill 
} from 'remotion';

export const DemoVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animations
  const titleOpacity = interpolate(frame, [0, 30], [0, 1]);
  const titleY = interpolate(frame, [0, 30], [50, 0]);
  
  const logoScale = spring({
    frame: frame - 30,
    fps,
    from: 0,
    to: 1,
    config: { damping: 10 }
  });

  const taglineOpacity = interpolate(frame, [60, 90], [0, 1]);
  
  const featureOpacity = interpolate(frame, [120, 150], [0, 1]);
  const featureY = interpolate(frame, [120, 150], [30, 0]);

  const ctaOpacity = interpolate(frame, [240, 270], [0, 1]);
  const ctaScale = interpolate(frame, [240, 270], [0.8, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: '#0a0a0a' }}>
      {/* Background gradient */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse at center, rgba(34, 211, 238, 0.15) 0%, transparent 70%)',
        }}
      />

      {/* Logo */}
      <div
        style={{
          position: 'absolute',
          top: 200,
          left: '50%',
          transform: `translateX(-50%) scale(${logoScale})`,
          width: 200,
          height: 200,
          borderRadius: 24,
          backgroundColor: 'rgba(34, 211, 238, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 120,
        }}
      >
        🦷
      </div>

      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: 450,
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <h1
          style={{
            fontSize: 80,
            fontWeight: 900,
            color: 'white',
            margin: 0,
            letterSpacing: -2,
          }}
        >
          SWIMMING
        </h1>
        <h1
          style={{
            fontSize: 80,
            fontWeight: 900,
            color: '#22d3ee',
            margin: 0,
            letterSpacing: -2,
          }}
        >
          PAULS
        </h1>
      </div>

      {/* Tagline */}
      <p
        style={{
          position: 'absolute',
          top: 650,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontSize: 36,
          color: '#9ca3af',
          fontStyle: 'italic',
          opacity: taglineOpacity,
        }}
      >
        "Let the Pauls cook."
      </p>

      {/* Features */}
      <div
        style={{
          position: 'absolute',
          top: 800,
          left: 80,
          right: 80,
          opacity: featureOpacity,
          transform: `translateY(${featureY}px)`,
        }}
      >
        {[
          '🔮 100+ AI agents debate your question',
          '📊 Predictions, PR sim, Marketing tests',
          '📖 Story analysis, Research design',
          '💯 100% local - no cloud, no API keys',
        ].map((feature, i) => (
          <div
            key={i}
            style={{
              backgroundColor: 'rgba(255,255,255,0.05)',
              borderRadius: 16,
              padding: '24px 32px',
              marginBottom: 16,
              fontSize: 32,
              color: 'white',
              opacity: interpolate(frame, [150 + i * 10, 180 + i * 10], [0, 1]),
              transform: `translateX(${interpolate(frame, [150 + i * 10, 180 + i * 10], [-30, 0])}px)`,
            }}
          >
            {feature}
          </div>
        ))}
      </div>

      {/* CTA */}
      <div
        style={{
          position: 'absolute',
          bottom: 150,
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: ctaOpacity,
          transform: `scale(${ctaScale})`,
        }}
      >
        <div
          style={{
            backgroundColor: '#22d3ee',
            color: 'black',
            padding: '24px 48px',
            borderRadius: 16,
            fontSize: 36,
            fontWeight: 'bold',
            display: 'inline-block',
          }}
        >
          🐟 Try it free → swimmingpauls.vercel.app
        </div>
      </div>

      {/* Footer */}
      <p
        style={{
          position: 'absolute',
          bottom: 60,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontSize: 24,
          color: '#6b7280',
        }}
      >
        Built by HOWARD • Open Source on GitHub
      </p>
    </AbsoluteFill>
  );
};
