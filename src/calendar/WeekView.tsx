import { useState } from 'react';
import {
  format,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addWeeks,
  subWeeks,
  isSameDay,
  addHours,
  startOfDay,
  differenceInMinutes,
} from 'date-fns';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { CalendarEvent } from '@/types';

interface WeekViewProps {
  events: CalendarEvent[];
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
  onAddEvent: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);

export function WeekView({
  events,
  selectedDate,
  onSelectDate,
  onAddEvent,
  onEventClick,
}: WeekViewProps) {
  const [currentWeek, setCurrentWeek] = useState(startOfWeek(selectedDate));

  const weekStart = startOfWeek(currentWeek);
  const weekEnd = endOfWeek(currentWeek);
  const days = eachDayOfInterval({ start: weekStart, end: weekEnd });

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

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">
            {format(weekStart, 'MMM d')} - {format(weekEnd, 'MMM d, yyyy')}
          </h2>
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentWeek(subWeeks(currentWeek, 1))}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentWeek(addWeeks(currentWeek, 1))}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => setCurrentWeek(startOfWeek(new Date()))}
        >
          Today
        </Button>
      </div>

      {/* Weekday Headers */}
      <div className="grid grid-cols-8 gap-1 mb-2">
        <div className="text-center text-sm font-medium text-muted-foreground py-2">
          Time
        </div>
        {days.map((day) => (
          <div
            key={day.toISOString()}
            className={`
              text-center py-2 cursor-pointer rounded-lg transition-colors
              ${isSameDay(day, selectedDate) ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}
              ${isSameDay(day, new Date()) && !isSameDay(day, selectedDate) ? 'text-primary font-bold' : ''}
            `}
            onClick={() => onSelectDate(day)}
          >
            <div className="text-xs uppercase">{format(day, 'EEE')}</div>
            <div className="text-lg">{format(day, 'd')}</div>
          </div>
        ))}
      </div>

      {/* Time Grid */}
      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-8 gap-1 relative" style={{ minHeight: '1440px' }}>
          {/* Time Labels */}
          <div className="relative">
            {HOURS.map((hour) => (
              <div
                key={hour}
                className="absolute text-xs text-muted-foreground text-right pr-2"
                style={{ top: `${(hour / 24) * 100}%`, transform: 'translateY(-50%)' }}
              >
                {format(addHours(startOfDay(new Date()), hour), 'h a')}
              </div>
            ))}
          </div>

          {/* Day Columns */}
          {days.map((day) => {
            const dayEvents = getEventsForDay(day);

            return (
              <div
                key={day.toISOString()}
                className="relative border-l border-border"
              >
                {/* Hour Grid Lines */}
                {HOURS.map((hour) => (
                  <div
                    key={hour}
                    className="absolute w-full border-t border-border/50"
                    style={{ top: `${(hour / 24) * 100}%` }}
                  />
                ))}

                {/* Events */}
                {dayEvents.map((event) => {
                  const position = getEventPosition(event, day);
                  return (
                    <div
                      key={event.id}
                      className="absolute left-0 right-1 px-2 py-1 rounded text-xs cursor-pointer hover:opacity-80 overflow-hidden"
                      style={{
                        top: `${position.top}%`,
                        height: `${Math.max(position.height, 2)}%`,
                        backgroundColor: event.color + '30',
                        borderLeft: `3px solid ${event.color}`,
                      }}
                      onClick={() => onEventClick(event)}
                    >
                      <div className="font-medium truncate">{event.title}</div>
                      {!event.allDay && (
                        <div className="text-muted-foreground">
                          {format(new Date(event.startTime), 'h:mm a')} - {format(new Date(event.endTime), 'h:mm a')}
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Click to add */}
                <div
                  className="absolute inset-0 cursor-pointer"
                  onClick={() => onAddEvent(day)}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
