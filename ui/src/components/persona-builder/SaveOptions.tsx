import React, { useState, useCallback } from 'react';
import { PaulPersona, STORAGE_KEYS } from './types';
import { 
  Save, 
  Download, 
  Github, 
  Check, 
  AlertCircle,
  Loader2,
  Share2,
  Upload,
  Copy,
  ExternalLink
} from 'lucide-react';

interface SaveOptionsProps {
  paul: PaulPersona | null;
  onSave: (paul: PaulPersona) => void;
  existingPauls?: PaulPersona[];
}

export const SaveOptions: React.FC<SaveOptionsProps> = ({ 
  paul, 
  onSave,
  existingPauls = []
}) => {
  const [activeTab, setActiveTab] = useState<'local' | 'export' | 'github' | 'share'>('local');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [githubToken, setGithubToken] = useState('');
  const [githubRepo, setGithubRepo] = useState('');
  const [githubPath, setGithubPath] = useState('data/custom-pauls.json');
  const [isGitHubSaving, setIsGitHubSaving] = useState(false);
  const [githubStatus, setGithubStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);

  // Save to localStorage
  const saveToLocal = useCallback(() => {
    if (!paul) return;
    
    setIsSaving(true);
    
    try {
      // Get existing custom Pauls
      const existing = localStorage.getItem(STORAGE_KEYS.CUSTOM_PAULS);
      const customPauls: PaulPersona[] = existing ? JSON.parse(existing) : [];
      
      // Check if updating existing or creating new
      const existingIndex = customPauls.findIndex(p => p.id === paul.id);
      
      if (existingIndex >= 0) {
        customPauls[existingIndex] = { ...paul, updatedAt: new Date().toISOString() };
      } else {
        customPauls.push({ ...paul, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() });
      }
      
      localStorage.setItem(STORAGE_KEYS.CUSTOM_PAULS, JSON.stringify(customPauls));
      
      setSaveSuccess(true);
      onSave(paul);
      
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    } finally {
      setIsSaving(false);
    }
  }, [paul, onSave]);

  // Export as JSON
  const exportAsJSON = useCallback(() => {
    if (!paul) return;
    
    const dataStr = JSON.stringify(paul, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${paul.name.toLowerCase().replace(/\s+/g, '-')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }, [paul]);

  // Export all Pauls as JSON
  const exportAllAsJSON = useCallback(() => {
    const allPauls = [...existingPauls];
    if (paul && !allPauls.find(p => p.id === paul.id)) {
      allPauls.push(paul);
    }
    
    const dataStr = JSON.stringify(allPauls, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `swimming-pauls-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }, [existingPauls, paul]);

  // Save to GitHub
  const saveToGitHub = useCallback(async () => {
    if (!paul || !githubToken || !githubRepo) {
      setGithubStatus({ type: 'error', message: 'Please provide GitHub token and repository' });
      return;
    }
    
    setIsGitHubSaving(true);
    setGithubStatus(null);
    
    try {
      // Parse owner/repo
      const [owner, repo] = githubRepo.split('/');
      if (!owner || !repo) {
        throw new Error('Repository must be in format: owner/repo');
      }
      
      // First, try to get existing file to get SHA
      let existingSha: string | undefined;
      let existingContent: PaulPersona[] = [];
      
      try {
        const getResponse = await fetch(
          `https://api.github.com/repos/${owner}/${repo}/contents/${githubPath}`,
          {
            headers: {
              'Authorization': `token ${githubToken}`,
              'Accept': 'application/vnd.github.v3+json'
            }
          }
        );
        
        if (getResponse.ok) {
          const data = await getResponse.json();
          existingSha = data.sha;
          const content = atob(data.content);
          existingContent = JSON.parse(content);
        }
      } catch (e) {
        // File doesn't exist yet, that's ok
      }
      
      // Add or update the Paul
      const existingIndex = existingContent.findIndex(p => p.id === paul.id);
      if (existingIndex >= 0) {
        existingContent[existingIndex] = { ...paul, updatedAt: new Date().toISOString() };
      } else {
        existingContent.push({ ...paul, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() });
      }
      
      // Save back to GitHub
      const content = btoa(JSON.stringify(existingContent, null, 2));
      
      const response = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${githubPath}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `token ${githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: `Update custom Pauls: Add/Update ${paul.name}`,
            content,
            sha: existingSha
          })
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to save to GitHub');
      }
      
      // Successfully saved
      setGithubStatus({ 
        type: 'success', 
        message: `Successfully saved to ${githubPath}`,
      });
      
      // Store credentials for next time
      localStorage.setItem(STORAGE_KEYS.GITHUB_TOKEN, githubToken);
      localStorage.setItem(STORAGE_KEYS.GITHUB_REPO, githubRepo);
      
      onSave(paul);
    } catch (error: any) {
      setGithubStatus({ type: 'error', message: error.message || 'Failed to save to GitHub' });
    } finally {
      setIsGitHubSaving(false);
    }
  }, [paul, githubToken, githubRepo, githubPath, onSave]);

  // Generate share URL
  const generateShareUrl = useCallback(() => {
    if (!paul) return;
    
    const paulData = btoa(JSON.stringify(paul));
    const url = `${window.location.origin}${window.location.pathname}?paul=${paulData}`;
    setShareUrl(url);
  }, [paul]);

  // Copy to clipboard
  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [shareUrl]);

  if (!paul) {
    return (
      <div className="glass-card p-6 text-center">
        <AlertCircle size={48} className="mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400">Create a Paul to see save options</p>
      </div>
    );
  }

  return (
    <div className="glass-card">
      {/* Tabs */}
      <div className="flex border-b border-dark-600">
        {[
          { id: 'local', label: 'Save Local', icon: Save },
          { id: 'export', label: 'Export JSON', icon: Download },
          { id: 'github', label: 'GitHub', icon: Github },
          { id: 'share', label: 'Share', icon: Share2 },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as any)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 text-sm font-medium transition-all ${
              activeTab === id
                ? 'text-accent-cyan border-b-2 border-accent-cyan bg-accent-blue/10'
                : 'text-gray-400 hover:text-white hover:bg-dark-700/50'
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      <div className="p-6">
        {/* Local Save */}
        {activeTab === 'local' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Save this Paul to your browser's local storage. 
              It will be available even after you close the page.
            </p>
            
            <button
              onClick={saveToLocal}
              disabled={isSaving}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              {isSaving ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Saving...
                </>
              ) : saveSuccess ? (
                <>
                  <Check size={18} />
                  Saved Successfully!
                </>
              ) : (
                <>
                  <Save size={18} />
                  Save to Local Storage
                </>
              )}
            </button>
            
            {saveSuccess && (
              <p className="text-sm text-green-400 text-center">
                Paul saved! You can view it in the gallery.
              </p>
            )}
          </div>
        )}

        {/* Export JSON */}
        {activeTab === 'export' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Export your Paul as a JSON file that can be imported later or shared with others.
            </p>
            
            <div className="space-y-2">
              <button
                onClick={exportAsJSON}
                className="w-full btn-secondary flex items-center justify-center gap-2"
              >
                <Download size={18} />
                Export {paul.name}.json
              </button>
              
              <button
                onClick={exportAllAsJSON}
                className="w-full btn-secondary flex items-center justify-center gap-2"
              >
                <Download size={18} />
                Export All Pauls
              </button>
            </div>
            
            <div className="p-3 bg-dark-900/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Upload size={14} className="text-gray-500" />
                <span className="text-xs text-gray-500">Import Paul</span>
              </div>
              <input
                type="file"
                accept=".json"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      try {
                        const importedPaul = JSON.parse(event.target?.result as string);
                        onSave(importedPaul);
                        alert(`Imported ${importedPaul.name}!`);
                      } catch (err) {
                        alert('Failed to import Paul. Invalid JSON file.');
                      }
                    };
                    reader.readAsText(file);
                  }
                }}
                className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-dark-700 file:text-gray-300 hover:file:bg-dark-600"
              />
            </div>
          </div>
        )}

        {/* GitHub Integration */}
        {activeTab === 'github' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Save your Paul directly to a GitHub repository. 
              Requires a personal access token with repo permissions.
            </p>
            
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">GitHub Token</label>
                <input
                  type="password"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxx"
                  className="w-full px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-white placeholder:text-gray-600"
                />
              </div>
              
              <div>
                <label className="block text-xs text-gray-500 mb-1">Repository (owner/repo)</label>
                <input
                  type="text"
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                  placeholder="username/swimming-pauls"
                  className="w-full px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-white placeholder:text-gray-600"
                />
              </div>
              
              <div>
                <label className="block text-xs text-gray-500 mb-1">File Path</label>
                <input
                  type="text"
                  value={githubPath}
                  onChange={(e) => setGithubPath(e.target.value)}
                  placeholder="data/custom-pauls.json"
                  className="w-full px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-white placeholder:text-gray-600"
                />
              </div>
            </div>
            
            <button
              onClick={saveToGitHub}
              disabled={isGitHubSaving || !githubToken || !githubRepo}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              {isGitHubSaving ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Committing...
                </>
              ) : (
                <>
                  <Github size={18} />
                  Commit to Repository
                  <ExternalLink size={14} />
                </>
              )}
            </button>
            
            {githubStatus && (
              <div className={`flex items-center gap-2 p-3 rounded-lg ${
                githubStatus.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
              }`}>
                {githubStatus.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                <span className="text-sm">{githubStatus.message}</span>
              </div>
            )}
          </div>
        )}

        {/* Share */}
        {activeTab === 'share' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Generate a shareable link to this Paul. Anyone with the link can import it.
            </p>
            
            {!shareUrl ? (
              <button
                onClick={generateShareUrl}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                <Share2 size={18} />
                Generate Share Link
              </button>
            ) : (
              <div className="space-y-3">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={shareUrl}
                    readOnly
                    className="flex-1 px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg text-sm text-gray-300 truncate"
                  />
                  <button
                    onClick={copyToClipboard}
                    className="px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors"
                  >
                    {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                  </button>
                </div>
                
                {copied && (
                  <p className="text-sm text-green-400 text-center">Copied to clipboard!</p>
                )}
                
                <button
                  onClick={() => setShareUrl('')}
                  className="w-full text-sm text-gray-500 hover:text-gray-300"
                >
                  Generate new link
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SaveOptions;
