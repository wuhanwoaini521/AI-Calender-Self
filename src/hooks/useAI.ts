import { useState, useCallback } from 'react';
import { api } from '@/services/api';
import type { CalendarEvent } from '@/types';

export function useAI() {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);

  const chat = useCallback(async (message: string, context?: { currentDate?: string; selectedDate?: string; events?: CalendarEvent[] }) => {
    setIsLoading(true);
    try {
      setMessages((prev) => [...prev, { role: 'user', content: message }]);
      const response = await api.chat(message, context);
      setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
      return response;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getSuggestions = useCallback(async (date?: string) => {
    setIsLoading(true);
    try {
      return await api.getSuggestions(date);
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    isLoading,
    messages,
    chat,
    getSuggestions,
    clearMessages,
  };
}
