import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, ChevronRight, Repeat } from 'lucide-react';
import type { DayEvents, CalendarEvent } from '@/types';

interface DayCardProps {
  dayEvents: DayEvents;
  index: number;
  isActive?: boolean;
  onClick?: () => void;
}

export function DayCard({ dayEvents, index, isActive, onClick }: DayCardProps) {
  const { displayDate, events, isToday, isTomorrow } = dayEvents;
  
  const isRecurringEvent = (event: CalendarEvent) => {
    return event.is_recurring || event.recurrence_rule || event.parent_event_id;
  };

  const getEventTime = (event: { start_time: string }) => {
    const start = new Date(event.start_time);
    return `${start.getHours().toString().padStart(2, '0')}:${start.getMinutes().toString().padStart(2, '0')}`;
  };

  const getDateLabel = () => {
    if (isToday) return '今天';
    if (isTomorrow) return '明天';
    return displayDate;
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, rotate: -2 }}
      animate={{ 
        opacity: 1, 
        y: 0,
        rotate: index % 2 === 0 ? -1 : 1,
      }}
      whileHover={{ 
        scale: 1.03,
        rotate: 0,
        y: -8,
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        relative w-[280px] h-[380px] shrink-0 cursor-pointer
        bg-white border-2 border-black
        ${isActive ? 'ring-2 ring-black ring-offset-4 ring-offset-white' : ''}
      `}
      style={{ 
        borderRadius: '30px 2px 30px 2px / 2px 30px 2px 30px',
        boxShadow: '6px 6px 0 rgba(0, 0, 0, 0.15)'
      }}
    >
      {/* 角标 */}
      <div className="absolute -top-3 -left-2 w-8 h-8 bg-black text-white flex items-center justify-center font-bold text-sm"
        style={{ borderRadius: '2% 98% 2% 98% / 98% 2% 98% 2%' }}
      >
        {index + 1}
      </div>

      {/* 胶带装饰 */}
      <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-20 h-5 bg-black/10" 
        style={{ 
          clipPath: 'polygon(5% 0%, 95% 0%, 100% 100%, 0% 100%)',
          transform: 'translateX(-50%) rotate(-2deg)'
        }} 
      />

      {/* 内容 */}
      <div className="relative h-full p-6 flex flex-col">
        {/* 日期头部 */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className={`
              w-11 h-11 flex items-center justify-center border-2 border-black
              ${isToday || isTomorrow ? 'bg-black text-white' : 'bg-white'}
            `}
            style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
            >
              <Calendar className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xl font-bold">{getDateLabel()}</p>
              <p className="text-xs text-black/50 font-medium">{events.length} 个事件</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-black/30" />
        </div>

        {/* 手绘分隔线 */}
        <div className="sketchy-line mb-5" />

        {/* 事件列表 */}
        <div className="flex-1 space-y-3 overflow-hidden">
          {events.slice(0, 5).map((event, idx) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 + idx * 0.05 }}
              className="group flex items-start gap-3 p-3 border-2 border-black/10 hover:border-black hover:bg-black/[0.02] transition-all"
              style={{ borderRadius: '4px 12px 4px 12px' }}
            >
              {/* 时间点 */}
              <div className="flex flex-col items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-black group-hover:scale-125 transition-transform" />
                {idx < events.slice(0, 5).length - 1 && (
                  <div className="w-0.5 h-8 bg-black/10" />
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <p className="text-sm font-bold text-black truncate">
                    {event.title}
                  </p>
                  {isRecurringEvent(event) && (
                    <Repeat className="w-3 h-3 text-primary flex-shrink-0" />
                  )}
                </div>
                <div className="flex items-center gap-1.5 mt-1">
                  <Clock className="w-3 h-3 text-black/40" />
                  <span className="text-xs text-black/50 font-medium">{getEventTime(event)}</span>
                </div>
              </div>
            </motion.div>
          ))}
          
          {events.length > 5 && (
            <div className="flex items-center justify-center py-2">
              <span className="text-xs font-medium border-2 border-black px-3 py-1"
                style={{ borderRadius: '20px 4px 20px 4px' }}
              >
                +{events.length - 5} 更多
              </span>
            </div>
          )}

          {events.length === 0 && (
            <div className="flex flex-col items-center justify-center h-32 text-black/25">
              <Clock className="w-10 h-10 mb-2" strokeWidth={1.5} />
              <p className="text-sm font-medium">暂无事件</p>
            </div>
          )}
        </div>

        {/* 底部 */}
        <div className="mt-4 pt-4 border-t-2 border-black/10">
          <div className="flex items-center justify-between text-xs text-black/40">
            <span className="font-medium">点击查看详情</span>
            <MapPin className="w-4 h-4" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
