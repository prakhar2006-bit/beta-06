import React from 'react';
import { Bot, User } from 'lucide-react';
import { SchemeResultCard } from './SchemeResultCard';
import { EligibilityResult } from './EligibilityResult';
import { MissingDocuments } from './MissingDocuments';
import { FormattedMessage } from './FormattedMessage';

export const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-2.5 my-2.5 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-xs">
          <Bot className="w-3.5 h-3.5" />
        </div>
      )}

      <div className={`max-w-[85%] sm:max-w-[80%] space-y-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-3.5 py-2.5 rounded-2xl text-xs leading-relaxed ${
            isUser
              ? 'bg-slate-900 text-white rounded-br-xs shadow-xs font-medium'
              : 'glass-card text-slate-800 rounded-bl-xs border border-white/80 shadow-2xs'
          }`}
        >
          <FormattedMessage text={message.content} isDark={isUser} />
        </div>

        {/* Structured Scheme Result Cards */}
        {message.schemes && message.schemes.length > 0 && (
          <div className="space-y-1.5 pt-1">
            {message.schemes.map((sch) => (
              <SchemeResultCard key={sch.scheme_id} scheme={sch} />
            ))}
          </div>
        )}

        {/* Eligibility Result Card */}
        {message.eligibility && (
          <EligibilityResult eligibility={message.eligibility} />
        )}

        {/* Missing Documents Checklist */}
        {message.missing_documents && message.missing_documents.length > 0 && (
          <MissingDocuments documents={message.missing_documents} />
        )}

        {/* Timestamp */}
        <div className={`text-[9px] text-slate-400 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp
            ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : ''}
        </div>
      </div>

      {isUser && (
        <div className="w-7 h-7 rounded-xl bg-slate-800 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-xs">
          <User className="w-3.5 h-3.5" />
        </div>
      )}
    </div>
  );
};

