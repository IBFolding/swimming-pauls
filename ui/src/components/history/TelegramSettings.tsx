/**
 * TelegramSettings Component
 * Settings panel for Telegram bot integration
 */

import React, { useState } from 'react';
import type { TelegramSettings as TelegramSettingsType, TelegramNotification } from '../types';
import { cn } from '../../../utils';

interface TelegramSettingsProps {
  settings: TelegramSettingsType;
  notifications: TelegramNotification[];
  isTesting: boolean;
  testResult: { success: boolean; message: string } | null;
  onUpdateSettings: (settings: Partial<TelegramSettingsType>) => void;
  onTestConnection: () => Promise<void>;
  onClearHistory: () => void;
  onResetSettings: () => void;
}

export const TelegramSettingsPanel: React.FC<TelegramSettingsProps> = ({
  settings,
  notifications,
  isTesting,
  testResult,
  onUpdateSettings,
  onTestConnection,
  onClearHistory,
  onResetSettings,
}) => {
  const [showToken, setShowToken] = useState(false);

  return (
    <div className="space-y-6">
      {/* Enable Toggle */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold">📱 Telegram Notifications</h3>
            <p className="text-sm text-gray-400">
              Get notified when predictions are resolved
            </p>
          </div>
          
          <button
            onClick={() => onUpdateSettings({ enabled: !settings.enabled })}
            className={cn(
              "w-14 h-8 rounded-full transition-colors relative",
              settings.enabled ? "bg-accent-blue" : "bg-dark-600"
            )}
          >
            <span className={cn(
              "absolute top-1 w-6 h-6 rounded-full bg-white transition-all",
              settings.enabled ? "left-7" : "left-1"
            )}
          />
          </button>
        </div>
      </div>

      {settings.enabled && (
        <>
          {/* Bot Configuration */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold mb-4">🤖 Bot Configuration</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Bot Token
                  <a 
                    href="https://t.me/BotFather" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-accent-blue hover:underline ml-2"
                  >
                    Get from @BotFather →
                  </a>
                </label>
                
                <div className="relative">
                  <input
                    type={showToken ? "text" : "password"}
                    value={settings.botToken}
                    onChange={(e) => onUpdateSettings({ botToken: e.target.value })}
                    placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                    className="input-field pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowToken(!showToken)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                  >
                    {showToken ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Chat ID
                  <a 
                    href="https://t.me/userinfobot" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-accent-blue hover:underline ml-2"
                  >
                    Get from @userinfobot →
                  </a>
                </label>
                
                <input
                  type="text"
                  value={settings.chatId}
                  onChange={(e) => onUpdateSettings({ chatId: e.target.value })}
                  placeholder="123456789 or @channelusername"
                  className="input-field"
                />
              </div>

              <button
                onClick={onTestConnection}
                disabled={isTesting || !settings.botToken || !settings.chatId}
                className="btn-secondary w-full"
              >
                {isTesting ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    Testing...
                  </span>
                ) : (
                  '🧪 Test Connection'
                )}
              </button>

              {testResult && (
                <div className={cn(
                  "p-3 rounded-lg text-sm",
                  testResult.success ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                )}
                >
                  {testResult.message}
                </div>
              )}
            </div>
          </div>

          {/* Notification Preferences */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold mb-4">🔔 Notification Preferences</h3>
            
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg bg-dark-700/50 cursor-pointer">
                <span>Notify on correct predictions</span>
                <input
                  type="checkbox"
                  checked={settings.notifyOnCorrect}
                  onChange={(e) => onUpdateSettings({ notifyOnCorrect: e.target.checked })}
                  className="w-5 h-5 accent-accent-blue"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg bg-dark-700/50 cursor-pointer">
                <span>Notify on wrong predictions</span>
                <input
                  type="checkbox"
                  checked={settings.notifyOnWrong}
                  onChange={(e) => onUpdateSettings({ notifyOnWrong: e.target.checked })}
                  className="w-5 h-5 accent-accent-blue"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg bg-dark-700/50 cursor-pointer">
                <span>Include link to full results</span>
                <input
                  type="checkbox"
                  checked={settings.includeLink}
                  onChange={(e) => onUpdateSettings({ includeLink: e.target.checked })}
                  className="w-5 h-5 accent-accent-blue"
                />
              </label>
            </div>

            {settings.includeLink && (
              <div className="mt-4">
                <label className="block text-sm text-gray-400 mb-2">App URL</label>
                <input
                  type="text"
                  value={settings.appUrl || ''}
                  onChange={(e) => onUpdateSettings({ appUrl: e.target.value })}
                  placeholder="https://swimmingpauls.example.com"
                  className="input-field"
                />
              </div>
            )}
          </div>

          {/* Custom Messages */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold mb-4">💬 Custom Messages (Optional)</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Correct prediction message
                </label>
                <input
                  type="text"
                  value={settings.customMessageCorrect || ''}
                  onChange={(e) => onUpdateSettings({ customMessageCorrect: e.target.value })}
                  placeholder="The Pauls were RIGHT about [question]"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Wrong prediction message
                </label>
                <input
                  type="text"
                  value={settings.customMessageWrong || ''}
                  onChange={(e) => onUpdateSettings({ customMessageWrong: e.target.value })}
                  placeholder="The Pauls were WRONG about [question]"
                  className="input-field"
                />
              </div>
            </div>
          </div>

          {/* Notification History */}
          {notifications.length > 0 && (
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">📨 Notification History</h3>
                <button
                  onClick={onClearHistory}
                  className="text-sm text-red-400 hover:underline"
                >
                  Clear History
                </button>
              </div>

              <div className="space-y-2 max-h-48 overflow-y-auto">
                {notifications.slice(0, 20).map((notif) => (
                  <div 
                    key={notif.id}
                    className="flex items-center justify-between p-2 rounded-lg bg-dark-700/30 text-sm"
                  >
                    <span className="truncate flex-1">
                      {notif.predictionId.slice(0, 8)}...
                    </span>
                    
                    <span className={cn(
                      "px-2 py-0.5 rounded text-xs",
                      notif.status === 'sent' && "bg-green-500/20 text-green-400",
                      notif.status === 'pending' && "bg-yellow-500/20 text-yellow-400",
                      notif.status === 'failed' && "bg-red-500/20 text-red-400"
                    )}>
                      {notif.status}
                    </span>

                    {notif.sentAt && (
                      <span className="text-xs text-gray-500">
                        {new Date(notif.sentAt).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Reset */}
      <div className="glass-card p-6">
        <button
          onClick={onResetSettings}
          className="text-red-400 hover:text-red-300 text-sm"
        >
          Reset all Telegram settings to default
        </button>
      </div>
    </div>
  );
};
