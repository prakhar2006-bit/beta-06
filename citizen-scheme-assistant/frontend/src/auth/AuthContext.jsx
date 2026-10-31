import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase, setRememberDevice } from '../lib/supabaseClient';
import { useLanguage } from '../i18n/LanguageContext';
import { uploadDocument as uploadFile, signedDocumentUrl } from '../documents/documentService';

const AuthContext = createContext(null);

const profileFields = 'id, full_name, preferred_language, state_code';

const AuthProvider = ({ children }) => {
  const { setLanguage } = useLanguage();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(Boolean(supabase));
  const [profileDetails, setProfileDetails] = useState(null);
  const [documents, setDocuments] = useState([]);

  const loadPrivateData = async (userId) => {
    const now = new Date().toISOString();
    // Cleanup runs on sign-in: remove private Storage objects first, then their database rows.
    const expiredDocs = await supabase.from('user_documents').select('id, storage_path').eq('user_id', userId).lt('expires_at', now);
    if (expiredDocs.error) throw expiredDocs.error;
    const paths = (expiredDocs.data || []).map((document) => document.storage_path).filter(Boolean);
    if (paths.length) {
      const removed = await supabase.storage.from('user-documents').remove(paths);
      if (removed.error) throw removed.error;
    }
    const deletedDocs = await supabase.from('user_documents').delete().eq('user_id', userId).lt('expires_at', now);
    if (deletedDocs.error) throw deletedDocs.error;
    const deletedDetails = await supabase.from('profile_details').delete().eq('user_id', userId).lt('expires_at', now);
    if (deletedDetails.error) throw deletedDetails.error;
    const details = await supabase.from('profile_details').select('user_id, answers, consent_at, updated_at, expires_at').eq('user_id', userId).maybeSingle();
    if (details.error) throw details.error;
    const docs = await supabase.from('user_documents').select('id, user_id, doc_type, storage_path, file_name, size_bytes, mime_type, confirmed_values, issued_on, uploaded_at, expires_at').eq('user_id', userId).order('uploaded_at', { ascending: false });
    if (docs.error) throw docs.error;
    setProfileDetails(details.data || null); setDocuments(docs.data || []);
  };

  const ensureProfile = async (currentUser, defaults = {}) => {
    const { data, error } = await supabase.from('profiles').select(profileFields).eq('id', currentUser.id).maybeSingle();
    if (error) throw error;
    if (data) {
      setProfile(data);
      if (data.preferred_language) setLanguage(data.preferred_language);
      await loadPrivateData(currentUser.id); return data;
    }
    const values = {
      id: currentUser.id,
      full_name: defaults.full_name || currentUser.user_metadata?.full_name || '',
      preferred_language: defaults.preferred_language || currentUser.user_metadata?.preferred_language || 'hi',
      state_code: defaults.state_code || '',
    };
    const result = await supabase.from('profiles').upsert(values, { onConflict: 'id' }).select(profileFields).single();
    if (result.error) throw result.error;
    setProfile(result.data);
    setLanguage(result.data.preferred_language);
    await loadPrivateData(currentUser.id); return result.data;
  };

  useEffect(() => {
    let active = true;
    if (!supabase) return () => { active = false; };
    const load = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        if (active && data.session?.user) {
          setUser(data.session.user);
          await ensureProfile(data.session.user);
        }
      } finally { if (active) setLoading(false); }
    };
    load();
    const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
      if (!active) return;
      setUser(session?.user || null);
      if (!session?.user) { setProfile(null); setLoading(false); }
      else if (event !== 'INITIAL_SESSION') ensureProfile(session.user).catch(() => {}).finally(() => setLoading(false));
    });
    return () => { active = false; listener.subscription.unsubscribe(); };
  }, []);

  const signUp = async ({ email, password, fullName, preferredLanguage }) => {
    if (!supabase) return { needsConfirmation: false };
    const { data, error } = await supabase.auth.signUp({ email, password, options: { data: { full_name: fullName, preferred_language: preferredLanguage } } });
    if (error) throw error;
    if (data.session?.user) await ensureProfile(data.session.user, { full_name: fullName, preferred_language: preferredLanguage });
    return { ...data, needsConfirmation: !data.session };
  };

  const signIn = async ({ email, password, remember }) => {
    if (!supabase) return {};
    setRememberDevice(remember);
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    if (data.user) await ensureProfile(data.user);
    return data;
  };

  const signOut = async () => {
    try { if (supabase) await supabase.auth.signOut(); }
    finally {
      ['yojanamitra_session_id', 'yojanamitra_answers', 'yojanamitra_results'].forEach((key) => sessionStorage.removeItem(key));
      setUser(null); setProfile(null); setProfileDetails(null); setDocuments([]);
    }
  };

  const updateProfile = async (updates) => {
    const values = { full_name: updates.full_name || '', preferred_language: updates.preferred_language === 'en' ? 'en' : 'hi', state_code: updates.state_code || '' };
    const { data, error } = await supabase.from('profiles').update(values).eq('id', user.id).select(profileFields).single();
    if (error) throw error;
    setProfile(data); setLanguage(data.preferred_language); return data;
  };

  const deleteProfileData = async () => {
    const rows = await supabase.from('user_documents').select('storage_path').eq('user_id', user.id);
    if (rows.error) throw rows.error;
    if (rows.data?.length) await supabase.storage.from('user-documents').remove(rows.data.map((row) => row.storage_path));
    const docs = await supabase.from('user_documents').delete().eq('user_id', user.id);
    if (docs.error) throw docs.error;
    const details = await supabase.from('profile_details').delete().eq('user_id', user.id);
    if (details.error) throw details.error;
    const profileRow = await supabase.from('profiles').delete().eq('id', user.id);
    if (profileRow.error) throw profileRow.error;
    await signOut();
  };

  const saveProfileDetails = async (answers, consentAt) => {
    const expires = new Date(Date.now() + 90 * 86400000).toISOString();
    const result = await supabase.from('profile_details').upsert({ user_id: user.id, answers, consent_at: consentAt, updated_at: new Date().toISOString(), expires_at: expires }, { onConflict: 'user_id' }).select('user_id, answers, consent_at, updated_at, expires_at').single();
    if (result.error) throw result.error; setProfileDetails(result.data); return result.data;
  };

  const uploadDocument = async (type, file) => { const document = await uploadFile(user.id, type, file); setDocuments((current) => [document, ...current]); return document; };
  const refreshDocuments = async () => { const result = await supabase.from('user_documents').select('*').eq('user_id', user.id).order('uploaded_at', { ascending: false }); if (result.error) throw result.error; setDocuments(result.data || []); };
  const deleteDocument = async (document) => { await supabase.storage.from('user-documents').remove([document.storage_path]); const result = await supabase.from('user_documents').delete().eq('id', document.id).eq('user_id', user.id); if (result.error) throw result.error; setDocuments((current) => current.filter((item) => item.id !== document.id)); };
  const getDocumentUrl = (path) => signedDocumentUrl(path);
  const confirmDocument = async (document, confirmedValues, issuedOn) => {
    const expires = new Date(Date.now() + 90 * 86400000).toISOString();
    const result = await supabase.from('user_documents').update({ confirmed_values: confirmedValues, issued_on: issuedOn || null, expires_at: expires }).eq('id', document.id).eq('user_id', user.id).select('*').single();
    if (result.error) throw result.error; setDocuments((current) => current.map((item) => item.id === document.id ? result.data : item)); return result.data;
  };
  const markDocument = async (docType, checked) => {
    if (checked) {
      const result = await supabase.from('user_documents').insert({ user_id: user.id, doc_type: docType, confirmed_values: { tick_only: true }, expires_at: new Date(Date.now() + 90 * 86400000).toISOString() }).select('*').single();
      if (result.error) throw result.error; setDocuments((current) => [result.data, ...current]);
    } else {
      const current = documents.find((item) => item.doc_type === docType && !item.storage_path);
      if (current) await deleteDocument(current);
    }
  };

  return <AuthContext.Provider value={{ user, profile, profileDetails, documents, loading, available: Boolean(supabase), signUp, signIn, signOut, updateProfile, deleteProfileData, saveProfileDetails, uploadDocument, refreshDocuments, deleteDocument, getDocumentUrl, confirmDocument, markDocument }}>{children}</AuthContext.Provider>;
};

export { AuthProvider };
export const useAuth = () => useContext(AuthContext);

export const getAuthErrorKey = (error) => {
  const message = String(error?.message || '').toLowerCase();
  if (message.includes('invalid login credentials')) return 'authInvalidCredentials';
  if (message.includes('already registered')) return 'authAlreadyRegistered';
  if (message.includes('password')) return 'authWeakPassword';
  if (message.includes('rate limit')) return 'authRateLimit';
  if (message.includes('network') || message.includes('fetch')) return 'authNetworkError';
  return 'authGenericError';
};
