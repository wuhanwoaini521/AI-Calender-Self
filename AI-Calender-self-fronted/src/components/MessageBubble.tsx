import { Card, CardContent } from '@/components/ui/card';

import { User, Bot, Wrench } from 'lucide-react';
import type { ChatMessage, ToolCall } from '@/types';

interface MessageBubbleProps {
  message: ChatMessage;
  toolCalls?: ToolCall[];
}

export function MessageBubble({ message, toolCalls }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-muted-foreground'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* 消息内容 */}
      <div className={`flex-1 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <Card
          className={`max-w-[80%] ${
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted'
          }`}
        >
          <CardContent className="p-3">
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </CardContent>
        </Card>

        {/* 工具调用展示 */}
        {toolCalls !== undefined && (
          <div className="mt-2 space-y-1">
            {toolCalls.length > 0 ? (
              toolCalls.map((tool, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 text-xs text-muted-foreground"
                >
                  <Wrench className="w-3 h-3" />
                  <span>调用了工具: {tool.name}</span>
                </div>
              ))
            ) : (
              <div className="flex items-center gap-2 text-xs text-muted-foreground/50">
                <Wrench className="w-3 h-3" />
                <span>无工具调用</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
