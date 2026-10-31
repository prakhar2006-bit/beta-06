import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { schemeApi } from '../../services/schemeApi';
import { ArrowRight, Search, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { SearchBar } from './SearchBar';

export const HeroSection = () => {
  const { t } = useLanguage();
  const [schemeCount, setSchemeCount] = useState(5);

  useEffect(() => {
    let active = true;
    schemeApi.getSchemesCount().then((count) => {
      if (active && count > 0) setSchemeCount(count);
    }).catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="relative overflow-hidden pt-8 pb-4 md:pt-12 md:pb-6 flex flex-col justify-center">
      {/* Ambient 3D Glass Orbs & Lighting in Background */}
      <div
        className="absolute top-8 right-1/4 w-80 h-80 rounded-full glass-orb-saffron opacity-80 pointer-events-none blur-sm"
        aria-hidden="true"
      />
      <div
        className="absolute -bottom-10 left-12 w-44 h-44 rounded-full glass-orb-pearl pointer-events-none shadow-xl"
        aria-hidden="true"
      />
      <div
        className="absolute top-1/4 left-1/3 w-96 h-96 rounded-full bg-orange-200/40 blur-3xl pointer-events-none"
        aria-hidden="true"
      />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center w-full">
        
        {/* Initiative Pill */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-panel text-xs font-semibold text-slate-800 shadow-glass mb-4 md:mb-6">
          <span className="flex h-2 w-2 rounded-full bg-saffron-500 animate-ping" />
          <span>{t('heroBadge', 'Independent scheme guide')}</span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500 font-normal">{t('heroCitizenVoice', 'Hindi & English')}</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.12] mb-4 md:mb-6">
          {t('heroHeading', 'Government Schemes Made Simple for Everyone.')}
        </h1>

        {/* Supporting Text */}
        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal mb-6 md:mb-8">
          {t(
            'heroSubheading',
            'Discover government benefits, understand your eligibility, and find the right schemes for you — all in one place.'
          )}
        </p>

        {/* Hero CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6 md:mb-8">
          {/* Primary Dark Capsule Button */}
          <Link
            to="/screening"
            className="glass-dark-pill group w-full sm:w-auto inline-flex items-center justify-center gap-4 px-7 py-3.5 rounded-full text-sm font-semibold tracking-wide hover:bg-black transition-all shadow-lg active:scale-95"
          >
            <span>{t('heroCtaStart', 'Start Eligibility Check')}</span>
            <div className="w-6 h-6 rounded-full bg-white/20 group-hover:bg-saffron-500 flex items-center justify-center transition-colors">
              <ArrowRight className="w-3.5 h-3.5 text-white" />
            </div>
          </Link>

          {/* Frosted Glass Explore Button */}
          <Link
            to="/schemes"
            className="glass-panel glass-panel-hover w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-full text-sm font-semibold text-slate-800 transition-all shadow-glass"
          >
            <Search className="w-4 h-4 text-slate-500" />
            <span>{t('heroCtaExplore', 'Explore Schemes')}</span>
          </Link>
        </div>

        {/* Trust Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 max-w-2xl mx-auto">
          <div className="glass-card-subtle px-4 py-2.5 rounded-2xl flex items-center justify-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="text-xs font-semibold text-slate-700">
              {t('heroStatSchemes', `${schemeCount} Welfare Schemes`).replace('{count}', schemeCount)}
            </span>
          </div>
          <div className="glass-card-subtle px-4 py-2.5 rounded-2xl flex items-center justify-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="text-xs font-semibold text-slate-700">{t('heroStat2', 'Central & State Schemes')}</span>
          </div>
          <div className="glass-card-subtle px-4 py-2.5 rounded-2xl flex items-center justify-center gap-2.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="text-xs font-semibold text-slate-700">{t('heroStat3', 'Nothing is saved after you close it')}</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mt-8 max-w-2xl mx-auto">
          <SearchBar />
        </div>

      </div>
    </section>
  );
};
