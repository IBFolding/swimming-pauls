import React from 'react';
import { Insight, Recommendation } from '../../types/results';
import { getDirectionColor } from '../../utils/resultsHelpers';

interface InsightsPanelProps {
  insights: Insight[];
  recommendation: Recommendation;
  consensusDirection: 'bullish' | 'bearish' | 'neutral';
}

export const InsightsPanel: React.FC<InsightsPanelProps> = ({ 
  insights, 
  recommendation, 
  consensusDirection 
}) => {
  const opportunityInsights = insights.filter(i => i.type === 'opportunity');
  const riskInsights = insights.filter(i => i.type === 'risk');
  const factorInsights = insights.filter(i => i.type === 'factor');

  const getSeverityColor = (severity?: string): string => {
    switch (severity) {
      case 'high': return '#ef4444';
      case 'medium': return '#fbbf24';
      case 'low': return '#4ade80';
      default: return '#a0a0a0';
    }
  };

  const getUrgencyEmoji = (urgency: string): string => {
    switch (urgency) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div style={styles.container}>
      {/* Key Factors */}
      {factorInsights.length > 0 && (
        <div style={styles.section}>
          <h4 style={styles.sectionTitle}>🔑 Key Factors</h4>
          <ul style={styles.factorList}>
            {factorInsights.map((insight, idx) => (
              <li key={idx} style={styles.factorItem}>
                <span style={styles.factorBullet}>•</span>
                <div>
                  <strong>{insight.title}</strong>
                  <p style={styles.factorDesc}>{insight.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={styles.cardsRow}>
        {/* Opportunities */}
        {opportunityInsights.length > 0 && (
          <div style={{ ...styles.card, borderColor: '#4ade80' }}>
            <h4 style={{ ...styles.cardTitle, color: '#4ade80' }}>🚀 Opportunities</h4>
            <div style={styles.cardContent}>
              {opportunityInsights.map((insight, idx) => (
                <div key={idx} style={styles.cardItem}>
                  <div style={styles.cardItemHeader}>
                    <strong>{insight.title}</strong>
                    {insight.severity && (
                      <span 
                        style={{ 
                          ...styles.severityBadge, 
                          background: getSeverityColor(insight.severity) + '30',
                          color: getSeverityColor(insight.severity),
                        }}
                      >
                        {insight.severity}
                      </span>
                    )}
                  </div>
                  <p style={styles.cardItemDesc}>{insight.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Risks */}
        {riskInsights.length > 0 && (
          <div style={{ ...styles.card, borderColor: '#ef4444' }}>
            <h4 style={{ ...styles.cardTitle, color: '#ef4444' }}>⚠️ Risks</h4>
            <div style={styles.cardContent}>
              {riskInsights.map((insight, idx) => (
                <div key={idx} style={styles.cardItem}>
                  <div style={styles.cardItemHeader}>
                    <strong>{insight.title}</strong>
                    {insight.severity && (
                      <span 
                        style={{ 
                          ...styles.severityBadge, 
                          background: getSeverityColor(insight.severity) + '30',
                          color: getSeverityColor(insight.severity),
                        }}
                      >
                        {insight.severity}
                      </span>
                    )}
                  </div>
                  <p style={styles.cardItemDesc}>{insight.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recommendation Box */}
      <div 
        style={{ 
          ...styles.recommendationBox, 
          borderColor: getDirectionColor(consensusDirection),
          background: `linear-gradient(135deg, ${getDirectionColor(consensusDirection)}15 0%, transparent 100%)`,
        }}
      >
        <div style={styles.recHeader}>
          <h4 style={{ ...styles.recTitle, color: getDirectionColor(consensusDirection) }}>
            💡 Recommendation
          </h4>
          <div style={styles.urgencyBadge}>
            <span>{getUrgencyEmoji(recommendation.urgency)}</span>
            <span style={{ textTransform: 'uppercase', fontSize: '0.8em' }}>
              {recommendation.urgency} urgency
            </span>
          </div>
        </div>
        
        <div style={styles.recAction}>
          {recommendation.action}
        </div>
        
        <p style={styles.recReasoning}>{recommendation.reasoning}</p>
        
        <div style={styles.recTimeframe}>
          <strong>⏱️ Timeframe: </strong>
          {recommendation.timeframe}
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
  },
  section: {
    marginBottom: '25px',
  },
  sectionTitle: {
    color: '#e94560',
    fontSize: '1.1em',
    marginBottom: '15px',
  },
  factorList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  factorItem: {
    display: 'flex',
    gap: '12px',
    padding: '12px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '8px',
    marginBottom: '10px',
    alignItems: 'flex-start',
  },
  factorBullet: {
    color: '#e94560',
    fontWeight: 'bold',
    fontSize: '1.2em',
  },
  factorDesc: {
    margin: '5px 0 0 0',
    opacity: 0.8,
    fontSize: '0.9em',
    lineHeight: '1.4',
  },
  cardsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '20px',
    marginBottom: '25px',
  },
  card: {
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '12px',
    padding: '20px',
    border: '1px solid',
  },
  cardTitle: {
    fontSize: '1em',
    marginBottom: '15px',
    paddingBottom: '10px',
    borderBottom: '1px solid rgba(255,255,255,0.1)',
  },
  cardContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  cardItem: {
    padding: '12px',
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '8px',
  },
  cardItemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '6px',
  },
  severityBadge: {
    padding: '3px 8px',
    borderRadius: '10px',
    fontSize: '0.7em',
    textTransform: 'uppercase',
    fontWeight: 'bold',
  },
  cardItemDesc: {
    margin: 0,
    opacity: 0.8,
    fontSize: '0.85em',
    lineHeight: '1.4',
  },
  recommendationBox: {
    border: '2px solid',
    borderRadius: '15px',
    padding: '25px',
  },
  recHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '15px',
    flexWrap: 'wrap',
    gap: '10px',
  },
  recTitle: {
    fontSize: '1.2em',
    margin: 0,
  },
  urgencyBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 15px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '20px',
    fontSize: '0.9em',
  },
  recAction: {
    fontSize: '1.3em',
    fontWeight: 'bold',
    marginBottom: '15px',
    padding: '15px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '10px',
    textAlign: 'center',
  },
  recReasoning: {
    margin: '0 0 15px 0',
    opacity: 0.9,
    lineHeight: '1.6',
  },
  recTimeframe: {
    padding: '10px 15px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '8px',
    fontSize: '0.9em',
  },
};
