import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { Search, ArrowRight } from 'lucide-react';

export const SearchBar = ({ onSearch, initialValue = '', className = '' }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [query, setQuery] = useState(initialValue);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(query);
    } else {
      navigate(`/schemes?search=${encodeURIComponent(query)}`);
    }
  };

  const handleQuickTag = (tag) => {
    setQuery(tag);
    if (onSearch) {
      onSearch(tag);
    } else {
      navigate(`/schemes?search=${encodeURIComponent(tag)}`);
    }
  };

  return (
    <div className={`w-full max-w-4xl mx-auto ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="bg-white p-1.5 pl-4 flex items-center border border-stone-300 focus-within:border-slate-950 focus-within:ring-2 focus-within:ring-slate-950/10 transition-all">
          <div className="pr-2 text-slate-400">
            <Search className="w-5 h-5" aria-hidden="true" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t(
              'searchPlaceholder',
              'Search schemes by name, keyword or benefit (e.g., KISAN, Awas, Pension)...'
            )}
            className="w-full py-3 pr-3 text-slate-900 placeholder-stone-400 bg-transparent text-xs sm:text-sm font-medium focus:outline-none"
            aria-label="Search schemes"
          />
          <button
            type="submit"
            className="bg-slate-950 shrink-0 px-5 py-3 text-xs font-semibold text-white tracking-wide hover:bg-orange-700 transition-colors flex items-center gap-1.5 active:scale-[.98]"
          >
            <span>{t('searchButton', 'Search Schemes')}</span>
            <div className="w-4 h-4 flex items-center justify-center">
              <ArrowRight className="w-2.5 h-2.5 text-white" />
            </div>
          </button>
        </div>
      </form>

      {/* Popular quick tags */}
      <div className="mt-3.5 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-stone-300">
        <span className="font-semibold text-stone-300">{t('popularSearchesLabel', 'Popular:')}</span>
        {['PM-KISAN', 'Awas Yojana', 'Ujjwala', 'Vishwakarma', 'Ayushman', 'Ladli Behna'].map((tag) => (
          <button
            key={tag}
            type="button"
            onClick={() => handleQuickTag(tag)}
            className="text-stone-200 underline decoration-white/30 underline-offset-4 hover:text-orange-300 transition-colors text-[11px] font-semibold hover:-translate-y-0.5"
          >
            {tag}
          </button>
        ))}
      </div>
    </div>
  );
};
