import React from 'react';
import { CheckCircle2, HelpCircle, XCircle, FileQuestion, AlertCircle } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export const StatusBadge = ({ status, className = '' }) => {
  const { t } = useLanguage();

  const normalized = (status || '').toUpperCase();

  // 1. ELIGIBLE / POTENTIALLY_ELIGIBLE / ELIGIBLE_LIKELY
  if (normalized === 'ELIGIBLE_LIKELY' || normalized === 'POTENTIALLY_ELIGIBLE' || normalized === 'ELIGIBLE') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-emerald-100/80 text-emerald-900 border border-emerald-300/70 shadow-2xs ${className}`}
      >
        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" aria-hidden="true" />
        <span>{t(normalized === 'ELIGIBLE_LIKELY' ? 'likelyEligible' : 'statusPotentiallyEligible', normalized === 'ELIGIBLE_LIKELY' ? 'Potentially Eligible' : 'You may qualify')}</span>
      </span>
    );
  }

  // 2. NOT_ELIGIBLE / INELIGIBLE
  if (
    normalized === 'NOT_ELIGIBLE_LIKELY' || normalized === 'NOT_ELIGIBLE_UNDER_SCREENED_RULES' ||
    normalized === 'INELIGIBLE' ||
    normalized === 'NOT_ELIGIBLE'
  ) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-rose-100/80 text-rose-900 border border-rose-300/70 shadow-2xs ${className}`}
      >
        <XCircle className="w-4 h-4 text-rose-600 shrink-0" aria-hidden="true" />
        <span>{t(normalized==='NOT_ELIGIBLE_LIKELY'?'likelyIneligible':'statusIneligible', 'Not Eligible Under Screened Rules')}</span>
      </span>
    );
  }

  // 3. MAYBE / UNCERTAIN / NEEDS_VERIFICATION
  if (
    normalized === 'NEEDS_VERIFICATION' ||
    normalized === 'UNCERTAIN' ||
    normalized === 'MAYBE'
  ) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-amber-100/80 text-amber-950 border border-amber-300/70 shadow-2xs ${className}`}
      >
        <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" aria-hidden="true" />
        <span>{t('statusNeedsVerification', 'Needs Verification')}</span>
      </span>
    );
  }

  // 4. NO_CURRENT_RULES
  if (normalized === 'NO_CURRENT_RULES') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-slate-100/90 text-slate-800 border border-slate-300/80 shadow-2xs ${className}`}
      >
        <FileQuestion className="w-4 h-4 text-slate-600 shrink-0" aria-hidden="true" />
        <span>{t('statusNoCurrentRules', 'No Current Rules')}</span>
      </span>
    );
  }

  // 5. Unknown status fallback
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-slate-100/80 text-slate-700 border border-slate-300/70 shadow-2xs ${className}`}
    >
      <AlertCircle className="w-4 h-4 text-slate-500 shrink-0" aria-hidden="true" />
      <span>{t('statusUnknown', 'Unknown status, please check the official source')}</span>
    </span>
  );
};
