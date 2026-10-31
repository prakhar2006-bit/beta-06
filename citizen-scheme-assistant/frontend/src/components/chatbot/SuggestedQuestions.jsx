import React from 'react';
import { Sparkles } from 'lucide-react';

export const SuggestedQuestions = ({ questions = [], onSelectQuestion }) => {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="pt-2 pb-1 space-y-1.5">
      <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 px-1">
        <Sparkles className="w-3 h-3 text-orange-500" />
        <span>Suggested Questions</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {questions.map((q, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelectQuestion(q)}
            className="text-left text-[11px] font-medium text-slate-700 bg-white/90 hover:bg-orange-50 hover:text-orange-900 hover:border-orange-200 px-3 py-1.5 rounded-full border border-slate-200/80 transition-all shadow-2xs active:scale-95"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
};

