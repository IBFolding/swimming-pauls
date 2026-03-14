import React, { useEffect, useRef } from 'react';
import { DebateRound } from '../../types/results';
import { getDirectionColor } from '../../utils/resultsHelpers';

interface DebateTimelineProps {
  rounds: DebateRound[];
}

export const DebateTimeline: React.FC<DebateTimelineProps> = ({ rounds }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || rounds.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    ctx.clearRect(0, 0, width, height);

    const padding = 60;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const stepX = chartWidth / (rounds.length - 1 || 1);

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Draw Y-axis labels
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.font = '12px "Segoe UI", sans-serif';
    ctx.textAlign = 'right';
    const yLabels = ['Bearish', 'Slightly Bearish', 'Neutral', 'Slightly Bullish', 'Bullish'];
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i;
      ctx.fillText(yLabels[i], padding - 10, y + 4);
    }

    // Calculate positions for each round
    const points = rounds.map((round, index) => {
      let yValue = 50; // neutral
      if (round.direction === 'bearish') yValue = round.confidence < 60 ? 75 : 100;
      if (round.direction === 'bullish') yValue = round.confidence < 60 ? 25 : 0;
      if (round.direction === 'neutral') yValue = 50;

      return {
        x: padding + stepX * index,
        y: padding + (yValue / 100) * chartHeight,
        round,
        color: getDirectionColor(round.direction),
      };
    });

    // Draw connecting line with gradient
    if (points.length > 1) {
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      
      for (let i = 1; i < points.length; i++) {
        // Use bezier curves for smooth transitions
        const prev = points[i - 1];
        const curr = points[i];
        const cp1x = prev.x + (curr.x - prev.x) / 2;
        const cp1y = prev.y;
        const cp2x = prev.x + (curr.x - prev.x) / 2;
        const cp2y = curr.y;
        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, curr.x, curr.y);
      }

      // Create gradient for the line
      const gradient = ctx.createLinearGradient(padding, 0, width - padding, 0);
      gradient.addColorStop(0, points[0].color);
      gradient.addColorStop(1, points[points.length - 1].color);
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 3;
      ctx.stroke();
    }

    // Draw points
    points.forEach((point, index) => {
      // Outer glow
      ctx.beginPath();
      ctx.arc(point.x, point.y, 12, 0, 2 * Math.PI);
      ctx.fillStyle = point.color + '40';
      ctx.fill();

      // Inner point
      ctx.beginPath();
      ctx.arc(point.x, point.y, 8, 0, 2 * Math.PI);
      ctx.fillStyle = point.color;
      ctx.fill();

      // White center
      ctx.beginPath();
      ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI);
      ctx.fillStyle = '#fff';
      ctx.fill();

      // Round number
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.font = 'bold 11px "Segoe UI", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`R${index + 1}`, point.x, point.y + 25);
    });

    // Draw shifts annotations
    rounds.forEach((round, index) => {
      if (round.shifts && round.shifts.length > 0 && index > 0) {
        const point = points[index];
        const prevPoint = points[index - 1];
        
        if (round.direction !== prevPoint.round.direction) {
          ctx.fillStyle = '#e94560';
          ctx.font = '10px "Segoe UI", sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText('↻ Shift', point.x, point.y - 20);
        }
      }
    });

  }, [rounds]);

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>📊 Consensus Evolution</h3>
      <div style={styles.chartContainer}>
        <canvas 
          ref={canvasRef} 
          style={styles.canvas}
        />
      </div>
      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <span style={{ ...styles.legendDot, background: '#ef4444' }} />
          <span>Bearish</span>
        </div>
        <div style={styles.legendItem}>
          <span style={{ ...styles.legendDot, background: '#fbbf24' }} />
          <span>Neutral</span>
        </div>
        <div style={styles.legendItem}>
          <span style={{ ...styles.legendDot, background: '#4ade80' }} />
          <span>Bullish</span>
        </div>
      </div>
      <div style={styles.roundsSummary}>
        {rounds.map((round, index) => (
          <div key={index} style={styles.roundBadge}>
            <span style={{ ...styles.roundNumber, color: getDirectionColor(round.direction) }}>
              R{round.round}
            </span>
            <span style={styles.roundStrength}>{round.strength.slice(0, 1).toUpperCase()}</span>
          </div>
        ))}
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
  },
  title: {
    color: '#e94560',
    marginBottom: '20px',
    fontSize: '1.3em',
  },
  chartContainer: {
    height: '250px',
    position: 'relative',
  },
  canvas: {
    width: '100%',
    height: '100%',
  },
  legend: {
    display: 'flex',
    justifyContent: 'center',
    gap: '30px',
    marginTop: '15px',
    fontSize: '0.9em',
    opacity: 0.8,
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  legendDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
  },
  roundsSummary: {
    display: 'flex',
    justifyContent: 'center',
    gap: '10px',
    marginTop: '20px',
    flexWrap: 'wrap',
  },
  roundBadge: {
    background: 'rgba(0,0,0,0.3)',
    padding: '8px 12px',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '50px',
  },
  roundNumber: {
    fontWeight: 'bold',
    fontSize: '0.9em',
  },
  roundStrength: {
    fontSize: '0.7em',
    opacity: 0.6,
    marginTop: '2px',
  },
};
