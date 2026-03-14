import React from 'react';
import { SwimmingPaulsResult } from '../../types/results';
import { ConsensusDisplay } from './ConsensusDisplay';
import { DebateTimeline } from './DebateTimeline';
import { PaulBreakdown } from './PaulBreakdown';
import { InsightsPanel } from './InsightsPanel';
import { ExportOptions } from './ExportOptions';
import { getDirectionColor } from '../../utils/resultsHelpers';

interface ResultsPageProps {
  result: SwimmingPaulsResult;
  resultId: string;
  onNewPrediction: () => void;
}

export const ResultsPage: React.FC<ResultsPageProps> = ({ result, resultId, onNewPrediction }) => {
  const directionColor = getDirectionColor(result.consensus.direction);

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>
          <span style={{ color: directionColor }}>🏁</span> The Pauls Have Spoken
        </h2>
        <p style={styles.question}>"{result.question}"</p>
      </div>

      {/* Main Results Grid */}
      <div style={styles.mainGrid}>
        {/* Left Column - Consensus */}
        <div style={styles.consensusSection}>
          <ConsensusDisplay consensus={result.consensus} />
        </div>

        {/* Right Column - Timeline */}
        <div style={styles.timelineSection}>
          <DebateTimeline rounds={result.rounds} />
        </div>
      </div>

      {/* Paul Breakdown */}
      <div style={styles.section}>
        <PaulBreakdown pauls={result.pauls} />
      </div>

      {/* Insights Panel */}
      <div style={styles.section}>
        <InsightsPanel 
          insights={result.insights}
          recommendation={result.recommendation}
          consensusDirection={result.consensus.direction}
        />
      </div>

      {/* Export Options */}
      <div style={styles.section}>
        <ExportOptions result={result} resultId={resultId} />
      </div>

      {/* New Prediction Button */}
      <div style={styles.footer}>
        <button onClick={onNewPrediction} style={styles.newPredictionBtn}>
          🐟 Cast Another Pool
        </button>
      </div>
    </div>
  );
};

// Sample data generator for demo/testing
export const generateSampleResult = (): SwimmingPaulsResult => ({
  question: "Will Bitcoin reach $100,000 by end of 2024?",
  timestamp: new Date().toISOString(),
  consensus: {
    direction: 'bullish',
    confidence: 67,
    strength: 'moderate',
    agreementRatio: 0.65,
    totalPauls: 10,
    agreeingPauls: 7,
  },
  rounds: [
    { round: 1, direction: 'neutral', confidence: 45, strength: 'weak', shifts: [], keyArguments: ['Mixed signals'] },
    { round: 2, direction: 'bullish', confidence: 52, strength: 'weak', shifts: ['ETF momentum'], keyArguments: ['Institutional interest'] },
    { round: 3, direction: 'bullish', confidence: 58, strength: 'moderate', shifts: [], keyArguments: ['Halving effect'] },
    { round: 4, direction: 'neutral', confidence: 50, strength: 'weak', shifts: ['Regulatory concerns'], keyArguments: ['SEC developments'] },
    { round: 5, direction: 'bullish', confidence: 62, strength: 'moderate', shifts: ['Tech breakout'], keyArguments: ['Price action'] },
    { round: 6, direction: 'bullish', confidence: 65, strength: 'moderate', shifts: [], keyArguments: ['Macro tailwinds'] },
    { round: 7, direction: 'bullish', confidence: 67, strength: 'moderate', shifts: [], keyArguments: ['Consensus forming'] },
  ],
  pauls: [
    { id: '1', name: 'Analyst Paul', emoji: '📊', type: 'Data-driven', direction: 'bullish', confidence: 78, reasoning: 'On-chain metrics support continued upward momentum', factors: ['Exchange reserves declining', 'Hash rate at ATH'] },
    { id: '2', name: 'Trader Paul', emoji: '📈', type: 'Market timing', direction: 'bullish', confidence: 82, reasoning: 'Technical setup is primed for a breakout', factors: ['Golden cross forming', 'Volume profile supportive'] },
    { id: '3', name: 'Visionary Paul', emoji: '🔮', type: 'Long-term', direction: 'bullish', confidence: 75, reasoning: 'Historical 4-year cycle suggests new highs', factors: ['Post-halving dynamics', 'Adoption curve'] },
    { id: '4', name: 'Skeptic Paul', emoji: '🤨', type: 'Contrarian', direction: 'bearish', confidence: 65, reasoning: 'Too much euphoria in the market', factors: ['Retail FOMO', 'Leverage levels'] },
    { id: '5', name: 'Producer Paul', emoji: '💰', type: 'Budget-focused', direction: 'neutral', confidence: 55, reasoning: 'Uncertain macro environment', factors: ['Fed policy', 'Dollar strength'] },
    { id: '6', name: 'Hedgie Paul', emoji: '🛡️', type: 'Risk-aware', direction: 'bullish', confidence: 60, reasoning: 'Risk/reward favors longs', factors: ['Downside limited', 'Asymmetric upside'] },
    { id: '7', name: 'Entrepreneur Paul', emoji: '🚀', type: 'Innovation', direction: 'bullish', confidence: 85, reasoning: 'Institutional adoption accelerating', factors: ['ETF flows', 'Corporate treasury'] },
    { id: '8', name: 'Director Paul', emoji: '🎬', type: 'Creative', direction: 'neutral', confidence: 50, reasoning: 'Narrative is strong but timing uncertain', factors: ['Media coverage', 'Sentiment shifts'] },
    { id: '9', name: 'Coder Paul', emoji: '💻', type: 'Technical', direction: 'bullish', confidence: 72, reasoning: 'Network fundamentals are solid', factors: ['Developer activity', 'Protocol upgrades'] },
    { id: '10', name: 'Diplomat Paul', emoji: '🤝', type: 'Consensus', direction: 'bullish', confidence: 68, reasoning: 'General consensus among experts', factors: ['Analyst consensus', 'Institutional research'] },
  ],
  insights: [
    { type: 'factor', title: 'ETF Momentum', description: 'Institutional inflows via ETFs are creating sustained demand pressure' },
    { type: 'factor', title: 'Halving Cycle', description: 'Historical 4-year cycle suggests bullish continuation post-halving' },
    { type: 'opportunity', title: 'Institutional Adoption', description: 'Major corporations adding BTC to treasuries', severity: 'high' },
    { type: 'opportunity', title: 'Global Uncertainty', description: 'Geopolitical tensions driving store-of-value demand', severity: 'medium' },
    { type: 'risk', title: 'Regulatory Uncertainty', description: 'Potential policy changes could impact price action', severity: 'medium' },
    { type: 'risk', title: 'Macro Headwinds', description: 'High interest rates may limit risk asset appreciation', severity: 'low' },
  ],
  recommendation: {
    action: 'Cautiously accumulate with dollar-cost averaging strategy',
    urgency: 'medium',
    reasoning: 'The Pauls show moderate bullish consensus with 67% confidence. While the trend is positive, the moderate strength suggests maintaining disciplined position sizing.',
    timeframe: '3-6 months',
  },
  metadata: {
    totalRounds: 7,
    simulationType: 'standard',
    duration: 3250,
  },
});

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '40px',
    padding: '30px',
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '20px',
    border: '1px solid rgba(255,255,255,0.1)',
  },
  title: {
    fontSize: '2em',
    marginBottom: '15px',
  },
  question: {
    fontSize: '1.2em',
    opacity: 0.8,
    fontStyle: 'italic',
  },
  mainGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
    gap: '25px',
    marginBottom: '30px',
  },
  consensusSection: {
    minWidth: 0,
  },
  timelineSection: {
    minWidth: 0,
  },
  section: {
    marginBottom: '25px',
  },
  footer: {
    textAlign: 'center',
    marginTop: '40px',
    padding: '30px',
  },
  newPredictionBtn: {
    padding: '20px 50px',
    fontSize: '1.3em',
    background: 'linear-gradient(135deg, #e94560 0%, #ff6b6b 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: '2px',
  },
};

export default ResultsPage;
