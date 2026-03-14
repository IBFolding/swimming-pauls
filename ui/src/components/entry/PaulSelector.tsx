import { useState, useMemo } from 'react';
import { Check, Users, Sparkles } from 'lucide-react';
import type { Paul } from '../types';
import { cn } from '../utils';

interface PaulSelectorProps {
  pauls: Paul[];
  onPaulsChange: (pauls: Paul[]) => void;
}

const PAUL_TYPES = {
  analyst: { color: 'text-blue-400 bg-blue-400/10 border-blue-400/30', label: 'Analyst' },
  creative: { color: 'text-purple-400 bg-purple-400/10 border-purple-400/30', label: 'Creative' },
  technical: { color: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/30', label: 'Technical' },
  researcher: { color: 'text-green-400 bg-green-400/10 border-green-400/30', label: 'Researcher' },
  reviewer: { color: 'text-orange-400 bg-orange-400/10 border-orange-400/30', label: 'Reviewer' },
};

const SAMPLE_PAULS: Omit<Paul, 'selected'>[] = [
  { id: '1', name: 'Data Paul', emoji: '📊', type: 'analyst', description: 'Crunches numbers and finds patterns', bias: 0, confidence: 0.75 },
  { id: '2', name: 'Creative Paul', emoji: '🎨', type: 'creative', description: 'Thinks outside the box', bias: 0.3, confidence: 0.7 },
  { id: '3', name: 'Tech Paul', emoji: '💻', type: 'technical', description: 'Knows every stack overflow answer', bias: 0.1, confidence: 0.8 },
  { id: '4', name: 'Research Paul', emoji: '🔬', type: 'researcher', description: 'Digs deep into any topic', bias: -0.1, confidence: 0.65 },
  { id: '5', name: 'Critique Paul', emoji: '🔍', type: 'reviewer', description: 'Finds what others miss', bias: -0.3, confidence: 0.7 },
  { id: '6', name: 'Vision Paul', emoji: '👁️', type: 'creative', description: 'Sees the big picture', bias: 0.4, confidence: 0.75 },
  { id: '7', name: 'Logic Paul', emoji: '🧮', type: 'analyst', description: 'Follows the data trail', bias: 0, confidence: 0.8 },
  { id: '8', name: 'Code Paul', emoji: '⚡', type: 'technical', description: 'Optimizes everything', bias: 0.2, confidence: 0.7 },
  { id: '9', name: 'Source Paul', emoji: '📚', type: 'researcher', description: 'Verifies all claims', bias: -0.2, confidence: 0.75 },
  { id: '10', name: 'Detail Paul', emoji: '✨', type: 'reviewer', description: 'Catches the edge cases', bias: -0.1, confidence: 0.8 },
  { id: '11', name: 'Idea Paul', emoji: '💡', type: 'creative', description: 'Generates breakthrough concepts', bias: 0.5, confidence: 0.6 },
  { id: '12', name: 'Stat Paul', emoji: '📈', type: 'analyst', description: 'Makes sense of metrics', bias: 0.1, confidence: 0.85 },
];

export function PaulSelector({ pauls, onPaulsChange }: PaulSelectorProps) {
  const [filter, setFilter] = useState<string | null>(null);

  // Initialize pauls if empty
  const activePauls = useMemo(() => {
    if (pauls.length === 0) {
      return SAMPLE_PAULS.map(p => ({ ...p, selected: false }));
    }
    return pauls;
  }, [pauls]);

  const togglePaul = (id: string) => {
    onPaulsChange(activePauls.map(p => 
      p.id === id ? { ...p, selected: !p.selected } : p
    ));
  };

  const selectAll = () => {
    const filtered = filter 
      ? activePauls.filter(p => p.type === filter)
      : activePauls;
    const filteredIds = new Set(filtered.map(p => p.id));
    
    onPaulsChange(activePauls.map(p => 
      filteredIds.has(p.id) ? { ...p, selected: true } : p
    ));
  };

  const clearAll = () => {
    const filtered = filter 
      ? activePauls.filter(p => p.type === filter)
      : activePauls;
    const filteredIds = new Set(filtered.map(p => p.id));
    
    onPaulsChange(activePauls.map(p => 
      filteredIds.has(p.id) ? { ...p, selected: false } : p
    ));
  };

  const selectedCount = activePauls.filter(p => p.selected).length;
  
  const filteredPauls = filter 
    ? activePauls.filter(p => p.type === filter)
    : activePauls;

  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    activePauls.forEach(p => {
      counts[p.type] = (counts[p.type] || 0) + 1;
    });
    return counts;
  }, [activePauls]);

  return (
    <div className="space-y-4">
      {/* Header with filter and actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-accent-blue/20 rounded-lg">
            <Users className="w-4 h-4 text-accent-blue" />
            <span className="text-sm font-medium text-accent-blue">
              {selectedCount} selected
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={selectAll}
            className="px-3 py-1.5 text-sm bg-dark-700 hover:bg-dark-600 rounded-lg 
                     text-gray-300 hover:text-white transition-colors"
          >
            Select All
          </button>
          <button
            onClick={clearAll}
            className="px-3 py-1.5 text-sm bg-dark-700 hover:bg-dark-600 rounded-lg 
                     text-gray-300 hover:text-white transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Type filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilter(null)}
          className={cn(
            "px-3 py-1.5 text-sm rounded-lg transition-all duration-200",
            filter === null 
              ? "bg-accent-blue text-white" 
              : "bg-dark-700 text-gray-400 hover:text-white hover:bg-dark-600"
          )}
        >
          All ({activePauls.length})
        </button>
        
        {Object.entries(PAUL_TYPES).map(([type, { label, color }]) => (
          <button
            key={type}
            onClick={() => setFilter(filter === type ? null : type)}
            className={cn(
              "px-3 py-1.5 text-sm rounded-lg transition-all duration-200 border",
              filter === type 
                ? color
                : "bg-dark-700 text-gray-400 hover:text-white hover:bg-dark-600 border-transparent"
            )}
          >
            {label} ({typeCounts[type] || 0})
          </button>
        ))}
      </div>

      {/* Paul grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {filteredPauls.map((paul, index) => {
          const typeStyle = PAUL_TYPES[paul.type];
          
          return (
            <button
              key={paul.id}
              onClick={() => togglePaul(paul.id)}
              className={cn(
                "relative p-4 rounded-xl border-2 text-left transition-all duration-300 group",
                "hover:scale-[1.02] active:scale-[0.98]",
                paul.selected 
                  ? `${typeStyle.color} shadow-lg` 
                  : "bg-dark-800/50 border-dark-600/50 hover:border-dark-500"
              )}
              style={{ animationDelay: `${index * 30}ms` }}
            >
              {/* Selection indicator */}
              <div className={cn(
                "absolute top-2 right-2 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all duration-200",
                paul.selected 
                  ? "bg-accent-blue border-accent-blue" 
                  : "border-dark-500 group-hover:border-gray-400"
              )}>
                {paul.selected && <Check className="w-3 h-3 text-white" />}
              </div>
              
              {/* Emoji */}
              <div className="text-3xl mb-2">{paul.emoji}</div>
              
              {/* Name */}
              <p className={cn(
                "font-medium text-sm mb-1",
                paul.selected ? "text-white" : "text-gray-300"
              )}>
                {paul.name}
              </p>
              
              {/* Type badge */}
              <span className={cn(
                "inline-block px-2 py-0.5 text-xs rounded-md",
                typeStyle.color
              )}>
                {typeStyle.label}
              </span>
              
              {/* Description - shown on hover or selected */}
              <p className={cn(
                "text-xs mt-2 line-clamp-2 transition-opacity duration-200",
                paul.selected ? "text-gray-300 opacity-100" : "text-gray-500 opacity-0 group-hover:opacity-100"
              )}>
                {paul.description}
              </p>
            </button>
          );
        })}
      </div>

      {filteredPauls.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No Pauls match the selected filter
        </div>
      )}

      {/* Selected summary */}
      {selectedCount > 0 && (
        <div className="p-4 bg-gradient-to-r from-accent-blue/10 to-accent-cyan/10 
                     border border-accent-blue/20 rounded-xl animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-accent-blue/20 rounded-lg">
              <Sparkles className="w-5 h-5 text-accent-blue" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-white">
                {selectedCount} Paul{selectedCount !== 1 ? 's' : ''} ready to swim
              </p>
              <p className="text-xs text-gray-400 mt-0.5">
                {activePauls.filter(p => p.selected && p.type === 'analyst').length} Analysts •{' '}
                {activePauls.filter(p => p.selected && p.type === 'creative').length} Creatives •{' '}
                {activePauls.filter(p => p.selected && p.type === 'technical').length} Technical •{' '}
                {activePauls.filter(p => p.selected && p.type === 'researcher').length} Researchers •{' '}
                {activePauls.filter(p => p.selected && p.type === 'reviewer').length} Reviewers
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}