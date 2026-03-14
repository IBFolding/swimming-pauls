import React, { useState, useMemo, useEffect } from 'react';
import { 
  PaulPersona, 
  BuiltInPaul, 
  BUILT_IN_PAULS, 
  STORAGE_KEYS,
  TRAIT_OPTIONS,
  PROFESSION_OPTIONS,
} from './types';
import { 
  Search, 
  Filter, 
  Trash2, 
  Edit3, 
  Copy,
  Star,
  Users,
  User,
  X,
  Grid3X3,
  List,
  Sparkles
} from 'lucide-react';

interface PaulGalleryProps {
  onEdit?: (paul: PaulPersona) => void;
  onSelect?: (paul: PaulPersona) => void;
  selectedId?: string;
}

export const PaulGallery: React.FC<PaulGalleryProps> = ({ 
  onEdit, 
  onSelect,
  selectedId 
}) => {
  const [customPauls, setCustomPauls] = useState<PaulPersona[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    showBuiltIn: true,
    showCustom: true,
    profession: '',
    biasRange: 'all', // 'all', 'bullish', 'bearish', 'neutral'
    specialty: '',
    trait: '',
  });
  const [sortBy, setSortBy] = useState<'name' | 'bias' | 'confidence' | 'created'>('name');

  // Load custom Pauls from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.CUSTOM_PAULS);
    if (stored) {
      try {
        setCustomPauls(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to parse custom Pauls:', e);
      }
    }
  }, []);

  // Reload custom Pauls when localStorage changes
  useEffect(() => {
    const handleStorageChange = () => {
      const stored = localStorage.getItem(STORAGE_KEYS.CUSTOM_PAULS);
      if (stored) {
        try {
          setCustomPauls(JSON.parse(stored));
        } catch (e) {
          console.error('Failed to parse custom Pauls:', e);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Delete custom Paul
  const deletePaul = (id: string) => {
    if (!confirm('Are you sure you want to delete this Paul?')) return;
    
    const updated = customPauls.filter(p => p.id !== id);
    setCustomPauls(updated);
    localStorage.setItem(STORAGE_KEYS.CUSTOM_PAULS, JSON.stringify(updated));
  };

  // Duplicate custom Paul
  const duplicatePaul = (paul: PaulPersona) => {
    const newPaul: PaulPersona = {
      ...paul,
      id: `custom-${Date.now()}`,
      name: `${paul.name} (Copy)`,
      isCustom: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    const updated = [...customPauls, newPaul];
    setCustomPauls(updated);
    localStorage.setItem(STORAGE_KEYS.CUSTOM_PAULS, JSON.stringify(updated));
  };

  // Filter and sort Pauls
  const filteredPauls = useMemo(() => {
    let allPauls: (PaulPersona | BuiltInPaul)[] = [];
    
    if (filters.showBuiltIn) {
      allPauls = [...allPauls, ...BUILT_IN_PAULS];
    }
    if (filters.showCustom) {
      allPauls = [...allPauls, ...customPauls];
    }

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      allPauls = allPauls.filter(paul => 
        paul.name.toLowerCase().includes(query) ||
        paul.codename.toLowerCase().includes(query) ||
        paul.backstory.toLowerCase().includes(query)
      );
    }

    // Apply profession filter
    if (filters.profession) {
      allPauls = allPauls.filter(paul => paul.profession === filters.profession);
    }

    // Apply bias filter
    if (filters.biasRange !== 'all') {
      allPauls = allPauls.filter(paul => {
        if (filters.biasRange === 'bullish') return paul.bias > 0.2;
        if (filters.biasRange === 'bearish') return paul.bias < -0.2;
        if (filters.biasRange === 'neutral') return paul.bias >= -0.2 && paul.bias <= 0.2;
        return true;
      });
    }

    // Apply specialty filter
    if (filters.specialty) {
      allPauls = allPauls.filter(paul => 
        paul.specialties.includes(filters.specialty as any)
      );
    }

    // Apply trait filter
    if (filters.trait) {
      allPauls = allPauls.filter(paul => 
        paul.traits.includes(filters.trait as any)
      );
    }

    // Sort
    allPauls.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'bias':
          return b.bias - a.bias;
        case 'confidence':
          return b.confidence - a.confidence;
        case 'created':
          return new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime();
        default:
          return 0;
      }
    });

    return allPauls;
  }, [customPauls, searchQuery, filters, sortBy]);

  const getBiasColor = (bias: number) => {
    if (bias > 0.3) return 'text-green-400';
    if (bias < -0.3) return 'text-red-400';
    return 'text-gray-400';
  };

  const getProfessionLabel = (profession: string) => {
    return PROFESSION_OPTIONS.find(p => p.value === profession)?.label || profession;
  };

  const getProfessionEmoji = (profession: string) => {
    return PROFESSION_OPTIONS.find(p => p.value === profession)?.emoji || '💼';
  };

  return (
    <div className="space-y-4">
      {/* Header with search and controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Pauls..."
            className="w-full pl-10 pr-4 py-2.5 bg-dark-800 border border-dark-600 rounded-xl text-white placeholder:text-gray-500 focus:border-accent-blue/50 focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
            >
              <X size={16} />
            </button>
          )}
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border transition-all ${
              showFilters
                ? 'bg-accent-blue/20 border-accent-blue/50 text-accent-blue'
                : 'bg-dark-800 border-dark-600 text-gray-400 hover:text-white'
            }`}
          >
            <Filter size={18} />
            Filters
          </button>
          
          <div className="flex bg-dark-800 border border-dark-600 rounded-xl overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2.5 ${viewMode === 'grid' ? 'bg-accent-blue/20 text-accent-blue' : 'text-gray-400 hover:text-white'}`}
            >
              <Grid3X3 size={18} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2.5 ${viewMode === 'list' ? 'bg-accent-blue/20 text-accent-blue' : 'text-gray-400 hover:text-white'}`}
            >
              <List size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="glass-card p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-white flex items-center gap-2">
              <Filter size={16} className="text-accent-cyan" />
              Filters
            </h4>
            <button
              onClick={() => setFilters({
                showBuiltIn: true,
                showCustom: true,
                profession: '',
                biasRange: 'all',
                specialty: '',
                trait: '',
              })}
              className="text-xs text-gray-400 hover:text-white"
            >
              Reset
            </button>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-2">Show</label>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.showBuiltIn}
                    onChange={(e) => setFilters({ ...filters, showBuiltIn: e.target.checked })}
                    className="rounded border-dark-600 bg-dark-700 text-accent-blue"
                  />
                  <Star size={14} className="text-yellow-400" /> Built-in
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.showCustom}
                    onChange={(e) => setFilters({ ...filters, showCustom: e.target.checked })}
                    className="rounded border-dark-600 bg-dark-700 text-accent-blue"
                  />
                  <Sparkles size={14} className="text-accent-cyan" /> Custom
                </label>
              </div>
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-2">Profession</label>
              <select
                value={filters.profession}
                onChange={(e) => setFilters({ ...filters, profession: e.target.value })}
                className="w-full px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-white"
              >
                <option value="">All Professions</option>
                {PROFESSION_OPTIONS.map(p => (
                  <option key={p.value} value={p.value}>{p.emoji} {p.label}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-2">Bias</label>
              <select
                value={filters.biasRange}
                onChange={(e) => setFilters({ ...filters, biasRange: e.target.value })}
                className="w-full px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-white"
              >
                <option value="all">All</option>
                <option value="bullish">🚀 Bullish (&gt;0.2)</option>
                <option value="neutral">⚖️ Neutral</option>
                <option value="bearish">🐻 Bearish (&lt;-0.2)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-white"
              >
                <option value="name">Name (A-Z)</option>
                <option value="bias">Bias (High-Low)</option>
                <option value="confidence">Confidence (High-Low)</option>
                <option value="created">Created (Newest)</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Results Count */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4 text-gray-400">
          <span className="flex items-center gap-1">
            <Users size={14} />
            {filteredPauls.length} Pauls
          </span>
          <span className="text-dark-600">|</span>
          <span className="flex items-center gap-1">
            <Star size={14} className="text-yellow-400" />
            {BUILT_IN_PAULS.length} Built-in
          </span>
          <span className="text-dark-600">|</span>
          <span className="flex items-center gap-1">
            <User size={14} className="text-accent-cyan" />
            {customPauls.length} Custom
          </span>
        </div>
      </div>

      {/* Pauls Grid/List */}
      {filteredPauls.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Users size={48} className="mx-auto mb-4 text-gray-600" />
          <p className="text-gray-400 mb-2">No Pauls found</p>
          <p className="text-sm text-gray-500">Try adjusting your filters or create a new Paul</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredPauls.map((paul) => (
            <div
              key={paul.id}
              onClick={() => onSelect?.(paul)}
              className={`glass-card-hover p-4 cursor-pointer ${
                selectedId === paul.id ? 'ring-2 ring-accent-blue' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-dark-700 to-dark-600 flex items-center justify-center text-2xl">
                    {paul.emoji}
                  </div>
                  <div>
                    <h4 className="font-semibold text-white text-sm">{paul.name}</h4>
                    <p className="text-xs text-gray-500">{paul.codename}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-1">
                  {'isBuiltIn' in paul && (
                    <Star size={14} className="text-yellow-400" />
                  )}
                  {'isCustom' in paul && paul.isCustom && (
                    <Sparkles size={14} className="text-accent-cyan" />
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2 mb-3">
                <span className="px-2 py-1 bg-dark-700 rounded text-xs text-gray-400">
                  {getProfessionEmoji(paul.profession)} {getProfessionLabel(paul.profession)}
                </span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getBiasColor(paul.bias)} bg-dark-900`}>
                  {paul.bias > 0 ? '+' : ''}{(paul.bias * 100).toFixed(0)}%
                </span>
              </div>
              
              <div className="flex flex-wrap gap-1 mb-3">
                {paul.traits.slice(0, 3).map((trait) => {
                  const traitOption = TRAIT_OPTIONS.find(t => t.value === trait);
                  return (
                    <span
                      key={trait}
                      className="px-1.5 py-0.5 rounded text-xs"
                      style={{
                        backgroundColor: `${traitOption?.color}20`,
                        color: traitOption?.color,
                      }}
                    >
                      {traitOption?.emoji}
                    </span>
                  );
                })}
                {paul.traits.length > 3 && (
                  <span className="px-1.5 py-0.5 rounded text-xs text-gray-500 bg-dark-700">
                    +{paul.traits.length - 3}
                  </span>
                )}
              </div>
              
              {/* Actions for custom Pauls */}
              {'isCustom' in paul && paul.isCustom && (
                <div className="flex gap-2 pt-3 border-t border-dark-600">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit?.(paul);
                    }}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 bg-dark-700 hover:bg-dark-600 rounded-lg text-xs text-gray-300 transition-colors"
                  >
                    <Edit3 size={12} /> Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      duplicatePaul(paul);
                    }}
                    className="flex items-center justify-center p-1.5 bg-dark-700 hover:bg-dark-600 rounded-lg text-gray-400 transition-colors"
                  >
                    <Copy size={12} />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePaul(paul.id);
                    }}
                    className="flex items-center justify-center p-1.5 bg-dark-700 hover:bg-red-500/20 hover:text-red-400 rounded-lg text-gray-400 transition-colors"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full">
            <thead className="bg-dark-800">
              <tr>
                <th className="text-left p-4 text-xs font-medium text-gray-400">Paul</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400">Profession</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400">Bias</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400">Confidence</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400">Traits</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400">Type</th>
                <th className="text-right p-4 text-xs font-medium text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700">
              {filteredPauls.map((paul) => (
                <tr 
                  key={paul.id}
                  onClick={() => onSelect?.(paul)}
                  className={`hover:bg-dark-800/50 cursor-pointer ${
                    selectedId === paul.id ? 'bg-accent-blue/10' : ''
                  }`}
                >
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{paul.emoji}</span>
                      <div>
                        <p className="font-medium text-white">{paul.name}</p>
                        <p className="text-xs text-gray-500">{paul.codename}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-gray-300">
                      {getProfessionEmoji(paul.profession)} {getProfessionLabel(paul.profession)}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`text-sm font-medium ${getBiasColor(paul.bias)}`}>
                      {paul.bias > 0 ? '+' : ''}{(paul.bias * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-dark-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-accent-blue to-accent-cyan"
                          style={{ width: `${paul.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">{Math.round(paul.confidence * 100)}%</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-1">
                      {paul.traits.slice(0, 3).map((trait) => {
                        const traitOption = TRAIT_OPTIONS.find(t => t.value === trait);
                        return (
                          <span
                            key={trait}
                            className="px-1.5 py-0.5 rounded text-xs"
                            style={{
                              backgroundColor: `${traitOption?.color}20`,
                              color: traitOption?.color,
                            }}
                          >
                            {traitOption?.label}
                          </span>
                        );
                      })}
                      {paul.traits.length > 3 && (
                        <span className="px-1.5 py-0.5 rounded text-xs text-gray-500">
                          +{paul.traits.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="p-4">
                    {'isBuiltIn' in paul ? (
                      <span className="flex items-center gap-1 text-xs text-yellow-400">
                        <Star size={12} /> Built-in
                      </span>
                    ) : paul.isCustom ? (
                      <span className="flex items-center gap-1 text-xs text-accent-cyan">
                        <Sparkles size={12} /> Custom
                      </span>
                    ) : null}
                  </td>
                  <td className="p-4">
                    {'isCustom' in paul && paul.isCustom ? (
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onEdit?.(paul);
                          }}
                          className="p-2 hover:bg-dark-700 rounded-lg text-gray-400 hover:text-white transition-colors"
                        >
                          <Edit3 size={14} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            duplicatePaul(paul);
                          }}
                          className="p-2 hover:bg-dark-700 rounded-lg text-gray-400 hover:text-white transition-colors"
                        >
                          <Copy size={14} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deletePaul(paul.id);
                          }}
                          className="p-2 hover:bg-red-500/20 rounded-lg text-gray-400 hover:text-red-400 transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-gray-500">Read-only</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PaulGallery;
