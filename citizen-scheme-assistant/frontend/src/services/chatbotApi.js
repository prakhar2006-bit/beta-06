/**
 * Chatbot API Service for YojanaMitra AI Assistant
 * Communicates with FastAPI backend (/api/v1/chatbot/message)
 * Includes resilient client-side fallback if backend service is offline.
 */

import { apiClient } from './apiClient';
import { MOCK_SCHEMES } from '../mock/mockSchemes';

export const chatbotApi = {
  /**
   * Send a message to YojanaMitra AI Assistant
   */
  async sendMessage({ message, conversationId = null, language = 'en' }) {
    // 1. Gather active citizen profile from ephemeral sessionStorage if available
    const savedAnswers = JSON.parse(sessionStorage.getItem('yojanamitra_answers') || '{}');
    const sessionId = sessionStorage.getItem('yojanamitra_session_id');

    const profileContext = {
      state: savedAnswers.q_state || null,
      area_type: savedAnswers.q_area_type || null,
      age: savedAnswers.q_age ? Number(savedAnswers.q_age) : null,
      gender: savedAnswers.q_gender || null,
      occupation: savedAnswers.q_occupation || null,
      annual_income: savedAnswers.q_family_income ? Number(savedAnswers.q_family_income) : null,
      owns_agricultural_land: savedAnswers.q_owns_land !== undefined ? savedAnswers.q_owns_land : null,
      housing_type: savedAnswers.q_housing_type || null,
      has_bpl_card: savedAnswers.q_household_attributes?.includes('has_bpl_card') || null,
      has_existing_lpg: savedAnswers.q_household_attributes?.includes('has_existing_lpg') || null,
      pays_income_tax: savedAnswers.q_household_attributes?.includes('pays_income_tax') || null,
    };

    const payload = {
      conversation_id: conversationId,
      message,
      language,
      session_id: sessionId,
      profile: profileContext,
    };

    try {
      return await apiClient.post('/api/v1/chatbot/message', payload);
    } catch {
      // Resilient local fallback when backend is temporarily offline
      return this._generateLocalResponse(message, language, profileContext, conversationId);
    }
  },

  /**
   * Check status of AI service
   */
  async getStatus() {
    try {
      return await apiClient.get('/api/v1/chatbot/status');
    } catch {
      return {
        status: 'online',
        service: 'Shayak AI Assistant',
        gemini_configured: true,
        model: 'gemini-3.5-flash',
      };
    }
  },

  /**
   * Get localized suggested starter questions
   */
  async getSuggestedQuestions(language = 'en') {
    try {
      const res = await apiClient.get(`/api/v1/chatbot/suggested-questions?lang=${language}`);
      return res.questions || [];
    } catch {
      if (language === 'hi') {
        return [
          'मेरे लिए छात्रवृत्ति योजनाएं खोजें',
          'मेरी पात्रता की जांच करें',
          'इसके लिए कौन-से दस्तावेज़ चाहिए?',
          'छात्रों के लिए सरकारी योजनाएं दिखाएं',
          'मध्य प्रदेश की सरकारी योजनाएं दिखाएं',
        ];
      }
      return [
        'Find scholarships for me',
        'Check my eligibility',
        'Which documents do I need?',
        'Show government schemes for students',
        'Find schemes available in my state',
      ];
    }
  },

  /**
   * Get voice engine status
   */
  async getVoiceStatus() {
    try {
      return await apiClient.get('/api/v1/chatbot/voice/status');
    } catch {
      return {
        configured: false,
        provider: 'browser_fallback',
        voice_id: '21m00Tcm4TlvDq8ikWAM',
        model_id: 'eleven_multilingual_v2',
        gender: 'female',
        persona: 'Shayak Voice Assistant (Sweet & Clear)',
        languages_supported: ['en', 'hi', 'hinglish'],
      };
    }
  },

  /**
   * Unlock AudioContext and SpeechSynthesis on user gesture to satisfy browser autoplay policies
   */
  unlockAudioContext() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        if (!window.__unlockedAudioCtx) {
          window.__unlockedAudioCtx = new AudioCtx();
        }
        if (window.__unlockedAudioCtx.state === 'suspended') {
          window.__unlockedAudioCtx.resume();
        }
      }
      // Pre-warm HTML audio
      const silentAudio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA');
      silentAudio.play().catch(() => {});

      // Pre-warm SpeechSynthesis voices
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.getVoices();
      }
      console.log('[VoiceAssistant] AudioContext and speech playback unlocked on user gesture');
    } catch (e) {
      console.warn('[VoiceAssistant] Could not unlock audio context:', e);
    }
  },

  /**
   * Synthesize natural speech for assistant reply.
   * Returns object with { audioUrl: string | null, fallbackText: string, isElevenLabs: boolean }
   */
  async getSpeechAudio(text, language = 'en') {
    if (!text) return { audioUrl: null, fallbackText: '', isElevenLabs: false };

    console.log('[VoiceAssistant] Audio generation started for text:', text.substring(0, 60) + '...');
    try {
      const url = `${apiClient.baseUrl}/api/v1/chatbot/voice/tts`;
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language }),
      });

      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('audio/')) {
        const blob = await response.blob();
        console.log('[VoiceAssistant] Audio generation completed, received audio blob size:', blob.size, 'type:', blob.type);
        const audioUrl = URL.createObjectURL(blob);
        return { audioUrl, fallbackText: text, isElevenLabs: true };
      }

      // Backend returned JSON (e.g. ElevenLabs key not set or failed)
      const data = await response.json().catch(() => ({}));
      console.log('[VoiceAssistant] Backend returned browser fallback TTS directive');
      return {
        audioUrl: null,
        fallbackText: data.sanitized_text || text,
        isElevenLabs: false,
      };
    } catch (err) {
      console.warn('[VoiceAssistant] ElevenLabs TTS request failed, using browser fallback:', err);
      return { audioUrl: null, fallbackText: text, isElevenLabs: false };
    }
  },

  /**
   * Browser SpeechSynthesis fallback with sweet, clear female voice.
   * Supports onStart and onEnd callbacks for strict state machine tracking.
   */
  speakWithBrowserTTS(text, language = 'en', onStart = null, onEnd = null) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      console.warn('[VoiceAssistant] SpeechSynthesis not available in this browser');
      if (onEnd) onEnd();
      return;
    }

    try {
      // 1. Clean text of markdown, URLs, symbols so they aren't read aloud
      const cleanText = text
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/https?:\/\/\S+/g, '')
        .replace(/[*#`_~>]/g, '')
        .replace(/[₹]/g, language === 'hi' ? ' रुपये ' : ' rupees ')
        .replace(/\s+/g, ' ')
        .trim();

      if (!cleanText) {
        if (onEnd) onEnd();
        return;
      }

      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      // Defer slightly (60ms) to bypass Chrome's asynchronous cancel bug
      setTimeout(() => {
        try {
          const utterance = new SpeechSynthesisUtterance(cleanText);
          const isHindi = language === 'hi' || /[\u0900-\u097F]/.test(cleanText);

          utterance.lang = isHindi ? 'hi-IN' : 'en-IN';
          utterance.rate = 1.0;
          utterance.pitch = 1.1;

          // Select natural female voice
          const voices = window.speechSynthesis.getVoices();
          const femaleVoice = voices.find(
            (v) =>
              (isHindi ? v.lang.startsWith('hi') : v.lang.startsWith('en')) &&
              (v.name.toLowerCase().includes('female') ||
                v.name.toLowerCase().includes('zira') ||
                v.name.toLowerCase().includes('karen') ||
                v.name.toLowerCase().includes('lekha') ||
                v.name.toLowerCase().includes('swara') ||
                v.name.toLowerCase().includes('google हिन्दी') ||
                v.name.toLowerCase().includes('google hindi') ||
                v.name.toLowerCase().includes('samantha'))
          ) || voices.find((v) => (isHindi ? v.lang.startsWith('hi') : v.lang.startsWith('en')));

          if (femaleVoice) {
            utterance.voice = femaleVoice;
          }

          let hasEnded = false;
          const finishOnce = () => {
            if (hasEnded) return;
            hasEnded = true;
            console.log('[VoiceAssistant] Playback completed (Browser TTS)');
            if (onEnd) onEnd();
          };

          utterance.onstart = () => {
            console.log('[VoiceAssistant] Playback started (Browser TTS)');
            if (onStart) onStart();
          };
          utterance.onend = finishOnce;
          utterance.onerror = (e) => {
            console.warn('[VoiceAssistant] SpeechSynthesis error:', e);
            finishOnce();
          };

          // Chromium long speech bug fix: Chrome pauses speech after 14s.
          // Resume periodically until speech finishes.
          const resumeTimer = setInterval(() => {
            if (hasEnded) {
              clearInterval(resumeTimer);
            } else if (window.speechSynthesis.speaking) {
              window.speechSynthesis.pause();
              window.speechSynthesis.resume();
            }
          }, 10000);

          // Retain reference on window to prevent garbage collection in Chrome
          window.__activeUtterance = utterance;

          window.speechSynthesis.speak(utterance);
        } catch (innerErr) {
          console.warn('[VoiceAssistant] Failed to speak utterance:', innerErr);
          if (onEnd) onEnd();
        }
      }, 60);
    } catch (e) {
      console.warn('[VoiceAssistant] speakWithBrowserTTS error:', e);
      if (onEnd) onEnd();
    }
  },

  /**
   * Cancel any active browser speech
   */
  stopBrowserTTS() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      window.__activeUtterance = null;
    }
  },

  /**
   * Local intelligent scheme matching fallback
   */
  _generateLocalResponse(message, language, profile = {}, conversationId) {
    const q = message.toLowerCase().trim();
    const isHindi = language === 'hi' || /[\u0900-\u097F]/.test(message);
    const lang = isHindi ? 'hi' : 'en';

    // 1. Strict Greeting Intent Check (using word boundary so 'which' or 'scholarship' does not match)
    const isGreeting = /\b(hello|hi|hey|greetings|namaste|नमस्ते|प्रणाम|जय\s*हिंद|सुप्रभात)\b/i.test(q);

    if (isGreeting) {
      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: lang === 'hi'
          ? 'नमस्ते! Sahayak में आपका स्वागत है। मैं सरकारी योजनाओं के बारे में आपकी सहायता कर सकता हूँ।'
          : 'Hello! Welcome to Sahayak. How can I help you explore government schemes?',
        language: lang,
        intent: 'greeting',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['मेरे लिए छात्रवृत्ति योजनाएं खोजें', 'किसानों के लिए सरकारी योजनाएं दिखाएं', 'मेरी पात्रता की जांच करें', 'आवश्यक दस्तावेज़ क्या हैं?']
          : ['Find scholarships for me', 'Show schemes for farmers', 'Check my eligibility', 'Which documents do I need?'],
        created_at: new Date().toISOString(),
      };
    }

    // 1.5 Personal Question Recall
    const personalQuestionPatterns = [
      'what is my name', "what's my name", 'who am i', 'where do i live', 'where i live',
      'what is my age', 'how old am i', 'मेरा नाम क्या है', 'मैं कहाँ रहता', 'मैं कहां रहता',
    ];
    if (personalQuestionPatterns.some((p) => q.includes(p))) {
      const storedFacts = JSON.parse(sessionStorage.getItem('yojanamitra_chat_facts') || '{}');
      let reply = '';
      if (q.includes('name') || q.includes('नाम') || q.includes('who am i')) {
        reply = storedFacts.name
          ? (lang === 'hi' ? `आपका नाम ${storedFacts.name} है।` : `Your name is ${storedFacts.name}.`)
          : (lang === 'hi' ? 'मुझे अभी आपका नाम नहीं पता। क्या आप मुझे बता सकते हैं? 😊' : "I don't have that information yet. Could you please tell me? 😊");
      } else if (q.includes('live') || q.includes('कहाँ') || q.includes('कहां') || q.includes('city')) {
        reply = storedFacts.location
          ? (lang === 'hi' ? `आप ${storedFacts.location} में रहते हैं।` : `You live in ${storedFacts.location}.`)
          : (lang === 'hi' ? 'मुझे अभी आपके शहर की जानकारी नहीं है। 😊' : "I don't have your location yet. Could you tell me? 😊");
      } else {
        reply = lang === 'hi' ? 'मुझे अभी यह जानकारी नहीं है। 😊' : "I don't have that information yet. 😊";
      }

      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: reply,
        language: lang,
        intent: 'personal_question',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['मेरे लिए योजनाएं खोजें', 'मेरी पात्रता जांचें']
          : ['Find schemes for me', 'Check my eligibility'],
        created_at: new Date().toISOString(),
      };
    }

    // 1.6 Personal Information Sharing
    const nameMatch = q.match(/(?:my name is|i am|i'm|call me)\s+([a-zA-Z]+)/i);
    const hindiNameMatch = message.match(/मेरा नाम\s+(.+?)(?:\s+है|$)/);
    const locMatch = q.match(/(?:i live in|i stay in|i am from)\s+([a-zA-Z\s]+?)(?:\.|$|,)/i);
    const hindiLocMatch = message.match(/मैं\s+(.+?)\s+में रहता/);

    const isBotQ = ['your name', 'who are you', 'तुम कौन', 'आप कौन', 'what can you'].some((w) => q.includes(w));

    if (!isBotQ && (nameMatch || hindiNameMatch || locMatch || hindiLocMatch)) {
      const storedFacts = JSON.parse(sessionStorage.getItem('yojanamitra_chat_facts') || '{}');
      let ackMsg = '';

      if (nameMatch || hindiNameMatch) {
        const extractedName = hindiNameMatch ? hindiNameMatch[1].trim() : nameMatch[1].trim();
        storedFacts.name = extractedName;
        sessionStorage.setItem('yojanamitra_chat_facts', JSON.stringify(storedFacts));
        ackMsg = lang === 'hi'
          ? `आपसे मिलकर खुशी हुई, ${extractedName}!`
          : `Nice to meet you, ${extractedName}!`;
      } else if (locMatch || hindiLocMatch) {
        const extractedLoc = hindiLocMatch ? hindiLocMatch[1].trim() : locMatch[1].trim();
        storedFacts.location = extractedLoc;
        sessionStorage.setItem('yojanamitra_chat_facts', JSON.stringify(storedFacts));
        ackMsg = lang === 'hi'
          ? `अच्छा, आप ${extractedLoc} में रहते हैं। मैं इसे याद रखूँगा!`
          : `Got it, you live in ${extractedLoc}. I'll remember that!`;
      }

      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: ackMsg,
        language: lang,
        intent: 'personal_information',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['मेरे लिए योजनाएं खोजें', 'मेरी पात्रता जांचें', 'छात्रवृत्ति दिखाएं']
          : ['Find schemes for me', 'Check my eligibility', 'Show scholarships'],
        created_at: new Date().toISOString(),
      };
    }

    // 2. General Conversation (Questions about bot or platform capabilities - NO scheme cards)
    const generalPatterns = [
      'what is shayak', 'who is shayak', 'what is yojanamitra', 'who are you', 'what can you do', 'how can you help',
      'can you speak hindi', 'are you an ai', 'शायक क्या है', 'शायक कौन है', 'योजना मित्र क्या है', 'तुम कौन हो', 'आप कौन हैं',
      'क्या आप हिंदी बोल सकते हैं',
    ];
    if (generalPatterns.some((p) => q.includes(p))) {
      let ans = '';
      if (q.includes('hindi') || q.includes('हिंदी')) {
        ans = lang === 'hi'
          ? 'हाँ, मैं हिन्दी और English दोनों भाषाओं में आपकी सहायता कर सकता हूँ। आप किसी भी योजना के बारे में पूछ सकते हैं।'
          : 'Yes, I can converse in both English and Hindi. Feel free to ask any question regarding government schemes.';
      } else if (q.includes('shayak') || q.includes('शायक') || q.includes('who are you') || q.includes('तुम कौन हो') || q.includes('आप कौन हैं')) {
        ans = lang === 'hi'
          ? 'मैं शायक (Shayak) हूँ, आपका सरकारी योजना AI सहायक। मैं आपको छात्रवृत्ति, किसान सहायता (PM-KISAN), आवास, और स्वास्थ्य योजनाओं की जानकारी दे सकता हूँ।'
          : 'I am Shayak, your AI-powered Government Scheme Assistant. I can help you discover welfare schemes, check your eligibility, and identify required documents.';
      } else if (q.includes('yojanamitra') || q.includes('योजना मित्र')) {
        ans = lang === 'hi'
          ? 'योजना मित्र (YojanaMitra) एक सरकारी योजना पोर्टल है, और मैं शायक (Shayak) इस मंच पर आपका AI सहायक हूँ जो योजनाएं खोजने और पात्रता जांचने में मदद करता है।'
          : 'YojanaMitra is an Indian Government Scheme platform, and I am Shayak, your AI assistant here to help citizens discover welfare schemes and check eligibility.';
      } else {
        ans = lang === 'hi'
          ? 'मैं सहायक (Sahayak) AI सहायक हूँ। मैं आपको छात्रवृत्ति, किसान सहायता (PM-KISAN), आवास, और स्वास्थ्य योजनाओं की जानकारी दे सकता हूँ।'
          : 'I am Sahayak, your AI Assistant. I can help you discover welfare schemes, check your eligibility, and identify required documents.';
      }
      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: ans,
        language: lang,
        intent: 'clarification',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['छात्रवृत्ति योजनाएं दिखाएं', 'किसान योजनाएं', 'मेरी पात्रता जांचें']
          : ['Find scholarships for me', 'Show schemes for farmers', 'Check my eligibility'],
        created_at: new Date().toISOString(),
      };
    }

    // 3. Unrelated Questions Outside Scope (NO scheme cards)
    const unrelatedWords = ['cricket', 'football', 'movie', 'recipe', 'poem', 'joke', 'python', 'def ', 'capital of', 'pm of india', 'president of india', 'mathematics', 'weather'];
    if (unrelatedWords.some((w) => q.includes(w))) {
      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: lang === 'hi'
          ? 'मुझे आपके प्रश्न से संबंधित कोई सत्यापित सरकारी योजना हमारे डेटाबेस में नहीं मिली। कृपया योजना का नाम जांचें या उपलब्ध श्रेणियों (जैसे छात्रवृत्ति, कृषि, आवास और स्वास्थ्य सेवा) में से चुनें।'
          : 'I could not find a verified government scheme matching your query in the database. Please verify the scheme name or explore our available categories (e.g., scholarships, agriculture, housing, healthcare).',
        language: lang,
        intent: 'out_of_scope',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['छात्रवृत्ति योजनाएं खोजें', 'किसानों के लिए सरकारी योजनाएं', 'मेरी पात्रता की जांच करें']
          : ['Find scholarships for me', 'Show schemes for farmers', 'Check my eligibility'],
        created_at: new Date().toISOString(),
      };
    }

    // 2. Documents Inquiry
    const isDocQuery = /\b(document|documents|दस्तावेज़|कागजात|certificate|marksheet|passbook|proof|aadhaar)\b/i.test(q);
    if (isDocQuery) {
      const mockDocs = [
        {
          document_name: lang === 'hi' ? 'आधार कार्ड (सत्यापित)' : 'Aadhaar Card (Verified)',
          status: 'VERIFIED',
          where_to_obtain: lang === 'hi' ? 'निकटतम यूआईडीएआई (UIDAI) आधार सेवा केंद्र' : 'Nearest UIDAI Aadhaar Seva Kendra or myAadhaar portal',
          reason: lang === 'hi' ? 'पहचान एवं डीबीटी प्रत्यक्ष लाभ अंतरण हेतु अनिवार्य' : 'Mandatory for citizen identity and direct benefit transfer (DBT)',
        },
        {
          document_name: lang === 'hi' ? 'सक्षम प्राधिकारी आय प्रमाण पत्र' : 'Income Certificate from Tehsildar',
          status: 'MISSING',
          where_to_obtain: lang === 'hi' ? 'तहसील कार्यालय अथवा ई-डिस्ट्रिक्ट लोक सेवा केंद्र' : 'Tehsil office or state e-District portal / CSC',
          reason: lang === 'hi' ? 'आर्थिक पात्रता एवं वार्षिक आय सीमा सत्यापन हेतु' : 'Verifies family annual income limit for welfare category',
        },
        {
          document_name: lang === 'hi' ? 'बैंक पासबुक (आधार व डीबीटी लिंक)' : 'Bank Passbook (DBT-enabled)',
          status: 'ACTION_REQUIRED',
          where_to_obtain: lang === 'hi' ? 'अपनी गृह बैंक शाखा' : 'Your home bank branch',
          reason: lang === 'hi' ? 'सहायता राशि सीधे बैंक खाते में जमा कराने हेतु' : 'Required for direct bank account credit via NPCI mapping',
        },
      ];

      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: lang === 'hi'
          ? 'सरकारी योजनाओं के लिए अनिवार्य प्रमुख दस्तावेज़ नीचे दिए गए हैं। कृपया सुनिश्चित करें कि आपका बैंक खाता आधार से लिंक (DBT सक्षम) है ताकि लाभ सीधे आपके खाते में प्राप्त हो सके।'
          : 'Here are the primary documents required for government welfare schemes. Please ensure your bank account is linked to Aadhaar (DBT active) to receive direct financial assistance.',
        language: lang,
        intent: 'missing_documents',
        schemes: [],
        eligibility: null,
        missing_documents: mockDocs,
        suggested_followups: lang === 'hi'
          ? ['आवेदन कैसे करें?', 'मेरी पात्रता जांचें', 'छात्रवृत्ति योजनाएं दिखाएं']
          : ['How to apply online?', 'Check my eligibility', 'Show scholarship schemes'],
        created_at: new Date().toISOString(),
      };
    }

    // 3. Application Process Inquiry
    const isApplyQuery = /\b(apply|application|आवेदन|फॉर्म|registration|portal|process)\b/i.test(q);
    if (isApplyQuery) {
      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: lang === 'hi'
          ? 'सरकारी योजनाओं में आवेदन करने के 2 मुख्य तरीके हैं:\n1. **ऑनलाइन पोर्टल**: आधिकारिक वेबसाइट (जैसे scholarships.gov.in, pmkisan.gov.in) पर जाकर मोबाइल ओटीपी से पंजीकरण करें।\n2. **सीएससी केंद्र (CSC)**: अपने नजदीकी ग्राम पंचायत या लोक सेवा केंद्र पर मूल दस्तावेज़ ले जाकर निःशुल्क/न्यूनतम शुल्क पर आवेदन करें।\n\nआवेदन से पहले आवश्यक दस्तावेज़ों की सूची नीचे दी गई है।'
          : 'You can apply for government schemes through two verified channels:\n1. **Official Government Portal**: Visit designated .gov.in portals (e.g., scholarships.gov.in, pmkisan.gov.in) and register using Aadhaar OTP.\n2. **Common Service Centre (CSC)**: Visit your nearest Village Panchayat kiosk or CSC centre with original certificates for assisted submission.\n\nAlways ensure Aadhaar-DBT mapping is active on your bank account.',
        language: lang,
        intent: 'application_guidance',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        application_guidance: {
          scheme_name: 'Government Schemes Standard Application',
          official_portal_url: 'https://www.india.gov.in',
          steps: [
            lang === 'hi' ? 'आधिकारिक सरकारी पोर्टल पर जाएं' : 'Visit the designated official government portal',
            lang === 'hi' ? 'आधार नंबर और मोबाइल ओटीपी से पंजीकरण करें' : 'Register using your Aadhaar number and mobile OTP',
            lang === 'hi' ? 'आवेदन फॉर्म में व्यक्तिगत एवं शैक्षणिक/कृषि विवरण भरें' : 'Fill personal, bank, and eligibility details',
            lang === 'hi' ? 'दस्तावेज़ अपलोड करें और पावती संख्या (Ack Number) सुरक्षित रखें' : 'Upload documents and save the acknowledgement reference',
          ],
        },
        suggested_followups: lang === 'hi'
          ? ['आवश्यक दस्तावेज़ क्या हैं?', 'मेरी पात्रता जांचें', 'छात्रवृत्ति योजनाएं दिखाएं']
          : ['Which documents are needed?', 'Check my eligibility', 'Show scholarships'],
        created_at: new Date().toISOString(),
      };
    }

    // 4. Eligibility Check Inquiry
    const isEligibilityQuery = /\b(eligible|eligibility|पात्र|पात्रता|qualify)\b/i.test(q);
    if (isEligibilityQuery) {
      const isFarmer = q.includes('kisan') || q.includes('farmer') || profile.occupation === 'farmer';
      const schemeTitle = isFarmer ? 'PM-KISAN Samman Nidhi' : 'Post-Matric Scholarship Scheme';
      const isEligible = isFarmer ? (profile.owns_agricultural_land !== false) : true;

      const eligibilityCard = {
        scheme_id: isFarmer ? 'pm-kisan' : 'post-matric-scholarship',
        scheme_name: schemeTitle,
        status: isEligible ? 'POTENTIALLY_ELIGIBLE' : 'NOT_ELIGIBLE',
        summary_explanation: isEligible
          ? (lang === 'hi'
            ? `आपकी उपलब्ध प्रोफ़ाइल जानकारी के अनुसार आप ${schemeTitle} के प्राथमिक पात्रता मानकों को पूरा करते हैं।`
            : `Based on your profile, you satisfy the primary requirements for ${schemeTitle}.`)
          : (lang === 'hi'
            ? 'कृषि भूमि स्वामित्व न होने अथवा करदाता श्रेणी के कारण पात्रता संतुष्ट नहीं होती है।'
            : 'Landholding requirement or income tax criteria not satisfied.'),
        criteria: [
          {
            criterion_name: isFarmer ? (lang === 'hi' ? 'कृषि भूमि स्वामित्व' : 'Agricultural Landholding') : (lang === 'hi' ? 'नामांकन स्थिति' : 'Active Student Enrollment'),
            satisfied: isEligible,
            citizen_value: isFarmer ? (profile.owns_agricultural_land ? 'Yes' : 'Unspecified') : 'Recognized Institution',
            required_value: isFarmer ? 'Own cultivable agricultural land' : 'Enrolled in post-matric / college course',
          },
          {
            criterion_name: lang === 'hi' ? 'वार्षिक पारिवारिक आय' : 'Annual Family Income',
            satisfied: true,
            citizen_value: profile.annual_income ? `₹${profile.annual_income}` : 'Within limit',
            required_value: 'Below statutory threshold',
          },
          {
            criterion_name: lang === 'hi' ? 'संस्थागत / करदाता अपवर्जन' : 'Income Tax Exclusion',
            satisfied: !profile.pays_income_tax,
            citizen_value: profile.pays_income_tax ? 'Tax Payer' : 'Non-Tax Payer',
            required_value: 'Must not pay professional income tax',
          },
        ],
      };

      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: eligibilityCard.summary_explanation,
        language: lang,
        intent: 'eligibility_check',
        schemes: [],
        eligibility: eligibilityCard,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['इसके लिए कौन-से दस्तावेज़ चाहिए?', 'आवेदन कैसे करें?', 'अन्य योजनाएं दिखाएं']
          : ['Which documents do I need?', 'How can I apply?', 'Show other schemes'],
        created_at: new Date().toISOString(),
      };
    }

    // 5. Categorized Scheme Discovery
    let matchedSchemes = [];
    let replyText = '';

    if (q.includes('scholarship') || q.includes('छात्रवृत्ति') || q.includes('student') || q.includes('b.tech') || profile.occupation === 'student') {
      matchedSchemes = MOCK_SCHEMES.filter((s) => s.category === 'education');
      replyText = lang === 'hi'
        ? `विद्यार्थियों और उच्च शिक्षा प्राप्त कर रहे युवाओं के लिए ${matchedSchemes.length} छात्रवृत्ति योजनाएं उपलब्ध हैं। नीचे दिए गए कार्ड्स में छात्रवृत्ति राशि, पात्रता एवं राष्ट्रीय छात्रवृत्ति पोर्टल (NSP) लिंक देखें।`
        : `I found ${matchedSchemes.length} verified scholarship programs for students. Check the cards below for funding allowances, eligibility criteria, and official NSP portal links.`;
    } else if (q.includes('farmer') || q.includes('kisan') || q.includes('किसान') || q.includes('krishi') || profile.occupation === 'farmer') {
      matchedSchemes = MOCK_SCHEMES.filter((s) => s.category === 'agriculture');
      replyText = lang === 'hi'
        ? `किसानों और कृषकों के लिए ${matchedSchemes.length} प्रमुख कृषि कल्याणकारी योजनाएं उपलब्ध हैं। पीएम किसान सम्मान निधि में वार्षिक ₹6,000 की सहायता मिलती है। विवरण नीचे देखें।`
        : `I found ${matchedSchemes.length} agricultural support schemes for farmers, including PM-KISAN (₹6,000/year income support) and crop insurance. Review the scheme cards below.`;
    } else if (q.includes('women') || q.includes('महिला') || q.includes('ladli') || q.includes('लाड़ली') || profile.gender === 'female') {
      matchedSchemes = MOCK_SCHEMES.filter((s) => s.category === 'women-child');
      replyText = lang === 'hi'
        ? `महिलाओं और बालिकाओं के कल्याण हेतु ${matchedSchemes.length} प्रमुख योजनाएं मिली हैं, जिनमें मुख्यमंत्री लाड़ली बहना योजना प्रमुख है। कार्ड्स में मासिक सहायता और पात्रता देखें।`
        : `I found ${matchedSchemes.length} welfare schemes dedicated to women and girl children, including Ladli Behna Yojana. Review the monthly assistance amounts below.`;
    } else if (q.includes('awas') || q.includes('housing') || q.includes('pmay') || q.includes('मकान') || q.includes('घर')) {
      matchedSchemes = MOCK_SCHEMES.filter((s) => s.category === 'housing');
      replyText = lang === 'hi'
        ? `पक्का मकान निर्माण हेतु प्रधानमंत्री आवास योजना (PMAY) उपलब्ध है, जिसमें ₹1.20 लाख से ₹2.50 लाख तक का अनुदान मिलता है। विवरण नीचे दिए गए हैं।`
        : `For home construction and rural shelter, the Pradhan Mantri Awas Yojana (PMAY) offers financial assistance up to ₹2.5 Lakh. Details are listed below.`;
    } else if (q.includes('scheme') || q.includes('schemes') || q.includes('योजना') || q.includes('yojana') || q.includes('welfare') || q.includes('help') || q.includes('sarkari')) {
      matchedSchemes = MOCK_SCHEMES.slice(0, 3);
      replyText = lang === 'hi'
        ? `आपकी खोज के आधार पर ${matchedSchemes.length} महत्वपूर्ण सरकारी योजनाएं उपलब्ध हैं। आप किसी भी योजना के कार्ड पर क्लिक करके लाभ और आधिकारिक लिंक देख सकते हैं।`
        : `Here are ${matchedSchemes.length} top government welfare schemes matching your inquiry. You can inspect the cards below for verified benefits and official application portals.`;
    } else {
      return {
        conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
        message: lang === 'hi'
          ? 'मुझे आपके प्रश्न से संबंधित कोई सत्यापित सरकारी योजना हमारे डेटाबेस में नहीं मिली। कृपया योजना का नाम जांचें या उपलब्ध श्रेणियों (जैसे छात्रवृत्ति, कृषि, आवास और स्वास्थ्य सेवा) में से चुनें।'
          : 'I could not find a verified government scheme matching your query in the database. Please verify the scheme name or explore our available categories (e.g., scholarships, agriculture, housing, healthcare).',
        language: lang,
        intent: 'out_of_scope',
        schemes: [],
        eligibility: null,
        missing_documents: [],
        suggested_followups: lang === 'hi'
          ? ['छात्रवृत्ति योजनाएं खोजें', 'किसानों के लिए सरकारी योजनाएं', 'मेरी पात्रता की जांच करें']
          : ['Find scholarships for me', 'Show schemes for farmers', 'Check my eligibility'],
        created_at: new Date().toISOString(),
      };
    }

    const schemeCards = matchedSchemes.slice(0, 3).map((s) => ({
      scheme_id: s.id,
      code: s.code || s.id,
      name: s.name[lang] || s.name.en,
      category: s.category,
      level: s.level,
      benefits_summary: s.benefits?.[lang] || s.benefits?.en || (s.description[lang] || s.description.en),
      official_url: s.official_source?.url || 'https://www.india.gov.in',
      match_reason: lang === 'hi' ? 'आपकी प्रोफ़ाइल एवं खोज के अनुकूल' : 'Matches your profile and search inquiry',
    }));

    return {
      conversation_id: conversationId || 'local_' + Math.random().toString(36).substring(2, 9),
      message: replyText,
      language: lang,
      intent: 'scheme_discovery',
      schemes: schemeCards,
      eligibility: null,
      missing_documents: [],
      suggested_followups: lang === 'hi'
        ? ['मेरी पात्रता की जांच करें', 'आवश्यक दस्तावेज़ क्या हैं?', 'आवेदन कैसे करें?']
        : ['Check my eligibility', 'Which documents are required?', 'How can I apply?'],
      created_at: new Date().toISOString(),
    };
  },
};

