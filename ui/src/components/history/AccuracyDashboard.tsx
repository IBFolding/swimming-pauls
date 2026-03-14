/**
 * AccuracyDashboard Component
 * Shows overall accuracy stats, Paul leaderboard, and win/loss charts
 */

import React, { useMemo } from 'react';
import type { OverallAccuracyStats, PaulAccuracyStats, QuestionCategory } from '../types';
import { QUESTION_CATEGORIES } from '../types';
import { cn } from '../../../utils';

interface AccuracyDashboardProps {
  stats: OverallAccuracyStats;
  paulStats: PaulAccuracyStats[];
  onCategoryClick?: (category: QuestionCategory) => void;
}

export const AccuracyDashboard: React.FC<AccuracyDashboardProps> = ({
  stats,
  paulStats,
  onCategoryClick,
}) => {
  const winLossData = useMemo(() => {
    if (stats.monthlyStats.length === 0) return [];
    
    return stats.monthlyStats.map(m => ({
      ...m,
      winRate: m.total > 0 ? (m.correct / m.total) * 100 : 0,
    }));
  }, [stats.monthlyStats]);

  const maxMonthlyTotal = useMemo(() => {
    if (stats.monthlyStats.length === 0) return 1;
    return Math.max(...stats.monthlyStats.map(m => m.total));
  }, [stats.monthlyStats]);

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">Total Predictions</p>
          <p className="text-3xl font-bold">{stats.totalPredictions}</p>
        </div>
        
        <div className="glass-card p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">Resolved</p>
          <p className="text-3xl font-bold text-blue-400">{stats.resolvedPredictions}</p>
        </div>
        
        <div className="glass-card p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">Pending</p>
          <p className="text-3xl font-bold text-yellow-400">{stats.pendingPredictions}</p>
        </div>
        
        <div className="glass-card p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">Overall Accuracy</p>
          <p className={cn(
            "text-3xl font-bold",
            stats.overallAccuracy >= 60 ? "text-green-400" : 
            stats.overallAccuracy >= 40 ? "text-yellow-400" : "text-red-400"
          )}>
            {stats.overallAccuracy.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Win/Loss Breakdown */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold mb-4">📊 Results Breakdown</h3>
          
          <div className="space-y-4">
            {/* Correct */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-green-400">✅ Correct</span>
                <span>{stats.correctCount}</span>
              </div>
              <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full"
                  style={{ 
                    width: `${stats.resolvedPredictions > 0 ? (stats.correctCount / stats.resolvedPredictions) * 100 : 0}%` 
                  }}
                />
              </div>
            </div>

            {/* Wrong */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-red-400">❌ Wrong</span>
                <span>{stats.wrongCount}</span>
              </div>
              <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full"
                  style={{ 
                    width: `${stats.resolvedPredictions > 0 ? (stats.wrongCount / stats.resolvedPredictions) * 100 : 0}%` 
                  }}
                />
              </div>
            </div>

            {/* Partial */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-orange-400">⚡ Partial</span>
                <span>{stats.partialCount}</span>
              </div>
              <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-orange-500 rounded-full"
                  style={{ 
                    width: `${stats.resolvedPredictions > 0 ? (stats.partialCount / stats.resolvedPredictions) * 100 : 0}%` 
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Consensus Accuracy */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold mb-4">🎯 Consensus Accuracy</h3>
          
          <div className="text-center py-4">
            <div className="inline-block relative">
              <svg viewBox="0 0 100 100" className="w-32 h-32">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#1a1a25"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke={stats.consensusAccuracy >= 60 ? '#4ade80' : stats.consensusAccuracy >= 40 ? '#fbbf24' : '#ef4444'}
                  strokeWidth="8"
                  strokeDasharray={`${stats.consensusAccuracy * 2.51} 251`}
                  strokeDashoffset="0"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={cn(
                  "text-2xl font-bold",
                  stats.consensusAccuracy >= 60 ? "text-green-400" : 
                  stats.consensusAccuracy >= 40 ? "text-yellow-400" : "text-red-400"
                )}>
                  {stats.consensusAccuracy.toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
          
          <p className="text-center text-sm text-gray-400">
            {stats.consensusCorrect}/{stats.consensusTotal} consensus predictions correct
          </p>
        </div>
      </div>

      {/* Monthly Chart */}
      {winLossData.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold mb-4">📈 Win/Loss Over Time</h3>
          
          <div className="space-y-4">
            <div className="flex gap-4 text-sm">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-green-500 rounded"></span> Correct
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-red-500 rounded"></span> Wrong
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-orange-500 rounded"></span> Partial
              </span>
            </div>

            <div className="flex items-end gap-2 h-48 overflow-x-auto">
              {winLossData.map((month) => (
                <div 
                  key={month.month} 
                  className="flex-1 min-w-[60px] flex flex-col items-center gap-1"
                >
                  <div className="w-full flex flex-col-reverse gap-0.5">
                    {month.correct > 0 && (
                      <div 
                        className="w-full bg-green-500 rounded-t"
                        style={{ 
                          height: `${(month.correct / maxMonthlyTotal) * 160}px`,
                          minHeight: month.correct > 0 ? '4px' : '0'
                        }}
                        title={`${month.correct} correct`}
                      />
                    )}
                    {month.partial > 0 && (
                      <div 
                        className="w-full bg-orange-500"
                        style={{ 
                          height: `${(month.partial / maxMonthlyTotal) * 160}px`,
                          minHeight: month.partial > 0 ? '4px' : '0'
                        }}
                        title={`${month.partial} partial`}
                      />
                    )}
                    {month.wrong > 0 && (
                      <div 
                        className="w-full bg-red-500 rounded-b"
                        style={{ 
                          height: `${(month.wrong / maxMonthlyTotal) * 160}px`,
                          minHeight: month.wrong > 0 ? '4px' : '0'
                        }}
                        title={`${month.wrong} wrong`}
                      />
                    )}
                  </div>
                  
                  <span className="text-xs text-gray-500">{month.monthLabel}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Paul Leaderboard */}
      {paulStats.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold mb-4">🏆 Paul Leaderboard</h3>
          
          <div className="space-y-3">
            {paulStats.slice(0, 10).map((paul, idx) => {
              const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx + 1}.`;
              
              return (
                <div 
                  key={paul.paulId}
                  className="flex items-center gap-4 p-3 rounded-xl bg-dark-700/50"
                >
                  <span className="text-xl w-8">{medal}</span>
                  
                  <span className="text-2xl">{paul.paulEmoji}</span>
                  
                  <div className="flex-1">
                    <p className="font-medium">{paul.paulName}</p>
                    <p className="text-sm text-gray-400">{paul.paulType}</p>
                  </div>
                  
                  <div className="text-right">
                    <p className={cn(
                      "text-xl font-bold",
                      paul.accuracyPercentage >= 60 ? "text-green-400" :
                      paul.accuracyPercentage >= 40 ? "text-yellow-400" : "text-red-400"
                    )}>
                      {paul.accuracyPercentage.toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-400">
                      {paul.correctPredictions}/{paul.totalPredictions}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Accuracy by Category */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-bold mb-4">📂 Accuracy by Category</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {QUESTION_CATEGORIES.map((cat) => {
            const catStats = stats.categoryStats[cat.value];
            const hasData = catStats.total > 0;
            const accuracy = hasData 
              ? ((catStats.correct + catStats.partial * 0.5) / catStats.total) * 100 
              : 0;

            return (
              <button
                key={cat.value}
                onClick={() => onCategoryClick?.(cat.value)}
                className={cn(
                  "p-4 rounded-xl text-center transition-colors",
                  hasData ? "bg-dark-700 hover:bg-dark-600" : "bg-dark-800 opacity-50"
                )}
                disabled={!hasData}
              >
                <span className="text-2xl">{cat.emoji}</span>
                <p className="font-medium mt-2">{cat.label}</p>
                
                {hasData ? (
                  <p className={cn(
                    "text-lg font-bold",
                    accuracy >= 60 ? "text-green-400" :
                    accuracy >= 40 ? "text-yellow-400" : "text-red-400"
                  )}
                  >
                    {accuracy.toFixed(0)}%
                  </p>
                ) : (
                  <p className="text-sm text-gray-500">No data</p>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
