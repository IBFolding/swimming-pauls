export interface UploadedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  progress: number;
  preview?: string;
  status: 'uploading' | 'completed' | 'error';
}

export interface Paul {
  id: string;
  name: string;
  emoji: string;
  type: 'analyst' | 'creative' | 'technical' | 'researcher' | 'reviewer';
  description: string;
  selected: boolean;
}

export interface ScaleConfig {
  paulCount: number;
  rounds: number;
}

export interface SystemInfo {
  cpuCores: number;
  memoryGB: number;
  browser: string;
}

export interface Question {
  id: string;
  text: string;
  isPrimary: boolean;
}

export type FileType = 'image' | 'video' | 'pdf' | 'csv' | 'json' | 'unknown';

export const QUESTION_TEMPLATES = [
  { id: 'analyze', label: '🔍 Analyze this', text: 'Please analyze the content and provide key insights.' },
  { id: 'summarize', label: '📝 Summarize', text: 'Provide a concise summary of the main points.' },
  { id: 'extract', label: '📊 Extract data', text: 'Extract all relevant data and present it in a structured format.' },
  { id: 'compare', label: '⚖️ Compare', text: 'Compare and contrast the different elements presented.' },
  { id: 'evaluate', label: '✅ Evaluate', text: 'Evaluate the quality, accuracy, and completeness of this content.' },
  { id: 'recommend', label: '💡 Recommend', text: 'Based on this content, what recommendations would you make?' },
] as const;