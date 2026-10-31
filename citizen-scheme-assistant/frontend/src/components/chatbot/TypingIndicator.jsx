import React from 'react';
import { Bot } from 'lucide-react';

export const TypingIndicator = () => {
  return (
    <div className="flex items-end gap-2 my-2 animate-fade-in">
      <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-white shrink-0 shadow-xs">
        <Bot className="w-3.5 h-3.5" />
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-bl-sm glass-card border border-white/80 shadow-2xs flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-orange-500 animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 rounded-full bg-orange-500 animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 rounded-full bg-orange-500 animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
};

