/**
 * HistoryPage Component
 * Main container for prediction history and tracking
 */

import React, { useState, useEffect } from 'react';
import { usePredictionHistory } from './usePredictionHistory';
import { usePaulAccuracy } from './usePaulAccuracy';
import { useTelegramIntegration } from './useTelegramIntegration';
import { PredictionHistory } from './PredictionHistory';
import { PredictionDetail } from './PredictionDetail';
import { AccuracyDashboard } from './AccuracyDashboard';
import { ResolutionModal } from './ResolutionModal';
import { TelegramSettingsPanel } from './TelegramSettings';
import type { HistoricalPrediction, ResolutionInput, QuestionCategory } from './types';
import { cn } from '../../utils';

type View = 'list' | 'detail' | 'dashboard' | 'settings';

export const HistoryPage: React.FC = () => {
  const [view, setView] = useState<View>('list');
  const [selectedPrediction, setSelectedPrediction] = useState<HistoricalPrediction | null>(null);
  const [resolvingPrediction, setResolvingPrediction] = useState<HistoricalPrediction | null>(null);

  const {
    predictions,
    isLoaded: historyLoaded,
    deletePrediction,
    getPrediction,
    resolvePrediction,
    updateNotes,
    getOverallStats,
    clearHistory,
    exportHistory,
    importHistory,
  } = usePredictionHistory();

  const {
    getAllPaulStats,
    resetStats: resetPaulStats,
  } = usePaulAccuracy(predictions);

  const {
    settings: telegramSettings,
    notifications: telegramNotifications,
    isTesting: telegramTesting,
    testResult: telegramTestResult,
    updateSettings: updateTelegramSettings,
    testConnection: testTelegramConnection,
    sendNotification,
    clearNotificationHistory,
    resetSettings: resetTelegramSettings,
  } = useTelegramIntegration();

  const handleSelectPrediction = (prediction: HistoricalPrediction) => {
    setSelectedPrediction(prediction);
    setView('detail');
  };

  const handleBack = () => {
    setSelectedPrediction(null);
    setView('list');
  };

  const handleResolve = (prediction: HistoricalPrediction) => {
    setResolvingPrediction(prediction);
  };

  const handleResolveSubmit = async (resolution: ResolutionInput) => {
    if (!resolvingPrediction) return;

    const result = resolvePrediction(resolvingPrediction.id, resolution);
    
    if (result) {
      // Send Telegram notification if enabled
      if (telegramSettings.enabled) {
        const updatedPrediction = getPrediction(resolvingPrediction.id);
        if (updatedPrediction) {
          await sendNotification(updatedPrediction);
        }
      }

      setResolvingPrediction(null);
      
      // Refresh detail view if viewing the resolved prediction
      if (selectedPrediction?.id === resolvingPrediction.id) {
        const updated = getPrediction(resolvingPrediction.id);
        if (updated) {
          setSelectedPrediction(updated);
        }
      }
    }
  };

  const handleUpdateNotes = (notes: string) => {
    if (selectedPrediction) {
      updateNotes(selectedPrediction.id, notes);
    }
  };

  const handleCategoryClick = (category: QuestionCategory) => {
    // Could filter by category in the future
    console.log('Category clicked:', category);
  };

  const handleExport = () => {
    const data = exportHistory();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `swimming-pauls-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        if (importHistory(content)) {
          alert('History imported successfully!');
        } else {
          alert('Failed to import history. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }
    e.target.value = '';
  };

  if (!historyLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-accent-blue/30 border-t-accent-blue rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">📜 Prediction History</h1>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setView('list')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              view === 'list' ? "bg-accent-blue text-white" : "bg-dark-700 text-gray-300 hover:text-white"
            )}
          >
            📋 List
          </button>
          
          <button
            onClick={() => setView('dashboard')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              view === 'dashboard' ? "bg-accent-blue text-white" : "bg-dark-700 text-gray-300 hover:text-white"
            )}
          >
            📊 Dashboard
          </button>
          
          <button
            onClick={() => setView('settings')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              view === 'settings' ? "bg-accent-blue text-white" : "bg-dark-700 text-gray-300 hover:text-white"
            )}
          >
            ⚙️ Settings
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      {view !== 'detail' && (
        <div className="grid grid-cols-4 gap-4">
          <div className="glass-card p-3 text-center">
            <p className="text-xs text-gray-400">Total</p>
            <p className="text-xl font-bold">{predictions.length}</p>
          </div>
          
          <div className="glass-card p-3 text-center">
            <p className="text-xs text-gray-400">Resolved</p>
            <p className="text-xl font-bold text-blue-400">{predictions.filter(p => p.status !== 'pending').length}</p>
          </div>
          
          <div className="glass-card p-3 text-center">
            <p className="text-xs text-gray-400">Pending</p>
            <p className="text-xl font-bold text-yellow-400">{predictions.filter(p => p.status === 'pending').length}</p>
          </div>
          
          <div className="glass-card p-3 text-center">
            <p className="text-xs text-gray-400">Accuracy</p>
            <p className="text-xl font-bold text-green-400">
              {getOverallStats().overallAccuracy.toFixed(0)}%
            </p>
          </div>
        </div>
      )}

      {/* Content */}
      <div>
        {view === 'list' && (
          <PredictionHistory
            predictions={predictions}
            onSelect={handleSelectPrediction}
            onDelete={deletePrediction}
            onResolve={handleResolve}
          />
        )}

        {view === 'detail' && selectedPrediction && (
          <PredictionDetail
            prediction={selectedPrediction}
            onBack={handleBack}
            onResolve={handleResolve}
            onUpdateNotes={handleUpdateNotes}
          />
        )}

        {view === 'dashboard' && (
          <AccuracyDashboard
            stats={getOverallStats()}
            paulStats={getAllPaulStats()}
            onCategoryClick={handleCategoryClick}
          />
        )}

        {view === 'settings' && (
          <div className="space-y-6">
            <TelegramSettingsPanel
              settings={telegramSettings}
              notifications={telegramNotifications}
              isTesting={telegramTesting}
              testResult={telegramTestResult}
              onUpdateSettings={updateTelegramSettings}
              onTestConnection={testTelegramConnection}
              onClearHistory={clearNotificationHistory}
              onResetSettings={resetTelegramSettings}
            />

            <div className="glass-card p-6">
              <h3 className="text-lg font-bold mb-4">💾 Data Management</h3>
              
              <div className="flex flex-wrap gap-3">
                <button onClick={handleExport} className="btn-secondary">
                  📤 Export History
                </button>

                <label className="btn-secondary cursor-pointer">
                  📥 Import History
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleImport}
                    className="hidden"
                  />
                </label>

                <button 
                  onClick={clearHistory} 
                  className="px-4 py-2 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                >
                  🗑️ Clear All History
                </button>

                <button 
                  onClick={resetPaulStats}
                  className="px-4 py-2 rounded-xl bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 transition-colors"
                >
                  🔄 Reset Paul Stats
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Resolution Modal */}
      {resolvingPrediction && (
        <ResolutionModal
          prediction={resolvingPrediction}
          onClose={() => setResolvingPrediction(null)}
          onResolve={handleResolveSubmit}
        />
      )}
    </div>
  );
};
