import React from 'react';
import { useLanguage } from '../../i18n/LanguageContext';

export const HowItWorks = ({ className = '' }) => {
  const { t } = useLanguage();
  const steps = [
    { number: '01', titleKey: 'step1Title', descKey: 'step1Desc' },
    { number: '02', titleKey: 'step2Title', descKey: 'step2Desc' },
    { number: '03', titleKey: 'step3Title', descKey: 'step3Desc' },
  ];

  return (
    <section id="how-it-works" className={`py-24 md:py-32 relative bg-stone-100/70 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mb-12 md:mb-16">
          <p className="eyebrow mb-4">Transparent process</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight mb-3">
            {t('howItWorksHeading', 'How Scheme Sahayak Works')}
          </h2>
          <p className="text-base text-stone-500">
            {t('howItWorksSubheading', 'Three straightforward steps to identify and claim your citizen entitlements')}
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-stone-300">
          {steps.map((step) => (
            <div key={step.number} className="relative pt-6 md:pr-10 md:mr-10 border-b md:border-b-0 md:border-r border-stone-300 last:border-0 pb-8 md:pb-0">
              <span className="text-sm font-mono text-orange-700 mb-5 block">{step.number}</span>
              <h3 className="text-lg font-bold text-slate-950 mb-3">{t(step.titleKey)}</h3>
              <p className="text-sm text-stone-600 leading-relaxed font-normal">{t(step.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
