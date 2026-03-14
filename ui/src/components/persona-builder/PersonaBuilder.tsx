import React, { useState, useCallback, useEffect } from 'react';
import { PaulFormData, PaulPersona, STORAGE_KEYS, BUILT_IN_PAULS } from './types';
import PaulCreatorForm from './PaulCreatorForm';
import TraitSelector from './TraitSelector';
import PaulPreview from './PaulPreview';
import SaveOptions from './SaveOptions';
import PaulGallery from './PaulGallery';
import { 
  UserPlus, 
  Eye, 
  Grid3X3,
  ChevronRight,
  Sparkles,
  ArrowLeft,
  CheckCircle2
} from 'lucide-react';

type BuilderView = 'create' | 'gallery';

interface PersonaBuilderProps {
  initialPaulId?: string;
  onPaulCreated?: (paul: PaulPersona) => void;
}

export const PersonaBuilder: React.FC<PersonaBuilderProps> = ({ 
  initialPaulId,
  onPaulCreated 
}) => {
  const [currentView, setCurrentView] = useState<BuilderView>(initialPaulId ? 'create' : 'gallery');
  const [editingPaul, setEditingPaul] = useState<PaulPersona | null>(null);
  const [activeTab, setActiveTab] = useState<'form' | 'traits' | 'preview'>('form');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  
  const [formData, setFormData] = useState<PaulFormData>({
    name: '',
    emoji: '🐟',
    profession: 'swing_trader',
    bias: 0,
    confidence: 0.5,
    backstory: '',
    specialties: [],
    traits: [],
  });

  // Load Paul for editing
  useEffect(() => {
    if (initialPaulId) {
      // Check built-in Pauls
      const builtIn = BUILT_IN_PAULS.find(p => p.id === initialPaulId);
      if (builtIn) {
        setEditingPaul(builtIn);
        setFormData({
          name: builtIn.name,
          emoji: builtIn.emoji,
          profession: builtIn.profession,
          bias: builtIn.bias,
          confidence: builtIn.confidence,
          backstory: builtIn.backstory,
          specialties: builtIn.specialties,
          traits: builtIn.traits,
        });
        return;
      }
      
      // Check custom Pauls
      const stored = localStorage.getItem(STORAGE_KEYS.CUSTOM_PAULS);
      if (stored) {
        const customPauls: PaulPersona[] = JSON.parse(stored);
        const custom = customPauls.find(p => p.id === initialPaulId);
        if (custom) {
          setEditingPaul(custom);
          setFormData({
            name: custom.name,
            emoji: custom.emoji,
            profession: custom.profession,
            bias: custom.bias,
            confidence: custom.confidence,
            backstory: custom.backstory,
            specialties: custom.specialties,
            traits: custom.traits,
          });
        }
      }
    }
  }, [initialPaulId]);

  // Create Paul from form data
  const createPaulFromForm = useCallback((): PaulPersona => {
    const now = new Date().toISOString();
    const id = editingPaul?.id || `custom-${Date.now()}`;
    
    // Check if editingPaul has isBuiltIn property (i.e., it's a BuiltInPaul)
    const isEditingBuiltIn = editingPaul && 'isBuiltIn' in editingPaul;
    
    return {
      id,
      name: formData.name,
      codename: generateCodename(),
      emoji: formData.emoji,
      profession: formData.profession,
      bias: formData.bias,
      confidence: formData.confidence,
      backstory: formData.backstory,
      catchphrase: generateCatchphrase(),
      specialties: formData.specialties,
      traits: formData.traits,
      isCustom: !isEditingBuiltIn,
      createdAt: editingPaul?.createdAt || now,
      updatedAt: now,
    };
  }, [formData, editingPaul]);

  // Generate codename
  const generateCodename = (): string => {
    const suffixes = ['Trader', 'Analyst', 'Oracle', 'Seeker', 'Hunter', 'Master', 'Wizard', 'Pilot'];
    const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
    return `The ${suffix}`;
  };

  // Generate catchphrase
  const generateCatchphrase = (): string => {
    const phrases = [
      "The market is my playground.",
      "Data doesn't lie.",
      "Patience pays.",
      "Trust the process.",
      "Fortune favors the bold.",
    ];
    return phrases[Math.floor(Math.random() * phrases.length)];
  };

  // Handle form changes
  const handleFormChange = useCallback((data: PaulFormData) => {
    setFormData(data);
    // Clear errors when user types
    if (formErrors.name && data.name) {
      setFormErrors(prev => ({ ...prev, name: '' }));
    }
  }, [formErrors]);

  // Handle trait changes
  const handleTraitsChange = useCallback((traits: any[]) => {
    setFormData(prev => ({ ...prev, traits }));
  }, []);

  // Handle save
  const handleSave = useCallback((paul: PaulPersona) => {
    setShowSuccessToast(true);
    setTimeout(() => setShowSuccessToast(false), 3000);
    onPaulCreated?.(paul);
  }, [onPaulCreated]);

  // Handle edit from gallery
  const handleEditFromGallery = useCallback((paul: PaulPersona) => {
    setEditingPaul(paul);
    setFormData({
      name: paul.name,
      emoji: paul.emoji,
      profession: paul.profession,
      bias: paul.bias,
      confidence: paul.confidence,
      backstory: paul.backstory,
      specialties: paul.specialties,
      traits: paul.traits,
    });
    setCurrentView('create');
  }, []);

  // Handle select from gallery
  const handleSelectFromGallery = useCallback((paul: PaulPersona) => {
    // Could navigate to detail view or use in a simulation
    console.log('Selected Paul:', paul);
  }, []);

  // Reset form
  const resetForm = useCallback(() => {
    setEditingPaul(null);
    setFormData({
      name: '',
      emoji: '🐟',
      profession: 'swing_trader',
      bias: 0,
      confidence: 0.5,
      backstory: '',
      specialties: [],
      traits: [],
    });
    setFormErrors({});
  }, []);

  // Get current Paul for preview/save
  const currentPaul = createPaulFromForm();

  // Load custom Pauls for save options
  const [customPauls, setCustomPauls] = useState<PaulPersona[]>([]);
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.CUSTOM_PAULS);
    if (stored) {
      setCustomPauls(JSON.parse(stored));
    }
  }, []);

  return (
    <div className="min-h-screen bg-dark-900 text-white p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-blue to-accent-cyan flex items-center justify-center">
                <Sparkles size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">Persona Builder</h1>
                <p className="text-sm text-gray-400">Create and customize your Swimming Pauls</p>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => {
                if (currentView === 'create') {
                  resetForm();
                  setCurrentView('gallery');
                } else {
                  resetForm();
                  setCurrentView('create');
                }
              }}
              className="btn-secondary flex items-center gap-2"
            >
              {currentView === 'create' ? (
                <>
                  <Grid3X3 size={18} />
                  View Gallery
                </>
              ) : (
                <>
                  <UserPlus size={18} />
                  Create Paul
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Success Toast */}
      {showSuccessToast && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-3 px-6 py-4 bg-green-500/20 border border-green-500/50 rounded-xl">
          <CheckCircle2 size={24} className="text-green-400" />
          <div>
            <p className="font-medium text-green-400">Paul Saved!</p>
            <p className="text-sm text-green-300/70">Your creation has been stored</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {currentView === 'create' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Form/Tabs */}
            <div className="lg:col-span-2 space-y-6">
              {/* Tabs */}
              <div className="flex gap-2 p-1 bg-dark-800 rounded-xl">
                {[
                  { id: 'form', label: 'Basics', icon: UserPlus },
                  { id: 'traits', label: 'Traits', icon: Sparkles },
                  { id: 'preview', label: 'Preview', icon: Eye },
                ].map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id as any)}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
                      activeTab === id
                        ? 'bg-accent-blue text-white'
                        : 'text-gray-400 hover:text-white hover:bg-dark-700'
                    }`}
                  >
                    <Icon size={16} />
                    {label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="glass-card p-6">
                {activeTab === 'form' && (
                  <div className="space-y-6">
                    <div className="flex items-center gap-2 mb-4">
                      <UserPlus size={20} className="text-accent-cyan" />
                      <h2 className="text-xl font-semibold">{editingPaul ? 'Edit Paul' : 'Create New Paul'}</h2>
                    </div>
                    <PaulCreatorForm
                      initialData={formData}
                      onChange={handleFormChange}
                      errors={formErrors}
                    />
                  </div>
                )}

                {activeTab === 'traits' && (
                  <TraitSelector
                    selectedTraits={formData.traits}
                    onChange={handleTraitsChange}
                  />
                )}

                {activeTab === 'preview' && (
                  <div className="space-y-6">
                    <div className="flex items-center gap-2 mb-4">
                      <Eye size={20} className="text-accent-cyan" />
                      <h2 className="text-xl font-semibold">Live Preview</h2>
                    </div>
                    <PaulPreview formData={formData} />
                  </div>
                )}
              </div>

              {/* Navigation */}
              <div className="flex justify-between">
                <button
                  onClick={() => {
                    const tabs = ['form', 'traits', 'preview'];
                    const currentIndex = tabs.indexOf(activeTab);
                    if (currentIndex > 0) {
                      setActiveTab(tabs[currentIndex - 1] as any);
                    }
                  }}
                  disabled={activeTab === 'form'}
                  className="btn-secondary flex items-center gap-2"
                >
                  <ArrowLeft size={18} />
                  Previous
                </button>
                
                <button
                  onClick={() => {
                    const tabs = ['form', 'traits', 'preview'];
                    const currentIndex = tabs.indexOf(activeTab);
                    if (currentIndex < tabs.length - 1) {
                      setActiveTab(tabs[currentIndex + 1] as any);
                    }
                  }}
                  disabled={activeTab === 'preview'}
                  className="btn-primary flex items-center gap-2"
                >
                  Next
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>

            {/* Right Column - Preview & Save */}
            <div className="space-y-6">
              <div className="glass-card p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Eye size={20} className="text-accent-cyan" />
                  <h2 className="text-xl font-semibold">Preview</h2>
                </div>
                
                <PaulPreview formData={formData} />
              </div>

              <SaveOptions
                paul={currentPaul}
                onSave={handleSave}
                existingPauls={customPauls}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Grid3X3 size={24} className="text-accent-cyan" />
                <div>
                  <h2 className="text-xl font-semibold">Paul Gallery</h2>
                  <p className="text-sm text-gray-400">Browse all your Pauls</p>
                </div>
              </div>
            </div>
            
            <PaulGallery
              onEdit={handleEditFromGallery}
              onSelect={handleSelectFromGallery}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonaBuilder;
