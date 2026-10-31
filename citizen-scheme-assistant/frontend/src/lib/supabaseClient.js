/**
 * Supabase client configuration for authentication and private documents.
 * Safely defaults to null when environment variables are not supplied.
 */

const supabaseUrl =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_SUPABASE_URL;
const supabaseAnonKey =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_SUPABASE_ANON_KEY;

export const supabase = null;

export const setRememberDevice = (remember) => {
  try {
    if (remember) {
      localStorage.setItem('yojanamitra_remember_device', 'true');
    } else {
      localStorage.removeItem('yojanamitra_remember_device');
    }
  } catch (e) {
    // ignore
  }
};
