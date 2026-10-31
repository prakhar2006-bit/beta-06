import React,{useState} from 'react';
import {useLanguage} from '../../i18n/LanguageContext';
export const DocumentChecklist=({results=[]})=>{
 const {t,getLocalized}=useLanguage();const [checked,setChecked]=useState({});
 const docs=[...new Map(results.flatMap(r=>(r.required_documents||[]).map(d=>[`${r.scheme_id}:${d.id}`,d])).map(entry=>entry)).entries()];
 if(!docs.length)return null;
 return <section className="rounded-2xl border border-slate-200 bg-slate-50 p-5 space-y-3"><h3 className="text-lg font-bold">{t('documentsHeading')}</h3>
 {docs.map(([key,d])=><label key={key} className="rounded-xl border border-slate-200 bg-white p-4 flex gap-3 items-start"><input type="checkbox" className="mt-1 h-4 w-4 accent-teal-800" checked={!!checked[key]} onChange={()=>setChecked(prev=>({...prev,[key]:!prev[key]}))}/><span className="text-sm leading-relaxed">{getLocalized(d.title)||t('unavailable')}{d.requirement==='conditional'&&<small className="block text-slate-500">{t('optionalCondition')}</small>}</span></label>)}</section>;
};
