// 重复规则类型
export interface RecurrenceRule {
  type: 'daily' | 'weekly' | 'monthly';
  days?: ('monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday')[];
  end_date?: string;  // ISO 8601 日期格式
}

// 日历事件类型
export interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  description?: string;
  location?: string;
  // 重复事件相关字段
  is_recurring?: boolean;
  parent_event_id?: string;
  recurrence_rule?: RecurrenceRule;
  created_at: string;
  updated_at: string;
}

// 按日期分组的事件
export interface DayEvents {
  date: string;  // YYYY-MM-DD
  displayDate: string;  // 格式化后的日期显示
  events: CalendarEvent[];
  isToday?: boolean;
  isTomorrow?: boolean;
}

// 创建事件请求
export interface CreateEventRequest {
  title: string;
  start_time: string;
  end_time: string;
  description?: string;
  location?: string;
  // 重复事件支持
  recurrence_rule?: RecurrenceRule;
}

// 更新事件请求
export interface UpdateEventRequest {
  title?: string;
  start_time?: string;
  end_time?: string;
  description?: string;
  location?: string;
}

// 聊天消息
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// 聊天请求
export interface ChatRequest {
  message: string;
  conversation_history: ChatMessage[];
}

// 工具调用
export interface ToolCall {
  name: string;
  input: Record<string, unknown>;
}

// 聊天响应
export interface ChatResponse {
  message: string;
  tool_calls?: ToolCall[];
  events_modified?: string[];
}

// 对话项（用于展示）
export interface ConversationItem {
  id: string;
  type: 'message' | 'day_card';
  role?: 'user' | 'assistant';
  content?: string;
  dayEvents?: DayEvents;
  tool_calls?: ToolCall[];
  timestamp: Date;
}
