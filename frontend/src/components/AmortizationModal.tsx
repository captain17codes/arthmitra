import React, { useState } from "react";
import { X } from "lucide-react";
import { Language, SchemePackage } from "../types";
import { formatINR, translations } from "../i18n";

interface Props {
  pkg: SchemePackage | null;
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
}

const inr = (v: string) => formatINR(Math.round(Number(v)));

/** Shows the backend-computed repayment schedule(s). Nothing is recalculated here. */
export const AmortizationModal: React.FC<Props> = ({ pkg, isOpen, onClose, lang }) => {
  const [trancheIdx, setTrancheIdx] = useState(0);
  if (!isOpen || !pkg) return null;
  const t = translations[lang];
  const mr = lang === "mr";
  const tranche = pkg.tranches[Math.min(trancheIdx, pkg.tranches.length - 1)];
  const unit = tranche.frequency_months === 3 ? (mr ? "तिमाही" : "Quarter") : mr ? "महिना" : "Month";

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-end sm:items-center justify-center p-0 sm:p-4" role="dialog" aria-modal="true">
      <div className="bg-white w-full max-w-md rounded-t-2xl sm:rounded-2xl max-h-[85vh] flex flex-col shadow-xl">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">{t.scheduleModalTitle}</h3>
            <p className="text-xs text-indigo-700 font-semibold truncate max-w-[280px]">
              {pkg.scheme_name?.[lang] || pkg.scheme_name?.en || pkg.scheme_code}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 min-w-[44px] min-h-[44px] flex items-center justify-center"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {pkg.tranches.length > 1 && (
          <div className="px-4 pt-2 flex gap-2">
            {pkg.tranches.map((tr, i) => (
              <button
                key={tr.name}
                type="button"
                onClick={() => setTrancheIdx(i)}
                className={`px-2 py-1 rounded-lg text-[11px] font-bold border min-h-[36px] ${
                  i === trancheIdx ? "bg-indigo-600 text-white border-indigo-700" : "bg-white text-slate-700 border-slate-200"
                }`}
              >
                {tr.name}
              </button>
            ))}
          </div>
        )}

        <div className="bg-slate-50 px-4 py-2 border-b border-slate-100 grid grid-cols-3 gap-2 text-center text-xs">
          <div>
            <span className="text-[10px] text-slate-500 block">{t.loanLabel}</span>
            <span className="font-bold text-slate-900">{inr(tranche.principal)}</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block">EMI / {unit}</span>
            <span className="font-bold text-emerald-700">{inr(tranche.emi)}</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block">{t.interestRateLabel}</span>
            <span className="font-bold text-slate-900">{Number(tranche.annual_rate_pct).toFixed(2)}%</span>
          </div>
        </div>

        <div className="overflow-y-auto flex-1 p-3">
          <table className="w-full text-xs text-left">
            <thead className="text-[10px] uppercase text-slate-500 bg-slate-100 sticky top-0">
              <tr>
                <th className="py-2 px-1 text-center">{mr ? "महिना" : "Month"}</th>
                <th className="py-2 px-1 text-right">{t.schedulePrincipal}</th>
                <th className="py-2 px-1 text-right">{t.scheduleInterest}</th>
                <th className="py-2 px-1 text-right">{t.scheduleBalance}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {tranche.schedule.map((row) => (
                <tr key={row.period} className={row.is_moratorium ? "bg-amber-50/60" : Number(row.subsidy_credit) > 0 ? "bg-emerald-50" : ""}>
                  <td className="py-1.5 px-1 text-center font-bold text-slate-700">
                    {row.due_month}
                    {row.is_moratorium ? " M" : ""}
                  </td>
                  <td className="py-1.5 px-1 text-right text-emerald-800">{inr(row.principal)}</td>
                  <td className="py-1.5 px-1 text-right text-amber-700">{inr(row.interest)}</td>
                  <td className="py-1.5 px-1 text-right text-slate-800">
                    {inr(row.closing_balance)}
                    {Number(row.subsidy_credit) > 0 && (
                      <span className="block text-[9px] text-emerald-700">
                        −{inr(row.subsidy_credit)} {mr ? "अनुदान" : "subsidy"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-[10px] text-slate-500 mt-2">
            {mr
              ? "M = मोरेटोरियम (फक्त व्याज / व्याज मुद्दलात जोडले). हिरवी ओळ = अनुदान कर्जात जमा."
              : "M = moratorium. Green row = subsidy credited to the loan."}
          </p>
        </div>

        <div className="p-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs">
          <span className="text-slate-500">
            {t.totalRepaymentLabel}: <strong className="text-slate-900">{inr(pkg.total_repayment)}</strong>
          </span>
          <button onClick={onClose} className="px-4 py-2 bg-indigo-600 text-white font-bold rounded-xl min-h-[44px]">
            {t.cancel}
          </button>
        </div>
      </div>
    </div>
  );
};
