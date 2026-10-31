import React from 'react';
import { useLanguage } from '../../i18n/LanguageContext';

export const TrustPrivacy = ({ className = '' }) => {
  const { t } = useLanguage();
  const trustPoints = [
    { number: '01', titleKey: 'trustPoint1Title', descKey: 'trustPoint1Desc' },
    { number: '02', titleKey: 'trustPoint2Title', descKey: 'trustPoint2Desc' },
    { number: '03', titleKey: 'trustPoint3Title', descKey: 'trustPoint3Desc' },
    { number: '04', titleKey: 'trustPoint4Title', descKey: 'trustPoint4Desc' },
  ];

  return (
    <section id="about" className={`py-24 md:py-32 relative ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mb-12 md:mb-16">
          <p className="eyebrow mb-4">Safety & integrity</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight mb-3">
            {t('trustHeading', 'Built on Trust, Privacy, and Official Sources')}
          </h2>
          <p className="text-base text-stone-500">{t('trustSubheading', 'Scheme Sahayak is designed specifically for public benefit and shared-phone safety.')}</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 border-t border-stone-300">
          {trustPoints.map((point) => (
            <div key={point.titleKey} className="px-6 sm:px-7 lg:px-8 pt-8 pb-9 lg:pb-2 border-b lg:border-b-0 lg:border-r border-stone-300 last:border-0 first:pl-0 last:pr-0 sm:first:pl-0 sm:last:pr-0">
              <span className="text-sm font-mono text-orange-700 mb-7 block">{point.number}</span>
              <h3 className="text-base sm:text-[17px] font-bold text-slate-950 leading-snug mb-4 max-w-[17rem]">{t(point.titleKey)}</h3>
              <p className="text-sm text-stone-600 leading-7 max-w-[18rem]">{t(point.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
