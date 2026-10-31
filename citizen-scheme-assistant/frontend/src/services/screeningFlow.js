import { sessionApi } from './sessionApi.js';
import { adaptResult, answerValue } from './adapters.js';
import { ApiError } from './apiClient.js';
export function questionnaireResponse(data, schemeId) {
  if (!data?.state || data.state.scheme_id !== schemeId || typeof data.completed !== 'boolean' || !data.progress || !data.evaluation
      || (data.completed ? data.current_question !== null : !data.current_question?.question_id)) throw new ApiError('INVALID_RESPONSE');
  return data;
}
export class ScreeningFlow {
  constructor(api = sessionApi) { this.api = api; this.current = null; this.history = []; this.result = null; this.revision = 0; }
  check(ticket) { if(ticket !== this.revision) throw new ApiError('REQUEST_ABORTED'); }
  async start(id, language) {
    if (!id || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(id)) throw new Error('SELECT_SCHEME');
    const ticket=++this.revision;
    const data = questionnaireResponse(await this.api.start(id, language),id); this.check(ticket); this.current = data; this.history = []; this.result = null; return data;
  }
  async update(questionId, action, input) {
    if (!this.current) throw new Error('SELECT_SCHEME');
    const value = action === 'answer' && input !== null ? answerValue(this.current.current_question, input) : input;
    const previous=this.current,ticket=++this.revision;
    const data = questionnaireResponse(await this.api.answer(previous.state, questionId, action, value),previous.state.scheme_id); this.check(ticket);
    this.history.push(previous); this.current = data; this.result = null; return data;
  }
  async back() {
    if (!this.history.length) return this.current;
    const previous = this.history[this.history.length - 1];
    const ticket=++this.revision;
    const refreshed = questionnaireResponse(await this.api.next(previous.state),previous.state.scheme_id); this.check(ticket); this.history.pop(); this.current = refreshed; this.result = null; return refreshed;
  }
  async language(language) {
    if (!this.current) return null;
    const ticket=++this.revision, id=this.current.state.scheme_id;
    const refreshed = questionnaireResponse(await this.api.next({ ...this.current.state, language }),id); this.check(ticket); this.current = refreshed; this.result = null; return refreshed;
  }
  async finish() {
    if (!this.current?.completed) throw new Error('QUESTIONNAIRE_INCOMPLETE');
    const ticket=++this.revision,id=this.current.state.scheme_id;
    const raw = await this.api.explain(this.current.state); this.check(ticket);
    if(raw.scheme_id!==id) throw new ApiError('INVALID_RESPONSE'); this.result = adaptResult(raw); return this.result;
  }
  clear() { this.revision++; this.current = null; this.history = []; this.result = null; this.api.clearSession?.(); }
}
export const screeningFlow = new ScreeningFlow();
