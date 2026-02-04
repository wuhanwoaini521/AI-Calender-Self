import { useState, useEffect, useCallback } from 'react';
import type { CalendarEvent, CreateEventRequest, CalendarView } from '@/types';
import { api } from '@/services/api';
import { format } from 'date-fns';

export function useCalendar(view: CalendarView, selectedDate: Date) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      const data = await api.getEvents(view, dateStr);
      setEvents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch events');
    } finally {
      setIsLoading(false);
    }
  }, [view, selectedDate]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const createEvent = async (event: CreateEventRequest) => {
    try {
      const newEvent = await api.createEvent(event);
      setEvents((prev) => [...prev, newEvent]);
      return newEvent;
    } catch (err) {
      throw err;
    }
  };

  const updateEvent = async (id: string, event: Partial<CreateEventRequest>) => {
    try {
      const updatedEvent = await api.updateEvent(id, event);
      setEvents((prev) =>
        prev.map((e) => (e.id === id ? updatedEvent : e))
      );
      return updatedEvent;
    } catch (err) {
      throw err;
    }
  };

  const deleteEvent = async (id: string) => {
    try {
      await api.deleteEvent(id);
      setEvents((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      throw err;
    }
  };

  return {
    events,
    isLoading,
    error,
    refreshEvents: fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent,
  };
}
