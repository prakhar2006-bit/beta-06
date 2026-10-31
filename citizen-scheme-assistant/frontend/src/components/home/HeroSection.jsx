import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { ArrowRight, Search, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { SearchBar } from './SearchBar';

export const HeroSection = () => {
  const { t } = useLanguage();
  const [cursor, setCursor] = useState({ x: 52, y: 42 });

  return (
    <section
      className="hero-section relative overflow-hidden bg-stone-950 bg-cover bg-center bg-no-repeat pt-16 pb-12 md:pt-24 md:pb-20"
      style={{ '--cursor-x': `${cursor.x}%`, '--cursor-y': `${cursor.y}%` }}
      onMouseMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        setCursor({ x: ((event.clientX - rect.left) / rect.width) * 100, y: ((event.clientY - rect.top) / rect.height) * 100 });
      }}
    >
      <div className="hero-overlay absolute inset-0" aria-hidden="true" />
      <div className="hero-cursor-glow absolute inset-0 pointer-events-none" aria-hidden="true" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="max-w-3xl">
          <h1 className="max-w-3xl text-4xl sm:text-6xl lg:text-7xl font-black text-white tracking-[-0.04em] leading-[1.02] mb-5 md:mb-7">
            {t('heroHeading', 'Government Schemes Made Simple for Everyone.')}
          </h1>
          <p className="text-base sm:text-lg text-stone-200 max-w-2xl leading-relaxed font-normal mb-8 md:mb-10">
            {t('heroSubheading', 'Discover government benefits, understand your eligibility, and find the right schemes for you — all in one place.')}
          </p>
          <div className="flex flex-col sm:flex-row items-start gap-3 mb-8">
            <Link to="/screening" className="hero-primary group w-full sm:w-auto inline-flex items-center justify-center gap-4 px-6 py-3.5 text-sm font-semibold tracking-wide text-white active:scale-95 transition-all">
              <span>{t('heroCtaStart', 'Start Eligibility Check')}</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link to="/schemes" className="group w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 border border-white/40 text-sm font-semibold text-white hover:bg-white/10 transition-all active:scale-95">
              <Search className="w-4 h-4 text-orange-300" />
              <span>{t('heroCtaExplore', 'Explore Schemes')}</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
          <div className="max-w-3xl border-y border-white/20 grid grid-cols-1 sm:grid-cols-3 gap-0 mb-8">
            <div className="px-4 py-3 flex items-center gap-2.5 border-b sm:border-b-0 sm:border-r border-white/20"><CheckCircle2 className="w-4 h-4 text-emerald-300 shrink-0" /><span className="text-xs font-semibold text-stone-100">{t('heroStat1', '100+ Welfare Schemes')}</span></div>
            <div className="px-4 py-3 flex items-center gap-2.5 border-b sm:border-b-0 sm:border-r border-white/20"><CheckCircle2 className="w-4 h-4 text-emerald-300 shrink-0" /><span className="text-xs font-semibold text-stone-100">{t('heroStat2', '28 States & 8 UTs')}</span></div>
            <div className="px-4 py-3 flex items-center gap-2.5"><ShieldCheck className="w-4 h-4 text-emerald-300 shrink-0" /><span className="text-xs font-semibold text-stone-100">{t('heroStat3', 'Shared-Phone Privacy')}</span></div>
          </div>
          <div className="max-w-3xl"><SearchBar /></div>
        </div>
      </div>
    </section>
  );
};
