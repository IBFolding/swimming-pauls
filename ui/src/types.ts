// Types for Swimming Pauls UI

export interface UploadedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  preview?: string;
  content?: string;
}

export interface Question {
  id: string;
  text: string;
  isPrimary?: boolean;
}

export interface Paul {
  id: string;
  name: string;
  emoji: string;
  type: string;
  description?: string;
  bias: number;
  confidence: number;
  selected: boolean;
  backstory?: string;
  specialties?: string[];
  traits?: string[];
  prediction?: string;
  reasoning?: string;
}

export interface ConsensusResult {
  direction: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  strength: 'strong' | 'moderate' | 'weak';
  sentiment: number;
}

export interface RoundResult {
  round: number;
  direction: string;
  confidence: number;
  strength: string;
}

export interface SimulationResult {
  id: string;
  question: string;
  timestamp: string;
  consensus: ConsensusResult;
  rounds: RoundResult[];
  pauls: Paul[];
  insights: string[];
  files: string[];
  status?: 'pending' | 'correct' | 'wrong' | 'partial';
  actualOutcome?: string;
}

export interface MarketPrice {
  symbol: string;
  price: number;
  change24h: number;
  volume24h?: number;
}

export interface SentimentData {
  overall: 'bullish' | 'bearish' | 'neutral';
  score: number;
  trending: string[];
}

export interface TelegramSettings {
  botToken: string;
  chatId: string;
  enabled: boolean;
}

export interface PaulPerformance {
  paulId: string;
  name: string;
  emoji: string;
  totalPredictions: number;
  correct: number;
  wrong: number;
  accuracy: number;
  streak: number;
}

// Additional types for components
export interface ScaleConfig {
  paulCount: number;
  rounds: number;
}

export interface SystemInfo {
  cores: number;
  ram: number;
  recommendedMax: number;
}

export type FileType = 'image' | 'video' | 'pdf' | 'csv' | 'json' | 'text';

export const QUESTION_TEMPLATES = {
  market: ['Will Bitcoin hit $100k?', 'Should I buy Tesla stock?', 'Is the market crashing?'],
  business: ['Will my startup succeed?', 'Should I pivot?', 'Is this a good hire?'],
  career: ['Should I quit my job?', 'Should I take this offer?', 'Is now the time to move?'],
  personal: ['Should I move cities?', 'Is this relationship right?', 'Should I buy a house?'],
} as const;

export interface ResultsPageProps {
  results: SimulationResult;
  onExport?: (format: string) => void;
}
