import React from 'react';
import {useLanguage} from '../../i18n/LanguageContext';
import {uniqueSources} from '../../services/adapters.js';
export const SourceReferences=({sources=[]})=>{
 const {t}=useLanguage();const distinct=uniqueSources(sources);
 if(!distinct.length)return null;
 return <details className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm">
  <summary className="cursor-pointer font-semibold text-slate-700">{t('sourceDetails')}</summary>
  <ul className="mt-4 space-y-3">{distinct.map(s=><li key={s.original_url}>
   {[...new Set(s.reference_ids)].map(id=><span id={`source-${id}`} key={id}/>)}
   <a className="underline text-blue-800 break-words" href={s.original_url} target="_blank" rel="noopener noreferrer">{s.title||s.source_title||new URL(s.original_url).hostname}</a>
   {s.last_checked_date&&<span className="block text-xs text-slate-500">{t('sourceCheckedOn')}: {s.last_checked_date}</span>}
  </li>)}</ul>
 </details>;
};
