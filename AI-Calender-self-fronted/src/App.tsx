import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DayCard } from '@/components/DayCard';
import { DayDetail } from '@/components/DayDetail';
import { ChatInput } from '@/components/ChatInput';
import { MessageBubble } from '@/components/MessageBubble';
import { MonthView } from '@/components/MonthView';
import { chatApi, eventApi } from '@/services/api';
import type {
  DayEvents,
  CalendarEvent,
  UpdateEventRequest,
  ChatMessage,
  ToolCall,
} from '@/types';
import { ChevronLeft, ChevronRight, RefreshCw, Trash2, ChevronUp, MessageSquare, LayoutGrid, Rows3 } from 'lucide-react';

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
  // const [lastToolCalls, setLastToolCalls] = useState<ToolCall[] | undefined>(undefined);
  const [messageToolCalls, setMessageToolCalls] = useState<Map<number, ToolCall[]>>(new Map());
  const [isChatExpanded, setIsChatExpanded] = useState(true);
  const [viewMode, setViewMode] = useState<'timeline' | 'month'>('timeline');
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadEvents();
  }, []);

  // 当 dayEvents 更新时，自动更新 selectedDay 以保持弹窗数据同步
  useEffect(() => {
    if (selectedDay && isDetailOpen) {
      const updatedDay = dayEvents.find(day => day.date === selectedDay.date);
      if (updatedDay) {
        setSelectedDay(updatedDay);
      } else {
        setSelectedDay({
          ...selectedDay,
          events: [],
        });
      }
    }
  }, [dayEvents, selectedDay?.date, isDetailOpen]);

  const loadEvents = useCallback(async (): Promise<DayEvents[]> => {
    try {
      const events = await eventApi.getEvents();
      console.log('Loaded events:', events);
      const grouped = groupEventsByDay(events);
      console.log('Grouped events:', grouped);
      setDayEvents(grouped);
      return grouped;
    } catch (error) {
      console.error('Failed to load events:', error);
      return [];
    }
  }, []);



  // 滚动消息到底部
  const scrollMessagesToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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

      const newMessageIndex = updatedHistory.length;
      setConversationHistory([
        ...updatedHistory,
        { role: 'assistant', content: response.message },
      ]);
      
      // 保存工具调用信息用于显示（按消息索引）
      setMessageToolCalls(prev => {
        const newMap = new Map(prev);
        newMap.set(newMessageIndex, response.tool_calls || []);
        return newMap;
      });
      
      // 同时保留最后一次的工具调用
      // setLastToolCalls(response.tool_calls);
      
      // 调试日志
      console.log('Chat response:', {
        message: response.message,
        tool_calls: response.tool_calls,
        events_modified: response.events_modified
      });
      
      // 检查是否有创建事件
      if (response.tool_calls) {
        response.tool_calls.forEach((tool, i) => {
          console.log(`Tool ${i}:`, tool.name, tool.input);
        });
      }

      // 重新加载事件列表
      const updatedDayEvents = await loadEvents();

      // 如果有创建或删除事件，智能滚动到对应位置
      if (response.tool_calls && response.tool_calls.length > 0) {
        const hasCreateEvent = response.tool_calls.some((t) => t.name === 'create_event');
        const hasDeleteEvent = response.tool_calls.some((t) => t.name === 'delete_event');
        
        if (hasCreateEvent && updatedDayEvents.length > 0) {
          // 找到新创建事件的日期索引
          let targetIndex = updatedDayEvents.length - 1; // 默认最后一天
          
          // 如果有 events_modified，尝试找到对应的日期位置
          if (response.events_modified && response.events_modified.length > 0) {
            const createdEventId = response.events_modified[0];
            // 在 updatedDayEvents 中找到包含该事件的日期
            const eventDayIndex = updatedDayEvents.findIndex(day => 
              day.events.some(event => event.id === createdEventId)
            );
            if (eventDayIndex !== -1) {
              targetIndex = eventDayIndex;
            }
          }
          
          setTimeout(() => {
            if (scrollContainerRef.current) {
              const container = scrollContainerRef.current;
              const cardWidth = 288; // DayCard 宽度 + gap (approximate)
              
              // 计算目标滚动位置
              let scrollLeft;
              if (targetIndex === updatedDayEvents.length - 1) {
                // 如果是最后一天，滚动到最右边
                scrollLeft = container.scrollWidth;
              } else {
                // 否则滚动到对应卡片的位置（居中显示）
                scrollLeft = targetIndex * cardWidth - container.clientWidth / 2 + cardWidth / 2;
                scrollLeft = Math.max(0, Math.min(scrollLeft, container.scrollWidth - container.clientWidth));
              }
              
              container.scrollTo({
                left: scrollLeft,
                behavior: 'smooth',
              });
            }
            // 高亮目标卡片
            setActiveCardIndex(targetIndex);
            setTimeout(() => setActiveCardIndex(null), 2000);
          }, 300);
        } else if (hasDeleteEvent) {
          // 删除事件后滚动到最左边（最早日期）
          setTimeout(() => {
            if (scrollContainerRef.current) {
              scrollContainerRef.current.scrollTo({
                left: 0,
                behavior: 'smooth',
              });
            }
          }, 300);
        }
        // 注意：list_events 查询不再触发自动滚动
      }
      
      // 延迟滚动消息到底部
      setTimeout(scrollMessagesToBottom, 100);
    } catch (error) {
      console.error('Chat error:', error);
      // 添加错误消息到对话历史
      setConversationHistory([
        ...updatedHistory,
        { role: 'assistant', content: '抱歉，发生了错误，请稍后重试。' },
      ]);
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
      const updatedEvents = await loadEvents();
      
      // 更新 selectedDay 以反映最新的数据，保持弹窗打开
      if (selectedDay) {
        const updatedDay = updatedEvents.find(day => day.date === selectedDay.date);
        if (updatedDay) {
          setSelectedDay(updatedDay);
        } else {
          // 该日期已没有事件，更新为显示空列表（显示"暂无日程"）
          setSelectedDay({
            ...selectedDay,
            events: [],
          });
        }
      }
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

  const clearConversation = () => {
    setConversationHistory([]);
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
          className="flex items-center justify-between px-8 py-4 border-b-2 border-black"
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

          <div className="flex items-center gap-3">
            {/* 视图切换按钮 */}
            <div className="flex items-center border-2 border-black bg-white">
              <button
                onClick={() => setViewMode('timeline')}
                className={`
                  px-3 py-2 flex items-center gap-1.5 text-sm font-medium transition-colors
                  ${viewMode === 'timeline' ? 'bg-black text-white' : 'hover:bg-black/10'}
                `}
                title="时间线视图"
              >
                <Rows3 className="w-4 h-4" />
                <span className="hidden sm:inline">时间线</span>
              </button>
              <div className="w-px h-6 bg-black" />
              <button
                onClick={() => setViewMode('month')}
                className={`
                  px-3 py-2 flex items-center gap-1.5 text-sm font-medium transition-colors
                  ${viewMode === 'month' ? 'bg-black text-white' : 'hover:bg-black/10'}
                `}
                title="月视图"
              >
                <LayoutGrid className="w-4 h-4" />
                <span className="hidden sm:inline">月视图</span>
              </button>
            </div>

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

        {/* 可收起的对话消息区域 */}
        <motion.div 
          className="border-b-2 border-black bg-white overflow-hidden"
          initial={false}
          animate={{ 
            height: isChatExpanded ? 'auto' : 48,
            flex: isChatExpanded ? 1 : 'none'
          }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {/* 控制栏 - 始终可见 */}
          <div 
            className="flex items-center justify-between px-8 py-3 bg-black/5 cursor-pointer hover:bg-black/10 transition-colors"
            onClick={() => setIsChatExpanded(!isChatExpanded)}
          >
            <div className="flex items-center gap-3">
              <MessageSquare className="w-4 h-4 text-black/60" />
              <span className="text-sm font-medium text-black/70">
                对话
                {conversationHistory.length > 0 && (
                  <span className="ml-2 text-xs text-black/40">
                    ({conversationHistory.length} 条消息)
                  </span>
                )}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {conversationHistory.length > 0 && isChatExpanded && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    clearConversation();
                  }}
                  className="flex items-center gap-1 px-2 py-1 text-xs text-destructive hover:bg-destructive/10 rounded transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                  清空
                </button>
              )}
              <motion.div
                animate={{ rotate: isChatExpanded ? 0 : 180 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronUp className="w-4 h-4 text-black/60" />
              </motion.div>
            </div>
          </div>

          {/* 消息内容区域 - 收起时隐藏 */}
          {isChatExpanded && (
            <div className="overflow-y-auto px-8 py-4" style={{ maxHeight: 'calc(50vh - 48px)' }}>
              {conversationHistory.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="h-full flex flex-col items-center justify-center text-black/30 py-8"
                >
                  <div className="w-20 h-20 border-2 border-black/20 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                  </div>
                  <p className="text-base font-medium mb-2">开始对话</p>
                  <p className="text-sm">在下方输入指令管理您的日程</p>
                  <p className="text-xs mt-3 text-black/20">例如："帮我创建一个明天下午3点的会议"</p>
                </motion.div>
              ) : (
                <div className="max-w-3xl mx-auto space-y-4">
                  {conversationHistory.map((message, index) => (
                    <MessageBubble
                      key={index}
                      message={message}
                      toolCalls={message.role === 'assistant' ? (messageToolCalls.get(index) ?? []) : undefined}
                    />
                  ))}
                  <div ref={messagesEndRef} /> {/* 滚动锚点 */}
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* 日历区域 - 动态高度 */}
        <motion.div 
          className="relative border-t-2 border-black bg-black/5 flex-1 min-h-[320px] overflow-hidden"
          initial={false}
          animate={{ 
            height: isChatExpanded ? '35%' : 'calc(100% - 48px - 88px)'  // 减去收起栏和输入区
          }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {/* 时间线视图 */}
          {viewMode === 'timeline' && (
            <>
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
            </>
          )}

          {/* 月视图 */}
          {viewMode === 'month' && (
            <div className="h-full w-full">
              <MonthView 
                events={dayEvents.flatMap(d => d.events)}
                onDateClick={(dateKey, clickedDayEvents) => {
                  // 找到对应日期的 DayEvents 或创建一个新的
                  const existingDay = dayEvents.find(d => d.date === dateKey);
                  if (existingDay) {
                    handleOpenDetail(existingDay);
                  } else if (clickedDayEvents.length > 0) {
                    // 创建一个临时的 DayEvents 对象
                    const tempDay: DayEvents = {
                      date: dateKey,
                      displayDate: new Date(dateKey).toLocaleDateString('zh-CN', {
                        month: 'short',
                        day: 'numeric',
                        weekday: 'short',
                      }),
                      events: clickedDayEvents,
                      isToday: dateKey === new Date().toISOString().split('T')[0],
                    };
                    handleOpenDetail(tempDay);
                  }
                }}
              />
            </div>
          )}
        </motion.div>

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
