import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Mic } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export const ChatInput = ({ onSend, disabled = false, onStartVoice }) => {
  const { language } = useLanguage();
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const placeholder =
    language === 'hi'
      ? 'सरकारी योजनाओं के बारे में पूछें... (Enter दबाएं)'
      : 'Ask about government schemes... (Press Enter)';

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleChange = (e) => {
    setText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 100)}px`;
  };

  return (
    <div className="p-3 border-t border-slate-100 bg-white/80 backdrop-blur-md shrink-0">
      <div className="relative flex items-end gap-2 bg-slate-50 border border-slate-200/90 rounded-2xl p-1.5 focus-within:ring-2 focus-within:ring-orange-400 focus-within:border-orange-400 transition-all">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          maxLength={2000}
          className="w-full bg-transparent text-xs text-slate-800 placeholder-slate-400 resize-none px-2.5 py-1.5 focus:outline-none max-h-24 leading-relaxed"
        />

        {onStartVoice && (
          <button
            type="button"
            onClick={onStartVoice}
            disabled={disabled}
            title={language === 'hi' ? 'बोलकर बात करें' : 'Speak to Sahayak'}
            aria-label="Speak with voice assistant"
            className="w-8 h-8 rounded-xl bg-orange-50 hover:bg-orange-100 border border-orange-200/80 text-orange-600 flex items-center justify-center shrink-0 transition-all shadow-xs active:scale-95"
          >
            <Mic className="w-3.5 h-3.5" />
          </button>
        )}

        <button
          type="button"
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          aria-label="Send message"
          className="w-8 h-8 rounded-xl bg-orange-600 hover:bg-orange-700 disabled:opacity-40 disabled:hover:bg-orange-600 text-white flex items-center justify-center shrink-0 transition-all shadow-xs active:scale-95"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex items-center justify-between text-[9px] text-slate-400 pt-1.5 px-1">
        <span className="flex items-center gap-1">
          <Sparkles className="w-2.5 h-2.5 text-orange-500" />
          <span>Bilingual AI Guidance (English / हिंदी)</span>
        </span>
        <span>{text.length}/2000</span>
      </div>
    </div>
  );
};

