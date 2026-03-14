import type { FileType, SystemInfo } from '../types';

export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function getFileType(file: File): FileType {
  const type = file.type.toLowerCase();
  if (type.startsWith('image/')) return 'image';
  if (type.startsWith('video/')) return 'video';
  if (type === 'application/pdf') return 'pdf';
  if (type === 'text/csv' || file.name.endsWith('.csv')) return 'csv';
  if (type === 'application/json' || file.name.endsWith('.json')) return 'json';
  return 'unknown';
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 11);
}

export function detectSystem(): SystemInfo {
  const memory = (navigator as Navigator & { deviceMemory?: number }).deviceMemory;
  const cores = navigator.hardwareConcurrency || 4;
  
  return {
    cpuCores: cores,
    memoryGB: memory || Math.min(cores * 2, 16),
    browser: navigator.userAgent.split(')')[0] + ')',
  };
}

export function estimateTime(paulCount: number, rounds: number, fileCount: number): number {
  // Rough estimate: base time + per-paul time + per-round time
  const baseTime = 5;
  const perPaulTime = 0.5;
  const perRoundTime = 2;
  const fileOverhead = fileCount * 3;
  
  return Math.ceil(baseTime + (paulCount * perPaulTime) + (rounds * perRoundTime) + fileOverhead);
}

export function formatTime(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export function createFilePreview(file: File): Promise<string | undefined> {
  return new Promise((resolve) => {
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      resolve(undefined);
      return;
    }
    
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = () => resolve(undefined);
    reader.readAsDataURL(file);
  });
}