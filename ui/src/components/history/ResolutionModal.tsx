/**
 * ResolutionModal Component
 * Modal for marking predictions as resolved and entering actual outcome
 */

import React, { useState } from 'react';
import type { HistoricalPrediction, ResolutionInput, PredictionStatus } from '../types';
import { STATUS_LABELS } from '../types';
import { cn } from '../../../utils';

interface ResolutionModalProps {
  prediction: HistoricalPrediction;
  onClose: () => void;
  onResolve: (resolution: ResolutionInput) => void;
}

export const ResolutionModal: React.FC<ResolutionModalProps> = ({
  prediction,
  onClose,
  onResolve,
}) => {
  const [status, setStatus] = useState<PredictionStatus>('correct');
  const [actualOutcome, setActualOutcome] = useState('');
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    const newErrors: Record<string, string> = {};
    
    if (!actualOutcome.trim()) {
      newErrors.outcome = 'Please describe the actual outcome';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onResolve({
      status,
      actualOutcome: actualOutcome.trim(),
      outcomeNotes: notes.trim() || undefined,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">Resolve Prediction</h2>
            <button 
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-dark-700 transition-colors"
            >
              ✕
            </button>
          </div>

          <div className="mb-6 p-4 rounded-xl bg-dark-700/50">
            <p className="text-sm text-gray-400 mb-1">Question</p>
            <p className="font-medium">{prediction.question}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Status Selection */}
            <div>
              <label className="block text-sm text-gray-400 mb-3">How did the Pauls do?</label>
              
              <div className="grid grid-cols-3 gap-3">
                {(['correct', 'wrong', 'partial'] as PredictionStatus[]).map((s) => {
                  const config = STATUS_LABELS[s];
                  
                  return (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setStatus(s)}
                      className={cn(
                        "p-3 rounded-xl border-2 text-center transition-all",
                        status === s
                          ? "border-accent-blue bg-accent-blue/10"
                          : "border-dark-600 hover:border-dark-500"
                      )}
                    >
                      <span className="text-2xl block mb-1">{config.emoji}</span>
                      <span className="text-sm font-medium">{config.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Actual Outcome */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                What actually happened?
              </label>
              <input
                type="text"
                value={actualOutcome}
                onChange={(e) => {
                  setActualOutcome(e.target.value);
                  setErrors(prev => ({ ...prev, outcome: '' }));
                }}
                placeholder="e.g., Bitcoin reached $105k, Project was cancelled"
                className={cn(
                  "input-field",
                  errors.outcome && "border-red-500 focus:border-red-500"
                )}
              />
              {errors.outcome && (
                <p className="text-sm text-red-400 mt-1">{errors.outcome}</p>
              )}
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any additional context about the outcome..."
                className="input-field min-h-[100px]"
              />
            </div>

            {/* Preview */}
            <div className="p-4 rounded-xl bg-dark-700/50">
              <p className="text-sm text-gray-400 mb-2">Preview:</p>
              
              <div className="space-y-2">
                <p>
                  {STATUS_LABELS[status].emoji} The Pauls were{' '}
                  <span style={{ color: STATUS_LABELS[status].color }}>
                    {status.toUpperCase()}
                  </span>
                  {' '}about
                </p>
                <p className="text-sm text-gray-300 italic">"{prediction.question}"</p>
                
                {actualOutcome && (
                  <p className="text-sm">
                    Actual outcome: {actualOutcome}
                  </p>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              
              <button
                type="submit"
                className="btn-primary flex-1"
              >
                Resolve Prediction
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
