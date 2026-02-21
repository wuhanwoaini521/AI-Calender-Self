import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, CalendarDays } from 'lucide-react';
import type { CalendarEvent } from '@/types';

interface MonthViewProps {
  events: CalendarEvent[];
  onDateClick?: (date: string, events: CalendarEvent[]) => void;
}

// 获取某月的天数
function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate();
}

// 获取某月第一天是星期几 (0=周日, 1=周一)
function getFirstDayOfMonth(year: number, month: number): number {
  return new Date(year, month, 1).getDay();
}

// 格式化日期
function formatDateKey(year: number, month: number, day: number): string {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

// 获取月份名称
function getMonthName(year: number, month: number): string {
  return new Date(year, month).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' });
}

export function MonthView({ events, onDateClick }: MonthViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  // 将事件按日期分组
  const eventsByDate = useMemo(() => {
    const map = new Map<string, CalendarEvent[]>();
    events.forEach(event => {
      const dateKey = event.start_time.split('T')[0];
      if (!map.has(dateKey)) {
        map.set(dateKey, []);
      }
      map.get(dateKey)!.push(event);
    });
    // 对每个日期的事件按时间排序
    map.forEach(dayEvents => {
      dayEvents.sort((a, b) => 
        new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      );
    });
    return map;
  }, [events]);

  // 生成日历网格数据
  const calendarDays = useMemo(() => {
    const daysInMonth = getDaysInMonth(year, month);
    const firstDayOfWeek = getFirstDayOfMonth(year, month); // 0=周日
    const days: Array<{ date: number | null; dateKey: string | null; events: CalendarEvent[]; isCurrentMonth: boolean }> = [];

    // 上个月的日期（填充第一周）
    const prevMonthDays = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1; // 转换为周一开始
    const prevMonth = month === 0 ? 11 : month - 1;
    const prevYear = month === 0 ? year - 1 : year;
    const daysInPrevMonth = getDaysInMonth(prevYear, prevMonth);

    for (let i = prevMonthDays - 1; i >= 0; i--) {
      const day = daysInPrevMonth - i;
      const dateKey = formatDateKey(prevYear, prevMonth, day);
      days.push({
        date: day,
        dateKey,
        events: eventsByDate.get(dateKey) || [],
        isCurrentMonth: false,
      });
    }

    // 当前月的日期
    for (let day = 1; day <= daysInMonth; day++) {
      const dateKey = formatDateKey(year, month, day);
      days.push({
        date: day,
        dateKey,
        events: eventsByDate.get(dateKey) || [],
        isCurrentMonth: true,
      });
    }

    // 下个月的日期（填充最后一周）
    const remainingCells = 42 - days.length; // 6行 x 7列 = 42
    const nextMonth = month === 11 ? 0 : month + 1;
    const nextYear = month === 11 ? year + 1 : year;

    for (let day = 1; day <= remainingCells; day++) {
      const dateKey = formatDateKey(nextYear, nextMonth, day);
      days.push({
        date: day,
        dateKey,
        events: eventsByDate.get(dateKey) || [],
        isCurrentMonth: false,
      });
    }

    return days;
  }, [year, month, eventsByDate]);

  // 判断是否是今天
  const isToday = (dateKey: string | null) => {
    if (!dateKey) return false;
    return dateKey === new Date().toISOString().split('T')[0];
  };

  // 切换月份
  const goToPrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  // 格式化时间
  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  const weekDays = ['一', '二', '三', '四', '五', '六', '日'];

  return (
    <div className="h-full flex flex-col bg-white">
      {/* 月份导航 */}
      <div className="flex items-center justify-between px-6 py-4 border-b-2 border-black">
        <div className="flex items-center gap-3">
          <CalendarDays className="w-5 h-5" />
          <h2 className="text-xl font-bold">{getMonthName(year, month)}</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={goToPrevMonth}
            className="w-10 h-10 flex items-center justify-center border-2 border-black hover:bg-black hover:text-white transition-colors"
            style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="px-4 py-2 border-2 border-black text-sm font-medium hover:bg-black hover:text-white transition-colors"
            style={{ borderRadius: '4px' }}
          >
            今天
          </button>
          <button
            onClick={goToNextMonth}
            className="w-10 h-10 flex items-center justify-center border-2 border-black hover:bg-black hover:text-white transition-colors"
            style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* 星期标题 */}
      <div className="grid grid-cols-7 border-b-2 border-black">
        {weekDays.map((day, index) => (
          <div
            key={day}
            className={`py-3 text-center text-sm font-bold ${
              index >= 5 ? 'text-black/60 bg-black/5' : ''
            }`}
          >
            星期{day}
          </div>
        ))}
      </div>

      {/* 日历网格 */}
      <div className="flex-1 grid grid-cols-7 grid-rows-6">
        {calendarDays.map((dayInfo, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: index * 0.01 }}
            className={`
              relative border-r border-b border-black/10 p-2 overflow-hidden cursor-pointer
              hover:bg-black/5 transition-colors
              ${!dayInfo.isCurrentMonth ? 'bg-black/[0.02]' : ''}
              ${dayInfo.dateKey && isToday(dayInfo.dateKey) ? 'bg-primary/10' : ''}
            `}
            onClick={() => dayInfo.dateKey && onDateClick?.(dayInfo.dateKey, dayInfo.events)}
          >
            {/* 日期数字 */}
            <div className={`
              flex items-center justify-center w-7 h-7 text-sm font-medium mb-1
              ${dayInfo.dateKey && isToday(dayInfo.dateKey) 
                ? 'bg-black text-white rounded-full' 
                : !dayInfo.isCurrentMonth ? 'text-black/40' : ''
              }
            `}>
              {dayInfo.date}
            </div>

            {/* 事件列表 */}
            <div className="space-y-1 overflow-hidden">
              {dayInfo.events.slice(0, 3).map((event, idx) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + idx * 0.05 }}
                  className={`
                    text-xs px-1.5 py-0.5 rounded truncate
                    ${event.is_recurring 
                      ? 'bg-primary/20 text-primary border border-primary/30' 
                      : 'bg-black/10 text-black border border-black/20'
                    }
                  `}
                  title={`${event.title} (${formatTime(event.start_time)})`}
                >
                  {formatTime(event.start_time)} {event.title}
                </motion.div>
              ))}
              {dayInfo.events.length > 3 && (
                <div className="text-xs text-black/40 pl-1">
                  +{dayInfo.events.length - 3} 更多
                </div>
              )}
            </div>

            {/* 事件数量指示点 */}
            {dayInfo.events.length > 0 && dayInfo.events.length <= 3 && (
              <div className="absolute bottom-1 right-1 flex gap-0.5">
                {dayInfo.events.map((_, i) => (
                  <div 
                    key={i} 
                    className={`w-1.5 h-1.5 rounded-full ${
                      dayInfo.events[i].is_recurring ? 'bg-primary' : 'bg-black/30'
                    }`} 
                  />
                ))}
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* 底部统计 */}
      <div className="px-6 py-3 border-t-2 border-black bg-black/5">
        <div className="flex items-center gap-6 text-sm">
          <span className="font-medium">
            本月共 <span className="text-primary font-bold">
              {calendarDays.reduce((sum, d) => sum + (d.isCurrentMonth ? d.events.length : 0), 0)}
            </span> 个事件
          </span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-primary" />
              <span className="text-black/60 text-xs">重复事件</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-black/30" />
              <span className="text-black/60 text-xs">普通事件</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
