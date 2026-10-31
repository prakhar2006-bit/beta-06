import { apiClient } from './apiClient.js';
import { isDemoCatalog } from './schemeApi.js';

const prefix = isDemoCatalog ? '/api/v1/demo' : '/api/v1';

export const sessionApi = {
  start: (scheme_id, language) =>
    apiClient.post(`${prefix}/questionnaire/start`, { scheme_id, language }),

  next: (state) =>
    apiClient.post(`${prefix}/questionnaire/next`, { state }),

  answer: (state, question_id, action, value) =>
    apiClient.post(`${prefix}/questionnaire/answer`, {
      state,
      question_id,
      action,
      ...(action === 'answer' ? { value } : {}),
    }),

  explain: (state) =>
    apiClient.post(`${prefix}/results/explain`, { state }),

  getSessionId() {
    if (typeof sessionStorage !== 'undefined') {
      return sessionStorage.getItem('yojanamitra_session_id');
    }
    return null;
  },

  clearSession() {
    if (typeof sessionStorage !== 'undefined') {
      for (const key of ['yojanamitra_session_id', 'yojanamitra_answers']) {
        sessionStorage.removeItem(key);
      }
    }
  },
};
