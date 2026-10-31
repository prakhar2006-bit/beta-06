import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { schemeApi } from '../../services/schemeApi';
import { SchemeCard } from '../schemes/SchemeCard';
import { ArrowRight } from 'lucide-react';

export const FeaturedSchemes = ({ className = '' }) => {
  const { t } = useLanguage();
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    schemeApi
      .getFeaturedSchemes()
      .then((data) => {
        if (mounted) {
          setSchemes(data.slice(0, 5));
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section className={`py-24 md:py-32 relative bg-white/50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 md:mb-10 gap-4">
          <div>
            <p className="eyebrow mb-4">Flagship programs</p>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight mb-3">
              {t('featuredHeading', 'Featured Government Schemes')}
            </h2>
            <p className="text-base text-stone-500 max-w-2xl">
              {t('featuredSubheading', 'High-impact welfare programmes available across Central and State Governments')}
            </p>
          </div>

          <Link
            to="/schemes"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-800 hover:text-orange-600 transition"
          >
            <span>{t('browseAllButton', 'Browse All Schemes')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Development sample content notice pill */}
        <div className="mb-8 py-3 border-y border-stone-200 text-xs text-stone-500 flex items-center justify-between">
          <span>{t('sampleNotice')}</span>
          <span className="font-mono text-[10px] text-slate-400">Contracts v1.0.0</span>
        </div>

        {/* Schemes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {schemes.map((scheme) => (
            <SchemeCard key={scheme.id || scheme.code} scheme={scheme} />
          ))}
        </div>

      </div>
    </section>
  );
};
