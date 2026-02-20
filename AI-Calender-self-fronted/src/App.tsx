import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DayCard } from '@/components/DayCard';
import { DayDetail } from '@/components/DayDetail';
import { ChatInput } from '@/components/ChatInput';
import { chatApi, eventApi } from '@/services/api';
import type {
  DayEvents,
  CalendarEvent,
  UpdateEventRequest,
  ChatMessage,
} from '@/types';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';

function groupEventsByDay(events: CalendarEvent[]): DayEvents[] {
  const groups: Map<string, CalendarEvent[]> = new Map();

  events.forEach((event) => {
    const date = new Date(event.start_time);
    const dateKey = date.toISOString().split('T')[0];
    
    if (!groups.has(dateKey)) {
      groups.set(dateKey, []);
    }
    groups.get(dateKey)!.push(event);
  });

  const sortedGroups = Array.from(groups.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([dateKey, dayEvents]) => {
      const date = new Date(dateKey);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      const dateTime = date.getTime();
      const isToday = dateTime === today.getTime();
      const isTomorrow = dateTime === tomorrow.getTime();

      return {
        date: dateKey,
        displayDate: date.toLocaleDateString('zh-CN', {
          month: 'short',
          day: 'numeric',
          weekday: 'short',
        }),
        events: dayEvents.sort((a, b) => 
          new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
        ),
        isToday,
        isTomorrow,
      };
    });

  return sortedGroups;
}

function App() {
  const [dayEvents, setDayEvents] = useState<DayEvents[]>([]);
  const [selectedDay, setSelectedDay] = useState<DayEvents | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<ChatMessage[]>([]);
  const [activeCardIndex, setActiveCardIndex] = useState<number | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = useCallback(async () => {
    try {
      const events = await eventApi.getEvents();
      const grouped = groupEventsByDay(events);
      setDayEvents(grouped);
    } catch (error) {
      console.error('Failed to load events:', error);
    }
  }, []);

  const scrollToEnd = useCallback(() => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      container.scrollTo({
        left: container.scrollWidth,
        behavior: 'smooth',
      });
    }
  }, []);

  const handleSendMessage = async (message: string) => {
    setIsLoading(true);

    const updatedHistory: ChatMessage[] = [
      ...conversationHistory,
      { role: 'user', content: message },
    ];
    setConversationHistory(updatedHistory);

    try {
      const response = await chatApi.sendMessage({
        message,
        conversation_history: conversationHistory,
      });

      setConversationHistory([
        ...updatedHistory,
        { role: 'assistant', content: response.message },
      ]);

      await loadEvents();

      if (response.tool_calls?.some((t) => t.name === 'list_events')) {
        setTimeout(scrollToEnd, 300);
      }

      if (response.events_modified && response.events_modified.length > 0) {
        setActiveCardIndex(dayEvents.length);
        setTimeout(() => setActiveCardIndex(null), 2000);
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateEvent = async (id: string, data: UpdateEventRequest) => {
    try {
      await eventApi.updateEvent(id, data);
      await loadEvents();
    } catch (error) {
      console.error('Failed to update event:', error);
    }
  };

  const handleDeleteEvent = async (id: string) => {
    try {
      await eventApi.deleteEvent(id);
      await loadEvents();
    } catch (error) {
      console.error('Failed to delete event:', error);
    }
  };

  const handleOpenDetail = (dayEvent: DayEvents) => {
    setSelectedDay(dayEvent);
    setIsDetailOpen(true);
  };

  const handleScroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const scrollAmount = 320;
      container.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="relative min-h-screen bg-white text-black overflow-hidden">
      {/* 极简液态背景 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-black liquid-blob" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-black liquid-blob-slow" />
      </div>

      {/* 主内容 */}
      <div className="relative z-10 flex flex-col h-screen">
        {/* 头部 */}
        <motion.header
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between px-8 py-6 border-b-2 border-black"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-black text-white flex items-center justify-center sketchy-border-rough">
              <span className="text-xl font-bold">AI</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold">Calendar</h1>
              <p className="text-black/50 text-sm">智能日程助手</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="px-4 py-2 border-2 border-black bg-white">
              <span className="text-sm font-medium">
                {dayEvents.length} 天 · {dayEvents.reduce((sum, d) => sum + d.events.length, 0)} 事件
              </span>
            </div>
            <button
              onClick={loadEvents}
              className="w-11 h-11 flex items-center justify-center border-2 border-black bg-white hover:bg-black hover:text-white transition-colors"
              style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </motion.header>

        {/* 卡片滚动区域 */}
        <div className="flex-1 relative">
          {/* 左滚动按钮 */}
          <button
            onClick={() => handleScroll('left')}
            className="absolute left-6 top-1/2 -translate-y-1/2 z-20 w-12 h-12 sketchy-btn flex items-center justify-center"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* 右滚动按钮 */}
          <button
            onClick={() => handleScroll('right')}
            className="absolute right-6 top-1/2 -translate-y-1/2 z-20 w-12 h-12 sketchy-btn flex items-center justify-center"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          {/* 滚动容器 */}
          <div
            ref={scrollContainerRef}
            className="h-full overflow-x-auto overflow-y-hidden scrollbar-hide"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            <div className={`flex items-center h-full px-24 gap-8 ${dayEvents.length <= 1 ? 'justify-center w-full' : 'min-w-max'}`}>
              <AnimatePresence mode="popLayout">
                {dayEvents.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center justify-center text-black/30"
                  >
                    <div className="w-32 h-32 border-2 border-black flex items-center justify-center mb-6" style={{ borderRadius: '2% 98% 2% 98% / 98% 2% 98% 2%' }}>
                      <svg className="w-16 h-16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                      </svg>
                    </div>
                    <p className="text-xl font-medium mb-2">暂无日程</p>
                    <p className="text-sm">在下方输入指令开始创建</p>
                  </motion.div>
                ) : (
                  dayEvents.map((day, index) => (
                    <motion.div
                      key={day.date}
                      layout
                      initial={{ opacity: 0, x: 100, scale: 0.8 }}
                      animate={{ 
                        opacity: 1, 
                        x: 0, 
                        scale: activeCardIndex === index ? 1.02 : 1,
                      }}
                      exit={{ opacity: 0, x: -100, scale: 0.8 }}
                      transition={{ 
                        type: 'spring',
                        stiffness: 200,
                        damping: 20,
                        delay: index * 0.08,
                      }}
                    >
                      <DayCard
                        dayEvents={day}
                        index={index}
                        isActive={activeCardIndex === index}
                        onClick={() => handleOpenDetail(day)}
                      />
                    </motion.div>
                  ))
                )}
              </AnimatePresence>

              {dayEvents.length > 1 && <div className="w-20 shrink-0" />}
            </div>
          </div>
        </div>

        {/* 底部输入区域 */}
        <div className="relative z-20 px-8 pb-8 pt-4 border-t-2 border-black bg-white">
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>

      {/* 详情弹窗 */}
      <DayDetail
        dayEvents={selectedDay}
        isOpen={isDetailOpen}
        onClose={() => {
          setIsDetailOpen(false);
          setSelectedDay(null);
        }}
        onUpdateEvent={handleUpdateEvent}
        onDeleteEvent={handleDeleteEvent}
      />
    </div>
  );
}

export default App;
