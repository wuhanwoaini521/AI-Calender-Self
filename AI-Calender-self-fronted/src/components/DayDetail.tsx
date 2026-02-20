import { motion, AnimatePresence } from 'framer-motion';
import { X, MapPin, Calendar, Edit2, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { DayEvents, CalendarEvent, UpdateEventRequest } from '@/types';
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

interface DayDetailProps {
  dayEvents: DayEvents | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdateEvent?: (id: string, data: UpdateEventRequest) => void;
  onDeleteEvent?: (id: string) => void;
}

export function DayDetail({ 
  dayEvents, 
  isOpen, 
  onClose, 
  onUpdateEvent, 
  onDeleteEvent 
}: DayDetailProps) {
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);
  const [deleteEventId, setDeleteEventId] = useState<string | null>(null);
  const [editData, setEditData] = useState<UpdateEventRequest>({});

  if (!dayEvents) return null;

  const { displayDate, events, isToday, isTomorrow } = dayEvents;

  const getDateLabel = () => {
    if (isToday) return '今天';
    if (isTomorrow) return '明天';
    return displayDate;
  };

  const formatTime = (time: string) => {
    const date = new Date(time);
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  const handleEdit = (event: CalendarEvent) => {
    setEditingEvent(event);
    setEditData({
      title: event.title,
      start_time: event.start_time,
      end_time: event.end_time,
      location: event.location,
      description: event.description,
    });
  };

  const handleSaveEdit = () => {
    if (editingEvent && onUpdateEvent) {
      onUpdateEvent(editingEvent.id, editData);
      setEditingEvent(null);
    }
  };

  const handleDelete = () => {
    if (deleteEventId && onDeleteEvent) {
      onDeleteEvent(deleteEventId);
      setDeleteEventId(null);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          {/* 背景遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-white/80 backdrop-blur-sm"
          />

          {/* 主内容卡片 */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 30 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 30 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-3xl max-h-[85vh] bg-white border-2 border-black overflow-hidden"
            style={{ 
              borderRadius: '30px 2px 30px 2px / 2px 30px 2px 30px',
              boxShadow: '8px 8px 0 rgba(0, 0, 0, 0.15)'
            }}
          >
            {/* 内容 */}
            <div className="relative h-full flex flex-col">
              {/* 头部 */}
              <div className="flex items-center justify-between p-8 border-b-2 border-black">
                <div className="flex items-center gap-4">
                  <div className={`
                    w-16 h-16 flex items-center justify-center border-2 border-black
                    ${isToday || isTomorrow ? 'bg-black text-white' : 'bg-white'}
                  `}
                  style={{ borderRadius: '2% 98% 2% 98% / 98% 2% 98% 2%' }}
                  >
                    <Calendar className="w-8 h-8" />
                  </div>
                  <div>
                    <motion.h2 
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="text-3xl font-bold"
                    >
                      {getDateLabel()}
                    </motion.h2>
                    <p className="text-black/50 mt-1 font-medium">{events.length} 个日程</p>
                  </div>
                </div>

                <button
                  onClick={onClose}
                  className="w-12 h-12 flex items-center justify-center border-2 border-black bg-white hover:bg-black hover:text-white transition-colors"
                  style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* 手绘分隔线 */}
              <div className="sketchy-line mx-8 my-0" />

              {/* 事件列表 */}
              <div className="flex-1 overflow-y-auto p-8 scrollbar-hide">
                <div className="space-y-4">
                  {events.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-black/30">
                      <Calendar className="w-16 h-16 mb-4" strokeWidth={1.5} />
                      <p className="text-lg font-medium">暂无日程</p>
                    </div>
                  ) : (
                    events.map((event, index) => (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="group relative p-6 border-2 border-black/10 hover:border-black bg-white hover:bg-black/[0.02] transition-all"
                        style={{ borderRadius: '8px 24px 8px 24px' }}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold">
                                {event.title}
                              </h3>
                              <span 
                                className="px-3 py-1 text-xs font-medium border-2 border-black bg-white"
                                style={{ borderRadius: '12px 4px 12px 4px' }}
                              >
                                {formatTime(event.start_time)} - {formatTime(event.end_time)}
                              </span>
                            </div>

                            {event.location && (
                              <div className="flex items-center gap-2 text-black/60 mb-2">
                                <MapPin className="w-4 h-4" />
                                <span className="font-medium">{event.location}</span>
                              </div>
                            )}

                            {event.description && (
                              <p className="text-black/40 mt-3 leading-relaxed">
                                {event.description}
                              </p>
                            )}
                          </div>

                          {/* 操作按钮 */}
                          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEdit(event)}
                              className="w-10 h-10 flex items-center justify-center border-2 border-black bg-white hover:bg-black hover:text-white transition-colors"
                              style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => setDeleteEventId(event.id)}
                              className="w-10 h-10 flex items-center justify-center border-2 border-black bg-white hover:bg-black hover:text-white transition-colors"
                              style={{ borderRadius: '15px 255px 15px 225px / 255px 15px 225px 15px' }}
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>

                        {/* 时间线装饰 */}
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-16 bg-black/10 rounded-full" />
                      </motion.div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </motion.div>

          {/* 编辑对话框 */}
          <Dialog open={!!editingEvent} onOpenChange={() => setEditingEvent(null)}>
            <DialogContent className="sm:max-w-[500px] bg-white border-2 border-black"
              style={{ borderRadius: '30px 2px 30px 2px / 2px 30px 2px 30px' }}
            >
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold">编辑事件</DialogTitle>
                <DialogDescription className="text-black/50">
                  修改事件的详细信息
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium text-black/60">标题</label>
                  <Input
                    value={editData.title || ''}
                    onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                    className="border-2 border-black focus:border-black/50"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-black/60">开始时间</label>
                    <Input
                      type="datetime-local"
                      value={editData.start_time?.slice(0, 16)}
                      onChange={(e) => setEditData({ ...editData, start_time: e.target.value })}
                      className="border-2 border-black focus:border-black/50"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-black/60">结束时间</label>
                    <Input
                      type="datetime-local"
                      value={editData.end_time?.slice(0, 16)}
                      onChange={(e) => setEditData({ ...editData, end_time: e.target.value })}
                      className="border-2 border-black focus:border-black/50"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-black/60">地点</label>
                  <Input
                    value={editData.location || ''}
                    onChange={(e) => setEditData({ ...editData, location: e.target.value })}
                    className="border-2 border-black focus:border-black/50"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-black/60">描述</label>
                  <Textarea
                    value={editData.description || ''}
                    onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                    className="border-2 border-black focus:border-black/50"
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setEditingEvent(null)} className="border-2 border-black hover:bg-black hover:text-white"
                  style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                >
                  取消
                </Button>
                <Button onClick={handleSaveEdit} className="bg-black text-white hover:bg-black/80"
                  style={{ borderRadius: '15px 255px 15px 225px / 255px 15px 225px 15px' }}
                >
                  保存
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* 删除确认对话框 */}
          <Dialog open={!!deleteEventId} onOpenChange={() => setDeleteEventId(null)}>
            <DialogContent className="bg-white border-2 border-black"
              style={{ borderRadius: '30px 2px 30px 2px / 2px 30px 2px 30px' }}
            >
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold">确认删除</DialogTitle>
                <DialogDescription className="text-black/50">
                  确定要删除这个事件吗？此操作无法撤销。
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDeleteEventId(null)} className="border-2 border-black hover:bg-black hover:text-white"
                  style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                >
                  取消
                </Button>
                <Button variant="destructive" onClick={handleDelete} className="bg-black text-white hover:bg-black/80"
                  style={{ borderRadius: '15px 255px 15px 225px / 255px 15px 225px 15px' }}
                >
                  删除
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
