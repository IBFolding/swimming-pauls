import { useState, useRef, useCallback } from 'react';
import { Mic, Plus, X, ChevronDown, Sparkles } from 'lucide-react';
import type { Question } from '../types';
import { QUESTION_TEMPLATES } from '../types';
import { generateId, cn } from '../utils';

interface QuestionsInterfaceProps {
  questions: Question[];
  onQuestionsChange: (questions: Question[]) => void;
}

export function QuestionsInterface({ questions, onQuestionsChange }: QuestionsInterfaceProps) {
  const [isListening, setIsListening] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [activeTextarea, setActiveTextarea] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const primaryQuestion = questions.find(q => q.isPrimary) || questions[0];
  const followUpQuestions = questions.filter(q => !q.isPrimary);

  // Initialize speech recognition
  const initSpeechRecognition = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser');
      return null;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    return recognition;
  }, []);

  const startListening = (questionId: string) => {
    const recognition = initSpeechRecognition();
    if (!recognition) return;
    
    setActiveTextarea(questionId);
    setIsListening(true);
    recognitionRef.current = recognition;
    
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join('');
      
      updateQuestion(questionId, transcript);
    };
    
    recognition.onerror = () => {
      setIsListening(false);
      setActiveTextarea(null);
    };
    
    recognition.onend = () => {
      setIsListening(false);
      setActiveTextarea(null);
    };
    
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
    setActiveTextarea(null);
  };

  const updateQuestion = (id: string, text: string) => {
    onQuestionsChange(questions.map(q => 
      q.id === id ? { ...q, text } : q
    ));
  };

  const addFollowUpQuestion = () => {
    const newQuestion: Question = {
      id: generateId(),
      text: '',
      isPrimary: false,
    };
    onQuestionsChange([...questions, newQuestion]);
  };

  const removeQuestion = (id: string) => {
    if (questions.find(q => q.id === id)?.isPrimary) return; // Can't remove primary
    onQuestionsChange(questions.filter(q => q.id !== id));
  };

  const applyTemplate = (templateId: string) => {
    const template = QUESTION_TEMPLATES.find(t => t.id === templateId);
    if (template && primaryQuestion) {
      updateQuestion(primaryQuestion.id, template.text);
    }
    setShowTemplates(false);
  };

  return (
    <div className="space-y-4">
      {/* Primary Question */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent-cyan" />
            Primary Question
          </label>
          
          {/* Template dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-dark-700 hover:bg-dark-600 
                       rounded-lg transition-colors text-gray-300"
            >
              Templates
              <ChevronDown className={cn("w-4 h-4 transition-transform", showTemplates && "rotate-180")} />
            </button>
            
            {showTemplates && (
              <div className="absolute right-0 top-full mt-1 w-64 bg-dark-800 border border-dark-600 
                           rounded-xl shadow-xl z-20 py-1 animate-fade-in">
                {QUESTION_TEMPLATES.map(template => (
                  <button
                    key={template.id}
                    onClick={() => applyTemplate(template.id)}
                    className="w-full px-4 py-2.5 text-left text-sm hover:bg-dark-700 transition-colors"
                  >
                    <span className="block font-medium text-white">{template.label}</span>
                    <span className="block text-xs text-gray-500 truncate">{template.text}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="relative">
          <textarea
            value={primaryQuestion?.text || ''}
            onChange={(e) => updateQuestion(primaryQuestion?.id || '', e.target.value)}
            placeholder="What would you like to ask the Pauls?"
            className="input-field min-h-[120px] resize-none pr-12"
          />
          
          {/* Voice input button */}
          <button
            onClick={() => isListening && activeTextarea === primaryQuestion?.id 
              ? stopListening() 
              : startListening(primaryQuestion?.id || '')
            }
            className={cn(
              "absolute bottom-3 right-3 p-2.5 rounded-lg transition-all duration-300",
              isListening && activeTextarea === primaryQuestion?.id
                ? "bg-red-500/20 text-red-400 animate-pulse"
                : "bg-dark-700 text-gray-400 hover:text-white hover:bg-dark-600"
            )}
            title={isListening ? 'Stop recording' : 'Start voice input'}
          >
            <Mic className={cn("w-5 h-5", isListening && activeTextarea === primaryQuestion?.id && "animate-pulse")} />
          </button>
        </div>
      </div>

      {/* Follow-up Questions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-300">
            Follow-up Questions ({followUpQuestions.length})
          </label>
          <button
            onClick={addFollowUpQuestion}
            className="flex items-center gap-1.5 text-sm text-accent-cyan hover:text-accent-blue 
                     transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add follow-up
          </button>
        </div>
        
        <div className="space-y-2">
          {followUpQuestions.map((question, index) => (
            <div
              key={question.id}
              className="flex gap-2 items-start animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="relative flex-1">
                <textarea
                  value={question.text}
                  onChange={(e) => updateQuestion(question.id, e.target.value)}
                  placeholder={`Follow-up question ${index + 1}`}
                  className="input-field min-h-[80px] resize-none pr-12 text-sm"
                />
                
                <button
                  onClick={() => isListening && activeTextarea === question.id 
                    ? stopListening() 
                    : startListening(question.id)
                  }
                  className={cn(
                    "absolute bottom-2.5 right-2.5 p-2 rounded-lg transition-all duration-300",
                    isListening && activeTextarea === question.id
                      ? "bg-red-500/20 text-red-400 animate-pulse"
                      : "bg-dark-700 text-gray-400 hover:text-white hover:bg-dark-600"
                  )}
                >
                  <Mic className="w-4 h-4" />
                </button>
              </div>
              
              <button
                onClick={() => removeQuestion(question.id)}
                className="p-2.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 
                         rounded-lg transition-all duration-200 mt-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
        
        {followUpQuestions.length === 0 && (
          <div className="text-center py-6 text-gray-500 text-sm border border-dashed border-dark-600 
                       rounded-xl bg-dark-800/30">
            No follow-up questions yet
          </div>
        )}
      </div>
      
      {/* Click outside to close templates */}
      {showTemplates && (
        <div 
          className="fixed inset-0 z-10" 
          onClick={() => setShowTemplates(false)} 
        />
      )}
    </div>
  );
}