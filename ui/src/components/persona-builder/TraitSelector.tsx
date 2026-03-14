import React from 'react';
import { TRAIT_OPTIONS, Trait } from './types';
import { Shield, Sparkles } from 'lucide-react';

interface TraitSelectorProps {
  selectedTraits: Trait[];
  onChange: (traits: Trait[]) => void;
  maxTraits?: number;
}

export const TraitSelector: React.FC<TraitSelectorProps> = ({
  selectedTraits,
  onChange,
  maxTraits = 6,
}) => {
  const toggleTrait = (trait: Trait) => {
    if (selectedTraits.includes(trait)) {
      onChange(selectedTraits.filter(t => t !== trait));
    } else if (selectedTraits.length < maxTraits) {
      onChange([...selectedTraits, trait]);
    }
  };

  const getTraitStyle = (trait: Trait, isSelected: boolean) => {
    const traitOption = TRAIT_OPTIONS.find(t => t.value === trait);
    const baseColor = traitOption?.color || '#6b7280';
    
    if (isSelected) {
      return {
        backgroundColor: `${baseColor}20`,
        borderColor: baseColor,
        color: baseColor,
      };
    }
    return {
      backgroundColor: 'transparent',
      borderColor: '#3f3f46',
      color: '#9ca3af',
    };
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield size={18} className="text-accent-cyan" />
          <h3 className="text-lg font-semibold text-white">Personality Traits</h3>
        </div>
        <span className={`text-sm ${selectedTraits.length >= maxTraits ? 'text-amber-400' : 'text-gray-400'}`}>
          {selectedTraits.length}/{maxTraits} selected
        </span>
      </div>

      <p className="text-sm text-gray-400">
        Select up to {maxTraits} traits that define this Paul\'s personality and trading style.
        Hover over each trait to see its description.
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {TRAIT_OPTIONS.map((traitOption) => {
          const isSelected = selectedTraits.includes(traitOption.value);
          const style = getTraitStyle(traitOption.value, isSelected);
          
          return (
            <div key={traitOption.value} className="relative group">
              <button
                type="button"
                onClick={() => toggleTrait(traitOption.value)}
                disabled={!isSelected && selectedTraits.length >= maxTraits}
                className={`w-full p-3 rounded-xl border-2 transition-all duration-200 text-left ${
                  !isSelected && selectedTraits.length >= maxTraits
                    ? 'opacity-50 cursor-not-allowed'
                    : 'cursor-pointer hover:scale-[1.02]'
                }`}
                style={{
                  ...style,
                  boxShadow: isSelected ? `0 0 20px ${traitOption.color}20` : 'none',
                }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xl">{traitOption.emoji}</span>
                  <span className="font-medium text-sm">{traitOption.label}</span>
                </div>
                
                {isSelected && (
                  <div 
                    className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: traitOption.color }}
                  >
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </button>

              {/* Tooltip on hover */}
              <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 bg-dark-800 border border-dark-600 rounded-xl shadow-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{traitOption.emoji}</span>
                  <span className="font-semibold text-white">{traitOption.label}</span>
                </div>
                <p className="text-xs text-gray-400">{traitOption.description}</p>
                
                <div 
                  className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-dark-800 border-r border-b border-dark-600 rotate-45"
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Traits Summary */}
      {selectedTraits.length > 0 && (
        <div className="mt-6 p-4 bg-dark-800/50 rounded-xl border border-dark-600">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={16} className="text-accent-cyan" />
            <span className="text-sm font-medium text-gray-300">Selected Traits</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedTraits.map((trait) => {
              const traitOption = TRAIT_OPTIONS.find(t => t.value === trait)!;
              return (
                <span
                  key={trait}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium"
                  style={{
                    backgroundColor: `${traitOption.color}20`,
                    color: traitOption.color,
                    border: `1px solid ${traitOption.color}40`,
                  }}
                >
                  <span>{traitOption.emoji}</span>
                  {traitOption.label}
                  <button
                    type="button"
                    onClick={() => toggleTrait(trait)}
                    className="ml-1 hover:opacity-70 transition-opacity"
                  >
                    ×
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default TraitSelector;
