import type {
  CalendarEvent,
  CreateEventRequest,
  UpdateEventRequest,
  ChatRequest,
  ChatResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// 通用请求函数
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// 聊天服务
export const chatApi = {
  // 发送消息
  sendMessage: (data: ChatRequest): Promise<ChatResponse> =>
    fetchApi<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// 事件服务
export const eventApi = {
  // 获取所有事件
  getEvents: (params?: {
    start_date?: string;
    end_date?: string;
    keyword?: string;
  }): Promise<CalendarEvent[]> => {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.append('start_date', params.start_date);
    if (params?.end_date) searchParams.append('end_date', params.end_date);
    if (params?.keyword) searchParams.append('keyword', params.keyword);
    
    const query = searchParams.toString();
    return fetchApi<CalendarEvent[]>(`/events${query ? `?${query}` : ''}`);
  },

  // 获取单个事件
  getEvent: (id: string): Promise<CalendarEvent> =>
    fetchApi<CalendarEvent>(`/events/${id}`),

  // 创建事件
  createEvent: (data: CreateEventRequest): Promise<CalendarEvent> =>
    fetchApi<CalendarEvent>('/events', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 更新事件
  updateEvent: (id: string, data: UpdateEventRequest): Promise<CalendarEvent> =>
    fetchApi<CalendarEvent>(`/events/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 删除事件
  deleteEvent: (id: string): Promise<{ message: string; event_id: string }> =>
    fetchApi<{ message: string; event_id: string }>(`/events/${id}`, {
      method: 'DELETE',
    }),
};
