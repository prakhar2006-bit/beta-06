import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import { getAuthErrorKey, useAuth } from '../auth/AuthContext';

export const LoginPage = () => {
  const { t } = useLanguage();
  const { available, signIn } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '', remember: false });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const redirect = new URLSearchParams(location.search).get('redirect') || '/';
  const update = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.type === 'checkbox' ? event.target.checked : event.target.value }));

  const submit = async (event) => {
    event.preventDefault(); setError('');
    if (form.password.length < 8) return setError('passwordMinError');
    setSubmitting(true);
    try { await signIn(form); navigate(redirect, { replace: true }); }
    catch (err) { setError(getAuthErrorKey(err)); }
    finally { setSubmitting(false); }
  };

  return <main className="flex-1 py-16 px-4"><div className="max-w-md mx-auto glass-panel rounded-[32px] p-6 sm:p-8 shadow-glass-lg">
    <h1 className="text-2xl font-black text-slate-900 mb-6">{t('loginTitle', 'Login')}</h1>
    {!available ? <p className="text-sm text-amber-900 bg-amber-50 p-4 rounded-2xl">{t('authUnavailable', 'Login is not available right now. You can continue as a guest.')}</p> : <form onSubmit={submit} className="space-y-5">
      <div><label htmlFor="login-email" className="block text-sm font-semibold text-slate-800 mb-2">{t('emailLabel', 'Email')}</label><input id="login-email" type="email" required autoComplete="email" value={form.email} onChange={update('email')} className="glass-input w-full rounded-2xl px-4 py-3 text-sm" /></div>
      <div><label htmlFor="login-password" className="block text-sm font-semibold text-slate-800 mb-2">{t('passwordLabel', 'Password')}</label><input id="login-password" type="password" required minLength={8} autoComplete="current-password" value={form.password} onChange={update('password')} className="glass-input w-full rounded-2xl px-4 py-3 text-sm" /></div>
      <label className="flex items-start gap-3 text-sm text-slate-600"><input type="checkbox" checked={form.remember} onChange={update('remember')} className="mt-1" />{t('rememberMe', 'This is my own phone, keep me signed in')}</label>
      {error && <p role="alert" className="text-sm text-rose-700">{t(error, 'Something went wrong. Please try again.')}</p>}
      <button type="submit" disabled={submitting} className="glass-dark-pill w-full rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-60">{submitting ? t('working', 'Please wait...') : t('loginButton', 'Login')}</button>
    </form>}
    <p className="mt-6 text-sm text-slate-600">{t('noAccount', "Don't have an account?")} <Link to={`/signup${location.search}`} className="font-semibold text-orange-700">{t('signupLink', 'Sign up')}</Link></p>
  </div></main>;
};
