import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations } from './translations';
import { integration } from './integration.js';

const LanguageContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    // Shared-phone privacy: only use sessionStorage, never persistent remote or long localStorage
    const saved = sessionStorage.getItem('yojanamitra_lang');
    if (saved === 'hi' || saved === 'en') {
      return saved;
    }
    return import.meta.env.VITE_DEFAULT_LANGUAGE || 'hi';
  });

  const setLanguage = (lang) => {
    if (lang === 'hi' || lang === 'en') {
      setLanguageState(lang);
      sessionStorage.setItem('yojanamitra_lang', lang);
    }
  };

  const t = (key, fallback = '') => {
    if (integration[language]?.[key]) return integration[language][key];
    if (translations[language] && translations[language][key]) {
      return translations[language][key];
    }
    if (translations.en && translations.en[key]) {
      return translations.en[key];
    }
    return fallback || key;
  };

  // Helper to extract bilingual field e.g. { en: "...", hi: "..." }
  const getLocalized = (obj, fallback = '') => {
    if (!obj) return fallback;
    if (typeof obj === 'string') return obj;
    return obj[language] || obj.en || obj.hi || fallback;
  };

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, getLocalized }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

