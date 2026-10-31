import React from 'react';
import { Bot, RotateCcw, X, Shield, Minus, Mic, MessageSquare } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';
import { chatbotApi } from '../../services/chatbotApi';

export const ChatHeader = ({ onReset, onClose, isOnline = true, mode = 'text', onToggleVoice }) => {
  const { language } = useLanguage();

  return (
    <div className="px-4 py-3.5 border-b border-orange-100 bg-gradient-to-r from-orange-500/10 via-amber-500/10 to-transparent flex items-center justify-between shrink-0">
      <div className="flex items-center gap-2.5">
        <div className="relative">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-white shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <span
            className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${
              isOnline ? 'bg-emerald-500' : 'bg-slate-400'
            }`}
            title={isOnline ? 'Online' : 'Offline'}
          />
        </div>

        <div>
          <div className="flex items-center gap-1.5">
            <h3 className="text-xs sm:text-sm font-black text-slate-900 leading-tight">
              {language === 'hi' ? 'सहायक AI' : 'Sahayak AI'}
            </h3>
            <span className="text-[9px] font-bold uppercase tracking-wider text-orange-700 bg-orange-100/80 px-1.5 py-0.2 rounded-md border border-orange-200/50">
              Beta
            </span>
          </div>
          <p className="text-[10px] text-slate-500 font-medium">
            {language === 'hi' ? 'सरकारी योजना सहायक' : 'Government Scheme Assistant'}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1">
        {onToggleVoice && (
          <button
            type="button"
            onClick={() => {
              chatbotApi.unlockAudioContext();
              onToggleVoice();
            }}
            title={mode === 'voice' ? 'Switch to Text Chat' : 'Switch to Voice Assistant'}
            aria-label={mode === 'voice' ? 'Switch to Text Chat' : 'Switch to Voice Assistant'}
            className="p-1.5 rounded-xl text-orange-600 hover:text-orange-700 hover:bg-orange-100/80 transition flex items-center gap-1 text-xs font-semibold"
          >
            {mode === 'voice' ? (
              <MessageSquare className="w-4 h-4 text-slate-700" />
            ) : (
              <Mic className="w-4 h-4 text-orange-600 animate-pulse" />
            )}
          </button>
        )}

        <button
          type="button"
          onClick={onReset}
          title="Start New Chat"
          aria-label="Start New Chat"
          className="p-1.5 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100/80 transition"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onClose}
          title="Minimize Chat"
          aria-label="Minimize Chat"
          className="p-1.5 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100/80 transition"
        >
          <Minus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

