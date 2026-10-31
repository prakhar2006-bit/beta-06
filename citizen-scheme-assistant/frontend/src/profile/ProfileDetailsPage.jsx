import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import { useAuth } from '../auth/AuthContext';
import { INCOME_BANDS } from '../config/incomeBands';
import { STATES } from '../constants/states';

const steps = [
  { title: 'profileStepAbout', fields: [
    ['gender', 'profileGender', ['female', 'male', 'other', 'prefer_not_to_say']], ['date_of_birth', 'profileDob', 'date'],
    ['marital_status', 'profileMarital', ['unmarried', 'married', 'widowed', 'divorced_separated', 'prefer_not_to_say']],
    ['disability', 'profileDisability', ['yes', 'no', 'prefer_not_to_say']], ['special_categories', 'profileSpecialCategories', ['ex_servicemen', 'freedom_fighter_family', 'registered_worker', 'none']],
  ] },
  { title: 'profileStepLocation', fields: [
    ['domicile', 'profileDomicile', 'state'], ['different_state', 'profileDifferentState', ['yes', 'no', 'dont_know']], ['rural_urban', 'profileRuralUrban', ['rural', 'urban', 'dont_know']], ['scheme_preference', 'profileSchemePreference', ['central', 'state', 'both']],
  ] },
  { title: 'profileStepWork', fields: [
    ['occupation', 'profileOccupation', 'occupation'], ['highest_education', 'profileEducation', 'education'], ['currently_studying', 'profileStudying', ['yes', 'no', 'prefer_not_to_say']], ['current_class', 'profileCurrentClass', 'text'], ['institution_type', 'profileInstitution', ['government', 'government_aided', 'private', 'other']],
  ] },
  { title: 'profileStepFamily', fields: [
    ['social_category', 'profileSocialCategory', ['general_ews', 'obc', 'sc', 'st', 'prefer_not_to_say', 'dont_know']], ['obc_list', 'profileObcList', ['central_list', 'state_list', 'dont_know']], ['annual_family_income', 'profileIncome', 'income'], ['ration_card_type', 'profileRationCard', ['none', 'apl', 'bpl', 'antyodaya', 'priority_nfsa', 'dont_know']], ['income_taxpayer', 'profileTaxpayer', ['yes', 'no', 'dont_know']], ['agricultural_land', 'profileLand', ['none', 'up_to_2_5', '2_5_to_5', 'above_5', 'dont_know']], ['house_type', 'profileHouseType', ['kutcha', 'semi_pucca', 'pucca', 'no_house']], ['lpg_connection', 'profileLpg', ['yes', 'no']], ['motor_vehicle', 'profileVehicle', ['yes', 'no']],
  ] },
];

const occupations = ['farmer', 'agricultural_labourer', 'street_vendor', 'traditional_artisan', 'construction_worker', 'government_salaried', 'private_salaried', 'self_employed', 'student', 'homemaker', 'unemployed', 'retired', 'other'];
const education = ['none', 'up_to_class_8', 'class_9_to_10', 'class_11_to_12', 'diploma_iti', 'graduate', 'postgraduate'];
const label = (key, value) => `${key}_${value}`;

export const ProfileDetailsPage = () => {
  const { t, language } = useLanguage();
  const { profileDetails, saveProfileDetails } = useAuth();
  const [step, setStep] = useState(0); const [answers, setAnswers] = useState(profileDetails?.answers || {}); const [consent, setConsent] = useState(Boolean(profileDetails?.consent_at)); const [message, setMessage] = useState(''); const [error, setError] = useState(''); const [saving, setSaving] = useState(false);
  const fields = steps[step].fields;
  useEffect(() => {
    if (profileDetails?.answers) setAnswers(profileDetails.answers);
    if (profileDetails?.consent_at) setConsent(true);
  }, [profileDetails]);
  const completeness = useMemo(() => Math.round((Object.values(answers).filter((item) => item?.value !== '' && item?.value !== null && item?.value !== undefined).length / 22) * 100), [answers]);
  const setValue = (key, value) => setAnswers((current) => ({ ...current, [key]: { value, source: 'self', confirmed_at: new Date().toISOString() } }));
  const valueOf = (key) => answers[key]?.value ?? '';
  const saveStep = async (nextStep) => {
    if (!consent) { setError('profileConsentRequired'); return; }
    setSaving(true); setError(''); setMessage('');
    try { await saveProfileDetails(answers, profileDetails?.consent_at || new Date().toISOString()); setMessage('profileDetailsSaved'); if (nextStep !== undefined) setStep(nextStep); }
    catch { setError('profileDetailsError'); }
    finally { setSaving(false); }
  };
  const renderOptions = (key, options) => <select value={valueOf(key)} onChange={(event) => setValue(key, event.target.value)} className="glass-input rounded-2xl w-full p-3 text-sm"><option value="">{t('profileSkip', 'Prefer not to say')}</option>{options.map((option) => <option key={option} value={option}>{t(label('profileOption', option), option.replaceAll('_', ' '))}</option>)}</select>;
  const renderField = ([key, titleKey, type]) => <div key={key} className="space-y-2"><label htmlFor={`profile-detail-${key}`} className="block text-sm font-semibold text-slate-800">{t(titleKey, key)}</label><p className="text-xs text-slate-500">{t(`${titleKey}Why`, 'This helps us show more relevant information.')} </p>{type === 'date' ? <input id={`profile-detail-${key}`} type="date" max={new Date().toISOString().slice(0, 10)} value={valueOf(key)} onChange={(event) => setValue(key, event.target.value)} className="glass-input rounded-2xl w-full p-3 text-sm" /> : type === 'state' ? <select id={`profile-detail-${key}`} value={valueOf(key)} onChange={(event) => setValue(key, event.target.value)} className="glass-input rounded-2xl w-full p-3 text-sm"><option value="">{t('profileSkip', 'Prefer not to say')}</option>{STATES.map(([code, en, hi]) => <option key={code} value={code}>{language === 'hi' ? hi : en}</option>)}</select> : type === 'income' ? <select id={`profile-detail-${key}`} value={valueOf(key)?.band_id || valueOf(key)} onChange={(event) => { const band = INCOME_BANDS.find((item) => item.id === event.target.value); setValue(key, band ? { band_id: band.id, min: null, max: null } : event.target.value); }} className="glass-input rounded-2xl w-full p-3 text-sm"><option value="">{t('profileSkip', 'Prefer not to say')}</option>{INCOME_BANDS.map((band) => <option key={band.id} value={band.id}>{t(band.labelKey, band.id)}</option>)}</select> : type === 'occupation' ? renderOptions(key, occupations) : type === 'education' ? renderOptions(key, education) : type === 'text' ? <input id={`profile-detail-${key}`} value={valueOf(key)} onChange={(event) => setValue(key, event.target.value)} className="glass-input rounded-2xl w-full p-3 text-sm" /> : renderOptions(key, type)}<button type="button" onClick={() => setValue(key, null)} className="text-xs text-slate-500 hover:text-orange-700">{t('profileSkipQuestion', 'Skip this question')}</button></div>;

  return <main className="flex-1 py-12 px-4"><div className="max-w-2xl mx-auto"><div className="flex items-center justify-between mb-6"><div><p className="text-xs text-orange-700 font-bold uppercase tracking-wider">{t('profileDetailsEyebrow', 'Optional profile')}</p><h1 className="text-3xl font-black text-slate-900">{t('profileDetailsTitle', 'Tell us about yourself')}</h1></div><Link to="/profile" className="glass-card-subtle rounded-full px-4 py-2 text-xs font-semibold">{t('backToProfile', 'Back to profile')}</Link></div><div className="glass-panel rounded-[32px] p-6 sm:p-8 shadow-glass-lg"><div className="mb-6"><div className="flex justify-between text-xs text-slate-500 mb-2"><span>{t(steps[step].title, steps[step].title)}</span><span>{step + 1} / 4 · {completeness}%</span></div><div className="h-2 rounded-full bg-stone-200"><div className="h-2 rounded-full bg-orange-500 transition-all" style={{ width: `${((step + 1) / 4) * 100}%` }} /></div><p className="text-xs text-slate-500 mt-2">{t('profileCompletenessNote', 'Completeness does not affect eligibility. Skipping is always okay.')}</p></div><div className="space-y-6">{fields.map(renderField)}</div><label className="flex items-start gap-3 text-xs text-slate-600 mt-8"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} className="mt-0.5" />{t('profileConsent', 'I agree to save these optional details to improve my experience.')} {t('profileRetentionPrivacy', 'Deleted when you next sign in after 90 days, or anytime you press Delete.')}</label>{message && <p role="status" className="text-sm text-emerald-700 mt-4">{t(message, 'Saved.')}</p>}{error && <p role="alert" className="text-sm text-rose-700 mt-4">{t(error, 'Could not save. Please try again.')}</p>}<div className="flex justify-between gap-3 mt-8"><button type="button" onClick={() => setStep((current) => Math.max(0, current - 1))} disabled={step === 0 || saving} className="glass-card-subtle rounded-full px-5 py-3 text-sm disabled:opacity-40">{t('profilePrevious', 'Previous')}</button>{step < 3 ? <button type="button" onClick={() => saveStep(step + 1)} disabled={saving} className="glass-dark-pill rounded-full px-5 py-3 text-sm disabled:opacity-40">{saving ? t('working', 'Please wait...') : t('profileSaveContinue', 'Save and continue')}</button> : <button type="button" onClick={() => saveStep()} disabled={saving} className="glass-dark-pill rounded-full px-5 py-3 text-sm disabled:opacity-40">{saving ? t('working', 'Please wait...') : t('saveProfile', 'Save')}</button>}</div></div></div></main>;
};
