import React, { useState, useCallback } from 'react';
import {
  OceanBackground,
  BubbleParticles,
  SwimmingPauls,
  AudioPlayer,
  GlassCard,
  LoadingSwimmer,
} from './components/immersive';
import type { UploadedFile, Question, Paul, SimulationResult } from './types';
import './styles/immersive.css';

const defaultPauls: Paul[] = [
  { id: 'analyst', name: 'Analyst Paul', emoji: '📊', type: 'Data-driven', bias: 0, confidence: 0.75, selected: true },
  { id: 'trader', name: 'Trader Paul', emoji: '📈', type: 'Market timing', bias: 0.2, confidence: 0.7, selected: true },
  { id: 'visionary', name: 'Visionary Paul', emoji: '🔮', type: 'Long-term', bias: 0.4, confidence: 0.8, selected: true },
  { id: 'skeptic', name: 'Skeptic Paul', emoji: '🤨', type: 'Contrarian', bias: -0.3, confidence: 0.65, selected: true },
  { id: 'hedgie', name: 'Hedgie Paul', emoji: '🛡️', type: 'Risk-aware', bias: -0.2, confidence: 0.7, selected: true },
];

function App() {
  const [activeTab, setActiveTab] = useState('predict');
  const [question, setQuestion] = useState('');
  const [paulCount, setPaulCount] = useState(50);
  const [rounds, setRounds] = useState(25);
  const [pauls, setPauls] = useState(defaultPauls);
  const [isSimulating, setIsSimulating] = useState(false);
  const [results, setResults] = useState(null);
  const [files, setFiles] = useState([]);

  const handleCastPool = () => {
    if (!question.trim()) {
      alert('Please enter a question!');
      return;
    }
    setIsSimulating(true);
    setTimeout(() => {
      setResults({
        consensus: { direction: 'BULLISH', confidence: 0.72, strength: 'strong', sentiment: 0.6 },
        rounds: Array.from({length: rounds}, (_, i) => ({
          round: i + 1,
          direction: ['BULLISH', 'NEUTRAL', 'BULLISH'][i % 3],
          confidence: 50 + Math.random() * 30,
          strength: 'moderate'
        })),
        insights: [
          'Multiple Pauls identified key market factors',
          'Risk factors were thoroughly debated',
          'Consensus emerged after careful analysis',
        ]
      });
      setIsSimulating(false);
    }, 3000);
  };

  const selectedCount = pauls.filter(p => p.selected).length;

  return (
    <div className="min-h-screen relative overflow-x-hidden">
      <OceanBackground />
      <BubbleParticles />
      <SwimmingPauls />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-6">
        {/* Header */}
        <GlassCard className="mb-6 p-8 text-center" hoverEffect="none">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            🐟 Swimming Pauls
          </h1>
          <p className="text-xl text-white/70 max-w-2xl mx-auto mb-2">
            "When MiroFish is too hard, ask Paul. And his multiples."
          </p>
          <p className="text-white/50 text-sm">
            Born on Sunset Boulevard, in a self-driving car, listening to Swimming Paul.
          </p>
        </GlassCard>

        {/* Audio */}
        <div className="flex justify-center mb-6">
          <AudioPlayer trackUrl="/swimming-paul.mp3" trackName="Swimming Paul" artistName="The Deep End" />
        </div>

        {/* Navigation */}
        <GlassCard className="mb-6 p-2" hoverEffect="none">
          <div className="flex flex-wrap justify-center gap-2">
            {[
              { id: 'predict', label: '🎣 Cast Pool' },
              { id: 'results', label: '📊 Results', disabled: !results },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setActiveTab(tab.id)}
                disabled={tab.disabled}
                className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white'
                    : tab.disabled ? 'opacity-50 text-white/40' : 'hover:bg-white/10 text-white/70'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </GlassCard>

        {/* Content */}
        {isSimulating ? (
          <GlassCard className="p-16 text-center">
            <LoadingSwimmer text="The Pauls are swimming..." size="lg" />
            <p className="mt-8 text-white/60">Casting {selectedCount} Pauls • {rounds} rounds</p>
          </GlassCard>
        ) : (
          <>
            {activeTab === 'predict' && (
              <div className="space-y-6">
                {/* Question */}
                <GlassCard className="p-6">
                  <h2 className="text-2xl font-bold text-cyan-400 mb-4">❓ Your Question</h2>
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., Will CRITIC succeed? Should I quit my job?"
                    className="w-full p-4 rounded-xl bg-black/30 border border-cyan-500/30 text-white placeholder-white/30 focus:border-cyan-500 focus:outline-none"
                    rows={3}
                  />
                </GlassCard>

                {/* Scale */}
                <GlassCard className="p-6">
                  <h2 className="text-2xl font-bold text-cyan-400 mb-4">⚙️ Scale</h2>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="text-white/70 mb-2 block">Pauls: {paulCount}</label>
                      <input
                        type="range"
                        min="10"
                        max="1000"
                        value={paulCount}
                        onChange={(e) => setPaulCount(parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="text-white/70 mb-2 block">Rounds: {rounds}</label>
                      <input
                        type="range"
                        min="5"
                        max="100"
                        value={rounds}
                        onChange={(e) => setRounds(parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  </div>
                </GlassCard>

                {/* Paul Selector */}
                <GlassCard className="p-6">
                  <h2 className="text-2xl font-bold text-cyan-400 mb-4">🐟 Select Pauls ({selectedCount})</h2>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {pauls.map((paul) => (
                      <button
                        key={paul.id}
                        onClick={() => setPauls(pauls.map(p => p.id === paul.id ? {...p, selected: !p.selected} : p))}
                        className={`p-4 rounded-xl border-2 transition-all ${
                          paul.selected
                            ? 'border-cyan-500 bg-cyan-500/20'
                            : 'border-white/10 bg-white/5 hover:border-white/30'
                        }`}
                      >
                        <div className="text-2xl mb-1">{paul.emoji}</div>
                        <div className="text-sm font-medium">{paul.name}</div>
                      </button>
                    ))}
                  </div>
                </GlassCard>

                {/* Cast Button */}
                <button
                  onClick={handleCastPool}
                  disabled={!question.trim() || selectedCount === 0}
                  className="w-full py-6 text-2xl font-bold uppercase tracking-widest bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 hover:from-pink-400 hover:via-purple-400 hover:to-cyan-400 disabled:opacity-50 rounded-2xl shadow-xl transition-all hover:scale-[1.02]"
                >
                  🐟 Cast {selectedCount} Pauls 🐟
                </button>
              </div>
            )}

            {activeTab === 'results' && results && (
              <div className="space-y-6">
                <GlassCard className="p-8 text-center">
                  <h2 className="text-3xl font-bold mb-4">🏁 Consensus</h2>
                  <div className="text-6xl font-bold text-green-400 mb-2">{results.consensus.direction}</div>
                  <div className="text-2xl">{(results.consensus.confidence * 100).toFixed(0)}% confidence</div>
                </GlassCard>

                <GlassCard className="p-6">
                  <h3 className="text-xl font-bold text-cyan-400 mb-4">📊 Debate Rounds</h3>
                  {results.rounds.slice(0, 10).map((round) => (
                    <div key={round.round} className="flex items-center py-2 border-b border-white/10">
                      <span className="w-20 text-white/60">Round {round.round}</span>
                      <span className={`flex-1 ${round.direction === 'BULLISH' ? 'text-green-400' : round.direction === 'BEARISH' ? 'text-red-400' : 'text-yellow-400'}`}>
                        {round.direction}
                      </span>
                      <span className="text-white/60">{round.confidence.toFixed(0)}%</span>
                    </div>
                  ))}
                </GlassCard>

                <GlassCard className="p-6">
                  <h3 className="text-xl font-bold text-cyan-400 mb-4">💡 Insights</h3>
                  <ul className="space-y-2">
                    {results.insights.map((insight, i) => (
                      <li key={i} className="text-white/80">• {insight}</li>
                    ))}
                  </ul>
                </GlassCard>
              </div>
            )}
          </>
        )}

        {/* Footer */}
        <GlassCard className="mt-8 p-6 text-center" hoverEffect="none">
          <p className="text-white/50">🐟 Swimming Pauls v2.0 • 100% Local • No Cloud</p>
          <p className="text-white/30 text-sm mt-2">
            Built by HOWARD • Named while listening to Swimming Paul driving down Sunset
          </p>
        </GlassCard>
      </div>
    </div>
  );
}

export default App;
