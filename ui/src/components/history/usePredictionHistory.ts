/**
 * usePredictionHistory Hook
 * Manages prediction history in localStorage
 */

import { useState, useEffect, useCallback } from 'react';
import type { 
  HistoricalPrediction, 
  PredictionFilter, 
  PredictionSort,
  ResolutionInput,
  ResolutionResult,
  PaulPerformance,
  PredictionStatus,
  OverallAccuracyStats,
  QuestionCategory
} from './types';
import { generateId } from '../../utils';

const STORAGE_KEY = 'swimming-pauls-history';

export function usePredictionHistory() {
  const [predictions, setPredictions] = useState<HistoricalPrediction[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setPredictions(parsed);
      } catch (e) {
        console.error('Failed to parse prediction history:', e);
      }
    }
    setIsLoaded(true);
  }, []);

  // Save to localStorage when predictions change
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(predictions));
    }
  }, [predictions, isLoaded]);

  // Add a new prediction
  const addPrediction = useCallback((
    question: string, 
    category: QuestionCategory,
    result: HistoricalPrediction['result']
  ): HistoricalPrediction => {
    const newPrediction: HistoricalPrediction = {
      id: generateId(),
      question,
      category,
      status: 'pending',
      createdAt: new Date().toISOString(),
      result,
    };

    setPredictions(prev => [newPrediction, ...prev]);
    return newPrediction;
  }, []);

  // Delete a prediction
  const deletePrediction = useCallback((id: string): boolean => {
    setPredictions(prev => prev.filter(p => p.id !== id));
    return true;
  }, []);

  // Get a single prediction
  const getPrediction = useCallback((id: string): HistoricalPrediction | undefined => {
    return predictions.find(p => p.id === id);
  }, [predictions]);

  // Resolve a prediction
  const resolvePrediction = useCallback((
    id: string, 
    resolution: ResolutionInput
  ): ResolutionResult | null => {
    const prediction = predictions.find(p => p.id === id);
    if (!prediction) return null;

    // Calculate Paul performances
    const paulPerformances: PaulPerformance[] = prediction.result.pauls.map(paul => {
      let wasCorrect = false;
      let accuracyScore = 0;

      // Determine if Paul was correct based on actual outcome and prediction
      if (resolution.status === 'correct') {
        wasCorrect = paul.direction === prediction.result.consensus.direction;
        accuracyScore = wasCorrect ? paul.confidence * 100 : 0;
      } else if (resolution.status === 'wrong') {
        wasCorrect = paul.direction !== prediction.result.consensus.direction;
        accuracyScore = wasCorrect ? paul.confidence * 100 : 0;
      } else if (resolution.status === 'partial') {
        // Partial credit if direction is neutral or somewhat aligned
        wasCorrect = paul.direction === 'neutral' || paul.direction === prediction.result.consensus.direction;
        accuracyScore = wasCorrect ? paul.confidence * 50 : 0;
      }

      return {
        paulId: paul.id,
        paulName: paul.name,
        paulEmoji: paul.emoji,
        prediction: paul.direction,
        confidence: paul.confidence,
        wasCorrect,
        accuracyScore,
      };
    });

    // Calculate overall accuracy score for this prediction
    const accuracyScore = resolution.status === 'correct' ? 100 : 
                         resolution.status === 'partial' ? 50 : 0;

    const updatedPrediction: HistoricalPrediction = {
      ...prediction,
      status: resolution.status,
      resolvedAt: new Date().toISOString(),
      actualOutcome: resolution.actualOutcome,
      outcomeNotes: resolution.outcomeNotes,
      accuracyScore,
      paulPerformances,
    };

    setPredictions(prev => 
      prev.map(p => p.id === id ? updatedPrediction : p)
    );

    return {
      predictionId: id,
      status: resolution.status,
      accuracyScore,
      paulPerformances,
      updatedStats: calculateOverallStats(
        predictions.map(p => p.id === id ? updatedPrediction : p)
      ),
    };
  }, [predictions]);

  // Update prediction notes
  const updateNotes = useCallback((id: string, notes: string): boolean => {
    setPredictions(prev =>
      prev.map(p =>
        p.id === id ? { ...p, outcomeNotes: notes } : p
      )
    );
    return true;
  }, []);

  // Filter and sort predictions
  const filterAndSort = useCallback((
    filter: PredictionFilter,
    sort: PredictionSort
  ): HistoricalPrediction[] => {
    let filtered = [...predictions];

    // Apply filters
    if (filter.searchQuery) {
      const query = filter.searchQuery.toLowerCase();
      filtered = filtered.filter(p =>
        p.question.toLowerCase().includes(query)
      );
    }

    if (filter.status !== 'all') {
      filtered = filtered.filter(p => p.status === filter.status);
    }

    if (filter.category !== 'all') {
      filtered = filtered.filter(p => p.category === filter.category);
    }

    if (filter.dateFrom) {
      filtered = filtered.filter(p => p.createdAt >= filter.dateFrom);
    }

    if (filter.dateTo) {
      filtered = filtered.filter(p => p.createdAt <= filter.dateTo);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sort.field) {
        case 'date':
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case 'question':
          comparison = a.question.localeCompare(b.question);
          break;
        case 'accuracy':
          const aAcc = a.accuracyScore ?? -1;
          const bAcc = b.accuracyScore ?? -1;
          comparison = aAcc - bAcc;
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'category':
          comparison = a.category.localeCompare(b.category);
          break;
      }

      return sort.direction === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [predictions]);

  // Get overall stats
  const getOverallStats = useCallback((): OverallAccuracyStats => {
    return calculateOverallStats(predictions);
  }, [predictions]);

  // Clear all history
  const clearHistory = useCallback((): void => {
    if (confirm('Are you sure you want to clear all prediction history? This cannot be undone.')) {
      setPredictions([]);
    }
  }, []);

  // Export history as JSON
  const exportHistory = useCallback((): string => {
    return JSON.stringify(predictions, null, 2);
  }, [predictions]);

  // Import history from JSON
  const importHistory = useCallback((json: string): boolean => {
    try {
      const imported = JSON.parse(json) as HistoricalPrediction[];
      if (Array.isArray(imported)) {
        setPredictions(imported);
        return true;
      }
      return false;
    } catch (e) {
      console.error('Failed to import history:', e);
      return false;
    }
  }, []);

  return {
    predictions,
    isLoaded,
    addPrediction,
    deletePrediction,
    getPrediction,
    resolvePrediction,
    updateNotes,
    filterAndSort,
    getOverallStats,
    clearHistory,
    exportHistory,
    importHistory,
  };
}

// Helper function to calculate overall stats
function calculateOverallStats(predictions: HistoricalPrediction[]): OverallAccuracyStats {
  const resolved = predictions.filter(p => p.status !== 'pending');
  const pending = predictions.filter(p => p.status === 'pending');

  const correct = resolved.filter(p => p.status === 'correct').length;
  const wrong = resolved.filter(p => p.status === 'wrong').length;
  const partial = resolved.filter(p => p.status === 'partial').length;

  // Calculate consensus accuracy (how often the Pauls' consensus was right)
  const consensusPredictions = resolved.filter(p => 
    p.paulPerformances && p.paulPerformances.length > 0
  );
  
  let consensusCorrect = 0;
  consensusPredictions.forEach(p => {
    if (p.status === 'correct') consensusCorrect++;
  });

  // Category stats
  const categoryStats: OverallAccuracyStats['categoryStats'] = {
    crypto: { correct: 0, wrong: 0, partial: 0, total: 0 },
    stocks: { correct: 0, wrong: 0, partial: 0, total: 0 },
    business: { correct: 0, wrong: 0, partial: 0, total: 0 },
    career: { correct: 0, wrong: 0, partial: 0, total: 0 },
    personal: { correct: 0, wrong: 0, partial: 0, total: 0 },
    politics: { correct: 0, wrong: 0, partial: 0, total: 0 },
    sports: { correct: 0, wrong: 0, partial: 0, total: 0 },
    other: { correct: 0, wrong: 0, partial: 0, total: 0 },
  };

  resolved.forEach(p => {
    const cat = categoryStats[p.category];
    cat.total++;
    if (p.status === 'correct') cat.correct++;
    else if (p.status === 'wrong') cat.wrong++;
    else if (p.status === 'partial') cat.partial++;
  });

  // Monthly stats
  const monthlyMap = new Map<string, { correct: number; wrong: number; partial: number; total: number }>();
  
  resolved.forEach(p => {
    const date = new Date(p.createdAt);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    
    if (!monthlyMap.has(monthKey)) {
      monthlyMap.set(monthKey, { correct: 0, wrong: 0, partial: 0, total: 0 });
    }
    
    const month = monthlyMap.get(monthKey)!;
    month.total++;
    if (p.status === 'correct') month.correct++;
    else if (p.status === 'wrong') month.wrong++;
    else if (p.status === 'partial') month.partial++;
  });

  const monthlyStats = Array.from(monthlyMap.entries())
    .map(([month, stats]) => ({
      month,
      monthLabel: new Date(month + '-01').toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
      ...stats,
      accuracy: stats.total > 0 ? (stats.correct + stats.partial * 0.5) / stats.total * 100 : 0,
    }))
    .sort((a, b) => a.month.localeCompare(b.month));

  return {
    totalPredictions: predictions.length,
    resolvedPredictions: resolved.length,
    pendingPredictions: pending.length,
    correctCount: correct,
    wrongCount: wrong,
    partialCount: partial,
    overallAccuracy: resolved.length > 0 ? (correct + partial * 0.5) / resolved.length * 100 : 0,
    categoryStats,
    monthlyStats,
    consensusCorrect,
    consensusTotal: consensusPredictions.length,
    consensusAccuracy: consensusPredictions.length > 0 ? consensusCorrect / consensusPredictions.length * 100 : 0,
  };
}
