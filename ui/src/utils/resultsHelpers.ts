export const getDirectionColor = (direction: 'bullish' | 'bearish' | 'neutral'): string => {
  switch (direction) {
    case 'bullish':
      return '#4ade80';
    case 'bearish':
      return '#ef4444';
    case 'neutral':
      return '#fbbf24';
    default:
      return '#a0a0a0';
  }
};

export const getDirectionGradient = (direction: 'bullish' | 'bearish' | 'neutral'): string => {
  switch (direction) {
    case 'bullish':
      return 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)';
    case 'bearish':
      return 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)';
    case 'neutral':
      return 'linear-gradient(135deg, #f7971e 0%, #ffd200 100%)';
    default:
      return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  }
};

export const getStrengthLabel = (strength: 'weak' | 'moderate' | 'strong'): string => {
  const labels = {
    weak: '🔸 Weak Consensus',
    moderate: '🔶 Moderate Consensus', 
    strong: '🔷 Strong Consensus'
  };
  return labels[strength];
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 70) return '#4ade80';
  if (confidence >= 50) return '#fbbf24';
  return '#ef4444';
};

export const downloadJSON = (data: unknown, filename: string): void => {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const generateShareLink = (resultId: string): string => {
  return `${window.location.origin}/results/${resultId}`;
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
};

export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
