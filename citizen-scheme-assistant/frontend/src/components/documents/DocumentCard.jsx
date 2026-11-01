import React from 'react';
import { Eye, FileText, Building2 } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';
import { getDocumentSample } from '../../data/documentSamples';

/**
 * Reusable DocumentCard component
 * Displays document title, issuing authority, and guidance.
 * Conditionally shows "View Sample" if a specimen is available.
 */
export default function DocumentCard({ doc, onViewSample, className = '' }) {
  const { language, t, getLocalized: localize } = useLanguage();

  const getLocalized = (field) => {
    if (!field) return '';
    if (typeof field === 'string') return field;
    return localize(field) || field[language] || field.en || '';
  };

  const sample = getDocumentSample(doc);
  const docTitle = getLocalized(doc.title);
  const guidance = getLocalized(doc.guidance);
  const issuingAuth = getLocalized(doc.issuing_authority);

  return (
    <div
      className={`p-4 sm:p-5 rounded-2xl border border-white/80 glass-card-subtle flex flex-col md:flex-row md:items-center justify-between gap-3.5 transition-all duration-200 hover:shadow-sm ${className}`}
    >
      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div className="w-8 h-8 rounded-xl bg-orange-100/70 border border-orange-200/60 flex items-center justify-center text-orange-600 shrink-0 mt-0.5">
          <FileText className="w-4 h-4" />
        </div>

        <div className="space-y-1 min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-bold text-slate-900 leading-snug">
              {docTitle}
            </h4>
            {doc.optional && (
              <span className="text-[10px] font-medium text-slate-500 bg-slate-100/80 px-2 py-0.5 rounded-full border border-slate-200/50">
                {t('optional', 'Optional')}
              </span>
            )}
          </div>

          {guidance && (
            <p className="text-xs text-slate-600 font-normal leading-relaxed">
              {guidance}
            </p>
          )}

          {issuingAuth && (
            <div className="flex items-center gap-1.5 text-[11px] text-slate-500 pt-0.5">
              <Building2 className="w-3 h-3 text-slate-400 shrink-0" />
              <span className="truncate">
                {t('issuingAuthority', 'Issuing Authority')}:{' '}
                <span className="font-medium text-slate-700">{issuingAuth}</span>
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 self-start md:self-center pt-2 md:pt-0 border-t md:border-t-0 border-slate-100 w-full md:w-auto justify-between md:justify-end">
        {issuingAuth && !guidance && (
          <span className="text-[11px] font-medium text-slate-600 bg-white/80 px-3 py-1 rounded-full border border-white shrink-0 md:hidden">
            {issuingAuth}
          </span>
        )}

        {/* View Sample Button - ONLY displayed if a verified specimen exists */}
        {sample && (
          <button
            type="button"
            onClick={() => onViewSample && onViewSample(sample)}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white/90 hover:bg-orange-50 text-orange-700 hover:text-orange-800 text-xs font-semibold border border-orange-200/80 shadow-sm transition-all duration-150 hover:shadow active:scale-95 focus:outline-none focus:ring-2 focus:ring-orange-400"
            title={`${t('viewSample', 'View Sample')} - ${docTitle}`}
          >
            <Eye className="w-3.5 h-3.5 text-orange-600" />
            <span>{t('viewSample', 'View Sample')}</span>
          </button>
        )}
      </div>
    </div>
  );
}
