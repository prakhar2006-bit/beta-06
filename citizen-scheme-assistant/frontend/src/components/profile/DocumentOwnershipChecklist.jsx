import React from 'react';
import { DOCUMENT_MATCHING } from '../../config/documentMatching';
import { useLanguage } from '../../i18n/LanguageContext';

export const DocumentOwnershipChecklist = ({ requiredDocuments = [], documents = [] }) => {
  const { t } = useLanguage();
  if (!requiredDocuments.length) return null;
  return <section className="glass-card-subtle rounded-2xl p-5">
    <h2 className="font-bold text-slate-900 mb-3">{t('documentsRequiredHeading', 'Documents you may need')}</h2>
    <div className="space-y-2">{requiredDocuments.map((document) => {
      const id = document.id || document.code || document;
      const owned = documents.some((item) => DOCUMENT_MATCHING[id] === item.doc_type || id === item.doc_type);
      return <div key={id} className="flex items-center gap-3 text-sm">
        <span className={`w-2.5 h-2.5 rounded-full ${owned ? 'bg-emerald-500' : 'bg-amber-500'}`} aria-hidden="true" />
        <span className="flex-1">{document.name || document.label || id}</span>
        <span className="text-xs text-slate-500">{owned ? t('documentAlreadyHave', 'Already added') : t('documentStillNeeded', 'Still needed')}</span>
      </div>;
    })}</div>
  </section>;
};
