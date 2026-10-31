import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import { schemeApi } from '../services/schemeApi';
import { STALE_RULES_THRESHOLD_DAYS } from '../config';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { Disclaimer } from '../components/common/Disclaimer';
import DocumentCard from '../components/documents/DocumentCard';
import DocumentPreviewModal from '../components/documents/DocumentPreviewModal';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  ExternalLink,
  CheckCircle,
  FileText,
  ListOrdered,
  ArrowRight,
  ShieldCheck,
  Share2,
  AlertTriangle,
} from 'lucide-react';

// Small bilingual label tables. These are UI labels only, not eligibility rules.
const CATEGORY_LABELS = {
  agriculture: { en: 'Agriculture', hi: 'कृषि' },
  'women-child': { en: 'Women & Child', hi: 'महिला एवं बाल' },
  education: { en: 'Education', hi: 'शिक्षा' },
  health: { en: 'Health', hi: 'स्वास्थ्य' },
  housing: { en: 'Housing', hi: 'आवास' },
  employment: { en: 'Employment', hi: 'रोज़गार' },
  business: { en: 'Business', hi: 'व्यवसाय' },
  'social-welfare': { en: 'Social Welfare', hi: 'सामाजिक कल्याण' },
};

const CRITICALITY_LABELS = {
  MANDATORY: { en: 'Required', hi: 'अनिवार्य' },
  DISQUALIFIER: { en: 'Must not apply', hi: 'लागू नहीं होना चाहिए' },
};

export const SchemeDetailsPage = () => {
  // ---------------------------------------------------------------
  // ALL HOOKS GO HERE, ABOVE EVERY EARLY RETURN (Rules of Hooks).
  // ---------------------------------------------------------------
  const { code } = useParams();
  const navigate = useNavigate();
  const { t, getLocalized } = useLanguage();

  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [selectedSample, setSelectedSample] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    schemeApi
      .getSchemeByCode(code)
      .then((data) => {
        if (active) {
          setScheme(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message || 'Scheme not found');
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [code]);

  // Stale-rules check (moved up from below the early returns: this was the crash).
  // scheme is null on the first render, so everything is read safely.
  const lastChecked = scheme?.official_source?.last_checked_date ?? null;

  const isStale = useMemo(() => {
    if (!lastChecked) return false;
    const checked = new Date(lastChecked);
    if (isNaN(checked.getTime())) return false;
    const diffDays = (Date.now() - checked.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays > STALE_RULES_THRESHOLD_DAYS;
  }, [lastChecked]);

  // ---------------------------------------------------------------
  // Plain functions and early returns come after all hooks.
  // ---------------------------------------------------------------
  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 py-20">
        <LoadingState />
      </div>
    );
  }

  if (error || !scheme) {
    return (
      <div className="flex-1 py-16 px-4">
        <ErrorState
          title={getLocalized({ en: 'Scheme Not Found', hi: 'योजना नहीं मिली' })}
          message={
            error ||
            getLocalized({
              en: `Could not find scheme with identifier "${code}".`,
              hi: `"${code}" पहचान वाली योजना नहीं मिली।`,
            })
          }
          onRetry={() => navigate('/schemes')}
        />
      </div>
    );
  }

  const schemeName = getLocalized(scheme.name);
  const schemeDesc = getLocalized(scheme.description);
  const benefits = getLocalized(scheme.benefits);
  const officialSource = scheme.official_source || {};
  const isCentral = scheme.level === 'central';
  const criteria = scheme.criteria || [];
  const documents = scheme.required_documents || [];
  const applicationSteps = scheme.application_steps || [];
  const categoryLabel = CATEGORY_LABELS[scheme.category]
    ? getLocalized(CATEGORY_LABELS[scheme.category])
    : scheme.category.replace('-', ' ');


  return (
    <div className="flex-1 py-10 sm:py-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Back Link & Action Bar */}
        <div className="flex items-center justify-between gap-4 mb-6">
          <Link
            to="/schemes"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full glass-card-subtle text-xs font-semibold text-slate-700 hover:text-black hover:bg-white transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{t('backToSchemes', 'Back to Schemes')}</span>
          </Link>

          <button
            type="button"
            onClick={handleShare}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700 hover:text-black glass-card-subtle px-4 py-2 rounded-full transition shadow-2xs hover:bg-white"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{copied ? t('linkCopied', 'Copied!') : t('copyLink', 'Share')}</span>
          </button>
        </div>

        {/* Rules NOT verified yet (no date at all) */}
        {!lastChecked && (
          <div className="bg-slate-100 border border-slate-300 text-slate-800 px-5 py-3.5 rounded-2xl mb-6 flex items-center gap-3 text-xs sm:text-sm font-semibold shadow-2xs">
            <AlertTriangle className="w-5 h-5 text-slate-600 shrink-0" aria-hidden="true" />
            <span>
              {getLocalized({
                en: 'We have not verified these rules against the official source yet. Please confirm on the official portal or with the concerned office before applying.',
                hi: 'हमने इन नियमों को अभी तक आधिकारिक स्रोत से सत्यापित नहीं किया है। आवेदन से पहले कृपया आधिकारिक पोर्टल या संबंधित कार्यालय से पुष्टि कर लें।',
              })}
            </span>
          </div>
        )}

        {/* Stale rules warning (date exists but is old) */}
        {isStale && (
          <div className="bg-amber-100/90 border border-amber-300 text-amber-950 px-5 py-3.5 rounded-2xl mb-6 flex items-center gap-3 text-xs sm:text-sm font-semibold shadow-2xs">
            <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0" aria-hidden="true" />
            <span>
              {t(
                'staleRulesWarning',
                'These rules were last checked on {date} and may be out of date.'
              ).replace('{date}', lastChecked)}
            </span>
          </div>
        )}

        {/* Main Scheme Hero Card */}
        <div className="glass-panel rounded-[36px] shadow-glass-lg p-6 sm:p-10 mb-8 border border-white/80">

          {/* Level and Category Badges */}
          <div className="flex flex-wrap items-center gap-2 mb-5">
            {isCentral ? (
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-blue-100/80 text-blue-900 border border-blue-200/60 shadow-2xs">
                <Building2 className="w-3.5 h-3.5" />
                <span>{t('centralGov', 'Central Government')}</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-emerald-100/80 text-emerald-900 border border-emerald-200/60 shadow-2xs">
                <MapPin className="w-3.5 h-3.5" />
                <span>
                  {scheme.state_code === 'MP'
                    ? getLocalized({ en: 'Madhya Pradesh', hi: 'मध्य प्रदेश' })
                    : t('stateGov', 'State Government')}
                </span>
              </span>
            )}

            <span className="px-3.5 py-1 rounded-full text-xs font-bold glass-card-subtle text-slate-700 capitalize">
              {categoryLabel}
            </span>

            {lastChecked && (
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-medium text-slate-500 glass-card-subtle ml-auto">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>
                  {t('lastCheckedOn', 'Rule verified on:')} {lastChecked}
                </span>
              </span>
            )}
          </div>

          {/* Scheme Title */}
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 mb-3 leading-tight">
            {schemeName}
          </h1>

          {/* Ministry / Department */}
          {officialSource.issuing_ministry && (
            <p className="text-xs font-medium text-slate-500 mb-6">
              <span className="text-slate-400">
                {getLocalized({ en: 'Department:', hi: 'विभाग:' })}
              </span>{' '}
              {getLocalized(officialSource.issuing_ministry)}
            </p>
          )}

          {/* Scheme Description */}
          <div className="mb-8 text-sm sm:text-base text-slate-700 leading-relaxed font-normal">
            <p>{schemeDesc}</p>
          </div>

          {/* Quick CTA to screening + official link */}
          <div className="flex flex-col sm:flex-row items-center gap-4 pt-6 border-t border-white/60">
            <Link
              to={`/screening?scheme_id=${encodeURIComponent(scheme.id || scheme.code || code)}`}
              className="glass-dark-pill w-full sm:w-auto inline-flex items-center justify-center gap-3 px-6 py-3.5 rounded-full text-xs font-semibold tracking-wide hover:bg-black transition shadow-md active:scale-95"
            >
              <span>{t('startCheckForThisScheme', 'Check Your Eligibility for this Scheme')}</span>
              <ArrowRight className="w-3.5 h-3.5 text-white" />
            </Link>

            {officialSource.url ? (
              <a
                href={officialSource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-full text-xs font-bold text-slate-700 glass-card-subtle hover:bg-white transition"
              >
                <span>{t('officialLink', 'Official Government Portal')}</span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
              </a>
            ) : (
              <span className="w-full sm:w-auto inline-flex items-center justify-center px-5 py-3.5 rounded-full text-xs font-semibold text-slate-500 glass-card-subtle">
                {getLocalized({
                  en: 'Official link not available yet',
                  hi: 'आधिकारिक लिंक अभी उपलब्ध नहीं है',
                })}
              </span>
            )}
          </div>
        </div>

        {/* Benefits Section */}
        {benefits && (
          <div className="glass-panel rounded-[32px] shadow-glass p-6 sm:p-8 mb-8 border border-white/80">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base sm:text-lg mb-4">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <h2>{t('benefitsHeading', 'Key Benefits & Entitlements')}</h2>
            </div>
            <div className="bg-emerald-500/10 rounded-2xl p-5 border border-emerald-300/60 text-xs sm:text-sm text-emerald-950 leading-relaxed font-semibold">
              {benefits}
            </div>
          </div>
        )}

        {/* Eligibility Criteria Overview */}
        {criteria.length > 0 && (
          <div className="glass-panel rounded-[32px] shadow-glass p-6 sm:p-8 mb-8 border border-white/80">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base sm:text-lg mb-4">
              <ShieldCheck className="w-5 h-5 text-orange-500" />
              <h2>{t('eligibilityHeading', 'Eligibility Criteria Overview')}</h2>
            </div>

            <div className="space-y-4">
              {criteria.map((crit, idx) => (
                <div
                  key={crit.id || idx}
                  className="p-4 sm:p-5 rounded-2xl border border-white/80 glass-card-subtle flex items-start gap-3.5"
                >
                  <span
                    className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shrink-0 mt-0.5 ${crit.criticality === 'MANDATORY'
                      ? 'bg-blue-100/90 text-blue-900'
                      : 'bg-rose-100/90 text-rose-900'
                      }`}
                  >
                    {CRITICALITY_LABELS[crit.criticality]
                      ? getLocalized(CRITICALITY_LABELS[crit.criticality])
                      : crit.criticality}
                  </span>
                  <div>
                    <p className="text-xs sm:text-sm font-bold text-slate-900">
                      {getLocalized(crit.explanation_if_met)}
                    </p>
                    {crit.explanation_if_violated && (
                      <p className="text-xs text-slate-500 mt-1 font-normal">
                        <span className="font-semibold text-rose-600">
                          {getLocalized({ en: 'Note:', hi: 'ध्यान दें:' })}
                        </span>{' '}
                        {getLocalized(crit.explanation_if_violated)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Required Documents */}
        {documents.length > 0 && (
          <div className="glass-panel rounded-[32px] shadow-glass p-6 sm:p-8 mb-8 border border-white/80">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5">
              <div className="flex items-center gap-2 text-slate-900 font-bold text-base sm:text-lg">
                <FileText className="w-5 h-5 text-orange-500" />
                <h2>{t('documentsHeading', 'Required Documents')}</h2>
              </div>
              <span className="text-xs text-slate-500 font-normal">
                {t('knowYourDocumentsSub', 'Click "View Sample" to see specimen guides')}
              </span>
            </div>

            <div className="space-y-3">
              {documents.map((doc, idx) => (
                <DocumentCard
                  key={doc.id || idx}
                  doc={doc}
                  onViewSample={(sample) => setSelectedSample(sample)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Application Steps */}
        {applicationSteps.length > 0 && (
          <div className="glass-panel rounded-[32px] shadow-glass p-6 sm:p-8 mb-8 border border-white/80">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base sm:text-lg mb-6">
              <ListOrdered className="w-5 h-5 text-orange-500" />
              <h2>{t('applicationHeading', 'How to Apply')}</h2>
            </div>

            <div className="space-y-6">
              {applicationSteps.map((step) => (
                <div key={step.step_number} className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center shrink-0 shadow-xs">
                    {step.step_number}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 mb-1">
                      {getLocalized(step.title)}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                      {getLocalized(step.description)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Verification & Official Source Info */}
        <div className="glass-card-subtle rounded-2xl p-6 border border-white/80 mb-8 text-xs text-slate-600 space-y-2">
          <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
            {t('officialSourceHeading', 'Official Source & Verification')}
          </h4>
          <p className="font-normal">
            {t(
              'verifyNotice',
              'Always verify criteria and latest amendments on the official portal before submitting applications.'
            )}
          </p>
          {officialSource.gazette_or_order_ref && (
            <p className="font-mono text-[10px] text-slate-500">
              {getLocalized({ en: 'Ref:', hi: 'संदर्भ:' })} {officialSource.gazette_or_order_ref}
            </p>
          )}
        </div>

        {/* Disclaimer */}
        <Disclaimer />

        {/* Specimen Preview Modal (Know Your Documents) */}
        <DocumentPreviewModal
          sample={selectedSample}
          isOpen={Boolean(selectedSample)}
          onClose={() => setSelectedSample(null)}
        />
      </div>
    </div>
  );
};
