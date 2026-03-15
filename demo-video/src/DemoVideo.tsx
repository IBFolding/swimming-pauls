import React from 'react';
import { 
  useCurrentFrame, 
  useVideoConfig, 
  spring,
  interpolate,
  AbsoluteFill,
  Img,
  staticFile
} from 'remotion';

export const DemoVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 30 second video (900 frames @ 30fps)
  
  // Section 1: Intro (0-4s)
  const introLogoScale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: { damping: 10 }
  });
  const introTitleOpacity = interpolate(frame, [30, 60], [0, 1]);
  const introTitleY = interpolate(frame, [30, 60], [50, 0]);
  const introTaglineOpacity = interpolate(frame, [90, 120], [0, 1]);

  // Section 2: The Problem (4-8s)
  const problemOpacity = interpolate(frame, [120, 150], [0, 1]);
  const problemY = interpolate(frame, [120, 150], [30, 0]);

  // Section 3: UI Screenshot 1 - Main Interface (8-14s)
  const ui1Opacity = interpolate(frame, [240, 270], [0, 1]);
  const ui1Scale = interpolate(frame, [240, 270], [0.9, 1]);
  const ui1Y = interpolate(frame, [240, 270], [50, 0]);

  // Section 4: UI Screenshot 2 - Results (14-20s)
  const ui2Opacity = interpolate(frame, [420, 450], [0, 1]);
  const ui2Scale = interpolate(frame, [420, 450], [0.9, 1]);

  // Section 5: Features (20-26s)
  const featuresOpacity = interpolate(frame, [600, 630], [0, 1]);

  // Section 6: CTA (26-30s)
  const ctaOpacity = interpolate(frame, [780, 810], [0, 1]);
  const ctaScale = spring({
    frame: frame - 780,
    fps,
    from: 0.8,
    to: 1,
    config: { damping: 10 }
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#0a0a0a' }}>
      {/* Background gradient */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse at center, rgba(34, 211, 238, 0.1) 0%, transparent 70%)',
        }}
      />

      {/* Section 1: Intro Logo + Title */}
      {frame < 240 && (
        <>
          <div
            style={{
              position: 'absolute',
              top: 150,
              left: '50%',
              transform: `translateX(-50%) scale(${introLogoScale})`,
              width: 180,
              height: 180,
              borderRadius: 24,
              backgroundColor: 'rgba(34, 211, 238, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 100,
            }}
          >
            🦷
          </div>

          <div
            style={{
              position: 'absolute',
              top: 380,
              left: 0,
              right: 0,
              textAlign: 'center',
              opacity: introTitleOpacity,
              transform: `translateY(${introTitleY}px)`,
            }}
          >
            <h1 style={{ fontSize: 72, fontWeight: 900, color: 'white', margin: 0, letterSpacing: -2 }}>
              SWIMMING
            </h1>
            <h1 style={{ fontSize: 72, fontWeight: 900, color: '#22d3ee', margin: 0, letterSpacing: -2 }}>
              PAULS
            </h1>
          </div>

          <p
            style={{
              position: 'absolute',
              top: 580,
              left: 0,
              right: 0,
              textAlign: 'center',
              fontSize: 32,
              color: '#9ca3af',
              fontStyle: 'italic',
              opacity: introTaglineOpacity,
            }}
          >
            "Let the Pauls cook."
          </p>
        </>
      )}

      {/* Section 2: The Problem */}
      {frame >= 120 && frame < 240 && (
        <div
          style={{
            position: 'absolute',
            top: 200,
            left: 60,
            right: 60,
            opacity: problemOpacity,
            transform: `translateY(${problemY}px)`,
          }}
        >
          <p style={{ fontSize: 36, color: '#9ca3af', textAlign: 'center', marginBottom: 40 }}>
            Every AI gives you ONE answer...
          </p>
          <p style={{ fontSize: 36, color: '#9ca3af', textAlign: 'center' }}>
            But real decisions need multiple perspectives
          </p>
        </div>
      )}

      {/* Section 3: UI Screenshot - Main Interface */}
      {frame >= 240 && frame < 420 && (
        <>
          <p
            style={{
              position: 'absolute',
              top: 60,
              left: 0,
              right: 0,
              textAlign: 'center',
              fontSize: 32,
              color: '#22d3ee',
              fontWeight: 'bold',
              opacity: ui1Opacity,
            }}
          >
            5 Prediction Modes
          </p>
          <div
            style={{
              position: 'absolute',
              top: 120,
              left: 40,
              right: 40,
              bottom: 120,
              opacity: ui1Opacity,
              transform: `translateY(${ui1Y}px) scale(${ui1Scale})`,
              borderRadius: 20,
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(34, 211, 238, 0.3)',
            }}
          >
            <Img
              src={staticFile('screenshot1.png')}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>
        </>
      )}

      {/* Section 4: UI Screenshot - Results */}
      {frame >= 420 && frame < 600 && (
        <>
          <p
            style={{
              position: 'absolute',
              top: 60,
              left: 0,
              right: 0,
              textAlign: 'center',
              fontSize: 32,
              color: '#22d3ee',
              fontWeight: 'bold',
              opacity: ui2Opacity,
            }}
          >
            Watch them debate & reach consensus
          </p>
          <div
            style={{
              position: 'absolute',
              top: 120,
              left: 40,
              right: 40,
              bottom: 120,
              opacity: ui2Opacity,
              transform: `scale(${ui2Scale})`,
              borderRadius: 20,
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(34, 211, 238, 0.3)',
            }}
          >
            <div
              style={{
                backgroundColor: '#1a1a1a',
                padding: 30,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
              }}
            >
              <div style={{ textAlign: 'center', marginBottom: 30 }}>
                <div style={{ fontSize: 64, marginBottom: 10 }}>🦷</div>
                <div style={{ fontSize: 48, fontWeight: 'bold', color: '#fbbf24', marginBottom: 10 }}>
                  NEUTRAL
                </div>
                <div style={{ fontSize: 24, color: '#9ca3af' }}>
                  63% confidence
                </div>
              </div>
              
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: 20, borderRadius: 12, marginBottom: 15 }}>
                <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 5 }}>Bullish</div>
                <div style={{ height: 8, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 4 }}>
                  <div style={{ height: '100%', width: '38%', backgroundColor: '#22c55e', borderRadius: 4 }} />
                </div>
                <div style={{ fontSize: 12, color: '#22c55e', marginTop: 5 }}>38%</div>
              </div>
              
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: 20, borderRadius: 12, marginBottom: 15 }}>
                <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 5 }}>Neutral</div>
                <div style={{ height: 8, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 4 }}>
                  <div style={{ height: '100%', width: '41%', backgroundColor: '#eab308', borderRadius: 4 }} />
                </div>
                <div style={{ fontSize: 12, color: '#eab308', marginTop: 5 }}>41%</div>
              </div>
              
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: 20, borderRadius: 12 }}>
                <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 5 }}>Bearish</div>
                <div style={{ height: 8, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 4 }}>
                  <div style={{ height: '100%', width: '21%', backgroundColor: '#ef4444', borderRadius: 4 }} />
                </div>
                <div style={{ fontSize: 12, color: '#ef4444', marginTop: 5 }}>21%</div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Section 5: Features */}
      {frame >= 600 && frame < 780 && (
        <div
          style={{
            position: 'absolute',
            top: 100,
            left: 60,
            right: 60,
            opacity: featuresOpacity,
          }}
        >
          <p style={{ fontSize: 36, color: '#22d3ee', textAlign: 'center', marginBottom: 40, fontWeight: 'bold' }}>
            What you get:
          </p>
          {[
            { icon: '🔮', text: 'Predictions - 100+ agents debate any question' },
            { icon: '📢', text: 'PR Sim - Test crisis responses before they happen' },
            { icon: '📊', text: 'Marketing - A/B test campaigns with AI audiences' },
            { icon: '📖', text: 'Story - Analyze plots & predict endings' },
            { icon: '🔬', text: 'Research - Design studies with power analysis' },
            { icon: '💯', text: '100% Local - No cloud, no API keys, private' },
          ].map((feature, i) => (
            <div
              key={i}
              style={{
                backgroundColor: 'rgba(255,255,255,0.05)',
                borderRadius: 16,
                padding: '20px 24px',
                marginBottom: 12,
                fontSize: 24,
                color: 'white',
                opacity: interpolate(frame, [630 + i * 15, 660 + i * 15], [0, 1]),
                transform: `translateX(${interpolate(frame, [630 + i * 15, 660 + i * 15], [-30, 0])}px)`,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <span style={{ fontSize: 28 }}>{feature.icon}</span>
              <span>{feature.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* Section 6: CTA */}
      {frame >= 780 && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: `translate(-50%, -50%) scale(${ctaScale})`,
            opacity: ctaOpacity,
            textAlign: 'center',
          }}
        >
          <div
            style={{
              backgroundColor: '#22d3ee',
              color: 'black',
              padding: '28px 48px',
              borderRadius: 16,
              fontSize: 32,
              fontWeight: 'bold',
              marginBottom: 20,
            }}
          >
            🐟 Try it free
          </div>
          <p style={{ fontSize: 24, color: '#9ca3af', marginBottom: 10 }}>
            swimmingpauls.vercel.app
          </p>
          <p style={{ fontSize: 18, color: '#6b7280' }}>
            Built by HOWARD • Open Source
          </p>
        </div>
      )}
    </AbsoluteFill>
  );
};
