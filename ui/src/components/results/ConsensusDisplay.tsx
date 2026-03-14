import React, { useEffect, useRef, useState } from 'react';
import { ConsensusResult } from '../../types/results';
import { getDirectionColor, getStrengthLabel, getConfidenceColor } from '../../utils/resultsHelpers';

interface ConsensusDisplayProps {
  consensus: ConsensusResult;
}

export const ConsensusDisplay: React.FC<ConsensusDisplayProps> = ({ consensus }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [animatedRatio, setAnimatedRatio] = useState(0);

  // Animate the gauge
  useEffect(() => {
    const duration = 1500;
    const startTime = Date.now();
    const startConfidence = 0;
    const targetConfidence = consensus.confidence;
    const targetRatio = (consensus.agreeingPauls / consensus.totalPauls) * 100;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);

      setAnimatedConfidence(Math.round(startConfidence + (targetConfidence - startConfidence) * easeOut));
      setAnimatedRatio(Math.round(targetRatio * easeOut));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [consensus.confidence, consensus.agreeingPauls, consensus.totalPauls]);

  // Draw the gauge
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height * 0.75;
    const radius = Math.min(canvas.width, canvas.height * 1.5) * 0.35;
    const lineWidth = 25;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background arc (neutral track)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineCap = 'round';
    ctx.stroke();

    // Calculate angle based on confidence (0-100 maps to PI to 2*PI)
    // For direction: bearish (left), neutral (center), bullish (right)
    let angleOffset = 0;
    if (consensus.direction === 'bearish') angleOffset = -0.5;
    if (consensus.direction === 'bullish') angleOffset = 0.5;
    
    const confidenceRatio = consensus.confidence / 100;
    const angle = Math.PI + (Math.PI * confidenceRatio) + (angleOffset * Math.PI * 0.3);

    // Draw gradient arc
    const gradient = ctx.createLinearGradient(centerX - radius, centerY, centerX + radius, centerY);
    gradient.addColorStop(0, '#ef4444');
    gradient.addColorStop(0.5, '#fbbf24');
    gradient.addColorStop(1, '#4ade80');

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, Math.min(angle, 2 * Math.PI));
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = gradient;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Draw needle
    const needleLength = radius - 10;
    const needleAngle = angle;
    const needleX = centerX + Math.cos(needleAngle) * needleLength;
    const needleY = centerY + Math.sin(needleAngle) * needleLength;

    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(needleX, needleY);
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#fff';
    ctx.stroke();

    // Draw needle center
    ctx.beginPath();
    ctx.arc(centerX, centerY, 8, 0, 2 * Math.PI);
    ctx.fillStyle = '#e94560';
    ctx.fill();

    // Draw labels
    ctx.font = 'bold 14px "Segoe UI", sans-serif';
    ctx.fillStyle = '#ef4444';
    ctx.textAlign = 'right';
    ctx.fillText('BEARISH', centerX - radius - 10, centerY + 5);

    ctx.fillStyle = '#fbbf24';
    ctx.textAlign = 'center';
    ctx.fillText('NEUTRAL', centerX, centerY - radius - 20);

    ctx.fillStyle = '#4ade80';
    ctx.textAlign = 'left';
    ctx.fillText('BULLISH', centerX + radius + 10, centerY + 5);
  }, [consensus.confidence, consensus.direction]);

  const directionColor = getDirectionColor(consensus.direction);
  const confidenceColor = getConfidenceColor(consensus.confidence);

  return (
    <div style={styles.container}>
      <div style={styles.gaugeContainer}>
        <canvas 
          ref={canvasRef} 
          width={400} 
          height={220}
          style={styles.canvas}
        />
        <div style={{ ...styles.directionLabel, color: directionColor }}>
          {consensus.direction.toUpperCase()}
        </div>
        <div style={styles.confidenceLabel}>
          <span style={{ ...styles.confidenceValue, color: confidenceColor }}>
            {animatedConfidence}%
          </span>
          <span style={styles.confidenceText}> Confidence</span>
        </div>
      </div>

      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <div style={styles.statValue}>{animatedRatio}%</div>
          <div style={styles.statLabel}>Agreement</div>
          <div style={styles.statSubtext}>
            {consensus.agreeingPauls}/{consensus.totalPauls} Pauls
          </div>
        </div>
        <div style={styles.statCard}>
          <div style={{ ...styles.strengthBadge, color: directionColor }}>
            {getStrengthLabel(consensus.strength)}
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '20px',
    padding: '30px',
    border: '1px solid rgba(255,255,255,0.1)',
    textAlign: 'center',
  },
  gaugeContainer: {
    position: 'relative',
    marginBottom: '20px',
  },
  canvas: {
    maxWidth: '100%',
    height: 'auto',
  },
  directionLabel: {
    fontSize: '2.5em',
    fontWeight: 'bold',
    marginTop: '-20px',
    textShadow: '0 0 20px currentColor',
  },
  confidenceLabel: {
    marginTop: '10px',
  },
  confidenceValue: {
    fontSize: '2em',
    fontWeight: 'bold',
  },
  confidenceText: {
    fontSize: '1.2em',
    opacity: 0.8,
  },
  statsRow: {
    display: 'flex',
    justifyContent: 'center',
    gap: '30px',
    flexWrap: 'wrap',
  },
  statCard: {
    background: 'rgba(0,0,0,0.2)',
    padding: '20px 30px',
    borderRadius: '10px',
    minWidth: '150px',
  },
  statValue: {
    fontSize: '2em',
    fontWeight: 'bold',
    color: '#e94560',
  },
  statLabel: {
    fontSize: '0.9em',
    opacity: 0.7,
    marginTop: '5px',
  },
  statSubtext: {
    fontSize: '0.8em',
    opacity: 0.5,
    marginTop: '3px',
  },
  strengthBadge: {
    fontSize: '1.1em',
    fontWeight: 'bold',
    padding: '10px 20px',
    background: 'rgba(255,255,255,0.1)',
    borderRadius: '20px',
  },
};
