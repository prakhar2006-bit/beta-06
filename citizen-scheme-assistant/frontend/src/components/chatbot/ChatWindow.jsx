import React, { useState, useEffect, useRef } from 'react';
import { ChatHeader } from './ChatHeader';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { SuggestedQuestions } from './SuggestedQuestions';
import { TypingIndicator } from './TypingIndicator';
import { VoiceAssistantView } from './VoiceAssistantView';
import { chatbotApi } from '../../services/chatbotApi';
import { useLanguage } from '../../i18n/LanguageContext';
import { AlertCircle } from 'lucide-react';

export const ChatWindow = ({ onClose }) => {
  const { language } = useLanguage();
  const [mode, setMode] = useState('text'); // 'text' | 'voice'
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const messagesEndRef = useRef(null);

  // Load welcome message and suggestions
  useEffect(() => {
    const initialWelcome =
      language === 'hi'
        ? {
            role: 'assistant',
            content:
              'नमस्ते! मैं **सहायक (Sahayak)** हूँ। मैं आपकी योग्यता के अनुसार केंद्र व राज्य सरकार की कल्याणकारी योजनाएं खोजने, पात्रता की जांच करने और आवश्यक दस्तावेज़ समझने में आपकी मदद कर सकता हूँ।\n\nआप नीचे दिए गए सुझावों में से चुन सकते हैं या अपना प्रश्न टाइप कर सकते हैं।',
            timestamp: new Date().toISOString(),
          }
        : {
            role: 'assistant',
            content:
              'Hello! I am **Sahayak**, your official government scheme assistant. I can help you discover Central and State Government schemes, check your eligibility, and identify required documents tailored to your profile.\n\nYou can select a question below or type your inquiry.',
            timestamp: new Date().toISOString(),
          };

    setMessages([initialWelcome]);

    chatbotApi.getSuggestedQuestions(language).then((questions) => {
      setSuggestedQuestions(questions);
    });
  }, [language]);

  // Auto-scroll to bottom whenever messages or loading changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (text) => {
    if (!text || isLoading) return;

    setErrorMessage('');
    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await chatbotApi.sendMessage({
        message: text,
        conversationId,
        language,
      });

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMsg = {
        role: 'assistant',
        content: response.message,
        schemes: response.schemes || [],
        eligibility: response.eligibility || null,
        missing_documents: response.missing_documents || [],
        timestamp: response.created_at || new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      if (response.suggested_followups && response.suggested_followups.length > 0) {
        setSuggestedQuestions(response.suggested_followups);
      }
    } catch (err) {
      console.error('Chatbot error:', err);
      setErrorMessage(
        language === 'hi'
          ? 'माफ़ कीजिए, सर्वर से संपर्क नहीं हो पाया। कृपया पुनः प्रयास करें।'
          : 'Unable to reach the assistant server. Please check your connection and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetChat = () => {
    setConversationId(null);
    setMessages([
      {
        role: 'assistant',
        content:
          language === 'hi'
            ? 'नया वार्तालाप प्रारंभ किया गया। मैं आपकी किस प्रकार सहायता करूँ?'
            : 'New conversation started. How may I help you with government schemes today?',
        timestamp: new Date().toISOString(),
      },
    ]);
    chatbotApi.getSuggestedQuestions(language).then((questions) => {
      setSuggestedQuestions(questions);
    });
    setErrorMessage('');
  };

  if (mode === 'voice') {
    return (
      <VoiceAssistantView
        onClose={onClose}
        onSwitchToText={() => setMode('text')}
        conversationId={conversationId}
        setConversationId={setConversationId}
        messages={messages}
        setMessages={setMessages}
      />
    );
  }

  return (
    <div className="flex flex-col h-[520px] sm:h-[580px] w-full max-w-sm sm:max-w-md bg-white/95 backdrop-blur-2xl rounded-3xl border border-white/80 shadow-2xl overflow-hidden animate-slide-up">
      {/* Header */}
      <ChatHeader
        onReset={handleResetChat}
        onClose={onClose}
        isOnline={true}
        mode={mode}
        onToggleVoice={() => setMode('voice')}
      />

      {/* Error alert banner */}
      {errorMessage && (
        <div className="px-3.5 py-2 bg-rose-50 border-b border-rose-200 text-rose-800 text-[11px] flex items-center gap-2">
          <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-1">
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Starter / Follow-up Pills */}
      {suggestedQuestions.length > 0 && !isLoading && (
        <div className="px-4 py-1.5 border-t border-slate-100 bg-slate-50/50">
          <SuggestedQuestions
            questions={suggestedQuestions}
            onSelectQuestion={handleSendMessage}
          />
        </div>
      )}

      {/* Message Input Bar with Voice Shortcut */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={isLoading}
        onStartVoice={() => setMode('voice')}
      />
    </div>
  );
};

