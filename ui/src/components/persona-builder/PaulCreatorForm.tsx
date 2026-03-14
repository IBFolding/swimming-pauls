import React, { useState, useCallback } from 'react';
import { 
  PAUL_EMOJIS, 
  PROFESSION_OPTIONS, 
  SPECIALTY_OPTIONS,
  PaulFormData,
  ProfessionType,
  Specialty,
} from './types';
import { User, Briefcase, BookOpen, Sparkles, AlertCircle } from 'lucide-react';

interface PaulCreatorFormProps {
  initialData?: Partial<PaulFormData>;
  onChange: (data: PaulFormData) => void;
  errors?: Record<string, string>;
}

const DEFAULT_FORM_DATA: PaulFormData = {
  name: '',
  emoji: '🐟',
  profession: 'swing_trader',
  bias: 0,
  confidence: 0.5,
  backstory: '',
  specialties: [],
  traits: [],
};

export const PaulCreatorForm: React.FC<PaulCreatorFormProps> = ({
  initialData,
  onChange,
  errors = {},
}) => {
  const [formData, setFormData] = useState<PaulFormData>({
    ...DEFAULT_FORM_DATA,
    ...initialData,
  });
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  const updateField = useCallback(<K extends keyof PaulFormData>(
    field: K,
    value: PaulFormData[K]
  ) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    onChange(newData);
  }, [formData, onChange]);

  const toggleSpecialty = useCallback((specialty: Specialty) => {
    const newSpecialties = formData.specialties.includes(specialty)
      ? formData.specialties.filter(s => s !== specialty)
      : [...formData.specialties, specialty];
    updateField('specialties', newSpecialties);
  }, [formData.specialties, updateField]);

  const getBiasLabel = (bias: number): string => {
    if (bias <= -0.7) return 'Ultra Bearish 🐻';
    if (bias <= -0.3) return 'Bearish 📉';
    if (bias < 0.3) return 'Neutral ⚖️';
    if (bias < 0.7) return 'Bullish 📈';
    return 'Ultra Bullish 🚀';
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence <= 0.2) return 'Uncertain 🤔';
    if (confidence <= 0.4) return 'Cautious ⚠️';
    if (confidence <= 0.6) return 'Moderate 😐';
    if (confidence <= 0.8) return 'Confident 😎';
    return 'Certain 💯';
  };

  return (
    <div className="space-y-6">
      {/* Name Input */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
          <User size={16} className="text-accent-cyan" />
          Paul Name
        </label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => updateField('name', e.target.value)}
          placeholder="e.g., Alpha Paul"
          className={`input-field ${errors.name ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}`}
          maxLength={30}
        />
        {errors.name && (
          <p className="flex items-center gap-1 text-xs text-red-400">
            <AlertCircle size={12} />
            {errors.name}
          </p>
        )}
        <p className="text-xs text-gray-500">{formData.name.length}/30 characters</p>
      </div>

      {/* Emoji Picker */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
          <Sparkles size={16} className="text-accent-cyan" />
          Choose Emoji
        </label>
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
            className="flex items-center gap-3 px-4 py-3 bg-dark-900/80 border border-dark-600 rounded-xl hover:border-accent-blue/50 transition-all"
          >
            <span className="text-3xl">{formData.emoji}</span>
            <span className="text-sm text-gray-400">Click to change</span>
          </button>
          
          {showEmojiPicker && (
            <div className="absolute z-50 mt-2 p-4 bg-dark-800 border border-dark-600 rounded-xl shadow-2xl w-80">
              <div className="grid grid-cols-8 gap-2">
                {PAUL_EMOJIS.map((emoji) => (
                  <button
                    key={emoji}
                    type="button"
                    onClick={() => {
                      updateField('emoji', emoji);
                      setShowEmojiPicker(false);
                    }}
                    className={`p-2 text-xl rounded-lg transition-all hover:bg-dark-700 ${
                      formData.emoji === emoji ? 'bg-accent-blue/30 ring-2 ring-accent-blue' : ''
                    }`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        {showEmojiPicker && (
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowEmojiPicker(false)}
          />
        )}
      </div>

      {/* Profession Dropdown */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
          <Briefcase size={16} className="text-accent-cyan" />
          Profession / Type
        </label>
        <select
          value={formData.profession}
          onChange={(e) => updateField('profession', e.target.value as ProfessionType)}
          className="input-field appearance-none cursor-pointer"
          style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }}
        >
          {PROFESSION_OPTIONS.map((prof) => (
            <option key={prof.value} value={prof.value} className="bg-dark-800">
              {prof.emoji} {prof.label}
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-500">
          {PROFESSION_OPTIONS.find(p => p.value === formData.profession)?.description}
        </p>
      </div>

      {/* Bias Slider */}
      <div className="space-y-3">
        <label className="flex items-center justify-between text-sm font-medium text-gray-300">
          <span>Market Bias</span>
          <span className="text-accent-cyan">{getBiasLabel(formData.bias)}</span>
        </label>
        <div className="relative">
          <input
            type="range"
            min="-1"
            max="1"
            step="0.1"
            value={formData.bias}
            onChange={(e) => updateField('bias', parseFloat(e.target.value))}
            className="w-full h-2 bg-dark-700 rounded-full appearance-none cursor-pointer accent-accent-blue"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>🐻 Bearish (-1)</span>
            <span>Neutral (0)</span>
            <span>Bullish 🚀 (+1)</span>
          </div>
        </div>
      </div>

      {/* Confidence Slider */}
      <div className="space-y-3">
        <label className="flex items-center justify-between text-sm font-medium text-gray-300">
          <span>Confidence Level</span>
          <span className="text-accent-cyan">{getConfidenceLabel(formData.confidence)}</span>
        </label>
        <div className="relative">
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={formData.confidence}
            onChange={(e) => updateField('confidence', parseFloat(e.target.value))}
            className="w-full h-2 bg-dark-700 rounded-full appearance-none cursor-pointer accent-accent-cyan"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      {/* Backstory Textarea */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
          <BookOpen size={16} className="text-accent-cyan" />
          Backstory
        </label>
        <textarea
          value={formData.backstory}
          onChange={(e) => updateField('backstory', e.target.value)}
          placeholder="Tell the story of this Paul... Where did they come from? What's their trading philosophy?"
          className={`input-field min-h-[100px] resize-none ${errors.backstory ? 'border-red-500' : ''}`}
          maxLength={500}
        />
        {errors.backstory && (
          <p className="flex items-center gap-1 text-xs text-red-400">
            <AlertCircle size={12} />
            {errors.backstory}
          </p>
        )}
        <p className="text-xs text-gray-500">{formData.backstory.length}/500 characters</p>
      </div>

      {/* Specialty Tags */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-300">
          Specialties (multi-select)
        </label>
        <div className="flex flex-wrap gap-2">
          {SPECIALTY_OPTIONS.map((specialty) => {
            const isSelected = formData.specialties.includes(specialty.value);
            return (
              <button
                key={specialty.value}
                type="button"
                onClick={() => toggleSpecialty(specialty.value)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isSelected
                    ? 'bg-accent-blue/30 text-accent-blue border border-accent-blue/50'
                    : 'bg-dark-700 text-gray-400 border border-dark-600 hover:border-dark-500'
                }`}
              >
                <span className="mr-1">{specialty.emoji}</span>
                {specialty.label}
              </button>
            );
          })}
        </div>
        {errors.specialties && (
          <p className="flex items-center gap-1 text-xs text-red-400">
            <AlertCircle size={12} />
            {errors.specialties}
          </p>
        )}
      </div>
    </div>
  );
};

export default PaulCreatorForm;
