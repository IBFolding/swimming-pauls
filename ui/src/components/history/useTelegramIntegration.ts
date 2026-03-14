/**
 * useTelegramIntegration Hook
 * Manages Telegram bot settings and notifications
 */

import { useState, useEffect, useCallback } from 'react';
import type { TelegramSettings, TelegramNotification, HistoricalPrediction } from './types';

const TELEGRAM_SETTINGS_KEY = 'swimming-pauls-telegram-settings';
const TELEGRAM_NOTIFICATIONS_KEY = 'swimming-pauls-telegram-notifications';

const DEFAULT_SETTINGS: TelegramSettings = {
  enabled: false,
  botToken: '',
  chatId: '',
  notifyOnResolve: true,
  notifyOnCorrect: true,
  notifyOnWrong: true,
  includeLink: true,
};

export function useTelegramIntegration() {
  const [settings, setSettings] = useState<TelegramSettings>(DEFAULT_SETTINGS);
  const [notifications, setNotifications] = useState<TelegramNotification[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  // Load settings from localStorage
  useEffect(() => {
    const storedSettings = localStorage.getItem(TELEGRAM_SETTINGS_KEY);
    const storedNotifications = localStorage.getItem(TELEGRAM_NOTIFICATIONS_KEY);

    if (storedSettings) {
      try {
        const parsed = JSON.parse(storedSettings);
        setSettings({ ...DEFAULT_SETTINGS, ...parsed });
      } catch (e) {
        console.error('Failed to parse Telegram settings:', e);
      }
    }

    if (storedNotifications) {
      try {
        const parsed = JSON.parse(storedNotifications);
        setNotifications(parsed);
      } catch (e) {
        console.error('Failed to parse Telegram notifications:', e);
      }
    }

    setIsLoaded(true);
  }, []);

  // Save settings to localStorage
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(TELEGRAM_SETTINGS_KEY, JSON.stringify(settings));
    }
  }, [settings, isLoaded]);

  // Save notifications to localStorage
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(TELEGRAM_NOTIFICATIONS_KEY, JSON.stringify(notifications));
    }
  }, [notifications, isLoaded]);

  // Update settings
  const updateSettings = useCallback((newSettings: Partial<TelegramSettings>): void => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  // Test the Telegram connection
  const testConnection = useCallback(async (): Promise<boolean> => {
    if (!settings.botToken || !settings.chatId) {
      setTestResult({ success: false, message: 'Bot token and chat ID are required' });
      return false;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      const response = await fetch(`https://api.telegram.org/bot${settings.botToken}/getMe`);
      const data = await response.json();

      if (data.ok) {
        // Try to send a test message
        const testMessage = `🐟 *Swimming Pauls Test*\n\nYour Telegram integration is working!\nBot: @${data.result.username}`;
        
        const sendResponse = await fetch(`https://api.telegram.org/bot${settings.botToken}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: settings.chatId,
            text: testMessage,
            parse_mode: 'Markdown',
          }),
        });

        const sendData = await sendResponse.json();

        if (sendData.ok) {
          setTestResult({ success: true, message: `Connected to @${data.result.username}! Test message sent.` });
          return true;
        } else {
          setTestResult({ success: false, message: `Bot connected but failed to send message: ${sendData.description}` });
          return false;
        }
      } else {
        setTestResult({ success: false, message: `Invalid bot token: ${data.description}` });
        return false;
      }
    } catch (error) {
      setTestResult({ success: false, message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}` });
      return false;
    } finally {
      setIsTesting(false);
    }
  }, [settings.botToken, settings.chatId]);

  // Send a notification
  const sendNotification = useCallback(async (
    prediction: HistoricalPrediction
  ): Promise<boolean> => {
    if (!settings.enabled || !settings.botToken || !settings.chatId) {
      return false;
    }

    // Check notification preferences
    if (prediction.status === 'correct' && !settings.notifyOnCorrect) return false;
    if (prediction.status === 'wrong' && !settings.notifyOnWrong) return false;
    if (prediction.status === 'partial' && !settings.notifyOnResolve) return false;

    const notificationId = `${prediction.id}-${Date.now()}`;
    
    // Add to pending notifications
    const newNotification: TelegramNotification = {
      id: notificationId,
      predictionId: prediction.id,
      status: 'pending',
    };
    setNotifications(prev => [newNotification, ...prev]);

    // Build the message
    const isCorrect = prediction.status === 'correct';
    const isWrong = prediction.status === 'wrong';
    const isPartial = prediction.status === 'partial';

    const emoji = isCorrect ? '✅' : isWrong ? '❌' : '⚡';
    const title = isCorrect 
      ? (settings.customMessageCorrect || 'The Pauls were RIGHT') 
      : isWrong 
        ? (settings.customMessageWrong || 'The Pauls were WRONG')
        : 'The Pauls were PARTIALLY RIGHT';

    const consensusEmoji = prediction.result.consensus.direction === 'bullish' ? '📈' :
                          prediction.result.consensus.direction === 'bearish' ? '📉' : '➡️';

    let message = `${emoji} *${title}*\n\n`;
    message += `*Question:* ${prediction.question}\n\n`;
    message += `*Pauls Predicted:* ${consensusEmoji} ${prediction.result.consensus.direction.toUpperCase()}\n`;
    message += `*Confidence:* ${prediction.result.consensus.confidence}%\n\n`;

    if (prediction.actualOutcome) {
      message += `*Actual Outcome:* ${prediction.actualOutcome}\n\n`;
    }

    // Add accuracy stats
    if (prediction.paulPerformances) {
      const correctPauls = prediction.paulPerformances.filter(p => p.wasCorrect).length;
      const totalPauls = prediction.paulPerformances.length;
      message += `*Paul Accuracy:* ${correctPauls}/${totalPauls} correct\n\n`;
    }

    // Add link if configured
    if (settings.includeLink && settings.appUrl) {
      const link = `${settings.appUrl}/history/${prediction.id}`;
      message += `[View Full Results](${link})`;
    }

    try {
      const response = await fetch(`https://api.telegram.org/bot${settings.botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: settings.chatId,
          text: message,
          parse_mode: 'Markdown',
          disable_web_page_preview: true,
        }),
      });

      const data = await response.json();

      if (data.ok) {
        setNotifications(prev =>
          prev.map(n =>
            n.id === notificationId
              ? { ...n, status: 'sent', sentAt: new Date().toISOString() }
              : n
          )
        );
        return true;
      } else {
        setNotifications(prev =>
          prev.map(n =>
            n.id === notificationId
              ? { ...n, status: 'failed', error: data.description }
              : n
          )
        );
        return false;
      }
    } catch (error) {
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId
            ? { ...n, status: 'failed', error: error instanceof Error ? error.message : 'Unknown error' }
            : n
        )
      );
      return false;
    }
  }, [settings]);

  // Clear notification history
  const clearNotificationHistory = useCallback((): void => {
    if (confirm('Clear all notification history?')) {
      setNotifications([]);
    }
  }, []);

  // Reset settings to default
  const resetSettings = useCallback((): void => {
    if (confirm('Reset Telegram settings to default?')) {
      setSettings(DEFAULT_SETTINGS);
      setTestResult(null);
    }
  }, []);

  // Get notification history for a prediction
  const getNotificationsForPrediction = useCallback((predictionId: string): TelegramNotification[] => {
    return notifications.filter(n => n.predictionId === predictionId);
  }, [notifications]);

  return {
    settings,
    notifications,
    isLoaded,
    isTesting,
    testResult,
    updateSettings,
    testConnection,
    sendNotification,
    clearNotificationHistory,
    resetSettings,
    getNotificationsForPrediction,
  };
}
