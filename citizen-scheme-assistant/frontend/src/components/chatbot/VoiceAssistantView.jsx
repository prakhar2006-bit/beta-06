import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Mic,
  MicOff,
  Square,
  Volume2,
  VolumeX,
  MessageSquare,
  Minus,
  Sparkles,
  AlertCircle,
  Radio,
  Play,
  RotateCcw,
} from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';
import { chatbotApi } from '../../services/chatbotApi';
import { SchemeResultCard } from './SchemeResultCard';
import { FormattedMessage } from './FormattedMessage';

/**
 * Voice Assistant State Machine:
 * - IDLE
 * - REQUESTING_PERMISSION
 * - LISTENING (Actual SpeechRecognition session is active)
 * - PROCESSING_INPUT (Utterance captured; preparing request)
 * - WAITING_FOR_GEMINI (Chatbot backend analyzing query & schemes)
 * - GENERATING_AUDIO (Synthesizing ElevenLabs audio / preparing TTS)
 * - SPEAKING (Audio is actively playing aloud)
 * - PAUSED (Manually paused or waiting)
 * - ERROR (Microphone error, network error, or permission denied)
 */
export const VoiceAssistantView = ({
  onClose,
  onSwitchToText,
  conversationId,
  setConversationId,
  messages,
  setMessages,
}) => {
  const { language } = useLanguage();
  const [voiceState, setVoiceState] = useState('IDLE');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [latestAssistantText, setLatestAssistantText] = useState('');
  const [latestSchemes, setLatestSchemes] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState(language || 'en');
  const [errorMessage, setErrorMessage] = useState('');
  const [isMuted, setIsMuted] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [pendingAutoplayAudio, setPendingAutoplayAudio] = useState(null);

  // References for managing active speech recognition & audio playback
  const recognitionRef = useRef(null);
  const currentAudioRef = useRef(null);
  const turnIdRef = useRef(0);
  const isComponentMountedRef = useRef(true);
  const silenceDebounceTimerRef = useRef(null);
  const autoRestartTimeoutRef = useRef(null);
  const hasSubmittedTurnRef = useRef(false);
  const accumulatedTranscriptRef = useRef('');
  const isUserSpeakingRef = useRef(false);
  const scrollRef = useRef(null);

  // Stop any active audio and speech synthesis
  const cleanupAudio = useCallback(() => {
    if (currentAudioRef.current) {
      try {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
        currentAudioRef.current.onplay = null;
        currentAudioRef.current.onended = null;
        currentAudioRef.current.onerror = null;
      } catch (e) {
        // ignore
      }
      currentAudioRef.current = null;
    }
    chatbotApi.stopBrowserTTS();
    setPendingAutoplayAudio(null);
  }, []);

  // Stop active speech recognition instance
  const stopRecognition = useCallback(() => {
    if (silenceDebounceTimerRef.current) {
      clearTimeout(silenceDebounceTimerRef.current);
      silenceDebounceTimerRef.current = null;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onstart = null;
        recognitionRef.current.onresult = null;
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.abort();
      } catch (e) {
        // ignore
      }
      recognitionRef.current = null;
    }
    isUserSpeakingRef.current = false;
  }, []);

  // Sync latest message when messages array updates
  useEffect(() => {
    if (messages.length > 0) {
      const last = messages[messages.length - 1];
      if (last.role === 'assistant') {
        setLatestAssistantText(last.content);
        setLatestSchemes(last.schemes || []);
      }
    }
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, voiceState]);

  // Handle user speech utterance -> Existing Chatbot Backend Pipeline
  const handleUserUtterance = useCallback(async (spokenText) => {
    if (!spokenText || !spokenText.trim() || !isComponentMountedRef.current) return;

    const trimmed = spokenText.trim();
    const currentTurn = ++turnIdRef.current;
    console.log(`[VoiceAssistant] Submitting user utterance (Turn ${currentTurn}): "${trimmed}"`);

    stopRecognition();
    cleanupAudio();
    setVoiceState('WAITING_FOR_GEMINI');
    setErrorMessage('');
    setInterimTranscript('');

    // Append user message to active shared conversation
    const userMsg = {
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      // Send to existing intelligent chatbot backend
      const response = await chatbotApi.sendMessage({
        message: trimmed,
        conversationId,
        language: selectedLanguage,
      });

      if (!isComponentMountedRef.current || currentTurn !== turnIdRef.current) {
        console.log(`[VoiceAssistant] Discarding response for stale turn ${currentTurn}`);
        return; // Interrupted by new user input
      }

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMsg = {
        role: 'assistant',
        content: response.message,
        schemes: response.schemes || [],
        eligibility: response.eligibility || null,
        missing_documents: response.missing_documents || [],
        application_guidance: response.application_guidance || null,
        timestamp: response.created_at || new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setLatestAssistantText(response.message);
      setLatestSchemes(response.schemes || []);

      // Speak response aloud via ElevenLabs or Browser TTS
      await playAssistantVoice(response.message, selectedLanguage, currentTurn);
    } catch (err) {
      console.error('[VoiceAssistant] Error processing utterance:', err);
      if (!isComponentMountedRef.current) return;
      setVoiceState('ERROR');
      setErrorMessage(
        selectedLanguage === 'hi'
          ? 'उत्तर प्राप्त करने में समस्या हुई। कृपया पुनः बोलें।'
          : 'Error receiving response from Sahayak. Please try speaking again.'
      );
    }
  }, [conversationId, selectedLanguage, setConversationId, setMessages, stopRecognition, cleanupAudio]);

  // Turn-taking: Automatically resume listening after assistant finishes speaking
  const resumeListeningLoop = useCallback(() => {
    if (!isComponentMountedRef.current) return;
    console.log('[VoiceAssistant] Resuming continuous listening cycle...');
    cleanupAudio();
    setInterimTranscript('');

    if (autoRestartTimeoutRef.current) {
      clearTimeout(autoRestartTimeoutRef.current);
    }

    // 400ms echo-prevention delay before reopening microphone
    autoRestartTimeoutRef.current = setTimeout(() => {
      if (isComponentMountedRef.current) {
        initiateListeningSession();
      }
    }, 400);
  }, [cleanupAudio]);

  // Play assistant voice via ElevenLabs or Browser SpeechSynthesis
  const playAssistantVoice = useCallback(async (text, lang, turnId) => {
    if (!isComponentMountedRef.current || turnId !== turnIdRef.current) return;

    if (isMuted) {
      console.log('[VoiceAssistant] Voice response is muted by user; skipping audio');
      resumeListeningLoop();
      return;
    }

    setVoiceState('GENERATING_AUDIO');

    try {
      const speechRes = await chatbotApi.getSpeechAudio(text, lang);

      if (!isComponentMountedRef.current || turnId !== turnIdRef.current) return;

      if (speechRes.audioUrl) {
        // High quality ElevenLabs voice audio received
        const audio = new Audio(speechRes.audioUrl);
        currentAudioRef.current = audio;

        audio.onplay = () => {
          console.log('[VoiceAssistant] Audio playback started (ElevenLabs)');
          if (isComponentMountedRef.current && turnId === turnIdRef.current) {
            setVoiceState('SPEAKING');
            setPendingAutoplayAudio(null);
          }
        };

        audio.onended = () => {
          console.log('[VoiceAssistant] Audio playback completed (ElevenLabs)');
          if (speechRes.audioUrl) {
            try {
              URL.revokeObjectURL(speechRes.audioUrl);
            } catch (e) {}
          }
          if (!isComponentMountedRef.current || turnId !== turnIdRef.current) return;
          resumeListeningLoop();
        };

        audio.onerror = (e) => {
          console.warn('[VoiceAssistant] ElevenLabs audio playback failed, falling back to browser TTS:', e);
          fallbackToBrowserSpeech(speechRes.fallbackText || text, lang, turnId);
        };

        try {
          await audio.play();
        } catch (playErr) {
          console.warn('[VoiceAssistant] Audio playback blocked by browser autoplay policy:', playErr);
          // Allow single-tap manual playback
          setPendingAutoplayAudio({ audio, text, lang, turnId });
          setVoiceState('PAUSED');
          setErrorMessage(
            selectedLanguage === 'hi'
              ? 'ऑडियो सुनने के लिए नीचे दिए गए बटन पर टैप करें।'
              : 'Tap the button below to listen to Sahayak\'s response.'
          );
        }
      } else {
        // Fallback to browser SpeechSynthesis
        fallbackToBrowserSpeech(speechRes.fallbackText || text, lang, turnId);
      }
    } catch (err) {
      console.warn('[VoiceAssistant] TTS error, using browser fallback:', err);
      fallbackToBrowserSpeech(text, lang, turnId);
    }
  }, [isMuted, resumeListeningLoop, selectedLanguage]);

  // Fallback to browser SpeechSynthesis
  const fallbackToBrowserSpeech = useCallback((text, lang, turnId) => {
    if (!isComponentMountedRef.current || turnId !== turnIdRef.current) return;

    chatbotApi.speakWithBrowserTTS(
      text,
      lang,
      () => {
        // On playback started
        if (isComponentMountedRef.current && turnId === turnIdRef.current) {
          setVoiceState('SPEAKING');
        }
      },
      () => {
        // On playback finished
        if (isComponentMountedRef.current && turnId === turnIdRef.current) {
          resumeListeningLoop();
        }
      }
    );
  }, [resumeListeningLoop]);

  // Initiate real SpeechRecognition session with browser permission checks
  const initiateListeningSession = useCallback(async () => {
    if (!isComponentMountedRef.current) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      setVoiceState('ERROR');
      setErrorMessage(
        selectedLanguage === 'hi'
          ? 'आपका ब्राउज़र वाक् पहचान का समर्थन नहीं करता है। कृपया Google Chrome या Microsoft Edge का उपयोग करें।'
          : 'Your browser does not support Speech Recognition. Please use Google Chrome or Microsoft Edge.'
      );
      return;
    }

    cleanupAudio();
    stopRecognition();
    setErrorMessage('');
    setInterimTranscript('');
    hasSubmittedTurnRef.current = false;
    accumulatedTranscriptRef.current = '';

    // Check & request microphone permission if needed
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        console.log('[VoiceAssistant] Requesting microphone access...');
        setVoiceState('REQUESTING_PERMISSION');
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Immediately release stream so SpeechRecognition can acquire exclusive access
        stream.getTracks().forEach((track) => track.stop());
        console.log('[VoiceAssistant] Microphone access verified');
      } catch (permErr) {
        console.warn('[VoiceAssistant] Microphone permission denied:', permErr);
        if (!isComponentMountedRef.current) return;
        setVoiceState('ERROR');
        setErrorMessage(
          selectedLanguage === 'hi'
            ? 'माइक्रोफ़ोन की अनुमति अस्वीकृत है। कृपया ब्राउज़र सेटिंग्स में माइक्रोफ़ोन की अनुमति दें।'
            : 'Microphone permission denied. Please allow microphone access in your browser settings.'
        );
        return;
      }
    }

    try {
      console.log(`[VoiceAssistant] Initializing SpeechRecognition for language: ${selectedLanguage}`);
      const recognition = new SpeechRecognition();
      recognition.continuous = true; // Stay active across brief natural pauses
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.lang = selectedLanguage === 'hi' ? 'hi-IN' : 'en-IN';

      recognition.onstart = () => {
        console.log('[VoiceAssistant] Speech recognition session started (onstart)');
        if (!isComponentMountedRef.current) return;
        setVoiceState('LISTENING');
        isUserSpeakingRef.current = true;
      };

      recognition.onresult = (event) => {
        if (!isComponentMountedRef.current) return;

        let finalPart = '';
        let interimPart = '';

        for (let i = 0; i < event.results.length; ++i) {
          const res = event.results[i];
          if (res.isFinal) {
            finalPart += res[0].transcript + ' ';
          } else {
            interimPart += res[0].transcript;
          }
        }

        const fullUtterance = (finalPart + interimPart).trim();
        if (fullUtterance) {
          accumulatedTranscriptRef.current = fullUtterance;
          setInterimTranscript(fullUtterance);
          console.log(`[VoiceAssistant] Transcript update: "${fullUtterance}"`);

          // Debounce finalization: 850ms of silence after speech completes the turn
          if (silenceDebounceTimerRef.current) {
            clearTimeout(silenceDebounceTimerRef.current);
          }

          silenceDebounceTimerRef.current = setTimeout(() => {
            if (
              isComponentMountedRef.current &&
              !hasSubmittedTurnRef.current &&
              accumulatedTranscriptRef.current.trim()
            ) {
              hasSubmittedTurnRef.current = true;
              const textToSend = accumulatedTranscriptRef.current.trim();
              console.log(`[VoiceAssistant] Final utterance captured by silence timeout: "${textToSend}"`);
              setVoiceState('PROCESSING_INPUT');
              stopRecognition();
              handleUserUtterance(textToSend);
            }
          }, 850);
        }
      };

      recognition.onerror = (event) => {
        console.warn(`[VoiceAssistant] Recognition error event: ${event.error}`);
        if (!isComponentMountedRef.current) return;

        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setVoiceState('ERROR');
          setErrorMessage(
            selectedLanguage === 'hi'
              ? 'माइक्रोफ़ोन की अनुमति अस्वीकृत है। कृपया ब्राउज़र सेटिंग्स में अनुमति दें।'
              : 'Microphone permission denied. Please allow microphone access in your browser settings.'
          );
        } else if (event.error === 'no-speech') {
          // Normal background silence: do not show scary error, keep listening
          console.log('[VoiceAssistant] No speech detected in active window');
        } else if (event.error === 'network') {
          setVoiceState('ERROR');
          setErrorMessage(
            selectedLanguage === 'hi'
              ? 'वाक् पहचान सर्वर से संपर्क नहीं हो सका। कृपया इंटरनेट जांचें।'
              : 'Speech recognition network error. Please check your connection.'
          );
        } else {
          console.log(`[VoiceAssistant] Recoverable speech error: ${event.error}`);
        }
      };

      recognition.onend = () => {
        console.log('[VoiceAssistant] Recognition session stopped (onend)');
        if (!isComponentMountedRef.current) return;

        // If an utterance was accumulated and not yet submitted, finalize it now
        if (
          !hasSubmittedTurnRef.current &&
          accumulatedTranscriptRef.current &&
          accumulatedTranscriptRef.current.trim()
        ) {
          hasSubmittedTurnRef.current = true;
          const textToSend = accumulatedTranscriptRef.current.trim();
          console.log(`[VoiceAssistant] Submitting final transcript on session end: "${textToSend}"`);
          setVoiceState('PROCESSING_INPUT');
          handleUserUtterance(textToSend);
          return;
        }

        // If still supposed to be listening and user did not speak yet, restart smoothly
        if (voiceState === 'LISTENING') {
          autoRestartTimeoutRef.current = setTimeout(() => {
            if (isComponentMountedRef.current && voiceState === 'LISTENING') {
              console.log('[VoiceAssistant] Keeping listening session active');
              initiateListeningSession();
            }
          }, 300);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.warn('[VoiceAssistant] Failed to start recognition instance:', err);
      if (isComponentMountedRef.current) {
        setVoiceState('PAUSED');
      }
    }
  }, [cleanupAudio, stopRecognition, selectedLanguage, handleUserUtterance, voiceState]);

  // Initialize SpeechRecognition on mount
  useEffect(() => {
    isComponentMountedRef.current = true;
    chatbotApi.unlockAudioContext();
    initiateListeningSession();

    return () => {
      isComponentMountedRef.current = false;
      cleanupAudio();
      stopRecognition();
      if (autoRestartTimeoutRef.current) {
        clearTimeout(autoRestartTimeoutRef.current);
      }
      if (silenceDebounceTimerRef.current) {
        clearTimeout(silenceDebounceTimerRef.current);
      }
    };
  }, []);

  // User interruption while assistant is speaking
  const handleInterrupt = useCallback(() => {
    console.log('[VoiceAssistant] User interrupted assistant');
    turnIdRef.current++; // Invalidate active audio turn
    cleanupAudio();
    chatbotApi.unlockAudioContext();
    initiateListeningSession();
  }, [cleanupAudio, initiateListeningSession]);

  // Toggle Pause / Resume
  const toggleListening = useCallback(() => {
    chatbotApi.unlockAudioContext();
    if (voiceState === 'SPEAKING') {
      handleInterrupt();
    } else if (voiceState === 'LISTENING' || voiceState === 'REQUESTING_PERMISSION') {
      console.log('[VoiceAssistant] User paused listening');
      stopRecognition();
      setVoiceState('PAUSED');
    } else {
      console.log('[VoiceAssistant] User started listening');
      initiateListeningSession();
    }
  }, [voiceState, handleInterrupt, stopRecognition, initiateListeningSession]);

  // Switch conversation language
  const handleLanguageSwitch = useCallback((newLang) => {
    console.log(`[VoiceAssistant] Switching language to: ${newLang}`);
    setSelectedLanguage(newLang);
    turnIdRef.current++;
    cleanupAudio();
    stopRecognition();
    setTimeout(() => {
      initiateListeningSession();
    }, 150);
  }, [cleanupAudio, stopRecognition, initiateListeningSession]);

  // Play pending autoplay-restricted audio on user tap
  const handlePlayPendingAudio = useCallback(async () => {
    if (pendingAutoplayAudio && pendingAutoplayAudio.audio) {
      try {
        chatbotApi.unlockAudioContext();
        await pendingAutoplayAudio.audio.play();
        setPendingAutoplayAudio(null);
        setErrorMessage('');
      } catch (err) {
        console.warn('[VoiceAssistant] Manual audio play failed, falling back:', err);
        fallbackToBrowserSpeech(pendingAutoplayAudio.text, pendingAutoplayAudio.lang, pendingAutoplayAudio.turnId);
        setPendingAutoplayAudio(null);
      }
    }
  }, [pendingAutoplayAudio, fallbackToBrowserSpeech]);

  return (
    <div className="flex flex-col h-[520px] sm:h-[580px] w-full max-w-sm sm:max-w-md bg-gradient-to-b from-slate-900 via-slate-950 to-black text-white rounded-3xl border border-slate-800 shadow-2xl overflow-hidden animate-slide-up select-none">
      {/* Voice Assistant Header */}
      <div className="px-4 py-3.5 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-white shadow-sm">
            <Radio className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h3 className="text-xs sm:text-sm font-black text-white leading-tight">
                {selectedLanguage === 'hi' ? 'सहायक वॉयस असिस्टेंट' : 'Sahayak Voice Assistant'}
              </h3>
              <span className="text-[9px] font-bold uppercase tracking-wider text-amber-400 bg-amber-500/10 px-1.5 py-0.2 rounded border border-amber-500/20">
                Live
              </span>
            </div>
            <p className="text-[10px] text-slate-400">
              {voiceState === 'REQUESTING_PERMISSION' && (
                <span className="text-amber-400 font-semibold animate-pulse">● Requesting microphone access...</span>
              )}
              {voiceState === 'LISTENING' && (
                <span className="text-emerald-400 font-semibold animate-pulse">● Listening naturally...</span>
              )}
              {voiceState === 'PROCESSING_INPUT' && (
                <span className="text-cyan-400 font-semibold animate-pulse">● Capturing your speech...</span>
              )}
              {voiceState === 'WAITING_FOR_GEMINI' && (
                <span className="text-amber-400 font-semibold animate-pulse">● Searching verified schemes...</span>
              )}
              {voiceState === 'GENERATING_AUDIO' && (
                <span className="text-indigo-400 font-semibold animate-pulse">● Synthesizing voice audio...</span>
              )}
              {voiceState === 'SPEAKING' && (
                <span className="text-orange-400 font-semibold animate-pulse">
                  ● {selectedLanguage === 'hi' ? 'सहायक बोल रहा है...' : 'Sahayak speaking...'}
                </span>
              )}
              {voiceState === 'PAUSED' && <span className="text-slate-400">Paused (Tap orb to speak)</span>}
              {voiceState === 'ERROR' && <span className="text-rose-400 font-semibold">Microphone error</span>}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5">
          {/* Hardware & Voice Diagnostic Tool */}
          <a
            href="/voice-diagnostic"
            target="_blank"
            rel="noopener noreferrer"
            title="Open Microphone & Voice Diagnostic Tool"
            aria-label="Open Microphone Diagnostic"
            className="flex items-center gap-1 px-2 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-400 hover:text-amber-300 text-xs font-semibold transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[11px]">Mic Test</span>
          </a>

          {/* Switch to Text Chat Mode */}
          <button
            type="button"
            onClick={onSwitchToText}
            title="Switch to Text Chat"
            aria-label="Switch to Text Chat"
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
          >
            <MessageSquare className="w-3.5 h-3.5 text-orange-400" />
            <span className="hidden sm:inline">Text</span>
          </button>

          {/* Minimize */}
          <button
            type="button"
            onClick={onClose}
            title="Minimize"
            aria-label="Minimize"
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <Minus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Autoplay restriction banner if browser blocked audio */}
      {pendingAutoplayAudio && (
        <div className="px-4 py-2 bg-amber-500/20 border-b border-amber-500/40 text-amber-200 text-xs flex items-center justify-between gap-2 animate-fade-in">
          <span className="text-[11px] font-medium">Browser blocked automatic playback.</span>
          <button
            type="button"
            onClick={handlePlayPendingAudio}
            className="flex items-center gap-1 px-3 py-1 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-bold text-xs shadow-sm transition"
          >
            <Play className="w-3 h-3 fill-white" />
            <span>Play Audio</span>
          </button>
        </div>
      )}

      {/* Error alert banner */}
      {errorMessage && !pendingAutoplayAudio && (
        <div className="px-3.5 py-2 bg-rose-950/80 border-b border-rose-800/60 text-rose-200 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span className="flex-1 text-[11px] leading-tight">{errorMessage}</span>
          <button
            type="button"
            onClick={initiateListeningSession}
            className="text-[11px] underline font-bold text-rose-300 hover:text-white shrink-0"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Voice Center Visualization */}
      <div className="flex-1 flex flex-col items-center justify-between px-4 py-3 overflow-y-auto">
        {/* Realtime Conversation Transcript Bubble */}
        <div className="w-full flex-1 max-h-[170px] overflow-y-auto px-2 space-y-2 mb-2">
          {interimTranscript && (
            <div className="p-2.5 rounded-2xl bg-slate-800/90 border border-slate-700/80 text-xs text-slate-100 flex items-start gap-2 shadow-sm animate-fade-in">
              <span className="font-bold text-orange-400 shrink-0">You:</span>
              <span className="italic">{interimTranscript}</span>
            </div>
          )}

          {latestAssistantText && (
            <div className="p-3 rounded-2xl bg-orange-950/40 border border-orange-500/20 text-xs text-orange-100 shadow-sm animate-fade-in">
              <div className="flex items-center gap-1.5 mb-1.5 text-[11px] font-bold text-orange-400">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Sahayak</span>
              </div>
              <FormattedMessage text={latestAssistantText} isDark={true} className="text-xs text-slate-200 line-clamp-6" />
            </div>
          )}

          {/* Quick scheme cards preview in voice mode */}
          {latestSchemes.length > 0 && (
            <div className="space-y-1.5 pt-1">
              {latestSchemes.slice(0, 1).map((s) => (
                <SchemeResultCard key={s.scheme_id} scheme={s} />
              ))}
            </div>
          )}

          <div ref={scrollRef} />
        </div>

        {/* Central Animated Orb */}
        <div className="flex flex-col items-center justify-center my-auto py-2">
          <div className="relative flex items-center justify-center">
            {/* Outer Soundwave Rings (Active ONLY when actually listening or speaking) */}
            {(voiceState === 'LISTENING' || voiceState === 'SPEAKING') && (
              <>
                <div
                  className={`absolute w-36 h-36 rounded-full border ${
                    voiceState === 'SPEAKING' ? 'border-orange-500/30' : 'border-emerald-500/30'
                  } animate-ping opacity-75`}
                  style={{ animationDuration: '2s' }}
                />
                <div
                  className={`absolute w-28 h-28 rounded-full border-2 ${
                    voiceState === 'SPEAKING' ? 'border-amber-500/40' : 'border-emerald-500/40'
                  } animate-pulse`}
                />
              </>
            )}

            {/* Glowing Orb Button */}
            <button
              type="button"
              onClick={voiceState === 'SPEAKING' ? handleInterrupt : toggleListening}
              title={
                voiceState === 'SPEAKING'
                  ? 'Click to Interrupt Sahayak'
                  : voiceState === 'LISTENING'
                  ? 'Listening... Click to pause'
                  : 'Click to Speak'
              }
              aria-label={
                voiceState === 'SPEAKING'
                  ? 'Interrupt assistant'
                  : voiceState === 'LISTENING'
                  ? 'Pause assistant'
                  : 'Start speaking'
              }
              className={`relative z-10 w-24 h-24 rounded-full flex flex-col items-center justify-center shadow-2xl transition-all duration-300 transform active:scale-95 ${
                voiceState === 'SPEAKING'
                  ? 'bg-gradient-to-tr from-rose-600 via-orange-500 to-amber-500 shadow-orange-500/50 animate-pulse'
                  : voiceState === 'LISTENING'
                  ? 'bg-gradient-to-tr from-emerald-600 via-teal-500 to-emerald-400 shadow-emerald-500/40 scale-105'
                  : voiceState === 'WAITING_FOR_GEMINI' || voiceState === 'GENERATING_AUDIO' || voiceState === 'PROCESSING_INPUT'
                  ? 'bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 shadow-indigo-500/40 animate-pulse'
                  : 'bg-slate-800 hover:bg-slate-700 border border-slate-700 shadow-slate-900/50'
              }`}
            >
              {voiceState === 'SPEAKING' ? (
                <>
                  <Square className="w-8 h-8 text-white fill-white" />
                  <span className="text-[9px] font-bold text-white uppercase tracking-wider mt-1">
                    Interrupt
                  </span>
                </>
              ) : voiceState === 'LISTENING' ? (
                <>
                  <Mic className="w-9 h-9 text-white animate-bounce" />
                  <span className="text-[9px] font-bold text-white uppercase tracking-wider mt-0.5">
                    Listening
                  </span>
                </>
              ) : voiceState === 'WAITING_FOR_GEMINI' || voiceState === 'GENERATING_AUDIO' || voiceState === 'PROCESSING_INPUT' ? (
                <>
                  <Sparkles className="w-8 h-8 text-white animate-spin" />
                  <span className="text-[9px] font-bold text-white uppercase tracking-wider mt-0.5">
                    Thinking
                  </span>
                </>
              ) : (
                <>
                  <MicOff className="w-8 h-8 text-slate-400" />
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-0.5">
                    Tap to Talk
                  </span>
                </>
              )}
            </button>
          </div>

          {/* Spoken Audio Equalizer Bars Visualizer */}
          {voiceState === 'SPEAKING' && (
            <div className="flex items-center gap-1 mt-4 h-6">
              {[40, 75, 100, 60, 90, 45, 80, 50, 95, 30].map((h, i) => (
                <span
                  key={i}
                  className="w-1 bg-gradient-to-t from-orange-500 to-amber-300 rounded-full animate-pulse"
                  style={{
                    height: `${h}%`,
                    animationDelay: `${i * 0.1}s`,
                    animationDuration: '0.6s',
                  }}
                />
              ))}
            </div>
          )}

          {/* Turn-taking Status Text */}
          <p className="text-[11px] text-slate-400 font-medium text-center mt-3 max-w-xs">
            {voiceState === 'SPEAKING' ? (
              <span className="text-orange-300">Tap orb to interrupt anytime</span>
            ) : voiceState === 'LISTENING' ? (
              <span>Speak naturally. Sahayak will answer automatically.</span>
            ) : voiceState === 'WAITING_FOR_GEMINI' || voiceState === 'GENERATING_AUDIO' ? (
              <span className="text-amber-300">Consulting government scheme database...</span>
            ) : (
              <span>Continuous mode ready. Tap microphone to speak.</span>
            )}
          </p>
        </div>

        {/* Bottom Control Bar */}
        <div className="w-full pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
          {/* Language Selector */}
          <div className="flex items-center gap-1 bg-slate-800/80 rounded-xl p-1 border border-slate-700/60">
            <button
              type="button"
              onClick={() => handleLanguageSwitch('en')}
              className={`px-2.5 py-1 rounded-lg font-bold transition text-[11px] ${
                selectedLanguage === 'en'
                  ? 'bg-orange-500 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => handleLanguageSwitch('hi')}
              className={`px-2.5 py-1 rounded-lg font-bold transition text-[11px] ${
                selectedLanguage === 'hi'
                  ? 'bg-orange-500 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              हिन्दी
            </button>
          </div>

          {/* Voice Mute / Unmute */}
          <button
            type="button"
            onClick={() => setIsMuted((prev) => !prev)}
            title={isMuted ? 'Unmute Audio Response' : 'Mute Audio Response'}
            aria-label={isMuted ? 'Unmute audio' : 'Mute audio'}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            {isMuted ? (
              <>
                <VolumeX className="w-3.5 h-3.5 text-rose-400" />
                <span className="text-[11px]">Muted</span>
              </>
            ) : (
              <>
                <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[11px]">Voice Active</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
