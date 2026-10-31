import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { schemeApi } from '../../services/schemeApi';
import { SchemeCard } from '../schemes/SchemeCard';
import { ArrowRight, Sparkles } from 'lucide-react';
import { errorKey } from '../../i18n/integration.js';

export const FeaturedSchemes = ({ className = '' }) => {
  const { t, language } = useLanguage();
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,setError] = useState('');

  useEffect(() => {
    let mounted = true;
    setLoading(true);setError('');
    schemeApi
      .getFeaturedSchemes(language)
      .then((data) => {
        if (mounted) {
          setSchemes(data.slice(0, 5));
          setLoading(false);
        }
      })
      .catch(e => {
        if (mounted) {setSchemes([]);setError(t(errorKey(e)));setLoading(false);}
      });
    return () => {
      mounted = false;
    };
  }, [language]);

  return (
    <section className={`py-12 md:py-16 relative ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 md:mb-10 gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full glass-card-subtle text-orange-800 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-orange-500" />
              <span>{t('publishedCatalog')}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mb-1.5">
              {t('featuredHeading', 'Featured Government Schemes')}
            </h2>
            <p className="text-sm text-slate-600 max-w-2xl">
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
        <div className="mb-6 p-3 px-4 rounded-2xl glass-card-subtle text-xs text-slate-500 flex items-center justify-between">
          <span role={error?'alert':'status'}>{error || (loading ? t('loading') : schemes.length ? t('publishedCatalog') : t('emptyPublished'))}</span>
        </div>

        {/* Schemes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.map((scheme) => (
            <SchemeCard key={scheme.id || scheme.code} scheme={scheme} />
          ))}
        </div>

      </div>
    </section>
  );
};
