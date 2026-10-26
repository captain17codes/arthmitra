import React, { useState } from "react";
import {
  AlertCircle,
  Award,
  CheckCircle2,
  FileCheck,
  FileText,
  Lightbulb,
  PieChart,
  Sliders,
  TrendingUp,
  Users,
} from "lucide-react";
import { CaseRecord, EvaluationResult, Language, SchemePackage } from "../types";
import { formatINR, formatNumberIN, translations } from "../i18n";
import { AmortizationModal } from "../components/AmortizationModal";

interface Props {
  caseRecord: CaseRecord;
  evaluation: EvaluationResult;
  onUpdateCase?: (updated: CaseRecord) => void;
  onGoToDpr: () => void;
  onBack?: () => void;
  lang: Language;
}

export const ResultsScreen: React.FC<Props> = ({
  caseRecord,
  evaluation,
  onGoToDpr,
  lang,
}) => {
  const t = translations[lang];
  const [activeTab, setActiveTab] = useState<
    "market" | "financing" | "viability" | "advisory"
  >("financing");

  const [selectedSchedulePkg, setSelectedSchedulePkg] =
    useState<SchemePackage | null>(null);

  // Udhar stress slider state
  const [currentUdharPct, setCurrentUdharPct] = useState<number>(
    evaluation.viability.udhar_pct || 20
  );

  const baseDscr = evaluation.viability.dscr;
  // Dynamic recalculation of DSCR under credit stress:
  const dynamicDscr = Math.max(
    1.1,
    +(baseDscr - (currentUdharPct / 100) * 0.55).toFixed(2)
  );

  const market = evaluation.market;
  const viability = evaluation.viability;
  const topSchemes = evaluation.top_schemes;
  const advisory = evaluation.advisory;

  const getSaturationColor = (band: "low" | "medium" | "high") => {
    switch (band) {
      case "low":
        return {
          pill: "bg-emerald-100 text-emerald-800 border-emerald-300",
          text: t.satLow,
        };
      case "medium":
        return {
          pill: "bg-amber-100 text-amber-800 border-amber-300",
          text: t.satMed,
        };
      case "high":
        return {
          pill: "bg-red-100 text-red-800 border-red-300",
          text: t.satHigh,
        };
    }
  };

  const satConfig = getSaturationColor(market.saturation_band);

  return (
    <div className="p-3 sm:p-4 space-y-3.5 pb-20">
      {/* Case Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 rounded-2xl p-4 text-white shadow-md space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-[10px] font-bold text-indigo-200 tracking-wider uppercase block">
              {t.evaluationResultsTitle}
            </span>
            <h2 className="text-base font-black text-white mt-0.5">
              {caseRecord.beneficiary.first_name}
            </h2>
            <p className="text-xs text-indigo-200 font-medium">
              {lang === "mr" ? caseRecord.business.name_mr : caseRecord.business.name_en} ·{" "}
              {lang === "mr" ? caseRecord.village.name_mr : caseRecord.village.name_en}
            </p>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-indigo-300 block">प्रकल्प खर्च</span>
            <span className="text-sm font-black text-emerald-400">
              {formatINR(caseRecord.target_project_cost)}
            </span>
          </div>
        </div>

        {/* Quick Summary Pill Bar */}
        <div className="pt-2 border-t border-indigo-700/60 grid grid-cols-3 gap-2 text-center text-[11px]">
          <div>
            <span className="text-[10px] text-indigo-300 block">सर्वोत्तम EMI</span>
            <span className="font-bold text-white">
              {topSchemes.length > 0 ? formatINR(topSchemes[0].monthly_emi) : "—"}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-indigo-300 block">DSCR प्रमाण</span>
            <span
              className={`font-bold ${
                dynamicDscr >= 1.5 ? "text-emerald-300" : "text-amber-300"
              }`}
            >
              {dynamicDscr}x
            </span>
          </div>
          <div>
            <span className="text-[10px] text-indigo-300 block">बाजार संधी</span>
            <span className="font-bold text-teal-300 uppercase">
              {market.saturation_band}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="grid grid-cols-4 gap-1 p-1 bg-slate-100 rounded-xl text-xs font-bold border border-slate-200">
        <button
          type="button"
          onClick={() => setActiveTab("financing")}
          className={`py-2 rounded-lg transition min-h-[40px] flex items-center justify-center gap-1 ${
            activeTab === "financing"
              ? "bg-white text-indigo-700 shadow-2xs font-extrabold"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Award className="w-3.5 h-3.5" />
          <span>{t.tabFinancing.split(" ")[0]}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("market")}
          className={`py-2 rounded-lg transition min-h-[40px] flex items-center justify-center gap-1 ${
            activeTab === "market"
              ? "bg-white text-indigo-700 shadow-2xs font-extrabold"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <PieChart className="w-3.5 h-3.5" />
          <span>{t.tabMarket.split(" ")[0]}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("viability")}
          className={`py-2 rounded-lg transition min-h-[40px] flex items-center justify-center gap-1 ${
            activeTab === "viability"
              ? "bg-white text-indigo-700 shadow-2xs font-extrabold"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <TrendingUp className="w-3.5 h-3.5" />
          <span>{t.tabViability.split(" ")[0]}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("advisory")}
          className={`py-2 rounded-lg transition min-h-[40px] flex items-center justify-center gap-1 ${
            activeTab === "advisory"
              ? "bg-white text-indigo-700 shadow-2xs font-extrabold"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" />
          <span>{t.tabAdvisory.split(" ")[0]}</span>
        </button>
      </div>

      {/* TAB 1: FINANCING SCHEMES */}
      {activeTab === "financing" && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              {t.financingCardTitle}
            </h3>
            <span className="text-[10px] text-slate-500 font-medium">
              Pure Python Engine Ranked
            </span>
          </div>

          {topSchemes.map((pkg, idx) => (
            <div
              key={pkg.scheme_code}
              className={`p-4 rounded-2xl border transition space-y-3 ${
                idx === 0
                  ? "bg-emerald-50/70 border-emerald-400 shadow-xs ring-1 ring-emerald-400"
                  : "bg-white border-slate-200"
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded ${
                        idx === 0
                          ? "bg-emerald-600 text-white"
                          : "bg-slate-200 text-slate-700"
                      }`}
                    >
                      # {idx + 1} पर्याय
                    </span>
                    <h4 className="text-xs font-bold text-slate-900 leading-tight">
                      {lang === "mr" ? pkg.scheme_name_mr : pkg.scheme_name_en}
                    </h4>
                  </div>
                  <span className="text-[10px] text-slate-500 mt-0.5 block">
                    योजना कोड: {pkg.scheme_code}
                  </span>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-slate-500 block">मासिक हप्ता</span>
                  <span className="text-sm font-black text-emerald-800">
                    {formatINR(pkg.monthly_emi)}
                  </span>
                </div>
              </div>

              {/* Numbers Grid */}
              <div className="grid grid-cols-3 gap-2 bg-white/80 p-2.5 rounded-xl border border-slate-200/80 text-xs text-center">
                <div>
                  <span className="text-[10px] text-slate-500 block">कर्ज रक्कम</span>
                  <span className="font-bold text-slate-900">
                    {formatINR(pkg.loan_amount)}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">अनुदान (Subsidy)</span>
                  <span className="font-bold text-emerald-700">
                    {formatINR(pkg.subsidy_amount)} ({pkg.subsidy_pct}%)
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">व्याज दर</span>
                  <span className="font-bold text-indigo-700">
                    {pkg.annual_interest_rate}% वा.
                  </span>
                </div>
              </div>

              {/* Extra terms */}
              <div className="flex items-center justify-between text-[11px] text-slate-600 px-1">
                <span>मुदत: <strong>{pkg.tenure_months} महिने</strong></span>
                <span>मोरेटोरियम: <strong>{pkg.moratorium_months} महिने</strong></span>
                <span>पहिला हप्ता: <strong>{pkg.first_emi_date}</strong></span>
              </div>

              {/* Action */}
              <div className="flex items-center justify-between pt-1 border-t border-slate-200/60">
                <button
                  type="button"
                  onClick={() => setSelectedSchedulePkg(pkg)}
                  className="text-xs font-bold text-indigo-700 hover:text-indigo-900 flex items-center gap-1"
                >
                  <FileText className="w-3.5 h-3.5" />
                  {t.viewScheduleBtn}
                </button>
                <a
                  href={pkg.portal_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] font-semibold text-slate-500 hover:text-slate-800 underline"
                >
                  अधिकृत पोर्टल
                </a>
              </div>
            </div>
          ))}

          {/* Ineligible schemes */}
          {evaluation.ineligible_schemes.length > 0 && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
              <span className="text-xs font-bold text-slate-700 block">
                {t.ineligibleSchemesTitle}
              </span>
              <div className="space-y-1">
                {evaluation.ineligible_schemes.map((s) => (
                  <div key={s.scheme_code} className="text-[11px] text-slate-600">
                    <strong className="text-slate-800">{s.scheme_name}:</strong>{" "}
                    {s.rejection_reasons.join(", ")}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: MARKET DEMAND */}
      {activeTab === "market" && (
        <div className="space-y-3">
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900">
              {t.marketCardTitle}
            </h3>

            {/* Saturation Badge */}
            <div className={`p-3 rounded-xl border flex items-center gap-2 ${satConfig.pill}`}>
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <div>
                <span className="text-xs font-black block">{satConfig.text}</span>
                <span className="text-[11px] font-medium leading-tight">
                  {lang === "mr" ? market.saturation_reason_mr : market.saturation_reason_en}
                </span>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block">
                  {t.catchmentPopLabel}
                </span>
                <span className="text-base font-black text-slate-900">
                  {formatNumberIN(market.catchment_population)} नागरिक
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block">
                  {t.monthlyDemandLabel}
                </span>
                <span className="text-base font-black text-emerald-800">
                  {formatINR(market.monthly_category_spend)}
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block">
                  {t.reportedCompetitorsLabel}
                </span>
                <span className="text-base font-black text-slate-900">
                  {market.competitors_reported} दुकाने
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block">
                  {t.bepMarketShareLabel}
                </span>
                <span className="text-base font-black text-indigo-700">
                  {market.breakeven_market_share_pct}%
                </span>
              </div>
            </div>
          </div>

          {/* Complementary Businesses */}
          {market.complementary_businesses.length > 0 && (
            <div className="p-4 bg-indigo-50/60 rounded-2xl border border-indigo-200 space-y-2">
              <h4 className="text-xs font-bold text-indigo-950 flex items-center gap-1.5">
                <Lightbulb className="w-3.5 h-3.5 text-indigo-600" />
                {t.complementaryTitle}
              </h4>
              <div className="space-y-1.5">
                {market.complementary_businesses.map((cb) => (
                  <div
                    key={cb.code}
                    className="p-2.5 bg-white rounded-xl border border-indigo-100 text-xs space-y-0.5"
                  >
                    <span className="font-bold text-slate-900 block">
                      {lang === "mr" ? cb.name_mr : cb.name_en}
                    </span>
                    <span className="text-[11px] text-slate-600">
                      {lang === "mr" ? cb.rationale_mr : cb.rationale_en}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: VIABILITY & UDHAR STRESS */}
      {activeTab === "viability" && (
        <div className="space-y-3">
          {/* Income Timing Warning */}
          {viability.income_timing_warning && (
            <div className="p-3.5 bg-amber-50 border-2 border-amber-400 rounded-2xl flex items-start gap-2.5 text-xs text-amber-950">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block text-sm">
                  {t.incomeTimingWarningTitle}
                </span>
                <span className="text-[11px] font-medium leading-relaxed mt-0.5 block">
                  {lang === "mr"
                    ? viability.income_timing_text_mr
                    : viability.income_timing_text_en}
                </span>
              </div>
            </div>
          )}

          {/* Viability Metrics Card */}
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900">
              {t.viabilityCardTitle}
            </h3>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <span className="text-[10px] text-emerald-700 font-bold block">
                  {t.dscrLabel}
                </span>
                <span className="text-xl font-black text-emerald-900">
                  {dynamicDscr}x
                </span>
                <span className="text-[9px] text-emerald-700 block mt-0.5">
                  {t.dscrBenchmarkHint}
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block">
                  {t.bepLabel}
                </span>
                <span className="text-xl font-black text-slate-900">
                  {viability.breakeven_capacity_pct}%
                </span>
                <span className="text-[9px] text-slate-500 block mt-0.5">
                  किमान ४३% क्षमतेवर खर्च निघतो
                </span>
              </div>
            </div>

            {/* Nayak Working Capital */}
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs flex items-center justify-between">
              <div>
                <span className="font-bold text-slate-800 block">
                  {t.nayakWorkingCapitalLabel}
                </span>
                <span className="text-[10px] text-slate-500">
                  नायक समिती: २५% उलाढाल निकष
                </span>
              </div>
              <span className="text-sm font-bold text-slate-900">
                {formatINR(viability.nayak_working_capital)}
              </span>
            </div>

            {/* Interactive Udhar Slider */}
            <div className="p-3.5 bg-amber-50/70 border border-amber-200 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-amber-950 flex items-center gap-1">
                  <Sliders className="w-3.5 h-3.5 text-amber-700" />
                  {t.udharSliderLabel}
                </label>
                <span className="text-xs font-black text-amber-900 bg-amber-200 px-2 py-0.5 rounded">
                  {currentUdharPct}%
                </span>
              </div>

              <input
                type="range"
                min={0}
                max={50}
                step={5}
                value={currentUdharPct}
                onChange={(e) => setCurrentUdharPct(parseInt(e.target.value) || 0)}
                className="w-full h-2 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />

              <div className="flex items-center justify-between text-[11px] text-amber-900 font-semibold pt-1">
                <span>{t.udharAdjustedDscrHint}</span>
                <span
                  className={`font-black text-xs px-1.5 py-0.5 rounded ${
                    dynamicDscr >= 1.5
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-amber-200 text-amber-900"
                  }`}
                >
                  DSCR: {dynamicDscr}x
                </span>
              </div>
            </div>
          </div>

          {/* 5-Year Projections Table */}
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2">
            <h4 className="text-xs font-bold text-slate-900">
              {t.projections5yrTitle}
            </h4>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-100 text-[10px] uppercase text-slate-600">
                  <tr>
                    <th className="py-1.5 px-2 font-bold">{t.yearCol}</th>
                    <th className="py-1.5 px-2 text-right font-bold">{t.revenueCol}</th>
                    <th className="py-1.5 px-2 text-right font-bold">{t.surplusCol}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {viability.projections_5yr.map((row) => (
                    <tr key={row.year} className="hover:bg-slate-50">
                      <td className="py-1.5 px-2 font-bold text-slate-700">
                        वर्ष {row.year}
                      </td>
                      <td className="py-1.5 px-2 text-right text-slate-900">
                        {formatINR(row.revenue)}
                      </td>
                      <td className="py-1.5 px-2 text-right font-bold text-emerald-700">
                        {formatINR(row.net_surplus)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: FACTS-GROUNDED AI ADVISORY */}
      {activeTab === "advisory" && advisory && (
        <div className="space-y-3">
          {/* Market Reach */}
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-1.5">
            <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-indigo-600" />
              {t.marketReachTitle}
            </h4>
            <p className="text-xs text-slate-700 leading-relaxed">
              {advisory.market_reach}
            </p>
          </div>

          {/* Opportunities */}
          <div className="p-4 bg-emerald-50/60 rounded-2xl border border-emerald-200 space-y-2">
            <h4 className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
              <Lightbulb className="w-3.5 h-3.5 text-emerald-600" />
              {t.opportunitiesTitle}
            </h4>
            <ul className="space-y-1 text-xs text-emerald-900">
              {advisory.opportunities.map((opp, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-emerald-600 font-bold">•</span>
                  <span>{opp}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* SWOT Matrix */}
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <h4 className="text-xs font-bold text-slate-900">
              स्थानिक SWOT विश्लेषण (Strengths, Weaknesses, Opportunities, Threats)
            </h4>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 bg-emerald-50/60 rounded-xl border border-emerald-100 space-y-1">
                <span className="font-bold text-emerald-900 block text-[11px]">
                  {t.swotStrengths}
                </span>
                <ul className="text-[10px] text-emerald-800 space-y-0.5">
                  {advisory.swot.strengths.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-2.5 bg-amber-50/60 rounded-xl border border-amber-100 space-y-1">
                <span className="font-bold text-amber-900 block text-[11px]">
                  {t.swotWeaknesses}
                </span>
                <ul className="text-[10px] text-amber-800 space-y-0.5">
                  {advisory.swot.weaknesses.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-2.5 bg-blue-50/60 rounded-xl border border-blue-100 space-y-1">
                <span className="font-bold text-blue-900 block text-[11px]">
                  {t.swotOpportunities}
                </span>
                <ul className="text-[10px] text-blue-800 space-y-0.5">
                  {advisory.swot.opportunities.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-2.5 bg-red-50/60 rounded-xl border border-red-100 space-y-1">
                <span className="font-bold text-red-900 block text-[11px]">
                  {t.swotThreats}
                </span>
                <ul className="text-[10px] text-red-800 space-y-0.5">
                  {advisory.swot.threats.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Pricing Guidance & Next Steps */}
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
            <h4 className="font-bold text-slate-900">{t.pricingTitle}</h4>
            <p className="text-slate-700">{advisory.pricing_guidance}</p>
          </div>
        </div>
      )}

      {/* Floating Bottom Action: Proceed to DPR */}
      <div className="pt-2">
        <button
          type="button"
          onClick={onGoToDpr}
          className="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition flex items-center justify-center gap-2 min-h-[48px]"
        >
          <FileCheck className="w-4 h-4" />
          <span>बँकेसाठी अधिकृत डीपीआर (PDF) तयार करा →</span>
        </button>
      </div>

      {/* Amortization Schedule Modal */}
      <AmortizationModal
        pkg={selectedSchedulePkg}
        isOpen={Boolean(selectedSchedulePkg)}
        onClose={() => setSelectedSchedulePkg(null)}
        lang={lang}
      />
    </div>
  );
};
