import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, X, Lightbulb, Calendar, Clock, Wrench, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAIV2 } from '@/hooks/useAIV2';
import type { CalendarEvent } from '@/types';
import { format } from 'date-fns';

interface AIAssistantProps {
  selectedDate: Date;
  events: CalendarEvent[];
}

const QUICK_ACTIONS = [
  { icon: Calendar, label: '查看日程', query: '我今天有什么安排？' },
  { icon: Clock, label: '空闲时间', query: '我什么时候有空？' },
  { icon: Lightbulb, label: '优化建议', query: '帮我优化今天的日程' },
  { icon: Send, label: '创建会议', query: '明天下午三点开会' },
];

export function AIAssistant({ selectedDate, events }: AIAssistantProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const { isLoading, messages, sendMessage, clearMessages } = useAIV2();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    await sendMessage(input, {
      currentDate: format(new Date(), 'yyyy-MM-dd'),
      selectedDate: format(selectedDate, 'yyyy-MM-dd'),
      events,
    }, true); // useSkills = true
    setInput('');
  };

  const handleQuickAction = async (query: string) => {
    await sendMessage(query, {
      currentDate: format(new Date(), 'yyyy-MM-dd'),
      selectedDate: format(selectedDate, 'yyyy-MM-dd'),
      events,
    }, true);
  };

  // 渲染消息内容
  const renderMessage = (msg: typeof messages[0], index: number) => {
    const isUser = msg.role === 'user';
    const isTool = msg.role === 'tool';
    const isSkill = msg.role === 'skill';

    if (isTool && msg.toolCall) {
      return (
        <div key={index} className="flex justify-start">
          <div className="max-w-[90%] rounded-2xl px-4 py-3 bg-blue-50 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="h-5 w-5 rounded-full bg-blue-100 flex items-center justify-center">
                <Wrench className="h-3 w-3 text-blue-600" />
              </div>
              <span className="text-xs font-medium text-blue-600">
                使用工具: {msg.toolCall.tool}
              </span>
            </div>
            <div className={`text-sm font-medium ${
              msg.toolCall.success ? 'text-green-600' : 'text-red-600'
            }`}>
              {msg.toolCall.success ? '✓ 执行成功' : '✗ 执行失败'}
            </div>
            {msg.toolCall.message && (
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">{msg.toolCall.message}</p>
            )}
          </div>
        </div>
      );
    }

    if (isSkill && msg.skillResult) {
      return (
        <div key={index} className="flex justify-start">
          <div className="max-w-[90%] rounded-2xl px-4 py-3 bg-purple-50 border border-purple-200">
            {/* 技能标题 */}
            <div className="flex items-center gap-2 mb-2">
              <div className="h-5 w-5 rounded-full bg-purple-100 flex items-center justify-center">
                <Zap className="h-3 w-3 text-purple-600" />
              </div>
              <span className="text-xs font-medium text-purple-600">
                执行技能: {msg.skillResult.skill}
              </span>
            </div>
            
            {/* 技能结果内容 */}
            <div className="text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">
              {msg.content}
            </div>
            
            {/* 执行步骤 */}
            {msg.skillResult.steps && msg.skillResult.steps.length > 0 && (
              <div className="mt-3 pt-2 border-t border-purple-200/50">
                <p className="text-xs font-medium text-purple-700 mb-1.5">执行步骤</p>
                <div className="space-y-1">
                  {msg.skillResult.steps.map((step, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                        step.success ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                      }`}>
                        {step.success ? '✓' : '✗'}
                      </span>
                      <span className="text-slate-600">{step.tool_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }

    return (
      <div
        key={index}
        className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      >
        <div
          className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${
            isUser
              ? 'bg-slate-900 text-white'
              : 'bg-slate-100 text-slate-800'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <Button
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg"
          onClick={() => setIsOpen(true)}
        >
          <Sparkles className="h-6 w-6" />
        </Button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-white border rounded-2xl shadow-2xl flex flex-col z-50">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-slate-900 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <div>
                <h3 className="font-semibold">AI Assistant</h3>
                <p className="text-xs text-slate-500">支持工具调用和技能执行</p>
              </div>
            </div>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={clearMessages}
                className="h-8 text-xs"
              >
                清空
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Quick Actions */}
          {messages.length === 0 && (
            <div className="p-4 grid grid-cols-4 gap-2">
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.query)}
                  className="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-slate-50 transition-colors"
                >
                  <action.icon className="h-5 w-5 text-slate-700" />
                  <span className="text-xs text-center text-slate-600">{action.label}</span>
                </button>
              ))}
            </div>
          )}

          {/* Messages */}
          <ScrollArea className="flex-1 p-4" ref={scrollRef}>
            <div className="space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-slate-500 py-8">
                  <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>你好！我是你的 AI 日历助手。</p>
                  <p className="text-sm mt-2">我可以帮你：</p>
                  <ul className="text-sm text-left mt-2 space-y-1 max-w-[200px] mx-auto">
                    <li>• 查看和管理日程</li>
                    <li>• 创建和修改事件</li>
                    <li>• 查找空闲时间</li>
                    <li>• 检测日程冲突</li>
                    <li>• 优化每日安排</li>
                  </ul>
                </div>
              )}
              {messages.map((msg, index) => renderMessage(msg, index))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 rounded-2xl px-4 py-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                      <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:100ms]" />
                      <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:200ms]" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input */}
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="输入消息...（例如：明天下午3点开会）"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
