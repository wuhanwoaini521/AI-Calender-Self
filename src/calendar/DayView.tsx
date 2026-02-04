import { useState } from 'react';
import {
  format,
  addHours,
  startOfDay,
  differenceInMinutes,
  isSameDay,
  addDays,
  subDays,
} from 'date-fns';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { CalendarEvent } from '@/types';

interface DayViewProps {
  events: CalendarEvent[];
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
  onAddEvent: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);

export function DayView({
  events,
  selectedDate,
  onSelectDate,
  onAddEvent,
  onEventClick,
}: DayViewProps) {
  const [currentDate, setCurrentDate] = useState(selectedDate);

  const getEventsForDay = (day: Date) => {
    return events.filter((event) => {
      const eventStart = new Date(event.startTime);
      const eventEnd = new Date(event.endTime);
      return (
        isSameDay(eventStart, day) ||
        isSameDay(eventEnd, day) ||
        (eventStart < day && eventEnd > day)
      );
    });
  };

  const getEventPosition = (event: CalendarEvent, day: Date) => {
    const dayStart = startOfDay(day);
    const eventStart = new Date(event.startTime);
    const eventEnd = new Date(event.endTime);
    
    const startMinutes = Math.max(0, differenceInMinutes(eventStart, dayStart));
    const endMinutes = Math.min(24 * 60, differenceInMinutes(eventEnd, dayStart));
    const duration = endMinutes - startMinutes;
    
    return {
      top: (startMinutes / (24 * 60)) * 100,
      height: (duration / (24 * 60)) * 100,
    };
  };

  const dayEvents = getEventsForDay(currentDate);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">
            {format(currentDate, 'EEEE, MMMM d, yyyy')}
          </h2>
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentDate(subDays(currentDate, 1))}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentDate(addDays(currentDate, 1))}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setCurrentDate(new Date())}
          >
            Today
          </Button>
          <Button onClick={() => onAddEvent(currentDate)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Event
          </Button>
        </div>
      </div>

      {/* Time Grid */}
      <div className="flex-1 overflow-auto">
        <div className="relative" style={{ minHeight: '1440px' }}>
          {/* Time Labels and Grid */}
          {HOURS.map((hour) => (
            <div
              key={hour}
              className="absolute w-full flex"
              style={{ top: `${(hour / 24) * 100}%` }}
            >
              <div className="w-16 text-xs text-muted-foreground text-right pr-4">
                {format(addHours(startOfDay(new Date()), hour), 'h a')}
              </div>
              <div className="flex-1 border-t border-border/50" />
            </div>
          ))}

          {/* Events */}
          <div className="absolute left-16 right-0 top-0 bottom-0">
            {dayEvents.map((event) => {
              const position = getEventPosition(event, currentDate);
              return (
                <div
                  key={event.id}
                  className="absolute left-2 right-2 px-4 py-2 rounded-lg cursor-pointer hover:opacity-80 overflow-hidden shadow-sm"
                  style={{
                    top: `${position.top}%`,
                    height: `${Math.max(position.height, 3)}%`,
                    backgroundColor: event.color + '20',
                    borderLeft: `4px solid ${event.color}`,
                  }}
                  onClick={() => onEventClick(event)}
                >
                  <div className="font-semibold text-sm">{event.title}</div>
                  {!event.allDay && (
                    <div className="text-xs text-muted-foreground">
                      {format(new Date(event.startTime), 'h:mm a')} - {format(new Date(event.endTime), 'h:mm a')}
                    </div>
                  )}
                  {event.location && (
                    <div className="text-xs text-muted-foreground mt-1">
                      📍 {event.location}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Click to add */}
          <div
            className="absolute left-16 right-0 top-0 bottom-0 cursor-pointer"
            onClick={() => onAddEvent(currentDate)}
          />
        </div>
      </div>
    </div>
  );
}
