/**
 * PredictionHistory Component
 * List of past predictions with search/filter/sort
 */

import React, { useState, useMemo } from 'react';
import type { HistoricalPrediction, PredictionFilter, PredictionSort, SortField, SortDirection } from '../types';
import { STATUS_LABELS, QUESTION_CATEGORIES } from '../types';
import { formatTimestamp, cn } from '../../../utils';

interface PredictionHistoryProps {
  predictions: HistoricalPrediction[];
  onSelect: (prediction: HistoricalPrediction) => void;
  onDelete: (id: string) => void;
  onResolve: (prediction: HistoricalPrediction) => void;
}

export const PredictionHistory: React.FC<PredictionHistoryProps> = ({
  predictions,
  onSelect,
  onDelete,
  onResolve,
}) => {
  const [filter, setFilter] = useState<PredictionFilter>({
    searchQuery: '',
    status: 'all',
    category: 'all',
  });
  
  const [sort, setSort] = useState<PredictionSort>({
    field: 'date',
    direction: 'desc',
  });

  const filteredPredictions = useMemo(() => {
    let filtered = [...predictions];

    // Search filter
    if (filter.searchQuery) {
      const query = filter.searchQuery.toLowerCase();
      filtered = filtered.filter(p =>
        p.question.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (filter.status !== 'all') {
      filtered = filtered.filter(p => p.status === filter.status);
    }

    // Category filter
    if (filter.category !== 'all') {
      filtered = filtered.filter(p => p.category === filter.category);
    }

    // Sort
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
  }, [predictions, filter, sort]);

  const handleSort = (field: SortField) => {
    setSort(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'desc' ? 'asc' : 'desc',
    }));
  };

  const getSortIcon = (field: SortField) => {
    if (sort.field !== field) return '↕️';
    return sort.direction === 'desc' ? '↓' : '↑';
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="glass-card p-4 space-y-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-gray-400 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search predictions..."
              value={filter.searchQuery}
              onChange={(e) => setFilter(prev => ({ ...prev, searchQuery: e.target.value }))}
              className="input-field"
            />
          </div>
          
          <div className="w-40">
            <label className="block text-sm text-gray-400 mb-1">Status</label>
            <select
              value={filter.status}
              onChange={(e) => setFilter(prev => ({ 
                ...prev, 
                status: e.target.value as PredictionFilter['status'] 
              }))}
              className="input-field"
            >
              <option value="all">All Status</option>
              <option value="pending">⏳ Pending</option>
              <option value="correct">✅ Correct</option>
              <option value="wrong">❌ Wrong</option>
              <option value="partial">⚡ Partial</option>
            </select>
          </div>
          
          <div className="w-40">
            <label className="block text-sm text-gray-400 mb-1">Category</label>
            <select
              value={filter.category}
              onChange={(e) => setFilter(prev => ({ 
                ...prev, 
                category: e.target.value as PredictionFilter['category'] 
              }))}
              className="input-field"
            >
              <option value="all">All Categories</option>
              {QUESTION_CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.emoji} {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>{filteredPredictions.length} prediction{filteredPredictions.length !== 1 ? 's' : ''}</span>
          <button
            onClick={() => {
              setFilter({ searchQuery: '', status: 'all', category: 'all' });
              setSort({ field: 'date', direction: 'desc' });
            }}
            className="text-accent-blue hover:underline"
          >
            Reset filters
          </button>
        </div>
      </div>

      {/* Predictions List */}
      <div className="space-y-2">
        {filteredPredictions.length === 0 ? (
          <div className="glass-card p-8 text-center text-gray-400">
            <p className="text-lg mb-2">📭 No predictions found</p>
            <p className="text-sm">Try adjusting your filters or make a new prediction</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="grid grid-cols-12 gap-4 px-4 py-2 text-sm text-gray-400 font-medium">
              <button 
                onClick={() => handleSort('question')}
                className="col-span-5 text-left hover:text-white flex items-center gap-2"
              >
                Question {getSortIcon('question')}
              </button>
              <button 
                onClick={() => handleSort('category')}
                className="col-span-2 text-left hover:text-white flex items-center gap-2"
              >
                Category {getSortIcon('category')}
              </button>
              <button 
                onClick={() => handleSort('status')}
                className="col-span-2 text-left hover:text-white flex items-center gap-2"
              >
                Status {getSortIcon('status')}
              </button>
              <button 
                onClick={() => handleSort('date')}
                className="col-span-2 text-left hover:text-white flex items-center gap-2"
              >
                Date {getSortIcon('date')}
              </button>
              <div className="col-span-1"></div>
            </div>

            {/* Rows */}
            {filteredPredictions.map((prediction) => {
              const statusConfig = STATUS_LABELS[prediction.status];
              const category = QUESTION_CATEGORIES.find(c => c.value === prediction.category);

              return (
                <div
                  key={prediction.id}
                  className="glass-card-hover p-4 grid grid-cols-12 gap-4 items-center cursor-pointer group"
                  onClick={() => onSelect(prediction)}
                >
                  <div className="col-span-5 truncate">
                    <p className="font-medium text-white truncate group-hover:text-accent-blue transition-colors">
                      {prediction.question}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {prediction.result.consensus.direction.toUpperCase()} • {prediction.result.consensus.confidence}% confidence
                    </p>
                  </div>

                  <div className="col-span-2">
                    <span className="inline-flex items-center gap-1 text-sm text-gray-300">
                      {category?.emoji} {category?.label}
                    </span>
                  </div>

                  <div className="col-span-2">
                    <span
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: `${statusConfig.color}20`,
                        color: statusConfig.color,
                      }}
                    >
                      {statusConfig.emoji} {statusConfig.label}
                    </span>
                  </div>

                  <div className="col-span-2 text-sm text-gray-400">
                    {formatTimestamp(prediction.createdAt)}
                  </div>

                  <div className="col-span-1 flex justify-end gap-2">
                    {prediction.status === 'pending' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onResolve(prediction);
                        }}
                        className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                        title="Resolve prediction"
                      >
                        ✓
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Delete this prediction?')) {
                          onDelete(prediction.id);
                        }
                      }}
                      className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors opacity-0 group-hover:opacity-100"
                      title="Delete prediction"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
};
