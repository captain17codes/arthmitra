import React from "react";
import { FolderKanban, PlusCircle, UserCircle, ShieldAlert } from "lucide-react";
import { Language } from "../types";
import { translations } from "../i18n";

export type NavTab = "cases" | "new_case" | "profile" | "supervisor";

interface Props {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  lang: Language;
}

export const BottomNav: React.FC<Props> = ({ currentTab, onSelectTab, lang }) => {
  const t = translations[lang];

  return (
    <nav className="sticky bottom-0 z-30 bg-white/95 backdrop-blur-xs border-t border-slate-200 px-2 py-1.5 flex items-center justify-around shadow-lg lg:order-1 lg:top-[57px] lg:bottom-auto lg:self-start lg:h-[calc(100vh-57px)] lg:w-60 lg:shrink-0 lg:flex-col lg:items-stretch lg:justify-start lg:gap-1 lg:px-3 lg:py-4 lg:border-t-0 lg:border-r lg:shadow-none">
      {/* Cases List */}
      <button
        onClick={() => onSelectTab("cases")}
        className={`flex flex-col items-center justify-center min-w-[64px] min-h-[48px] py-1 rounded-xl transition lg:flex-row lg:justify-start lg:gap-3 lg:px-3 lg:hover:bg-slate-100 ${
          currentTab === "cases"
            ? "text-indigo-600 font-bold"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <FolderKanban className="w-5 h-5 mb-0.5 lg:mb-0" />
        <span className="text-[11px] leading-none lg:text-sm">{t.casesTitle}</span>
      </button>

      {/* New Case CTA */}
      <button
        onClick={() => onSelectTab("new_case")}
        className={`flex flex-col items-center justify-center min-w-[76px] min-h-[48px] px-2 py-1 rounded-xl transition lg:flex-row lg:justify-start lg:gap-3 lg:px-3 lg:mb-2 ${
          currentTab === "new_case"
            ? "bg-emerald-600 text-white font-bold shadow-xs"
            : "bg-emerald-50 text-emerald-800 font-semibold border border-emerald-200"
        }`}
      >
        <PlusCircle className="w-5 h-5 mb-0.5 lg:mb-0" />
        <span className="text-[11px] leading-none lg:text-sm">{t.newCaseBtn.replace("+ ", "")}</span>
      </button>

      {/* Supervisor Console Tab */}
      <button
        onClick={() => onSelectTab("supervisor")}
        className={`flex flex-col items-center justify-center min-w-[64px] min-h-[48px] py-1 rounded-xl transition lg:flex-row lg:justify-start lg:gap-3 lg:px-3 lg:hover:bg-slate-100 ${
          currentTab === "supervisor"
            ? "text-indigo-600 font-bold"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <ShieldAlert className="w-5 h-5 mb-0.5 lg:mb-0" />
        <span className="text-[11px] leading-none lg:text-sm">पर्यवेक्षक</span>
      </button>

      {/* Agent Info */}
      <button
        onClick={() => onSelectTab("profile")}
        className={`flex flex-col items-center justify-center min-w-[64px] min-h-[48px] py-1 rounded-xl transition lg:flex-row lg:justify-start lg:gap-3 lg:px-3 lg:hover:bg-slate-100 ${
          currentTab === "profile"
            ? "text-indigo-600 font-bold"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <UserCircle className="w-5 h-5 mb-0.5 lg:mb-0" />
        <span className="text-[11px] leading-none lg:text-sm">{t.agentRole.split(" ")[0]}</span>
      </button>
    </nav>
  );
};
