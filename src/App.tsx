import { useState } from 'react';
import { format } from 'date-fns';
import { Header } from '@/components/Header';
import { AuthDialog } from '@/components/AuthDialog';
import { MonthView } from '@/calendar/MonthView';
import { WeekView } from '@/calendar/WeekView';
import { DayView } from '@/calendar/DayView';
import { EventDialog } from '@/calendar/EventDialog';
import { AIAssistant } from '@/ai/AIAssistant';
import { useCalendar } from '@/hooks/useCalendar';
import { useAuth } from '@/hooks/useAuth';
import type { CalendarView, CalendarEvent, CreateEventRequest } from '@/types';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';

function App() {
  const [currentView, setCurrentView] = useState<CalendarView>('month');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isEventDialogOpen, setIsEventDialogOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);
  const [eventDialogDate, setEventDialogDate] = useState<Date | undefined>();

  const { isAuthenticated } = useAuth();
  const {
    events,
    isLoading,
    error,
    createEvent,
    updateEvent,
    deleteEvent,
    refreshEvents,
  } = useCalendar(currentView, selectedDate);

  const handleAddEvent = (date?: Date) => {
    if (!isAuthenticated) {
      setIsAuthOpen(true);
      toast.error('Please sign in to add events');
      return;
    }
    setEditingEvent(null);
    setEventDialogDate(date || selectedDate);
    setIsEventDialogOpen(true);
  };

  const handleEditEvent = (event: CalendarEvent) => {
    setEditingEvent(event);
    setEventDialogDate(undefined);
    setIsEventDialogOpen(true);
  };

  const handleSaveEvent = async (eventData: CreateEventRequest) => {
    try {
      await createEvent(eventData);
      toast.success('Event created successfully');
      refreshEvents();
    } catch (err) {
      toast.error('Failed to create event');
    }
  };

  const handleUpdateEvent = async (id: string, eventData: Partial<CreateEventRequest>) => {
    try {
      await updateEvent(id, eventData);
      toast.success('Event updated successfully');
      refreshEvents();
    } catch (err) {
      toast.error('Failed to update event');
    }
  };

  const handleDeleteEvent = async (id: string) => {
    try {
      await deleteEvent(id);
      toast.success('Event deleted successfully');
      refreshEvents();
    } catch (err) {
      toast.error('Failed to delete event');
    }
  };

  const renderCalendarView = () => {
    const props = {
      events,
      selectedDate,
      onSelectDate: setSelectedDate,
      onAddEvent: handleAddEvent,
      onEventClick: handleEditEvent,
    };

    switch (currentView) {
      case 'month':
        return <MonthView {...props} />;
      case 'week':
        return <WeekView {...props} />;
      case 'day':
        return <DayView {...props} />;
      default:
        return <MonthView {...props} />;
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header
        currentView={currentView}
        onViewChange={setCurrentView}
        onOpenAuth={() => setIsAuthOpen(true)}
      />

      <main className="flex-1 container mx-auto px-4 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-96 text-destructive">
            {error}
          </div>
        ) : (
          <div className="h-[calc(100vh-140px)]">{renderCalendarView()}</div>
        )}
      </main>

      <AuthDialog isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />

      <EventDialog
        event={editingEvent}
        isOpen={isEventDialogOpen}
        onClose={() => setIsEventDialogOpen(false)}
        onSave={handleSaveEvent}
        onUpdate={handleUpdateEvent}
        onDelete={handleDeleteEvent}
        initialDate={eventDialogDate}
      />

      {isAuthenticated && <AIAssistant selectedDate={selectedDate} events={events} />}

      <Toaster position="top-right" />
    </div>
  );
}

export default App;
