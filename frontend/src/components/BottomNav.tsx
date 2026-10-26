import React from "react";
import { FolderKanban, PlusCircle, UserCircle } from "lucide-react";
import { Language } from "../types";
import { translations } from "../i18n";

export type NavTab = "cases" | "new_case" | "profile";

interface Props {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  lang: Language;
}

export const BottomNav: React.FC<Props> = ({ currentTab, onSelectTab, lang }) => {
  const t = translations[lang];

  return (
    <nav className="sticky bottom-0 z-30 bg-white/95 backdrop-blur-xs border-t border-slate-200 px-3 py-1.5 flex items-center justify-around shadow-lg">
      {/* Cases List */}
      <button
        onClick={() => onSelectTab("cases")}
        className={`flex flex-col items-center justify-center min-w-[72px] min-h-[48px] py-1 rounded-xl transition ${
          currentTab === "cases"
            ? "text-indigo-600 font-bold"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <FolderKanban className="w-5 h-5 mb-0.5" />
        <span className="text-[11px] leading-none">{t.casesTitle}</span>
      </button>

      {/* New Case CTA */}
      <button
        onClick={() => onSelectTab("new_case")}
        className={`flex flex-col items-center justify-center min-w-[80px] min-h-[48px] px-3 py-1 rounded-xl transition ${
          currentTab === "new_case"
            ? "bg-emerald-600 text-white font-bold shadow-xs"
            : "bg-emerald-50 text-emerald-800 font-semibold border border-emerald-200"
        }`}
      >
        <PlusCircle className="w-5 h-5 mb-0.5" />
        <span className="text-[11px] leading-none">{t.newCaseBtn.replace("+ ", "")}</span>
      </button>

      {/* Agent Info */}
      <button
        onClick={() => onSelectTab("profile")}
        className={`flex flex-col items-center justify-center min-w-[72px] min-h-[48px] py-1 rounded-xl transition ${
          currentTab === "profile"
            ? "text-indigo-600 font-bold"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <UserCircle className="w-5 h-5 mb-0.5" />
        <span className="text-[11px] leading-none">{t.agentRole.split(" ")[0]}</span>
      </button>
    </nav>
  );
};
