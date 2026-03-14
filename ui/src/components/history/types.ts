/**
 * Prediction History Types
 * TypeScript interfaces for prediction tracking and history
 */

import type { SwimmingPaulsResult, PaulPrediction, ConsensusResult } from '../types/results';

// ============================================================================
// Enums & Constants
// ============================================================================

export type PredictionStatus = 'pending' | 'correct' | 'wrong' | 'partial';
export type QuestionCategory = 
  | 'crypto' 
  | 'stocks' 
  | 'business' 
  | 'career' 
  | 'personal' 
  | 'politics' 
  | 'sports' 
  | 'other';

export const QUESTION_CATEGORIES: { value: QuestionCategory; label: string; emoji: string }[] = [
  { value: 'crypto', label: 'Crypto', emoji: '₿' },
  { value: 'stocks', label: 'Stocks', emoji: '📈' },
  { value: 'business', label: 'Business', emoji: '💼' },
  { value: 'career', label: 'Career', emoji: '🎯' },
  { value: 'personal', label: 'Personal', emoji: '🏠' },
  { value: 'politics', label: 'Politics', emoji: '🏛️' },
  { value: 'sports', label: 'Sports', emoji: '⚽' },
  { value: 'other', label: 'Other', emoji: '📌' },
];

export const STATUS_LABELS: Record<PredictionStatus, { label: string; emoji: string; color: string }> = {
  pending: { label: 'Pending', emoji: '⏳', color: '#fbbf24' },
  correct: { label: 'Correct', emoji: '✅', color: '#4ade80' },
  wrong: { label: 'Wrong', emoji: '❌', color: '#ef4444' },
  partial: { label: 'Partial', emoji: '⚡', color: '#f97316' },
};

// ============================================================================
// Core Prediction History Types
// ============================================================================

export interface HistoricalPrediction {
  id: string;
  question: string;
  category: QuestionCategory;
  status: PredictionStatus;
  createdAt: string;
  resolvedAt?: string;
  result: SwimmingPaulsResult;
  
  // Resolution data
  actualOutcome?: string;
  outcomeNotes?: string;
  resolvedBy?: string;
  
  // Calculated accuracy after resolution
  accuracyScore?: number; // 0-100
  paulPerformances?: PaulPerformance[];
}

export interface PaulPerformance {
  paulId: string;
  paulName: string;
  paulEmoji: string;
  prediction: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  wasCorrect: boolean;
  accuracyScore: number;
}

export interface PaulAccuracyStats {
  paulId: string;
  paulName: string;
  paulEmoji: string;
  paulType: string;
  
  // Overall stats
  totalPredictions: number;
  correctPredictions: number;
  wrongPredictions: number;
  partialPredictions: number;
  accuracyPercentage: number;
  
  // By direction
  bullishCorrect: number;
  bullishTotal: number;
  bearishCorrect: number;
  bearishTotal: number;
  neutralCorrect: number;
  neutralTotal: number;
  
  // By category
  categoryAccuracy: Record<QuestionCategory, { correct: number; total: number }>;
  
  // Recent trend (last 10 predictions)
  recentTrend: ('correct' | 'wrong' | 'partial' | null)[];
  
  // Confidence correlation
  avgConfidenceWhenCorrect: number;
  avgConfidenceWhenWrong: number;
}

export interface OverallAccuracyStats {
  totalPredictions: number;
  resolvedPredictions: number;
  pendingPredictions: number;
  
  correctCount: number;
  wrongCount: number;
  partialCount: number;
  
  overallAccuracy: number;
  
  // By category
  categoryStats: Record<QuestionCategory, { correct: number; wrong: number; partial: number; total: number }>;
  
  // Over time (monthly)
  monthlyStats: MonthlyStat[];
  
  // Consensus accuracy
  consensusCorrect: number;
  consensusTotal: number;
  consensusAccuracy: number;
}

export interface MonthlyStat {
  month: string; // YYYY-MM
  monthLabel: string; // Jan 2024
  correct: number;
  wrong: number;
  partial: number;
  total: number;
  accuracy: number;
}

// ============================================================================
// Filter & Sort Types
// ============================================================================

export interface PredictionFilter {
  searchQuery: string;
  status: PredictionStatus | 'all';
  category: QuestionCategory | 'all';
  dateFrom?: string;
  dateTo?: string;
  paulId?: string;
}

export type SortField = 'date' | 'question' | 'accuracy' | 'status' | 'category';
export type SortDirection = 'asc' | 'desc';

export interface PredictionSort {
  field: SortField;
  direction: SortDirection;
}

// ============================================================================
// Telegram Integration Types
// ============================================================================

export interface TelegramSettings {
  enabled: boolean;
  botToken: string;
  chatId: string;
  
  // Notification preferences
  notifyOnResolve: boolean;
  notifyOnCorrect: boolean;
  notifyOnWrong: boolean;
  
  // Custom messages
  customMessageCorrect?: string;
  customMessageWrong?: string;
  
  // Link to app
  includeLink: boolean;
  appUrl?: string;
}

export interface TelegramNotification {
  id: string;
  predictionId: string;
  status: 'pending' | 'sent' | 'failed';
  sentAt?: string;
  error?: string;
}

// ============================================================================
// Resolution Types
// ============================================================================

export interface ResolutionInput {
  actualOutcome: string;
  outcomeNotes?: string;
  status: PredictionStatus;
}

export interface ResolutionResult {
  predictionId: string;
  status: PredictionStatus;
  accuracyScore: number;
  paulPerformances: PaulPerformance[];
  updatedStats: OverallAccuracyStats;
}

// ============================================================================
// Detail View Types
// ============================================================================

export interface PredictionTimeline {
  predictionId: string;
  events: TimelineEvent[];
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  type: 'created' | 'round_completed' | 'consensus_reached' | 'resolved' | 'note_added';
  title: string;
  description: string;
  data?: Record<string, unknown>;
}

export interface PredictionNote {
  id: string;
  predictionId: string;
  content: string;
  createdAt: string;
  updatedAt?: string;
}
