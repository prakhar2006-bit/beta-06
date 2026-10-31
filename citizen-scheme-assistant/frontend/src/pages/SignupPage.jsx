import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import { getAuthErrorKey, useAuth } from '../auth/AuthContext';

export const SignupPage = () => {
  const { t } = useLanguage();
  const { available, signUp } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [form, setForm] = useState({ fullName: '', email: '', password: '', preferredLanguage: 'hi' });
  const [error, setError] = useState(''); const [message, setMessage] = useState(''); const [submitting, setSubmitting] = useState(false);
  const update = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));
  const redirect = new URLSearchParams(location.search).get('redirect') || '/';
  const submit = async (event) => {
    event.preventDefault(); setError(''); setMessage('');
    if (form.password.length < 8) return setError('passwordMinError');
    setSubmitting(true);
    try { const result = await signUp(form); if (result.needsConfirmation) setMessage('checkEmail'); else navigate(redirect, { replace: true }); }
    catch (err) { setError(getAuthErrorKey(err)); }
    finally { setSubmitting(false); }
  };

  return <main className="flex-1 py-16 px-4"><div className="max-w-md mx-auto glass-panel rounded-[32px] p-6 sm:p-8 shadow-glass-lg">
    <h1 className="text-2xl font-black text-slate-900 mb-6">{t('signupTitle', 'Create an account')}</h1>
    {!available ? <p className="text-sm text-amber-900 bg-amber-50 p-4 rounded-2xl">{t('authUnavailable', 'Login is not available right now. You can continue as a guest.')}</p> : <form onSubmit={submit} className="space-y-5">
      <div><label htmlFor="signup-name" className="block text-sm font-semibold text-slate-800 mb-2">{t('fullNameLabel', 'Full name')}</label><input id="signup-name" type="text" required autoComplete="name" value={form.fullName} onChange={update('fullName')} className="glass-input w-full rounded-2xl px-4 py-3 text-sm" /></div>
      <div><label htmlFor="signup-email" className="block text-sm font-semibold text-slate-800 mb-2">{t('emailLabel', 'Email')}</label><input id="signup-email" type="email" required autoComplete="email" value={form.email} onChange={update('email')} className="glass-input w-full rounded-2xl px-4 py-3 text-sm" /></div>
      <div><label htmlFor="signup-password" className="block text-sm font-semibold text-slate-800 mb-2">{t('passwordLabel', 'Password')}</label><input id="signup-password" type="password" required minLength={8} autoComplete="new-password" value={form.password} onChange={update('password')} className="glass-input w-full rounded-2xl px-4 py-3 text-sm" /><p className="text-xs text-slate-500 mt-2">{t('passwordHint', 'Use at least 8 characters.')}</p></div>
      <div><label htmlFor="signup-language" className="block text-sm font-semibold text-slate-800 mb-2">{t('preferredLanguageLabel', 'Preferred language')}</label><select id="signup-language" value={form.preferredLanguage} onChange={update('preferredLanguage')} className="glass-input w-full rounded-2xl px-4 py-3 text-sm"><option value="hi">हिंदी</option><option value="en">English</option></select></div>
      {message && <p role="status" className="text-sm text-emerald-700">{t(message, 'Check your email to confirm your account.')}</p>}
      {error && <p role="alert" className="text-sm text-rose-700">{t(error, 'Something went wrong. Please try again.')}</p>}
      <button type="submit" disabled={submitting} className="glass-dark-pill w-full rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-60">{submitting ? t('working', 'Please wait...') : t('signupButton', 'Sign up')}</button>
    </form>}
    <p className="mt-6 text-sm text-slate-600">{t('hasAccount', 'Already have an account?')} <Link to={`/login${location.search}`} className="font-semibold text-orange-700">{t('loginLink', 'Login')}</Link></p>
  </div></main>;
};
