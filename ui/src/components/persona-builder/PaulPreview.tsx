import React from 'react';
import { PaulFormData, BUILT_IN_PAULS, TRAIT_OPTIONS, PROFESSION_OPTIONS } from './types';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  Zap,
  Quote,
  Sparkles,
  BarChart3,
  Users
} from 'lucide-react';

interface PaulPreviewProps {
  formData: PaulFormData;
}

export const PaulPreview: React.FC<PaulPreviewProps> = ({ formData }) => {
  // Generate sample prediction based on form data
  const generateSamplePrediction = () => {
    const { bias, confidence, profession, specialties } = formData;
    
    const assetTypes = specialties.includes('memecoins') ? 'memecoins' : 
                      specialties.includes('defi') ? 'DeFi tokens' :
                      specialties.includes('nft') ? 'NFT projects' :
                      specialties.includes('layer1') ? 'Layer 1s' : 'crypto assets';
    
    const timeframe = profession === 'scalper' ? 'next 24 hours' :
                     profession === 'swing_trader' ? 'next 2 weeks' :
                     profession === 'position_trader' ? 'next 3 months' : 'the coming period';
    
    let direction: string;
    let reasoning: string;
    
    if (bias > 0.5) {
      direction = 'strongly bullish';
      reasoning = confidence > 0.7 
        ? 'Multiple confluence factors align with high conviction.'
        : 'Early signals suggest upward momentum building.';
    } else if (bias > 0) {
      direction = 'cautiously optimistic';
      reasoning = 'Selective opportunities emerging in quality projects.';
    } else if (bias > -0.5) {
      direction = 'neutral to bearish';
      reasoning = 'Mixed signals warrant defensive positioning.';
    } else {
      direction = 'bearish';
      reasoning = confidence > 0.7
        ? 'Multiple bearish divergences with high confidence.'
        : 'Risk-off posture advised given uncertainty.';
    }
    
    return {
      assetTypes,
      timeframe,
      direction,
      reasoning,
      conviction: Math.round(confidence * 100),
    };
  };

  const prediction = generateSamplePrediction();
  
  // Find similar Pauls for comparison
  const findSimilarPauls = () => {
    return BUILT_IN_PAULS.filter(paul => {
      const professionMatch = paul.profession === formData.profession;
      const biasSimilarity = Math.abs(paul.bias - formData.bias) < 0.3;
      const specialtyOverlap = paul.specialties.some(s => formData.specialties.includes(s as any));
      return professionMatch || (biasSimilarity && specialtyOverlap);
    }).slice(0, 3);
  };
  
  const similarPauls = findSimilarPauls();
  
  const professionLabel = PROFESSION_OPTIONS.find(p => p.value === formData.profession);
  
  // Calculate a mock "prediction accuracy" score
  const mockAccuracy = Math.round(50 + (formData.confidence * 30) + (Math.random() * 10));

  return (
    <div className="space-y-6">
      {/* Live Paul Card Preview */}
      <div className="glass-card p-6 glow-border">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-blue to-accent-cyan flex items-center justify-center text-4xl shadow-lg shadow-accent-blue/20">
              {formData.emoji || '🐟'}
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                {formData.name || 'Unnamed Paul'}
              </h3>
              <p className="text-sm text-gray-400">
                {professionLabel?.emoji} {professionLabel?.label || 'Trader'}
              </p>
            </div>
          </div>
          
          <div className="flex flex-col items-end gap-1">
            <div className={`flex items-center gap-1 text-sm font-medium ${
              formData.bias > 0 ? 'text-green-400' : formData.bias < 0 ? 'text-red-400' : 'text-gray-400'
            }`}>
              {formData.bias > 0 ? <TrendingUp size={16} /> : formData.bias < 0 ? <TrendingDown size={16} /> : <Activity size={16} />}
              {formData.bias > 0 ? `+${(formData.bias * 100).toFixed(0)}%` : `${(formData.bias * 100).toFixed(0)}%`} Bias
            </div>
            <div className="flex items-center gap-1 text-sm text-accent-cyan">
              <Target size={14} />
              {Math.round(formData.confidence * 100)}% Confidence
            </div>
          </div>
        </div>

        {/* Traits Display */}
        {formData.traits.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {formData.traits.slice(0, 4).map((trait) => {
              const traitOption = TRAIT_OPTIONS.find(t => t.value === trait);
              return (
                <span
                  key={trait}
                  className="px-2 py-1 rounded-lg text-xs font-medium"
                  style={{
                    backgroundColor: `${traitOption?.color}20`,
                    color: traitOption?.color,
                  }}
                >
                  {traitOption?.emoji} {traitOption?.label}
                </span>
              );
            })}
            {formData.traits.length > 4 && (
              <span className="px-2 py-1 rounded-lg text-xs text-gray-400 bg-dark-700">
                +{formData.traits.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Specialties */}
        {formData.specialties.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {formData.specialties.map((specialty) => (
              <span key={specialty} className="px-2 py-1 bg-dark-700 rounded-lg text-xs text-gray-300">
                {specialty}
              </span>
            ))}
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3 mt-4">
          <div className="p-3 bg-dark-900/50 rounded-xl text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-gray-500 mb-1">
              <Zap size={12} /> Accuracy
            </div>
            <div className="text-lg font-bold text-accent-cyan">{mockAccuracy}%</div>
          </div>
          <div className="p-3 bg-dark-900/50 rounded-xl text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-gray-500 mb-1">
              <BarChart3 size={12} /> Trades
            </div>
            <div className="text-lg font-bold text-white">{Math.round(100 + formData.confidence * 500)}</div>
          </div>
          <div className="p-3 bg-dark-900/50 rounded-xl text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-gray-500 mb-1">
              <Sparkles size={12} /> Streak
            </div>
            <div className="text-lg font-bold text-accent-purple">{Math.round(formData.confidence * 10)}d</div>
          </div>
        </div>
      </div>

      {/* Sample Prediction */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-3">
          <Quote size={18} className="text-accent-cyan" />
          <h4 className="font-semibold text-white">Sample Prediction</h4>
          <span className="text-xs text-gray-500 ml-auto">AI-generated preview</span>
        </div>
        
        <div className="p-4 bg-dark-900/50 rounded-xl border border-dark-600">
          <p className="text-sm text-gray-300 leading-relaxed">
            "I'm {prediction.direction} on {prediction.assetTypes} for the {prediction.timeframe}. 
            {prediction.reasoning} Operating with {prediction.conviction}% conviction on this thesis."
          </p>
          
          <div className="flex items-center gap-4 mt-4 pt-4 border-t border-dark-700">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Direction:</span>
              <span className={`text-sm font-medium ${
                formData.bias > 0 ? 'text-green-400' : formData.bias < 0 ? 'text-red-400' : 'text-gray-400'
              }`}>
                {prediction.direction.toUpperCase()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Conviction:</span>
              <div className="w-20 h-2 bg-dark-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-accent-blue to-accent-cyan"
                  style={{ width: `${prediction.conviction}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Similar Pauls Comparison */}
      {similarPauls.length > 0 && formData.name && (
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 mb-3">
            <Users size={18} className="text-accent-cyan" />
            <h4 className="font-semibold text-white">Similar to Existing Pauls</h4>
          </div>
          
          <div className="space-y-2">
            {similarPauls.map((paul) => (
              <div key={paul.id} className="flex items-center gap-3 p-3 bg-dark-900/50 rounded-lg">
                <span className="text-2xl">{paul.emoji}</span>
                <div className="flex-1">
                  <p className="font-medium text-white text-sm">{paul.name}</p>
                  <p className="text-xs text-gray-500">{paul.codename}</p>
                </div>
                <div className="text-right">
                  <div className={`text-xs font-medium ${
                    paul.bias > 0 ? 'text-green-400' : paul.bias < 0 ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    {paul.bias > 0 ? '+' : ''}{(paul.bias * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">{paul.traits.length} traits</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PaulPreview;
