import { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { CalendarEvent, UpdateEventRequest } from '@/types';
import { 
  Calendar, 
  MapPin, 
  MoreVertical, 
  Edit2, 
  Trash2,
  Check,
  X,
  Repeat
} from 'lucide-react';

interface EventCardProps {
  event: CalendarEvent;
  onUpdate?: (id: string, data: UpdateEventRequest) => void;
  onDelete?: (id: string) => void;
}

export function EventCard({ event, onUpdate, onDelete }: EventCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editData, setEditData] = useState<UpdateEventRequest>({
    title: event.title,
    description: event.description,
    location: event.location,
    start_time: event.start_time,
    end_time: event.end_time,
  });

  // 获取重复规则显示文本
  const getRecurrenceText = () => {
    if (!event.recurrence_rule && !event.is_recurring) return null;
    
    if (event.recurrence_rule) {
      const { type, days } = event.recurrence_rule;
      if (type === 'daily') return '每天重复';
      if (type === 'weekly') {
        if (days && days.length > 0) {
          const dayMap: Record<string, string> = {
            monday: '一', tuesday: '二', wednesday: '三', thursday: '四',
            friday: '五', saturday: '六', sunday: '日'
          };
          const dayNames = days.map(d => dayMap[d] || d).join('');
          return `每周${dayNames}重复`;
        }
        return '每周重复';
      }
      if (type === 'monthly') return '每月重复';
    }
    
    if (event.is_recurring) return '重复事件';
    return null;
  };

  const recurrenceText = getRecurrenceText();

  // 格式化日期时间
  const formatDateTime = (isoString: string) => {
    const date = new Date(isoString);
    return {
      date: date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        weekday: 'short',
      }),
      time: date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    };
  };

  const start = formatDateTime(event.start_time);
  const end = formatDateTime(event.end_time);

  const handleSave = () => {
    onUpdate?.(event.id, editData);
    setIsEditing(false);
  };

  const handleDelete = () => {
    onDelete?.(event.id);
    setIsDeleteDialogOpen(false);
  };

  // 编辑模式
  if (isEditing) {
    return (
      <Card className="w-full border-2 border-primary/20">
        <CardHeader>
          <CardTitle className="text-lg">编辑事件</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">标题</label>
            <Input
              value={editData.title}
              onChange={(e) => setEditData({ ...editData, title: e.target.value })}
              placeholder="事件标题"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">开始时间</label>
              <Input
                type="datetime-local"
                value={editData.start_time?.slice(0, 16)}
                onChange={(e) => setEditData({ ...editData, start_time: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium">结束时间</label>
              <Input
                type="datetime-local"
                value={editData.end_time?.slice(0, 16)}
                onChange={(e) => setEditData({ ...editData, end_time: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">地点</label>
            <Input
              value={editData.location || ''}
              onChange={(e) => setEditData({ ...editData, location: e.target.value })}
              placeholder="事件地点"
            />
          </div>
          <div>
            <label className="text-sm font-medium">描述</label>
            <Textarea
              value={editData.description || ''}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              placeholder="事件描述"
              rows={3}
            />
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={() => setIsEditing(false)}>
            <X className="w-4 h-4 mr-1" />
            取消
          </Button>
          <Button size="sm" onClick={handleSave}>
            <Check className="w-4 h-4 mr-1" />
            保存
          </Button>
        </CardFooter>
      </Card>
    );
  }

  return (
    <>
      <Card className="w-full hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-lg font-semibold line-clamp-1">
                {event.title}
              </CardTitle>
              <CardDescription className="flex items-center gap-2 mt-1 flex-wrap">
                <Calendar className="w-3.5 h-3.5" />
                <span>{start.date}</span>
                <Badge variant="secondary" className="text-xs">
                  {start.time} - {end.time}
                </Badge>
                {recurrenceText && (
                  <Badge variant="outline" className="text-xs flex items-center gap-1 text-primary">
                    <Repeat className="w-3 h-3" />
                    {recurrenceText}
                  </Badge>
                )}
              </CardDescription>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setIsEditing(true)}>
                  <Edit2 className="w-4 h-4 mr-2" />
                  编辑
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => setIsDeleteDialogOpen(true)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  删除
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        {(event.description || event.location) && (
          <CardContent className="pt-0 pb-3">
            {event.location && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                <MapPin className="w-3.5 h-3.5" />
                <span>{event.location}</span>
              </div>
            )}
            {event.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {event.description}
              </p>
            )}
          </CardContent>
        )}
      </Card>

      {/* 删除确认对话框 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除事件 "{event.title}" 吗？此操作无法撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
