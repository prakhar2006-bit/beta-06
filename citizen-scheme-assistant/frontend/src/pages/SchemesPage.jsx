import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import { errorKey } from '../i18n/integration.js';
import { schemeApi } from '../services/schemeApi.js';
import { SchemeCard } from '../components/schemes/SchemeCard';
import { Search, X } from 'lucide-react';

export const PublishedCatalog = ({ data, loading, error }) => {
  const { t } = useLanguage();
  if (error) {
    return (
      <div
        role="alert"
        className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm font-medium"
      >
        {error}
      </div>
    );
  }
  if (loading) {
    return (
      <p role="status" className="text-center py-12 text-slate-600 font-medium">
        {t('loading', 'Loading schemes...')}
      </p>
    );
  }
  if (!data?.items?.length) {
    return (
      <p
        role="status"
        className="glass-panel rounded-[28px] p-8 text-center text-slate-600 font-medium border border-white/80 shadow-glass"
      >
        {t('emptyPublished', 'No published schemes')}
      </p>
    );
  }
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {data.items.map((scheme) => (
        <SchemeCard key={scheme.id || scheme.code} scheme={scheme} />
      ))}
    </div>
  );
};

export const SchemesPage = () => {
  const { t, language } = useLanguage();
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get('search') || '');
  const [level, setLevel] = useState(params.get('level') || 'all');
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    schemeApi
      .getSchemes({ search, level, language, offset })
      .then((r) => {
        if (active) setData(r);
      })
      .catch((e) => {
        if (active) {
          setError(t(errorKey(e)));
          setData(null);
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [search, level, language, offset]);

  const handleSearchChange = (val) => {
    setSearch(val);
    setOffset(0);
    const newParams = new URLSearchParams(params);
    if (val) newParams.set('search', val);
    else newParams.delete('search');
    setParams(newParams);
  };

  const handleLevelChange = (val) => {
    setLevel(val);
    setOffset(0);
    const newParams = new URLSearchParams(params);
    if (val && val !== 'all') newParams.set('level', val);
    else newParams.delete('level');
    setParams(newParams);
  };

  return (
    <div className="flex-1 py-8 sm:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        {/* Page Header */}
        <div>
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full glass-card-subtle text-[11px] font-bold text-orange-700 uppercase tracking-wider mb-2">
            Catalog & Discovery
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mb-1.5">
            {t('exploreTitle', 'Explore Government Schemes')}
          </h1>
          <p className="text-sm text-slate-600">
            {t(
              'catalogueIntro',
              'Search and filter through Central and State Government welfare programs'
            )}
          </p>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              className="w-full pl-11 pr-10 py-3.5 glass-input rounded-full text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
              aria-label={t('searchSchemesInput', 'Search by scheme name or keyword...')}
              placeholder={t('searchSchemesInput', 'Search by scheme name or keyword...')}
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
            />
            {search && (
              <button
                type="button"
                onClick={() => handleSearchChange('')}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="shrink-0">
            <select
              className="glass-input rounded-full py-3.5 px-5 text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none cursor-pointer"
              aria-label={t('filterTitle', 'Level Filter')}
              value={level}
              onChange={(e) => handleLevelChange(e.target.value)}
            >
              <option value="all">{t('allSchemes', 'All schemes')}</option>
              {['central', 'state', 'ut', 'local'].map((l) => (
                <option value={l} key={l}>
                  {t(l === 'central' ? 'centralGov' : l === 'state' ? 'stateGov' : l, l)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Published Catalog Grid */}
        <PublishedCatalog data={data} loading={loading} error={error} />

        {/* Pagination */}
        <div className="flex items-center justify-between pt-4 border-t border-white/60">
          <button
            type="button"
            disabled={!offset || loading}
            onClick={() => setOffset(Math.max(0, offset - 20))}
            className="px-5 py-2.5 rounded-full text-xs font-bold glass-panel text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-white transition-all shadow-glass"
          >
            ← {t('btnBack', 'Previous')}
          </button>
          <span className="text-xs text-slate-500 font-semibold">
            {data?.total ? `${offset + 1} - ${Math.min(offset + 20, data.total)} of ${data.total}` : ''}
          </span>
          <button
            type="button"
            disabled={!data?.has_more || loading}
            onClick={() => setOffset(offset + 20)}
            className="px-5 py-2.5 rounded-full text-xs font-bold glass-dark-pill disabled:opacity-40 disabled:cursor-not-allowed hover:bg-black transition-all shadow-md"
          >
            {t('btnNext', 'Next')} →
          </button>
        </div>
      </div>
    </div>
  );
};
