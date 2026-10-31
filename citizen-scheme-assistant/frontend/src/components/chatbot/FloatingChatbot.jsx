import React, { useState } from 'react';
import { Bot, MessageSquare, X, Sparkles } from 'lucide-react';
import { ChatWindow } from './ChatWindow';
import { useLanguage } from '../../i18n/LanguageContext';

export const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { language } = useLanguage();

  return (
    <div className="fixed bottom-5 right-4 sm:right-6 z-50 flex flex-col items-end">
      {/* Chat Window Popup */}
      {isOpen && (
        <div className="mb-3.5 w-[calc(100vw-32px)] sm:w-auto max-w-[420px] transition-all">
          <ChatWindow onClose={() => setIsOpen(false)} />
        </div>
      )}

      {/* Floating Action Button */}
      <div className="flex items-center gap-2">
        {!isOpen && (
          <div className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white/90 backdrop-blur-md border border-orange-200/80 shadow-md text-xs font-bold text-slate-800 animate-bounce">
            <Sparkles className="w-3.5 h-3.5 text-orange-500" />
            <span>{language === 'hi' ? 'सहायक से पूछें' : 'Ask Sahayak'}</span>
          </div>
        )}

        <button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          aria-label={isOpen ? 'Close Chatbot' : 'Open Sahayak'}
          title={isOpen ? 'Close Chat' : 'Chat with Sahayak'}
          className={`w-14 h-14 rounded-full flex items-center justify-center text-white shadow-xl transition-all duration-300 focus-visible:ring-4 focus-visible:ring-orange-300 focus-visible:outline-none active:scale-95 ${
            isOpen
              ? 'bg-slate-900 hover:bg-black rotate-90'
              : 'bg-gradient-to-tr from-orange-600 via-orange-500 to-amber-500 hover:shadow-orange-500/40 hover:scale-105'
          }`}
        >
          {isOpen ? (
            <X className="w-6 h-6 transition-transform" />
          ) : (
            <div className="relative flex items-center justify-center">
              <Bot className="w-7 h-7" />
              <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-white animate-pulse" />
            </div>
          )}
        </button>
      </div>
    </div>
  );
};

