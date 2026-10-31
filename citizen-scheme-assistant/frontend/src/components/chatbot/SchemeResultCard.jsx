import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink, ArrowRight, ShieldCheck, Landmark } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export const SchemeResultCard = ({ scheme }) => {
  const { t } = useLanguage();

  return (
    <div className="p-3.5 sm:p-4 rounded-2xl bg-white/95 border border-orange-100 shadow-sm hover:shadow-md transition-all space-y-2.5 my-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-1.5 flex-wrap mb-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full border border-orange-200/50">
              {scheme.category}
            </span>
            <span className="text-[10px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200/50">
              {scheme.level === 'central' ? 'Central Scheme' : 'State Scheme'}
            </span>
          </div>
          <h4 className="text-xs sm:text-sm font-bold text-slate-900 leading-snug">
            {scheme.name}
          </h4>
        </div>
        <div className="w-7 h-7 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600 shrink-0">
          <Landmark className="w-3.5 h-3.5" />
        </div>
      </div>

      <p className="text-[11px] sm:text-xs text-slate-600 leading-relaxed">
        {scheme.benefits_summary}
      </p>

      {scheme.match_reason && (
        <div className="text-[10px] text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-xl border border-emerald-200/60 flex items-center gap-1.5">
          <ShieldCheck className="w-3 h-3 text-emerald-600 shrink-0" />
          <span>{scheme.match_reason}</span>
        </div>
      )}

      <div className="pt-1.5 flex items-center justify-between gap-2 border-t border-slate-100">
        <Link
          to={`/schemes/${scheme.code || scheme.scheme_id}`}
          className="inline-flex items-center gap-1 text-[11px] font-bold text-orange-600 hover:text-orange-700"
        >
          <span>{t('viewDetails', 'View Scheme Details')}</span>
          <ArrowRight className="w-3 h-3" />
        </Link>

        {scheme.official_url && (
          <a
            href={scheme.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-slate-800 transition"
          >
            <span>Official Portal</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
};

