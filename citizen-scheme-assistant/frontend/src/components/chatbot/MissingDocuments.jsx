import React from 'react';
import { FileCheck, AlertCircle, HelpCircle, ExternalLink } from 'lucide-react';

export const MissingDocuments = ({ documents = [] }) => {
  if (!documents || documents.length === 0) return null;

  return (
    <div className="p-3.5 sm:p-4 rounded-2xl bg-white/95 border border-slate-200 shadow-sm space-y-3 my-2 text-left">
      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
        <FileCheck className="w-4 h-4 text-orange-600" />
        <span>Required Document Checklist & Guidance</span>
      </div>

      <div className="space-y-2">
        {documents.map((doc, idx) => {
          const isAvailable = doc.status === 'AVAILABLE';
          const isMissing = doc.status === 'MISSING';

          return (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border text-[11px] space-y-1 ${
                isAvailable
                  ? 'bg-emerald-50/50 border-emerald-200/60'
                  : isMissing
                  ? 'bg-amber-50/60 border-amber-200/70'
                  : 'bg-slate-50 border-slate-200/60'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-bold text-slate-800">{doc.document_name}</span>
                <span
                  className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                    isAvailable
                      ? 'bg-emerald-100 text-emerald-800'
                      : isMissing
                      ? 'bg-rose-100 text-rose-800'
                      : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {isAvailable ? 'Available' : isMissing ? 'Required' : 'Check'}
                </span>
              </div>

              {doc.purpose && (
                <p className="text-[10px] text-slate-600">
                  <span className="font-medium text-slate-700">Purpose: </span>
                  {doc.purpose}
                </p>
              )}

              {doc.where_to_obtain && (
                <p className="text-[10px] text-slate-600">
                  <span className="font-medium text-slate-700">Where to obtain: </span>
                  {doc.where_to_obtain}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

