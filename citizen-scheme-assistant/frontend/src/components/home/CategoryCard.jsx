import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { ArrowUpRight } from 'lucide-react';

export const CategoryCard = ({ categoryId, titleKey, descKey, className = '' }) => {
  const { t } = useLanguage();
  return (
    <Link
      to={`/schemes?category=${categoryId}`}
      className={`group relative flex items-center justify-between py-5 pr-3 border-b border-stone-300 hover:border-orange-500 hover:-translate-y-1 hover:bg-orange-50/40 hover:shadow-[0_10px_24px_rgba(180,83,9,0.08)] transition-all ${className}`}
    >
      <div className="flex items-baseline gap-3">
        <span className="font-mono text-[10px] text-stone-400">{String(categoryId === 'agriculture' ? 1 : categoryId === 'women-child' ? 2 : categoryId === 'education' ? 3 : categoryId === 'health' ? 4 : categoryId === 'housing' ? 5 : categoryId === 'employment' ? 6 : categoryId === 'business' ? 7 : 8).padStart(2, '0')}</span>
        <div>
        <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-orange-700 transition-colors">
          {t(titleKey)}
        </h3>
        <p className="text-xs text-stone-500 leading-relaxed font-normal">{t(descKey)}</p>
        </div>
      </div>
      <ArrowUpRight className="w-4 h-4 text-stone-400 group-hover:text-orange-700 transition-colors" aria-hidden="true" />
    </Link>
  );
};
