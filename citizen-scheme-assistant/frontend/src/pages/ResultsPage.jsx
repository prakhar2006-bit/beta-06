import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import { errorKey } from '../i18n/integration.js';
import { screeningFlow as flow } from '../services/screeningFlow.js';
import { ResultCard } from '../components/results/ResultCard';
import { DocumentOwnershipChecklist } from '../components/profile/DocumentOwnershipChecklist';
import { useAuth } from '../auth/AuthContext';
import { Sparkles, Compass, RotateCcw } from 'lucide-react';

export const ResultsPage = () => {
  const { t, language } = useLanguage();
  const { documents } = useAuth();
  const [result, setResult] = useState(flow.result);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    if (flow.current && flow.current.state.language !== language) {
      setBusy(true);
      flow
        .language(language)
        .then(() => flow.finish())
        .then((r) => {
          if (active) setResult(r);
        })
        .catch((e) => {
          if (active) setError(t(errorKey(e)));
        })
        .finally(() => {
          if (active) setBusy(false);
        });
    }
    return () => {
      active = false;
    };
  }, [language]);

  const clear = () => {
    flow.clear();
    setResult(null);
    setError('');
  };

  return (
    <div className="flex-1 py-10 sm:py-16 relative">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-2">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full glass-card-subtle text-orange-800 text-[11px] font-bold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-orange-500" />
              <span>Preliminary Screening Summary</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              {t('resultsTitle', 'Screening Evaluation Results')}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/schemes"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold glass-panel hover:bg-white text-slate-800 transition-all shadow-glass"
            >
              <Compass className="w-4 h-4 text-orange-600" />
              <span>{t('selectScheme', 'Explore Schemes')}</span>
            </Link>
            <button
              type="button"
              onClick={clear}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold glass-card-subtle hover:bg-rose-50 text-slate-700 hover:text-rose-700 transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{t('clearData', 'Clear Data')}</span>
            </button>
          </div>
        </div>

        {error ? (
          <div
            role="alert"
            className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm font-medium"
          >
            {error}
          </div>
        ) : busy ? (
          <p role="status" className="text-center py-12 text-slate-600 font-medium">
            {t('loading', 'Loading evaluation...')}
          </p>
        ) : result ? (
          <div className="space-y-8">
            <ResultCard result={result} />
            <DocumentOwnershipChecklist
              requiredDocuments={result.raw?.required_documents || []}
              documents={documents}
            />
          </div>
        ) : (
          <div className="p-8 sm:p-12 text-center rounded-[28px] glass-panel border border-white/80 max-w-lg mx-auto my-8 shadow-glass">
            <p role="status" className="text-sm text-slate-600 mb-6 font-medium">
              {t('resultMissing', 'No screening results found. Please check a scheme to begin.')}
            </p>
            <Link
              to="/screening"
              className="px-6 py-3 rounded-full text-xs font-bold bg-orange-600 text-white hover:bg-orange-700 transition shadow-xs"
            >
              {t('retakeScreening', 'Start Screening')}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
