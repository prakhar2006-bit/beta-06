import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export const EligibilityResult = ({ eligibility }) => {
  if (!eligibility) return null;

  const { status, scheme_name, confidence_score, summary_explanation, criteria_breakdown = [] } = eligibility;

  const isEligible = status === 'POTENTIALLY_ELIGIBLE';
  const isUncertain = status === 'NEEDS_VERIFICATION' || status === 'INSUFFICIENT_INFO';

  const badgeConfig = isEligible
    ? {
        bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
        icon: <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />,
        label: 'Potentially Eligible / संभावित पात्र',
      }
    : isUncertain
    ? {
        bg: 'bg-amber-50 text-amber-800 border-amber-200',
        icon: <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />,
        label: 'Needs Verification / सत्यापन आवश्यक',
      }
    : {
        bg: 'bg-rose-50 text-rose-800 border-rose-200',
        icon: <XCircle className="w-4 h-4 text-rose-600 shrink-0" />,
        label: 'Not Eligible / अपात्र',
      };

  return (
    <div className="p-4 rounded-2xl bg-white/95 border border-slate-200 shadow-sm space-y-3 my-2 text-left">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <h4 className="text-xs font-bold text-slate-900">{scheme_name}</h4>
        <div className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border flex items-center gap-1.5 ${badgeConfig.bg}`}>
          {badgeConfig.icon}
          <span>{badgeConfig.label}</span>
        </div>
      </div>

      <p className="text-xs text-slate-700 leading-relaxed font-normal">
        {summary_explanation}
      </p>

      {criteria_breakdown.length > 0 && (
        <div className="pt-2 border-t border-slate-100 space-y-1.5">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Rules Evaluation Summary:
          </p>
          {criteria_breakdown.map((crit, idx) => (
            <div key={idx} className="flex items-start gap-2 text-[11px] text-slate-600">
              <span className="mt-0.5">
                {crit.satisfied ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                ) : (
                  <XCircle className="w-3.5 h-3.5 text-rose-500" />
                )}
              </span>
              <div>
                <span className="font-semibold text-slate-800">{crit.criterion_name}: </span>
                <span>{crit.explanation}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="text-[10px] text-slate-400 italic pt-1 border-t border-slate-100 flex items-center gap-1">
        <Info className="w-3 h-3 text-slate-400 shrink-0" />
        <span>Evaluation evaluated deterministically against verified government rules.</span>
      </div>
    </div>
  );
};

