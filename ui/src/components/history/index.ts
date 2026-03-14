/**
 * History Components - Swimming Pauls Prediction Tracking
 * 
 * A comprehensive prediction history and tracking system featuring:
 * - Prediction history list with search/filter/sort
 * - Detailed prediction view with timeline and Paul performance
 * - Accuracy dashboard with stats and leaderboard
 * - Resolution system for marking predictions
 * - Telegram integration for notifications
 */

// Main Page
export { HistoryPage } from './HistoryPage';

// Components
export { PredictionHistory } from './PredictionHistory';
export { PredictionDetail } from './PredictionDetail';
export { AccuracyDashboard } from './AccuracyDashboard';
export { ResolutionModal } from './ResolutionModal';
export { TelegramSettingsPanel } from './TelegramSettings';

// Hooks
export { usePredictionHistory } from './usePredictionHistory';
export { usePaulAccuracy } from './usePaulAccuracy';
export { useTelegramIntegration } from './useTelegramIntegration';

// Types
export type {
  HistoricalPrediction,
  PaulPerformance,
  PaulAccuracyStats,
  OverallAccuracyStats,
  MonthlyStat,
  PredictionFilter,
  PredictionSort,
  TelegramSettings,
  TelegramNotification,
  ResolutionInput,
  ResolutionResult,
  PredictionTimeline,
  TimelineEvent,
  PredictionNote,
  PredictionStatus,
  QuestionCategory,
  SortField,
  SortDirection,
} from './types';

// Constants
export { QUESTION_CATEGORIES, STATUS_LABELS } from './types';
