import React from 'react';
import { useLanguage } from '../../i18n/LanguageContext';
import { INDIAN_STATES, SCHEME_CATEGORIES } from '../../constants/schemeConstants';
import { Filter, X, RotateCcw } from 'lucide-react';

export const FilterSidebar = ({
  filters,
  onChange,
  onReset,
  className = '',
  isMobile = false,
  onCloseMobile,
}) => {
  const { t, getLocalized } = useLanguage();

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/60">
        <div className="flex items-center gap-2 text-slate-900 font-bold text-sm sm:text-base">
          <Filter className="w-4 h-4 text-orange-500" />
          <span>{t('filterTitle', 'Filters')}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-500 hover:text-slate-900 transition"
          >
            <RotateCcw className="w-3 h-3" />
            <span>{t('resetFilters', 'Reset')}</span>
          </button>

          {isMobile && (
            <button
              type="button"
              onClick={onCloseMobile}
              className="p-1 rounded-full text-slate-400 hover:text-slate-700 bg-white/70"
              aria-label="Close filters"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Government Level Filter */}
      <div>
        <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2.5">
          {t('filterGovernmentLevel', 'Government Level')}
        </label>
        <div className="space-y-1.5">
          {[
            { value: 'all', labelKey: 'filterAllLevels', defaultLabel: 'All Levels' },
            { value: 'central', labelKey: 'filterCentral', defaultLabel: 'Central Schemes' },
            { value: 'state', labelKey: 'filterState', defaultLabel: 'State Schemes' },
          ].map((lvl) => (
            <label
              key={lvl.value}
              className={`flex items-center gap-2.5 p-2 rounded-xl text-xs font-semibold cursor-pointer transition ${
                filters.level === lvl.value
                  ? 'bg-white text-slate-950 shadow-xs border border-orange-300'
                  : 'text-slate-600 hover:bg-white/60'
              }`}
            >
              <input
                type="radio"
                name="levelFilter"
                value={lvl.value}
                checked={filters.level === lvl.value}
                onChange={() => onChange('level', lvl.value)}
                className="w-3.5 h-3.5 text-orange-500 focus:ring-orange-400 border-slate-300"
              />
              <span>{t(lvl.labelKey, lvl.defaultLabel)}</span>
            </label>
          ))}
        </div>
      </div>

      {/* State / UT Selector */}
      <div>
        <label htmlFor="state-filter-select" className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2">
          {t('filterStateSelect', 'State / Union Territory')}
        </label>
        <select
          id="state-filter-select"
          value={filters.state}
          onChange={(e) => onChange('state', e.target.value)}
          className="w-full text-xs font-medium glass-input rounded-xl py-2.5 px-3 text-slate-900 focus:outline-none"
        >
          {INDIAN_STATES.map((st) => (
            <option key={st.code} value={st.code}>
              {getLocalized(st.name)}
            </option>
          ))}
        </select>
      </div>

      {/* Category Pills */}
      <div>
        <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2.5">
          {t('filterCategory', 'Category')}
        </label>
        <div className="space-y-1">
          {SCHEME_CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              type="button"
              onClick={() => onChange('category', cat.id)}
              className={`w-full text-left px-3 py-2 rounded-xl text-xs transition flex items-center justify-between ${
                filters.category === cat.id
                  ? 'bg-slate-900 text-white font-bold shadow-xs'
                  : 'text-slate-600 hover:bg-white/70 hover:text-slate-900 font-medium'
              }`}
            >
              <span>{t(cat.key)}</span>
              {filters.category === cat.id && (
                <span className="w-1.5 h-1.5 rounded-full bg-orange-400" />
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
