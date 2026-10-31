export const safeUrl = value => {
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? value : null; } catch { return null; }
};
export const displayText = value => typeof value === 'string' ? value : value?.text ?? '';
export const localized = value => value?.text && value?.content_language ? { [value.content_language]: value.text } : {};
export function adaptResult(raw) {
  const preliminary=raw?.screening_scope==='preliminary_only' && raw?.evaluation?.scope==='preliminary_only'
    && raw?.evaluation?.policy_review?.execution_enabled===false;
  if (!raw || !['ELIGIBLE', 'INELIGIBLE', 'NEEDS_VERIFICATION', ...(preliminary?['ELIGIBLE_LIKELY','NOT_ELIGIBLE_LIKELY']:[])].includes(raw.eligibility_status)) throw new Error('INVALID_RESPONSE');
  return { raw, scheme_id: raw.scheme_id, status: raw.eligibility_status,
    scheme_name: localized(raw.scheme_name), explanation: localized(raw.explanation),
    required_documents: (raw.required_documents?.items || []).map(d => ({ id: d.item_id, title: localized(d.title), guidance: localized(d.condition),
      requirement: d.requirement, requirement_explanation: d.requirement_explanation, source_ids: d.source_ids || [] })),
    sources: (raw.sources || []).map(s => ({ ...s, original_url: safeUrl(s.original_url) })),
    application_urls: (raw.official_application_urls?.items || []).filter(link => safeUrl(link.url)),
  };
}
export function uniqueSources(sources=[]) {
  const grouped=new Map();
  for(const source of sources) {
    const url=safeUrl(source.original_url); if(!url)continue;
    const canonical=new URL(url);canonical.hash='';
    for(const key of [...canonical.searchParams.keys()]) if(/^utm_/i.test(key)||['gclid','fbclid'].includes(key.toLowerCase()))canonical.searchParams.delete(key);
    canonical.searchParams.sort();
    const key=canonical.href,id=source.reference_id||source.id;
    if(grouped.has(key)) grouped.get(key).reference_ids.push(id,...(source.reference_ids||[]));
    else grouped.set(key,{...source,original_url:url,reference_ids:[id,...(source.reference_ids||[])].filter(Boolean)});
  }
  return [...grouped.values()];
}
export function answerValue(question, input) {
  if (question.answer_type === 'boolean') { if (typeof input !== 'boolean') throw new Error('INVALID_ANSWERS'); return input; }
  if (question.answer_type === 'category') { if (!question.allowed_values.includes(input)) throw new Error('INVALID_ANSWERS'); return input; }
  const text = String(input ?? '').trim();
  if (!text || !/^-?\d+(\.\d+)?$/.test(text)) throw new Error('INVALID_ANSWERS');
  if (question.answer_type === 'integer') {
    const n = Number(text); if (!Number.isSafeInteger(n) || n < 0) throw new Error('INVALID_ANSWERS'); return n;
  }
  if (question.answer_type === 'decimal') {
    if (!/^\d{1,19}(\.\d{1,6})?$/.test(text) || Number(text) > 1e18) throw new Error('INVALID_ANSWERS'); return text;
  }
  const n = Number(text); if (!Number.isFinite(n) || Math.abs(n) > 1e18) throw new Error('INVALID_ANSWERS'); return n;
}
export function speechValue(question, transcript) {
  const text = transcript.trim().toLowerCase();
  if (question.answer_type === 'boolean') {
    if (['yes', 'true', 'हाँ', 'हां'].includes(text)) return true;
    if (['no', 'false', 'नहीं'].includes(text)) return false;
    throw new Error('INVALID_ANSWERS');
  }
  return answerValue(question, transcript.replace(/[०-९]/g, c => String('०१२३४५६७८९'.indexOf(c))));
}
