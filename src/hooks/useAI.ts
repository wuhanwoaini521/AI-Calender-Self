/*
useAI Hook - AI Assistant with Tools / Skills / MCP Support

This hook provides:
- Streaming chat with tool calling
- Direct skill invocation
- Tool and skill discovery
*/

import { useState, useCallback, useRef } from 'react';
import { api } from '@/services/api';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'tool' | 'skill';
  content: string;
  toolCall?: ToolCallResult;
  skillResult?: SkillResult;
}

export interface ToolCallResult {
  tool: string;
  success: boolean;
  result: unknown;
  message: string;
}

export interface SkillStep {
  tool_name: string;
  params: Record<string, unknown>;
  result: unknown;
  success: boolean;
}

export interface SkillResult {
  skill: string;
  success: boolean;
  message: string;
  data: unknown;
  steps: SkillStep[];
}

export interface Tool {
  name: string;
  description: string;
  parameters: unknown[];
}

export interface Skill {
  name: string;
  description: string;
  tools: string[];
}

export function useAI() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [tools, setTools] = useState<Tool[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Fetch available tools
  const fetchTools = useCallback(async () => {
    try {
      const data = await api.fetch('/ai/v2/tools');
      if (data.success) {
        setTools(data.data.tools);
      }
    } catch (err) {
      console.error('Failed to fetch tools:', err);
    }
  }, []);

  // Fetch available skills
  const fetchSkills = useCallback(async () => {
    try {
      const data = await api.fetch('/ai/v2/skills');
      if (data.success) {
        setSkills(data.data.skills);
      }
    } catch (err) {
      console.error('Failed to fetch skills:', err);
    }
  }, []);

  // Call a tool directly
  const callTool = useCallback(async (tool: string, params: Record<string, unknown>) => {
    try {
      const data = await api.fetch('/ai/v2/tools/call', {
        method: 'POST',
        body: JSON.stringify({ tool, params }),
      });
      return data;
    } catch (err) {
      throw err;
    }
  }, []);

  // Call a skill directly
  const callSkill = useCallback(async (skill: string, params: Record<string, unknown>) => {
    try {
      setIsLoading(true);
      const data = await api.fetch('/ai/v2/skills/call', {
        method: 'POST',
        body: JSON.stringify({ skill, params }),
      });
      
      if (data.success) {
        const skillResult: SkillResult = {
          skill,
          success: data.success,
          message: data.message,
          data: data.data.data,
          steps: data.data.steps,
        };
        
        setMessages(prev => [...prev, {
          role: 'skill',
          content: data.message,
          skillResult,
        }]);
      }
      
      return data;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Send a chat message with streaming
  const sendMessage = useCallback(async (
    message: string,
    context?: {
      currentDate?: string;
      selectedDate?: string;
      events?: unknown[];
    },
    useSkills: boolean = true
  ) => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const abortController = new AbortController();
    abortControllerRef.current = abortController;
    
    setIsLoading(true);
    
    // Add user message
    const userMessage: ChatMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const history = messages.filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({ role: m.role, content: m.content }));
      
      const response = await fetch(`${api.getBaseUrl()}/ai/v2/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${api.getToken()}`,
        },
        body: JSON.stringify({
          message,
          history,
          context,
          use_skills: useSkills,
        }),
        signal: abortController.signal,
      });
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');
      
      let assistantContent = '';
      let currentToolCall: ToolCallResult | null = null;
      let currentSkillResult: SkillResult | null = null;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              
              switch (parsed.type) {
                case 'text':
                  // If it's the first text after tool/skill call, reset content
                  if (currentToolCall || currentSkillResult) {
                    assistantContent = parsed.content;
                    currentToolCall = null;
                    currentSkillResult = null;
                  } else {
                    assistantContent += parsed.content;
                  }
                  // Update the last assistant message or create new one
                  setMessages(prev => {
                    const last = prev[prev.length - 1];
                    // If last message is assistant without tool/skill call, update it
                    if (last && last.role === 'assistant' && !last.toolCall && !last.skillResult) {
                      return [...prev.slice(0, -1), { ...last, content: assistantContent }];
                    }
                    // Otherwise create new message
                    return [...prev, { role: 'assistant', content: assistantContent }];
                  });
                  break;
                  
                case 'tool_call':
                  currentToolCall = {
                    tool: parsed.tool,
                    success: parsed.success,
                    result: parsed.result,
                    message: parsed.message,
                  };
                  setMessages(prev => [...prev, {
                    role: 'tool',
                    content: `Used ${parsed.tool}`,
                    toolCall: currentToolCall!,
                  }]);
                  break;
                  
                case 'skill_start':
                  // Skill started executing
                  break;
                  
                case 'skill_result':
                  currentSkillResult = {
                    skill: parsed.skill,
                    success: parsed.success,
                    message: parsed.message,
                    data: parsed.data,
                    steps: parsed.steps,
                  };
                  setMessages(prev => [...prev, {
                    role: 'skill',
                    content: parsed.message,
                    skillResult: currentSkillResult!,
                  }]);
                  break;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        console.error('Chat error:', err);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '抱歉，发生了错误。请重试。',
        }]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [messages]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Abort current request
  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  }, []);

  return {
    messages,
    isLoading,
    tools,
    skills,
    sendMessage,
    callTool,
    callSkill,
    fetchTools,
    fetchSkills,
    clearMessages,
    abort,
  };
}