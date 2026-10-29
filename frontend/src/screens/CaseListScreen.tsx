import React, { useState } from "react";
import {
  ArrowRight,
  Building2,
  Calendar,
  MapPin,
  PlusCircle,
  Search,
} from "lucide-react";
import { CaseRecord, CaseStatus, Language } from "../types";
import { formatINR, translations } from "../i18n";
import { StatusBadge } from "../components/StatusBadge";

interface Props {
  cases: CaseRecord[];
  error?: string;
  onRefresh?: () => void;
  onSelectCase: (c: CaseRecord) => void;
  onNewCase: () => void;
  lang: Language;
}

export const CaseListScreen: React.FC<Props> = ({
  cases,
  error,
  onRefresh,
  onSelectCase,
  onNewCase,
  lang,
}) => {
  const t = translations[lang];
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filterTabs: Array<{ id: string; label: string }> = [
    { id: "all", label: t.all },
    { id: "ready", label: t.statusReady },
    { id: "dpr_generated", label: t.statusDpr },
    { id: "applied", label: t.statusApplied },
    { id: "draft", label: t.statusDraft },
  ];

  const filteredCases = cases.filter((c) => {
    const matchesFilter =
      statusFilter === "all" ? true : c.status === statusFilter;
    const q = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !q ||
      (c.beneficiary.first_name || "").toLowerCase().includes(q) ||
      (c.village?.name_en || "").toLowerCase().includes(q) ||
      (c.village?.name_mr || "").includes(q) ||
      (c.business?.name_en || c.business_code).toLowerCase().includes(q) ||
      (c.business?.name_mr || "").includes(q);
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="p-4 space-y-4">
      {error && (
        <div className="p-3 rounded-xl bg-amber-50 border border-amber-300 text-xs text-amber-900 flex items-center justify-between gap-2">
          <span>{error}</span>
          {onRefresh && (
            <button type="button" onClick={onRefresh} className="font-bold underline min-h-[40px]">
              {lang === "mr" ? "पुन्हा प्रयत्न" : "Retry"}
            </button>
          )}
        </div>
      )}
      {/* Top Banner & CTA */}
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-black text-slate-900">{t.casesTitle}</h2>
          <p className="text-xs text-slate-500 font-medium">
            {cases.length} {lang === "en" ? (cases.length === 1 ? "plan" : "plans") : lang === "hi" ? "प्लान" : "प्लॅन"}
          </p>
        </div>
        <button
          onClick={onNewCase}
          className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition min-h-[44px]"
        >
          <PlusCircle className="w-4 h-4" />
          <span>{t.newCaseBtn.replace("+ ", "")}</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
          <Search className="w-4 h-4" />
        </span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={t.searchCasesPlaceholder}
          className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 text-xs text-slate-900 bg-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 min-h-[44px]"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setStatusFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition min-h-[36px] ${
              statusFilter === tab.id
                ? "bg-indigo-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Cases List */}
      <div className="space-y-3 lg:space-y-0 lg:grid lg:grid-cols-2 xl:grid-cols-3 lg:gap-4">
        {filteredCases.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-2xl border border-dashed border-slate-200 space-y-2 lg:col-span-full">
            <p className="text-sm font-bold text-slate-700">{t.emptyCases}</p>
            <p className="text-xs text-slate-500">{t.emptyCasesSub}</p>
            <button
              onClick={onNewCase}
              className="mt-2 inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 text-white text-xs font-bold rounded-xl"
            >
              <PlusCircle className="w-4 h-4" />
              {t.newCaseBtn}
            </button>
          </div>
        ) : (
          filteredCases.map((c) => (
            <div
              key={c.id}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && onSelectCase(c)}
              onClick={() => onSelectCase(c)}
              className="p-4 bg-white rounded-2xl border border-slate-200 hover:border-indigo-300 shadow-2xs hover:shadow-xs transition cursor-pointer space-y-2.5 active:scale-[0.99]"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                    <Building2 className="w-4 h-4 text-indigo-600" />
                    {c.business ? (lang === "mr" ? c.business.name_mr : c.business.name_en) : c.business_code}
                  </h3>
                </div>
                <StatusBadge status={c.status as CaseStatus} lang={lang} />
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-100 text-slate-600">
                <div className="flex items-center gap-1 text-[11px]">
                  <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">
                    {c.village ? `${lang === "mr" ? c.village.name_mr : c.village.name_en} (${lang === "mr" ? c.village.district_mr : c.village.district_en})` : "—"}
                  </span>
                </div>
                <div className="text-right font-bold text-slate-900">
                  {c.target_project_cost ? formatINR(c.target_project_cost) : `${lang === "mr" ? "भांडवल" : "Own"} ${formatINR(c.margin_available)}`}
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  {new Date(c.created_at).toLocaleDateString(lang === "mr" ? "mr-IN" : "en-IN")}
                </span>
                <span className="font-bold text-indigo-600 flex items-center gap-0.5">
                  {t.viewDetails}
                  <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
