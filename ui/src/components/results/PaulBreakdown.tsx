import React, { useState, useMemo } from 'react';
import { PaulPrediction } from '../../types/results';
import { getDirectionColor, getDirectionGradient } from '../../utils/resultsHelpers';

interface PaulBreakdownProps {
  pauls: PaulPrediction[];
}

type SortBy = 'confidence' | 'name' | 'direction';
type FilterDirection = 'all' | 'bullish' | 'bearish' | 'neutral';

export const PaulBreakdown: React.FC<PaulBreakdownProps> = ({ pauls }) => {
  const [sortBy, setSortBy] = useState<SortBy>('confidence');
  const [filterDirection, setFilterDirection] = useState<FilterDirection>('all');
  const [expandedPaul, setExpandedPaul] = useState<string | null>(null);

  const filteredAndSortedPauls = useMemo(() => {
    let filtered = [...pauls];
    
    if (filterDirection !== 'all') {
      filtered = filtered.filter(p => p.direction === filterDirection);
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'confidence':
          return b.confidence - a.confidence;
        case 'name':
          return a.name.localeCompare(b.name);
        case 'direction':
          const dirOrder = { bullish: 0, neutral: 1, bearish: 2 };
          return dirOrder[a.direction] - dirOrder[b.direction];
        default:
          return 0;
      }
    });

    return filtered;
  }, [pauls, sortBy, filterDirection]);

  const getDirectionEmoji = (direction: string): string => {
    switch (direction) {
      case 'bullish': return '📈';
      case 'bearish': return '📉';
      case 'neutral': return '➡️';
      default: return '❓';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>🐟 Paul Predictions</h3>
        <div style={styles.controls}>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as SortBy)}
            style={styles.select}
          >
            <option value="confidence">Sort: Confidence</option>
            <option value="name">Sort: Name</option>
            <option value="direction">Sort: Direction</option>
          </select>
          <select 
            value={filterDirection} 
            onChange={(e) => setFilterDirection(e.target.value as FilterDirection)}
            style={styles.select}
          >
            <option value="all">Filter: All</option>
            <option value="bullish">Filter: Bullish 📈</option>
            <option value="bearish">Filter: Bearish 📉</option>
            <option value="neutral">Filter: Neutral ➡️</option>
          </select>
        </div>
      </div>

      <div style={styles.summaryBar}>
        {['bullish', 'neutral', 'bearish'].map((dir) => {
          const count = pauls.filter(p => p.direction === dir).length;
          const percentage = (count / pauls.length) * 100;
          return (
            <div key={dir} style={{ ...styles.summarySegment, 
              background: getDirectionColor(dir as any),
              flex: percentage,
            }} />
          );
        })}
      </div>
      <div style={styles.summaryLabels}>
        <span style={{ color: '#4ade80' }}>📈 {pauls.filter(p => p.direction === 'bullish').length}</span>
        <span style={{ color: '#fbbf24' }}>➡️ {pauls.filter(p => p.direction === 'neutral').length}</span>
        <span style={{ color: '#ef4444' }}>📉 {pauls.filter(p => p.direction === 'bearish').length}</span>
      </div>

      <div style={styles.cardsGrid}>
        {filteredAndSortedPauls.map((paul) => (
          <div 
            key={paul.id}
            style={{
              ...styles.paulCard,
              borderColor: getDirectionColor(paul.direction),
              background: expandedPaul === paul.id 
                ? 'rgba(255,255,255,0.1)' 
                : 'rgba(255,255,255,0.05)',
            }}
            onClick={() => setExpandedPaul(expandedPaul === paul.id ? null : paul.id)}
          >
            <div style={styles.cardHeader}>
              <div style={styles.paulIdentity}>
                <span style={styles.paulEmoji}>{paul.emoji}</span>
                <div>
                  <div style={styles.paulName}>{paul.name}</div>
                  <div style={styles.paulType}>{paul.type}</div>
                </div>
              </div>
              <div style={{ ...styles.directionBadge, color: getDirectionColor(paul.direction) }}>
                {getDirectionEmoji(paul.direction)} {paul.confidence}%
              </div>
            </div>

            <div style={styles.confidenceBar}>
              <div 
                style={{
                  ...styles.confidenceFill,
                  width: `${paul.confidence}%`,
                  background: getDirectionGradient(paul.direction),
                }}
              />
            </div>

            {expandedPaul === paul.id && (
              <div style={styles.expandedContent}>
                <p style={styles.reasoning}>{paul.reasoning}</p>
                {paul.factors && paul.factors.length > 0 && (
                  <div style={styles.factors}>
                    <strong>Key Factors:</strong>
                    <ul>
                      {paul.factors.map((factor, idx) => (
                        <li key={idx}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div style={styles.expandHint}>
              {expandedPaul === paul.id ? '▼ Click to collapse' : '▶ Click to expand'}
            </div>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    flexWrap: 'wrap',
    gap: '15px',
  },
  title: {
    color: '#e94560',
    fontSize: '1.3em',
  },
  controls: {
    display: 'flex',
    gap: '10px',
  },
  select: {
    padding: '10px 15px',
    borderRadius: '8px',
    border: '1px solid rgba(233, 69, 96, 0.3)',
    background: 'rgba(0,0,0,0.3)',
    color: '#fff',
    fontSize: '14px',
    cursor: 'pointer',
  },
  summaryBar: {
    display: 'flex',
    height: '8px',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '8px',
  },
  summarySegment: {
    height: '100%',
    transition: 'flex 0.3s ease',
  },
  summaryLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.85em',
    marginBottom: '20px',
    opacity: 0.8,
  },
  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '15px',
  },
  paulCard: {
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '12px',
    padding: '20px',
    borderLeft: '4px solid',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  },
  paulIdentity: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  paulEmoji: {
    fontSize: '2em',
  },
  paulName: {
    fontWeight: 'bold',
    fontSize: '1em',
  },
  paulType: {
    fontSize: '0.8em',
    opacity: 0.7,
  },
  directionBadge: {
    fontWeight: 'bold',
    fontSize: '0.9em',
    padding: '5px 10px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '15px',
  },
  confidenceBar: {
    height: '6px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  confidenceFill: {
    height: '100%',
    borderRadius: '3px',
    transition: 'width 0.5s ease',
  },
  expandedContent: {
    marginTop: '15px',
    paddingTop: '15px',
    borderTop: '1px solid rgba(255,255,255,0.1)',
  },
  reasoning: {
    fontSize: '0.9em',
    lineHeight: '1.5',
    opacity: 0.9,
    marginBottom: '10px',
  },
  factors: {
    fontSize: '0.85em',
    opacity: 0.8,
  },
  expandHint: {
    fontSize: '0.75em',
    opacity: 0.5,
    marginTop: '10px',
    textAlign: 'center',
  },
};
