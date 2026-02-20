import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="relative w-full max-w-2xl mx-auto"
    >
      {/* 手绘装饰线条 */}
      <svg className="absolute -top-6 left-0 w-full h-6 text-black/20" viewBox="0 0 400 24" preserveAspectRatio="none">
        <path 
          d="M0,12 Q100,6 200,12 T400,12" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>

      <div 
        className="relative flex items-end gap-3 p-2 bg-white border-2 border-black"
        style={{ 
          borderRadius: '30px 2px 30px 2px / 2px 30px 2px 30px',
          boxShadow: '4px 4px 0 rgba(0, 0, 0, 0.1)'
        }}
      >
        {/* 输入框 */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入指令，例如：帮我添加明天下午3点的会议..."
          className="flex-1 min-h-[48px] max-h-[120px] py-3 px-4 bg-transparent text-black placeholder:text-black/30 resize-none border-0 focus:outline-none text-base font-medium"
          rows={1}
          disabled={isLoading}
        />

        {/* 发送按钮 */}
        <button
          onClick={handleSubmit}
          disabled={!message.trim() || isLoading}
          className={`
            shrink-0 w-12 h-12 flex items-center justify-center
            border-2 border-black
            transition-all duration-200
            ${message.trim() && !isLoading 
              ? 'bg-black text-white hover:bg-white hover:text-black' 
              : 'bg-white text-black/30 cursor-not-allowed'
            }
          `}
          style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* 提示文字 */}
      <p className="text-center text-black/30 text-xs mt-3 font-medium">
        按 Enter 发送 · Shift + Enter 换行
      </p>
    </motion.div>
  );
}
