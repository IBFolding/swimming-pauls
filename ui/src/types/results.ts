export interface PaulPrediction {
  id: string;
  name: string;
  emoji: string;
  type: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  reasoning: string;
  factors: string[];
}

export interface DebateRound {
  round: number;
  direction: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  strength: 'weak' | 'moderate' | 'strong';
  shifts: string[];
  keyArguments: string[];
}

export interface ConsensusResult {
  direction: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  strength: 'weak' | 'moderate' | 'strong';
  agreementRatio: number;
  totalPauls: number;
  agreeingPauls: number;
}

export interface Insight {
  type: 'opportunity' | 'risk' | 'factor';
  title: string;
  description: string;
  severity?: 'low' | 'medium' | 'high';
}

export interface Recommendation {
  action: string;
  urgency: 'low' | 'medium' | 'high';
  reasoning: string;
  timeframe: string;
}

export interface SwimmingPaulsResult {
  question: string;
  timestamp: string;
  consensus: ConsensusResult;
  rounds: DebateRound[];
  pauls: PaulPrediction[];
  insights: Insight[];
  recommendation: Recommendation;
  metadata: {
    totalRounds: number;
    simulationType: string;
    duration: number;
  };
}
