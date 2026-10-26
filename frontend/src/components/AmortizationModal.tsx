import React from "react";
import { X } from "lucide-react";
import { Language, SchemePackage } from "../types";
import { formatINR, translations } from "../i18n";

interface Props {
  pkg: SchemePackage | null;
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
}

export const AmortizationModal: React.FC<Props> = ({
  pkg,
  isOpen,
  onClose,
  lang,
}) => {
  if (!isOpen || !pkg) return null;
  const t = translations[lang];

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-2xs flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div className="bg-white w-full max-w-md rounded-t-2xl sm:rounded-2xl max-h-[85vh] flex flex-col shadow-xl animate-in slide-in-from-bottom duration-200">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              {t.scheduleModalTitle}
            </h3>
            <p className="text-xs text-indigo-700 font-semibold truncate max-w-[280px]">
              {lang === "mr" ? pkg.scheme_name_mr : pkg.scheme_name_en}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 min-w-[36px] min-h-[36px] flex items-center justify-center"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scheme Summary Bar */}
        <div className="bg-slate-50 px-4 py-2 border-b border-slate-100 grid grid-cols-3 gap-2 text-center text-xs">
          <div>
            <span className="text-[10px] text-slate-500 block">{t.loanLabel}</span>
            <span className="font-bold text-slate-900">
              {formatINR(pkg.loan_amount)}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block">{t.monthlyEmiLabel}</span>
            <span className="font-bold text-emerald-700">
              {formatINR(pkg.monthly_emi)}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block">{t.interestRateLabel}</span>
            <span className="font-bold text-slate-900">{pkg.annual_interest_rate}%</span>
          </div>
        </div>

        {/* Schedule Table */}
        <div className="overflow-y-auto flex-1 p-3">
          <table className="w-full text-xs text-left">
            <thead className="text-[10px] uppercase text-slate-500 bg-slate-100 sticky top-0">
              <tr>
                <th className="py-2 px-1 text-center font-bold">
                  {t.scheduleMonth}
                </th>
                <th className="py-2 px-1 text-right font-bold">
                  {t.schedulePrincipal}
                </th>
                <th className="py-2 px-1 text-right font-bold">
                  {t.scheduleInterest}
                </th>
                <th className="py-2 px-1 text-right font-bold">
                  {t.scheduleBalance}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {pkg.amortization_schedule.map((row) => (
                <tr key={row.month} className="hover:bg-slate-50">
                  <td className="py-1.5 px-1 text-center font-bold text-slate-700">
                    M{row.month}
                  </td>
                  <td className="py-1.5 px-1 text-right text-emerald-800">
                    {formatINR(row.principal_payment)}
                  </td>
                  <td className="py-1.5 px-1 text-right text-amber-700">
                    {formatINR(row.interest_payment)}
                  </td>
                  <td className="py-1.5 px-1 text-right text-slate-800">
                    {formatINR(row.remaining_balance)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs">
          <span className="text-slate-500">
            {t.totalRepaymentLabel}:{" "}
            <strong className="text-slate-900">
              {formatINR(pkg.total_amount_paid)}
            </strong>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition"
          >
            {t.cancel}
          </button>
        </div>
      </div>
    </div>
  );
};
