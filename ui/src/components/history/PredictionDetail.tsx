/**
 * PredictionDetail Component
 * Shows full prediction results, timeline, and Paul performance
 */

import React, { useState } from 'react';
import type { HistoricalPrediction, PredictionNote } from '../types';
import { STATUS_LABELS, QUESTION_CATEGORIES } from '../types';
import { formatTimestamp, cn } from '../../../utils';
import { getDirectionColor, getDirectionGradient } from '../../../utils/resultsHelpers';

interface PredictionDetailProps {
  prediction: HistoricalPrediction;
  onBack: () => void;
  onResolve: (prediction: HistoricalPrediction) => void;
  onUpdateNotes: (notes: string) => void;
}

export const PredictionDetail: React.FC<PredictionDetailProps> = ({
  prediction,
  onBack,
  onResolve,
  onUpdateNotes,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'pauls' | 'notes'>('overview');
  const [notes, setNotes] = useState(prediction.outcomeNotes || '');
  const [isEditingNotes, setIsEditingNotes] = useState(false);

  const statusConfig = STATUS_LABELS[prediction.status];
  const category = QUESTION_CATEGORIES.find(c => c.value === prediction.category);

  const handleSaveNotes = () => {
    onUpdateNotes(notes);
    setIsEditingNotes(false);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={onBack} className="btn-secondary">
          ← Back
        </button>
        <div className="flex-1">
          <h2 className="text-xl font-bold">Prediction Details</h2>
        </div>
        
        {prediction.status === 'pending' && (
          <button 
            onClick={() => onResolve(prediction)}
            className="btn-primary"
          >
            Resolve Prediction
          </button>
        )}
      </div>

      {/* Question Card */}
      <div className="glass-card p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p className="text-sm text-gray-400 mb-2">Question</p>
            <h1 className="text-2xl font-bold mb-4">{prediction.question}</h1>
            
            <div className="flex flex-wrap gap-4 text-sm">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-700">
                {category?.emoji} {category?.label}
              </span>
              
              <span 
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full"
                style={{
                  backgroundColor: `${statusConfig.color}20`,
                  color: statusConfig.color,
                }}
              >
                {statusConfig.emoji} {statusConfig.label}
              </span>
              
              <span className="text-gray-400">
                📅 Created {formatTimestamp(prediction.createdAt)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-600 pb-2">
        {(['overview', 'timeline', 'pauls', 'notes'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === tab
                ? 'bg-accent-blue text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-700'
            )}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Consensus Result */}
            <div 
              className="p-6 rounded-2xl text-center"
              style={{ background: getDirectionGradient(prediction.result.consensus.direction) }}
            >
              <p className="text-sm opacity-80 mb-2">Consensus</p>
              <h2 className="text-4xl font-bold mb-2">
                {prediction.result.consensus.direction.toUpperCase()}
              </h2>
              <p className="text-lg">
                {prediction.result.consensus.confidence}% confidence
              </p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="glass-card p-4 text-center">
                <p className="text-sm text-gray-400 mb-1">Rounds</p>
                <p className="text-2xl font-bold">{prediction.result.rounds.length}</p>
              </div>
              
              <div className="glass-card p-4 text-center">
                <p className="text-sm text-gray-400 mb-1">Pauls</p>
                <p className="text-2xl font-bold">{prediction.result.pauls.length}</p>
              </div>
              
              

              {prediction.status !== 'pending' && (
                <>
                  <div className="glass-card p-4 text-center">
                    <p className="text-sm text-gray-400 mb-1">Accuracy Score</p>
                    <p className="text-2xl font-bold" style={{ color: statusConfig.color }}>
                      {prediction.accuracyScore}%
                    </p>
                  </div>
                  
                  <div className="glass-card p-4 text-center">
                    <p className="text-sm text-gray-400 mb-1">Pauls Correct</p>
                    <p className="text-2xl font-bold">
                      {prediction.paulPerformances?.filter(p => p.wasCorrect).length || 0}/{prediction.paulPerformances?.length || 0}
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Actual Outcome (if resolved) */}
            {prediction.status !== 'pending' && (
              <div className="glass-card p-6">
                <h3 className="text-lg font-bold mb-4">Resolution</h3>
                
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-400">Actual Outcome</p>
                    <p className="text-lg">{prediction.actualOutcome || 'Not specified'}</p>
                  </div>
                  
                  {prediction.resolvedAt && (
                    <div>
                      <p className="text-sm text-gray-400">Resolved</p>
                      <p>{formatTimestamp(prediction.resolvedAt)}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Insights */}
            {prediction.result.insights.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="text-lg font-bold mb-4">💡 Key Insights</h3>
                
                <div className="space-y-3">
                  {prediction.result.insights.map((insight, idx) => (
                    <div key={idx} className="flex gap-3">
                      <span className={cn(
                        'w-2 h-2 rounded-full mt-2 shrink-0',
                        insight.type === 'opportunity' && 'bg-green-500',
                        insight.type === 'risk' && 'bg-red-500',
                        insight.type === 'factor' && 'bg-blue-500'
                      )}></span>
                      <div>
                        <p className="font-medium">{insight.title}</p>
                        <p className="text-sm text-gray-400">{insight.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold mb-6">📊 Debate Timeline</h3>
            
            <div className="space-y-6">
              {/* Created */}
              <div className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-3 h-3 rounded-full bg-accent-blue"></div>
                  <div className="w-0.5 flex-1 bg-dark-600"></div>
                </div>
                <div className="pb-6">
                  <p className="font-medium">Prediction Created</p>
                  <p className="text-sm text-gray-400">{formatTimestamp(prediction.createdAt)}</p>
                </div>
              </div>

              {/* Rounds */}
              {prediction.result.rounds.map((round, idx) => (
                <div key={idx} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getDirectionColor(round.direction) }}
                    ></div>
                    {idx < prediction.result.rounds.length - 1 && (
                      <div className="w-0.5 flex-1 bg-dark-600"></div>
                    )}
                  </div>
                  
                  <div className={cn("pb-6", idx === prediction.result.rounds.length - 1 && 'pb-0')}>
                    <p className="font-medium">Round {round.round}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span 
                        className="text-sm px-2 py-0.5 rounded"
                        style={{ 
                          backgroundColor: `${getDirectionColor(round.direction)}20`,
                          color: getDirectionColor(round.direction)
                        }}
                      >
                        {round.direction.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-400">
                        {round.confidence}% confidence • {round.strength}
                      </span>
                    </div>
                    
                    {round.shifts.length > 0 && (
                      <p className="text-sm text-gray-500 mt-2">
                        Shifts: {round.shifts.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              ))}

              {/* Resolution (if resolved) */}
              {prediction.status !== 'pending' && prediction.resolvedAt && (
                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: statusConfig.color }}
                    ></div>
                  </div>
                  
                  <div>
                    <p className="font-medium">Resolved: {statusConfig.label}</p>
                    <p className="text-sm text-gray-400">{formatTimestamp(prediction.resolvedAt)}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'pauls' && (
          <div className="space-y-4">
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold mb-4">🐟 Paul Performances</h3>
              
              <div className="space-y-3">
                {prediction.result.pauls.map((paul) => {
                  const performance = prediction.paulPerformances?.find(
                    p => p.paulId === paul.id
                  );

                  return (
                    <div 
                      key={paul.id} 
                      className={cn(
                        "p-4 rounded-xl border",
                        performance?.wasCorrect && "border-green-500/30 bg-green-500/10",
                        !performance?.wasCorrect && prediction.status !== 'pending' && "border-red-500/30 bg-red-500/10",
                        prediction.status === 'pending' && "border-dark-600 bg-dark-700/50"
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{paul.emoji}</span>
                          <div>
                            <p className="font-medium">{paul.name}</p>
                            <p className="text-sm text-gray-400">{paul.type}</p>
                          </div>
                        </div>

                        <div className="text-right">
                          <p 
                            className="font-bold"
                            style={{ color: getDirectionColor(paul.direction) }}
                          >
                            {paul.direction.toUpperCase()}
                          </p>
                          <p className="text-sm text-gray-400">{paul.confidence}% confidence</p>
                        </div>
                      </div>

                      {prediction.status !== 'pending' && performance && (
                        <div className="mt-3 pt-3 border-t border-dark-600">
                          <div className="flex items-center justify-between">
                            <span className={cn(
                              "text-sm font-medium",
                              performance.wasCorrect ? "text-green-400" : "text-red-400"
                            )}>
                              {performance.wasCorrect ? '✓ Correct' : '✗ Incorrect'}
                            </span>
                            
                            <span className="text-sm text-gray-400">
                              Score: {performance.accuracyScore.toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notes' && (
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">📝 Notes</h3>
              
              {!isEditingNotes ? (
                <button 
                  onClick={() => setIsEditingNotes(true)}
                  className="btn-secondary text-sm"
                >
                  Edit
                </button>
              ) : (
                <div className="flex gap-2">
                  <button 
                    onClick={handleSaveNotes}
                    className="btn-primary text-sm"
                  >
                    Save
                  </button>
                  <button 
                    onClick={() => {
                      setNotes(prediction.outcomeNotes || '');
                      setIsEditingNotes(false);
                    }}
                    className="btn-secondary text-sm"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            {isEditingNotes ? (
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add notes about this prediction..."
                className="input-field min-h-[200px]"
              />
            ) : (
              <div className="min-h-[200px] p-4 rounded-xl bg-dark-900/50">
                {prediction.outcomeNotes ? (
                  <p className="whitespace-pre-wrap">{prediction.outcomeNotes}</p>
                ) : (
                  <p className="text-gray-500 italic">No notes added yet...</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
