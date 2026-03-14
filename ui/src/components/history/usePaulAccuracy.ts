/**
 * usePaulAccuracy Hook
 * Tracks individual Paul accuracy statistics
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import type { PaulAccuracyStats, QuestionCategory, HistoricalPrediction } from './types';

const ACCURACY_STORAGE_KEY = 'swimming-pauls-accuracy';

// Default Pauls configuration
const DEFAULT_PAULS: { id: string; name: string; emoji: string; type: string }[] = [
  { id: 'analyst', name: 'Analyst Paul', emoji: '📊', type: 'Data-driven' },
  { id: 'trader', name: 'Trader Paul', emoji: '📈', type: 'Market timing' },
  { id: 'visionary', name: 'Visionary Paul', emoji: '🔮', type: 'Long-term' },
  { id: 'skeptic', name: 'Skeptic Paul', emoji: '🤨', type: 'Contrarian' },
  { id: 'producer', name: 'Producer Paul', emoji: '💰', type: 'Budget-focused' },
  { id: 'director', name: 'Director Paul', emoji: '🎬', type: 'Creative' },
  { id: 'hedgie', name: 'Hedgie Paul', emoji: '🛡️', type: 'Risk-aware' },
  { id: 'entrepreneur', name: 'Entrepreneur Paul', emoji: '🚀', type: 'Innovation' },
];

export function usePaulAccuracy(predictions: HistoricalPrediction[]) {
  const [paulStats, setPaulStats] = useState<Record<string, PaulAccuracyStats>>({});
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(ACCURACY_STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setPaulStats(parsed);
      } catch (e) {
        console.error('Failed to parse Paul accuracy:', e);
      }
    }
    setIsLoaded(true);
  }, []);

  // Save to localStorage when stats change
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(ACCURACY_STORAGE_KEY, JSON.stringify(paulStats));
    }
  }, [paulStats, isLoaded]);

  // Recalculate stats when predictions change
  useEffect(() => {
    if (!isLoaded) return;

    const stats: Record<string, PaulAccuracyStats> = {};

    // Initialize with default Pauls
    DEFAULT_PAULS.forEach(paul => {
      stats[paul.id] = {
        paulId: paul.id,
        paulName: paul.name,
        paulEmoji: paul.emoji,
        paulType: paul.type,
        totalPredictions: 0,
        correctPredictions: 0,
        wrongPredictions: 0,
        partialPredictions: 0,
        accuracyPercentage: 0,
        bullishCorrect: 0,
        bullishTotal: 0,
        bearishCorrect: 0,
        bearishTotal: 0,
        neutralCorrect: 0,
        neutralTotal: 0,
        categoryAccuracy: {
          crypto: { correct: 0, total: 0 },
          stocks: { correct: 0, total: 0 },
          business: { correct: 0, total: 0 },
          career: { correct: 0, total: 0 },
          personal: { correct: 0, total: 0 },
          politics: { correct: 0, total: 0 },
          sports: { correct: 0, total: 0 },
          other: { correct: 0, total: 0 },
        },
        recentTrend: [],
        avgConfidenceWhenCorrect: 0,
        avgConfidenceWhenWrong: 0,
      };
    });

    // Process all resolved predictions
    const resolvedPredictions = predictions.filter(p => p.status !== 'pending');
    
    resolvedPredictions.forEach(prediction => {
      const category = prediction.category;
      
      prediction.paulPerformances?.forEach(perf => {
        if (!stats[perf.paulId]) {
          // Create stats for custom Paul
          stats[perf.paulId] = {
            paulId: perf.paulId,
            paulName: perf.paulName,
            paulEmoji: perf.paulEmoji,
            paulType: 'Custom',
            totalPredictions: 0,
            correctPredictions: 0,
            wrongPredictions: 0,
            partialPredictions: 0,
            accuracyPercentage: 0,
            bullishCorrect: 0,
            bullishTotal: 0,
            bearishCorrect: 0,
            bearishTotal: 0,
            neutralCorrect: 0,
            neutralTotal: 0,
            categoryAccuracy: {
              crypto: { correct: 0, total: 0 },
              stocks: { correct: 0, total: 0 },
              business: { correct: 0, total: 0 },
              career: { correct: 0, total: 0 },
              personal: { correct: 0, total: 0 },
              politics: { correct: 0, total: 0 },
              sports: { correct: 0, total: 0 },
              other: { correct: 0, total: 0 },
            },
            recentTrend: [],
            avgConfidenceWhenCorrect: 0,
            avgConfidenceWhenWrong: 0,
          };
        }

        const paulStat = stats[perf.paulId];
        paulStat.totalPredictions++;

        // Track by direction
        if (perf.prediction === 'bullish') {
          paulStat.bullishTotal++;
          if (perf.wasCorrect) paulStat.bullishCorrect++;
        } else if (perf.prediction === 'bearish') {
          paulStat.bearishTotal++;
          if (perf.wasCorrect) paulStat.bearishCorrect++;
        } else {
          paulStat.neutralTotal++;
          if (perf.wasCorrect) paulStat.neutralCorrect++;
        }

        // Track by result
        if (prediction.status === 'correct' && perf.wasCorrect) {
          paulStat.correctPredictions++;
        } else if (prediction.status === 'wrong' && !perf.wasCorrect) {
          paulStat.wrongPredictions++;
        } else if (prediction.status === 'partial') {
          paulStat.partialPredictions++;
        }

        // Track by category
        paulStat.categoryAccuracy[category].total++;
        if (perf.wasCorrect) {
          paulStat.categoryAccuracy[category].correct++;
        }

        // Add to recent trend (keep last 10)
        const trendEntry: 'correct' | 'wrong' | 'partial' = 
          prediction.status === 'correct' && perf.wasCorrect ? 'correct' :
          prediction.status === 'wrong' && !perf.wasCorrect ? 'wrong' :
          'partial';
        
        paulStat.recentTrend.push(trendEntry);
        if (paulStat.recentTrend.length > 10) {
          paulStat.recentTrend.shift();
        }
      });
    });

    // Calculate percentages and averages
    Object.values(stats).forEach(stat => {
      if (stat.totalPredictions > 0) {
        stat.accuracyPercentage = 
          (stat.correctPredictions + stat.partialPredictions * 0.5) / stat.totalPredictions * 100;
      }

      // Calculate average confidence when correct/wrong
      let correctConfidenceSum = 0;
      let correctCount = 0;
      let wrongConfidenceSum = 0;
      let wrongCount = 0;

      resolvedPredictions.forEach(pred => {
        pred.paulPerformances?.forEach(perf => {
          if (perf.paulId === stat.paulId) {
            if (perf.wasCorrect) {
              correctConfidenceSum += perf.confidence;
              correctCount++;
            } else {
              wrongConfidenceSum += perf.confidence;
              wrongCount++;
            }
          }
        });
      });

      if (correctCount > 0) {
        stat.avgConfidenceWhenCorrect = correctConfidenceSum / correctCount;
      }
      if (wrongCount > 0) {
        stat.avgConfidenceWhenWrong = wrongConfidenceSum / wrongCount;
      }
    });

    setPaulStats(stats);
  }, [predictions, isLoaded]);

  // Get all Paul stats sorted by accuracy
  const getAllPaulStats = useCallback((): PaulAccuracyStats[] => {
    return Object.values(paulStats).sort((a, b) => 
      b.accuracyPercentage - a.accuracyPercentage
    );
  }, [paulStats]);

  // Get a specific Paul's stats
  const getPaulStats = useCallback((paulId: string): PaulAccuracyStats | undefined => {
    return paulStats[paulId];
  }, [paulStats]);

  // Get leaderboard (top N Pauls)
  const getLeaderboard = useCallback((limit: number = 10): PaulAccuracyStats[] => {
    return getAllPaulStats().slice(0, limit);
  }, [getAllPaulStats]);

  // Get accuracy by category for a Paul
  const getCategoryAccuracy = useCallback((
    paulId: string, 
    category: QuestionCategory
  ): { correct: number; total: number; percentage: number } => {
    const stats = paulStats[paulId];
    if (!stats) return { correct: 0, total: 0, percentage: 0 };

    const catStats = stats.categoryAccuracy[category];
    return {
      ...catStats,
      percentage: catStats.total > 0 ? catStats.correct / catStats.total * 100 : 0,
    };
  }, [paulStats]);

  // Get accuracy by direction
  const getDirectionAccuracy = useCallback((paulId: string): {
    bullish: { correct: number; total: number; percentage: number };
    bearish: { correct: number; total: number; percentage: number };
    neutral: { correct: number; total: number; percentage: number };
  } => {
    const stats = paulStats[paulId];
    if (!stats) {
      return {
        bullish: { correct: 0, total: 0, percentage: 0 },
        bearish: { correct: 0, total: 0, percentage: 0 },
        neutral: { correct: 0, total: 0, percentage: 0 },
      };
    }

    return {
      bullish: {
        correct: stats.bullishCorrect,
        total: stats.bullishTotal,
        percentage: stats.bullishTotal > 0 ? stats.bullishCorrect / stats.bullishTotal * 100 : 0,
      },
      bearish: {
        correct: stats.bearishCorrect,
        total: stats.bearishTotal,
        percentage: stats.bearishTotal > 0 ? stats.bearishCorrect / stats.bearishTotal * 100 : 0,
      },
      neutral: {
        correct: stats.neutralCorrect,
        total: stats.neutralTotal,
        percentage: stats.neutralTotal > 0 ? stats.neutralCorrect / stats.neutralTotal * 100 : 0,
      },
    };
  }, [paulStats]);

  // Reset all stats
  const resetStats = useCallback((): void => {
    if (confirm('Are you sure you want to reset all Paul accuracy statistics?')) {
      setPaulStats({});
    }
  }, []);

  return {
    paulStats,
    isLoaded,
    getAllPaulStats,
    getPaulStats,
    getLeaderboard,
    getCategoryAccuracy,
    getDirectionAccuracy,
    resetStats,
  };
}
