export interface User {
  id: string;
  email: string;
  name: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  timezone: string;
  language: string;
  notificationEnabled: boolean;
  aiAssistantEnabled: boolean;
}

export interface CalendarEvent {
  id: string;
  userId: string;
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  allDay: boolean;
  location?: string;
  color: string;
  reminders: Reminder[];
  attendees?: Attendee[];
  createdAt: string;
  updatedAt: string;
}

export interface Reminder {
  id: string;
  type: 'notification' | 'email' | 'sms';
  minutesBefore: number;
}

export interface Attendee {
  id: string;
  email: string;
  name?: string;
  status: 'pending' | 'accepted' | 'declined' | 'tentative';
}

export interface AIInsight {
  id: string;
  userId: string;
  type: 'suggestion' | 'conflict' | 'optimization' | 'reminder';
  message: string;
  relatedEventIds?: string[];
  createdAt: string;
  read: boolean;
}

export interface ChatMessage {
  id: string;
  userId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface CreateEventRequest {
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  allDay?: boolean;
  location?: string;
  color?: string;
  reminders?: { type: 'notification' | 'email'; minutesBefore: number }[];
}

export type CalendarView = 'month' | 'week' | 'day';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}
