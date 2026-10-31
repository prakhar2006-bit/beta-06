import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { Building2, MapPin, ArrowRight, CheckCircle2 } from 'lucide-react';

export const SchemeCard = ({ scheme, className = '' }) => {
  const { t, getLocalized } = useLanguage();

  const schemeName = getLocalized(scheme.name);
  const schemeDesc = getLocalized(scheme.description);
  const benefitsText = getLocalized(scheme.benefits);
  const isCentral = scheme.level === 'central';

  return (
    <div
      className={`group relative bg-white/70 border border-stone-200 p-6 flex flex-col hover:-translate-y-1 hover:border-orange-300 hover:shadow-[0_16px_35px_rgba(180,83,9,0.10)] transition-all ${className}`}
    >
      <div>
        {/* Badges: Level & Category */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            {isCentral ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-700">
                <Building2 className="w-3 h-3" />
                <span>{t('centralGov', 'Central Government')}</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800">
                <MapPin className="w-3 h-3" />
                <span>
                  {scheme.state_code === 'MP' ? 'Madhya Pradesh' : t('stateGov', 'State Government')}
                </span>
              </span>
            )}

            <span className="text-[11px] font-medium text-stone-500 capitalize border-l border-stone-300 pl-2">
              {scheme.category.replace('-', ' ')}
            </span>
          </div>

          {/* Verification Source Indicator */}
            <span className="text-[10px] text-stone-400 font-mono tracking-tight">
            .gov.in verified
          </span>
        </div>

        {/* Scheme Title */}
        <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-2 leading-snug group-hover:text-orange-600 transition-colors">
          <Link to={`/schemes/${scheme.code || scheme.id}`}>{schemeName}</Link>
        </h3>

        {/* Short Description */}
        <p className="text-xs sm:text-sm text-slate-600 line-clamp-3 mb-3 leading-relaxed font-normal">
          {schemeDesc}
        </p>

        {/* Benefit Highlight snippet */}
        {benefitsText && (
          <div className="bg-stone-50 p-3 border-l-2 border-emerald-500 mb-4 flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <p className="text-xs text-slate-700 font-medium line-clamp-2">{benefitsText}</p>
          </div>
        )}
      </div>

      {/* Card Footer Actions */}
      <div className="mt-auto pt-4 border-t border-stone-200 flex items-center justify-between gap-3">
        <Link
          to={`/schemes/${scheme.code || scheme.id}`}
          className="text-xs font-semibold text-slate-700 hover:text-black flex items-center gap-1.5 transition"
        >
          <span>{t('viewDetails', 'View Details')}</span>
          <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
        </Link>

        <Link
          to="/screening"
          className="px-4 py-2 text-xs font-semibold text-white bg-slate-950 hover:bg-orange-700 transition-colors"
        >
          {t('checkEligibility', 'Check Eligibility')}
        </Link>
      </div>
    </div>
  );
};
