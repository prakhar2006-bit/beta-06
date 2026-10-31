import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCcw,
  Play,
  Square,
  ShieldCheck,
  Cpu,
  Radio,
  ExternalLink,
} from 'lucide-react';

/**
 * Independent Microphone & Speech Diagnostic Page
 * Runs completely independent of the chatbot to isolate:
 * 1. Hardware & browser mic permissions (getUserMedia)
 * 2. SpeechRecognition Web API support and live recognition events
 * 3. Interim and final transcript accuracy
 * 4. Audio output / TTS playback test
 */
export const VoiceDiagnosticPage = () => {
  // Diagnostic State Flags
  const [speechRecognitionSupported, setSpeechRecognitionSupported] = useState(false);
  const [apiVariant, setApiVariant] = useState('none');
  const [micPermissionStatus, setMicPermissionStatus] = useState('UNTESTED'); // UNTESTED, CHECKING, GRANTED, DENIED, ERROR
  const [micPermissionDetails, setMicPermissionDetails] = useState('');
  
  const [recognitionActive, setRecognitionActive] = useState(false);
  const [recognitionState, setRecognitionState] = useState('IDLE'); // IDLE, STARTING, LISTENING, PROCESSING, ENDED, ERROR
  const [selectedLang, setSelectedLang] = useState('en-IN');
  
  const [interimTranscript, setInterimTranscript] = useState('');
  const [finalTranscript, setFinalTranscript] = useState('');
  const [speechDetected, setSpeechDetected] = useState(false);
  const [lastError, setLastError] = useState(null);
  const [eventLogs, setEventLogs] = useState([]);

  // TTS playback state
  const [ttsStatus, setTtsStatus] = useState('IDLE'); // IDLE, PLAYING, COMPLETED, ERROR

  // References
  const recognitionInstanceRef = useRef(null);
  const isMountedRef = useRef(true);

  const addLog = useCallback((type, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setEventLogs((prev) => [
      { id: Date.now() + Math.random(), timestamp, type, message },
      ...prev.slice(0, 49),
    ]);
  }, []);

  // 1. Initial Browser Capabilities Check
  useEffect(() => {
    isMountedRef.current = true;
    const hasStandard = 'SpeechRecognition' in window;
    const hasWebkit = 'webkitSpeechRecognition' in window;

    if (hasStandard) {
      setSpeechRecognitionSupported(true);
      setApiVariant('window.SpeechRecognition (Standard)');
      addLog('INFO', 'Native SpeechRecognition detected');
    } else if (hasWebkit) {
      setSpeechRecognitionSupported(true);
      setApiVariant('window.webkitSpeechRecognition (Blink/Chrome/Edge)');
      addLog('INFO', 'webkitSpeechRecognition detected');
    } else {
      setSpeechRecognitionSupported(false);
      setApiVariant('None supported');
      addLog('ERROR', 'Web Speech Recognition API is NOT supported in this browser engine');
    }

    return () => {
      isMountedRef.current = false;
      if (recognitionInstanceRef.current) {
        try {
          recognitionInstanceRef.current.abort();
        } catch (e) {}
      }
    };
  }, [addLog]);

  // 2. Hardware Permission Test via getUserMedia
  const testMicrophoneHardwarePermission = async () => {
    setMicPermissionStatus('CHECKING');
    setMicPermissionDetails('Requesting hardware stream...');
    addLog('TEST', 'Executing navigator.mediaDevices.getUserMedia({ audio: true })');

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setMicPermissionStatus('ERROR');
      setMicPermissionDetails('navigator.mediaDevices.getUserMedia is unavailable (insecure context or unsupported browser)');
      addLog('ERROR', 'getUserMedia is not supported or page is not in secure origin');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const tracks = stream.getAudioTracks();
      const trackLabel = tracks.length > 0 ? tracks[0].label : 'Generic Mic';
      
      // Stop all tracks immediately to release the hardware
      tracks.forEach((track) => track.stop());

      setMicPermissionStatus('GRANTED');
      setMicPermissionDetails(`Hardware mic accessible: "${trackLabel}" (Tracks stopped)`);
      addLog('SUCCESS', `Microphone hardware access GRANTED: ${trackLabel}`);
    } catch (err) {
      console.error('[Diagnostic] Mic hardware check failed:', err);
      setMicPermissionStatus('DENIED');
      setMicPermissionDetails(`${err.name}: ${err.message}`);
      addLog('ERROR', `getUserMedia failed: ${err.name} - ${err.message}`);
    }
  };

  // 3. Speech Recognition Test using exact specs
  const startSpeechRecognitionTest = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      addLog('ERROR', 'Cannot start: SpeechRecognition is not supported');
      return;
    }

    if (recognitionInstanceRef.current) {
      try {
        recognitionInstanceRef.current.abort();
      } catch (e) {}
      recognitionInstanceRef.current = null;
    }

    setInterimTranscript('');
    setFinalTranscript('');
    setSpeechDetected(false);
    setLastError(null);
    setRecognitionState('STARTING');
    addLog('TEST', `Creating SpeechRecognition instance (lang: ${selectedLang}, continuous: false, interimResults: true)`);

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = selectedLang;
      recognition.continuous = false; // As specified in STEP 2
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onaudiostart = () => {
        addLog('EVENT', 'onaudiostart: Audio capture hardware active');
      };

      recognition.onsoundstart = () => {
        addLog('EVENT', 'onsoundstart: Sound/acoustics detected in room');
      };

      recognition.onspeechstart = () => {
        setSpeechDetected(true);
        addLog('EVENT', 'onspeechstart: Human speech recognized by audio engine');
      };

      recognition.onspeechend = () => {
        addLog('EVENT', 'onspeechend: Human speech stopped');
      };

      recognition.onaudioend = () => {
        addLog('EVENT', 'onaudioend: Audio hardware capture finished');
      };

      recognition.onstart = () => {
        if (!isMountedRef.current) return;
        setRecognitionActive(true);
        setRecognitionState('LISTENING');
        addLog('SUCCESS', 'onstart: SpeechRecognition service connected and actively LISTENING');
      };

      recognition.onresult = (event) => {
        if (!isMountedRef.current) return;
        setSpeechDetected(true);
        let interim = '';
        let final = '';

        for (let i = 0; i < event.results.length; ++i) {
          const res = event.results[i];
          if (res.isFinal) {
            final += res[0].transcript;
          } else {
            interim += res[0].transcript;
          }
        }

        if (interim) {
          setInterimTranscript(interim);
          addLog('RESULT', `Interim: "${interim}" (confidence: ${event.results[0]?.[0]?.confidence?.toFixed(2) || 'N/A'})`);
        }
        if (final) {
          setFinalTranscript(final);
          addLog('SUCCESS', `Final Transcript: "${final}" (confidence: ${event.results[0]?.[0]?.confidence?.toFixed(2) || 'N/A'})`);
        }
      };

      recognition.onerror = (event) => {
        if (!isMountedRef.current) return;
        setLastError(event.error);
        setRecognitionState('ERROR');
        addLog('ERROR', `onerror: ${event.error} (${event.message || 'No additional message'})`);
      };

      recognition.onend = () => {
        if (!isMountedRef.current) return;
        setRecognitionActive(false);
        setRecognitionState('ENDED');
        addLog('EVENT', 'onend: SpeechRecognition session disconnected');
        recognitionInstanceRef.current = null;
      };

      recognitionInstanceRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('[Diagnostic] Error starting SpeechRecognition:', err);
      setRecognitionState('ERROR');
      setLastError(err.message || 'Failed to start');
      addLog('ERROR', `Exception during start(): ${err.message}`);
    }
  };

  const stopSpeechRecognitionTest = () => {
    if (recognitionInstanceRef.current) {
      addLog('ACTION', 'Manual recognition.stop() requested');
      try {
        recognitionInstanceRef.current.stop();
      } catch (e) {
        addLog('WARN', `Stop error: ${e.message}`);
      }
    }
  };

  // 4. Audio Playback / TTS Hardware Diagnostic
  const testTtsPlayback = () => {
    if (!('speechSynthesis' in window)) {
      addLog('ERROR', 'window.speechSynthesis not supported');
      setTtsStatus('ERROR');
      return;
    }

    try {
      window.speechSynthesis.cancel();
      setTtsStatus('PLAYING');
      addLog('TEST', 'Starting SpeechSynthesis audio output test');

      const utterance = new SpeechSynthesisUtterance(
        selectedLang === 'hi-IN'
          ? 'नमस्ते! योजनामित्र सहायक वॉयस असिस्टेंट ऑडियो परीक्षण सफल रहा।'
          : 'Hello! Shayak Voice Assistant audio diagnostic test successful.'
      );
      utterance.lang = selectedLang;
      utterance.rate = 1.0;

      utterance.onstart = () => {
        addLog('EVENT', 'TTS playback started');
      };
      utterance.onend = () => {
        setTtsStatus('COMPLETED');
        addLog('SUCCESS', 'TTS playback completed successfully through speakers');
      };
      utterance.onerror = (e) => {
        setTtsStatus('ERROR');
        addLog('ERROR', `TTS playback error: ${e.error}`);
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      setTtsStatus('ERROR');
      addLog('ERROR', `SpeechSynthesis exception: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-orange-500/20 text-orange-400 border border-orange-500/30">
                Diagnostic Tool
              </span>
              <span className="text-xs text-slate-400 font-mono">Chrome / Edge Web Speech API</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
              Shayak Voice & Microphone Diagnostic
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Independent hardware, permission, and speech recognition verification for Indian Government Scheme Assistant.
            </p>
          </div>

          <a
            href="/"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 transition"
          >
            <span>Back to Home</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>

        {/* Diagnostic Status Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* 1. Browser API Card */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">1. Web Speech API</span>
              <Cpu className="w-5 h-5 text-indigo-400" />
            </div>
            <div className="flex items-center gap-2">
              {speechRecognitionSupported ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-rose-400 shrink-0" />
              )}
              <div>
                <p className="font-bold text-sm text-white">
                  {speechRecognitionSupported ? 'Supported' : 'Not Supported'}
                </p>
                <p className="text-xs text-slate-400 font-mono truncate max-w-[200px]" title={apiVariant}>
                  {apiVariant}
                </p>
              </div>
            </div>
            <p className="text-xs text-slate-500">
              Native speech recognition requires Chromium (Google Chrome, Microsoft Edge, Brave) or WebKit.
            </p>
          </div>

          {/* 2. Hardware / Mic Permission Card */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">2. Hardware / Mic Access</span>
              <ShieldCheck className="w-5 h-5 text-amber-400" />
            </div>
            <div className="flex items-center gap-2">
              {micPermissionStatus === 'GRANTED' && (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              )}
              {micPermissionStatus === 'DENIED' && (
                <XCircle className="w-6 h-6 text-rose-400 shrink-0" />
              )}
              {micPermissionStatus === 'CHECKING' && (
                <Radio className="w-6 h-6 text-amber-400 animate-spin shrink-0" />
              )}
              {micPermissionStatus === 'UNTESTED' && (
                <AlertTriangle className="w-6 h-6 text-slate-500 shrink-0" />
              )}
              {micPermissionStatus === 'ERROR' && (
                <XCircle className="w-6 h-6 text-rose-400 shrink-0" />
              )}
              <div>
                <p className="font-bold text-sm text-white">
                  {micPermissionStatus === 'GRANTED' && 'Permission Granted'}
                  {micPermissionStatus === 'DENIED' && 'Permission Denied'}
                  {micPermissionStatus === 'CHECKING' && 'Checking Stream...'}
                  {micPermissionStatus === 'UNTESTED' && 'Not Tested Yet'}
                  {micPermissionStatus === 'ERROR' && 'Insecure / Unavailable'}
                </p>
                <p className="text-xs text-slate-400 truncate max-w-[200px]" title={micPermissionDetails}>
                  {micPermissionDetails || 'Click Test Access button below'}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={testMicrophoneHardwarePermission}
              className="w-full py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition"
            >
              Test Hardware Mic (getUserMedia)
            </button>
          </div>

          {/* 3. Audio Playback / Speaker Card */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">3. Audio Speaker Test</span>
              <Volume2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="flex items-center gap-2">
              {ttsStatus === 'COMPLETED' && <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />}
              {ttsStatus === 'PLAYING' && <Radio className="w-6 h-6 text-orange-400 animate-pulse shrink-0" />}
              {ttsStatus === 'ERROR' && <XCircle className="w-6 h-6 text-rose-400 shrink-0" />}
              {ttsStatus === 'IDLE' && <Volume2 className="w-6 h-6 text-slate-500 shrink-0" />}
              <div>
                <p className="font-bold text-sm text-white">
                  {ttsStatus === 'PLAYING' && 'Speaking audio...'}
                  {ttsStatus === 'COMPLETED' && 'Audio Playback OK'}
                  {ttsStatus === 'ERROR' && 'Playback Failed'}
                  {ttsStatus === 'IDLE' && 'Speaker Diagnostic'}
                </p>
                <p className="text-xs text-slate-400">Verifies browser speech output</p>
              </div>
            </div>
            <button
              type="button"
              onClick={testTtsPlayback}
              className="w-full py-1.5 px-3 rounded-lg bg-orange-600 hover:bg-orange-500 text-xs font-semibold text-white transition flex items-center justify-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Test Speaker Audio</span>
            </button>
          </div>
        </div>

        {/* Live Speech Recognition Interaction Panel */}
        <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Mic className="w-5 h-5 text-orange-400" />
                <span>Live Speech Recognition Test Session</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Exact configuration: <code className="text-orange-300">lang="{selectedLang}"</code>, <code className="text-orange-300">continuous=false</code>, <code className="text-orange-300">interimResults=true</code>
              </p>
            </div>

            {/* Language Selection */}
            <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setSelectedLang('en-IN')}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  selectedLang === 'en-IN' ? 'bg-orange-500 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                English (en-IN)
              </button>
              <button
                type="button"
                onClick={() => setSelectedLang('hi-IN')}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  selectedLang === 'hi-IN' ? 'bg-orange-500 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                हिन्दी (hi-IN)
              </button>
            </div>
          </div>

          {/* Interactive Mic Trigger Section */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6 p-6 rounded-2xl bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-4">
              <button
                type="button"
                disabled={!speechRecognitionSupported}
                onClick={recognitionActive ? stopSpeechRecognitionTest : startSpeechRecognitionTest}
                className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all shadow-lg active:scale-95 disabled:opacity-50 ${
                  recognitionState === 'LISTENING'
                    ? 'bg-emerald-500 text-white shadow-emerald-500/40 animate-pulse'
                    : recognitionState === 'STARTING'
                    ? 'bg-amber-500 text-white shadow-amber-500/40 animate-spin'
                    : 'bg-orange-600 hover:bg-orange-500 text-white shadow-orange-600/30'
                }`}
              >
                {recognitionState === 'LISTENING' ? (
                  <Mic className="w-8 h-8 animate-bounce" />
                ) : (
                  <Mic className="w-8 h-8" />
                )}
              </button>

              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base text-white">
                    {recognitionState === 'IDLE' && 'Ready to Test Speech Recognition'}
                    {recognitionState === 'STARTING' && 'Connecting to Recognition Engine...'}
                    {recognitionState === 'LISTENING' && 'LISTENING (Microphone Active)'}
                    {recognitionState === 'ENDED' && 'Session Ended'}
                    {recognitionState === 'ERROR' && 'Recognition Error'}
                  </span>
                  {recognitionState === 'LISTENING' && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 animate-pulse">
                      Live
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {recognitionState === 'LISTENING'
                    ? 'Speak a test phrase into your microphone (e.g. "Find scholarships for students" or "PM-KISAN")'
                    : 'Click microphone button to begin. LISTENING will only display after onstart fires.'}
                </p>
              </div>
            </div>

            {recognitionActive && (
              <button
                type="button"
                onClick={stopSpeechRecognitionTest}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition flex items-center gap-1.5 shrink-0"
              >
                <Square className="w-4 h-4 fill-white" />
                <span>Stop Recognition</span>
              </button>
            )}
          </div>

          {/* Realtime Transcripts Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Interim Transcript */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                <span>Interim Transcript (Live Stream)</span>
              </span>
              <p className="text-sm font-medium text-cyan-200 min-h-[40px] italic">
                {interimTranscript || <span className="text-slate-600">Speech in progress will stream here...</span>}
              </p>
            </div>

            {/* Final Transcript */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Final Transcript (Captured Turn)</span>
              </span>
              <p className="text-sm font-bold text-emerald-300 min-h-[40px]">
                {finalTranscript || <span className="text-slate-600 font-normal">Final recognized words will lock here...</span>}
              </p>
            </div>
          </div>

          {/* Diagnostic Event Logs */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Event Log (Last 50 Events)
              </span>
              <button
                type="button"
                onClick={() => setEventLogs([])}
                className="text-xs text-slate-400 hover:text-white transition flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Clear Logs</span>
              </button>
            </div>

            <div className="h-48 overflow-y-auto rounded-xl bg-slate-950 p-3 font-mono text-xs border border-slate-800 space-y-1.5">
              {eventLogs.length === 0 ? (
                <p className="text-slate-600 italic">No events recorded yet. Click a test button above.</p>
              ) : (
                eventLogs.map((log) => (
                  <div key={log.id} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-slate-500 shrink-0">[{log.timestamp}]</span>
                    <span
                      className={`font-bold px-1.5 py-0.2 rounded text-[10px] shrink-0 ${
                        log.type === 'SUCCESS'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : log.type === 'ERROR'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : log.type === 'EVENT'
                          ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                          : log.type === 'RESULT'
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {log.type}
                    </span>
                    <span className="text-slate-300 break-all">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

