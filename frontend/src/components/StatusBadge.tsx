import React from "react";
import { CaseStatus, Language } from "../types";
import { translations } from "../i18n";

interface Props {
  status: CaseStatus;
  lang: Language;
}

export const StatusBadge: React.FC<Props> = ({ status, lang }) => {
  const t = translations[lang];

  const getStatusConfig = () => {
    switch (status) {
      case "draft":
        return {
          label: t.statusDraft,
          classes: "bg-slate-100 text-slate-700 border-slate-300",
        };
      case "ready":
        return {
          label: t.statusReady,
          classes: "bg-emerald-50 text-emerald-700 border-emerald-300",
        };
      case "dpr_generated":
        return {
          label: t.statusDpr,
          classes: "bg-blue-50 text-blue-700 border-blue-300",
        };
      case "applied":
        return {
          label: t.statusApplied,
          classes: "bg-indigo-50 text-indigo-700 border-indigo-300",
        };
      case "sanctioned":
        return {
          label: t.statusSanctioned,
          classes: "bg-green-100 text-green-800 border-green-400 font-bold",
        };
      case "rejected":
        return {
          label: t.statusRejected,
          classes: "bg-red-50 text-red-700 border-red-300",
        };
      case "disbursed":
        return {
          label: t.statusDisbursed,
          classes: "bg-teal-50 text-teal-800 border-teal-400 font-bold",
        };
      case "closed":
        return {
          label: t.statusClosed,
          classes: "bg-slate-200 text-slate-800 border-slate-400",
        };
      default:
        return {
          label: status,
          classes: "bg-slate-100 text-slate-700 border-slate-200",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${config.classes}`}
    >
      {config.label}
    </span>
  );
};
