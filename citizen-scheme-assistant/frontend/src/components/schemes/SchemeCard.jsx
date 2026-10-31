import React from 'react';
import {Link} from 'react-router-dom';
import {ArrowRight,Users} from 'lucide-react';
import {useLanguage} from '../../i18n/LanguageContext';

export const SchemeCard=({scheme,className=''})=>{
 const {t,getLocalized}=useLanguage();const id=scheme.code||scheme.id;
 const canScreen=scheme.screening_available===true||!scheme.is_demo;
 return <article className={'flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-teal-300 hover:shadow-md '+className}>
  <div className="mb-4 flex items-center justify-between gap-3 text-xs font-semibold">
   <span className="text-slate-500">{t(scheme.level==='central'?'centralGov':'stateGov')}</span>
   <span className={canScreen?'rounded-full bg-teal-50 px-3 py-1 text-teal-800':'text-slate-500'}>{t(canScreen?'quickCheck':'schemeGuide')}</span>
  </div>
  <h3 lang={scheme.language||undefined} className="text-lg font-bold leading-snug text-slate-900"><Link to={'/schemes/'+id}>{getLocalized(scheme.name)||id}</Link></h3>
  {scheme.benefit_highlight&&<p lang={scheme.language} className="mt-4 text-lg font-semibold leading-snug text-teal-800">{scheme.benefit_highlight}</p>}
  <p lang={scheme.language||undefined} className="mt-3 line-clamp-3 text-sm leading-relaxed text-slate-600">{getLocalized(scheme.description)||t('unavailable')}</p>
  {scheme.audience&&<p lang={scheme.language} className="mt-4 flex items-start gap-2 text-xs leading-relaxed text-slate-600"><Users className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true"/>{scheme.audience}</p>}
  {scheme.translation_fallback&&<p className="mt-2 text-xs text-slate-500">{t('sourceLanguage')}</p>}
  <div className="mt-auto pt-5"><div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5">
   <Link to={'/schemes/'+id} className="inline-flex items-center gap-1 text-sm font-semibold text-slate-700 hover:underline">{t('viewDetails')}<ArrowRight className="h-4 w-4" aria-hidden="true"/></Link>
   {canScreen&&<Link to={'/screening?scheme_id='+encodeURIComponent(scheme.id)} className="rounded-full bg-teal-800 px-4 py-2.5 text-xs font-semibold text-white hover:bg-teal-900">{t('preliminaryAction')}</Link>}
  </div></div>
 </article>;
};
