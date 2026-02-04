import type { User, CalendarEvent, CreateEventRequest, LoginRequest, RegisterRequest, AIInsight } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  getBaseUrl(): string {
    return API_BASE_URL;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  async fetch(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Auth
  async login(credentials: LoginRequest): Promise<{ user: User; token: string }> {
    const response = await this.fetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    this.setToken(response.data.token);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<{ user: User; token: string }> {
    const response = await this.fetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.data.token);
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await this.fetch('/auth/profile');
    return response.data.user;
  }

  // Events
  async getEvents(view?: string, date?: string): Promise<CalendarEvent[]> {
    const params = new URLSearchParams();
    if (view) params.append('view', view);
    if (date) params.append('date', date);
    const response = await this.fetch(`/events?${params.toString()}`);
    return response.data.events;
  }

  async getEventById(id: string): Promise<CalendarEvent> {
    const response = await this.fetch(`/events/${id}`);
    return response.data.event;
  }

  async createEvent(event: CreateEventRequest): Promise<CalendarEvent> {
    const response = await this.fetch('/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
    return response.data.event;
  }

  async updateEvent(id: string, event: Partial<CreateEventRequest>): Promise<CalendarEvent> {
    const response = await this.fetch(`/events/${id}`, {
      method: 'PUT',
      body: JSON.stringify(event),
    });
    return response.data.event;
  }

  async deleteEvent(id: string): Promise<void> {
    await this.fetch(`/events/${id}`, {
      method: 'DELETE',
    });
  }

  async getUpcomingEvents(limit: number = 5): Promise<CalendarEvent[]> {
    const response = await this.fetch(`/events/upcoming?limit=${limit}`);
    return response.data.events;
  }

  // AI
  async chat(message: string, context?: { currentDate?: string; selectedDate?: string; events?: CalendarEvent[] }): Promise<string> {
    const response = await this.fetch('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    });
    return response.data.message;
  }

  async getInsights(unreadOnly?: boolean): Promise<AIInsight[]> {
    const params = new URLSearchParams();
    if (unreadOnly) params.append('unreadOnly', 'true');
    const response = await this.fetch(`/ai/insights?${params.toString()}`);
    return response.data.insights;
  }

  async markInsightAsRead(id: string): Promise<void> {
    await this.fetch(`/ai/insights/${id}/read`, {
      method: 'PUT',
    });
  }

  async getSuggestions(date?: string): Promise<string[]> {
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    const response = await this.fetch(`/ai/suggestions?${params.toString()}`);
    return response.data.suggestions;
  }

  async generateSchedule(tasks: { name: string; duration?: number }[], date?: string, preferences?: { includeBreaks?: boolean }): Promise<any[]> {
    const response = await this.fetch('/ai/schedule', {
      method: 'POST',
      body: JSON.stringify({ tasks, date, preferences }),
    });
    return response.data.schedule;
  }
}

export const api = new ApiService();
