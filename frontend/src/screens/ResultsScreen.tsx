import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  Award,
  FileCheck,
  FileText,
  HelpCircle,
  Lightbulb,
  PieChart,
  RefreshCw,
  Sliders,
  TrendingUp,
  Volume2,
  VolumeX,
} from "lucide-react";
import { AdvisoryContent, CaseRecord, Language, SchemePackage } from "../types";
import { formatINR, formatNumberIN, translations } from "../i18n";
import { AmortizationModal } from "../components/AmortizationModal";
import { api } from "../services/api";

interface Props {
  caseRecord: CaseRecord;
  onCaseUpdated: (updated: CaseRecord) => void;
  onGoToDpr: () => void;
  lang: Language;
}

const n = (v: string | number | null | undefined) => (v === null || v === undefined || v === "" ? NaN : Number(v));
const inr = (v: string | number | null | undefined) => (Number.isFinite(n(v)) ? formatINR(Math.round(n(v))) : "—");
const humanize = (code: string) => code.replace(/_/g, " ");

export function schemeName(p: { scheme_name: Record<string, string>; scheme_code: string }, lang: Language) {
  return p.scheme_name?.[lang] || p.scheme_name?.en || p.scheme_code;
}

export function emiLabel(freq: number, lang: Language) {
  if (freq === 3) return lang === "en" ? "per quarter" : lang === "hi" ? "प्रति तिमाही" : "प्रति तिमाही";
  return lang === "en" ? "per month" : lang === "hi" ? "प्रति माह" : "प्रति महिना";
}

export const ResultsScreen: React.FC<Props> = ({ caseRecord, onCaseUpdated, onGoToDpr, lang }) => {
  const t = translations[lang];
  const mr = lang === "mr";
  const out = caseRecord.output;
  const [activeTab, setActiveTab] = useState<"financing" | "market" | "viability" | "advisory">("financing");
  const [schedulePkg, setSchedulePkg] = useState<SchemePackage | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [udharPct, setUdharPct] = useState<number>(
    Math.round(Number(out?.summary.udhar_stress.udhar_pct ?? 0.2) * 100)
  );
  const [recalcBusy, setRecalcBusy] = useState(false);
  const [recalcError, setRecalcError] = useState("");
  const [advisory, setAdvisory] = useState<AdvisoryContent | null>(null);
  const [advisoryMeta, setAdvisoryMeta] = useState<{ model: string; validator_passed: boolean } | null>(null);
  const [advisoryBusy, setAdvisoryBusy] = useState(false);
  const [advisoryError, setAdvisoryError] = useState("");

  useEffect(() => () => window.speechSynthesis?.cancel(), []);

  useEffect(() => {
    setAdvisory(null);
    setAdvisoryMeta(null);
    if (!caseRecord.evaluation_id) return;
    api
      .getAdvisory(caseRecord.evaluation_id)
      .then((a) => {
        if (a) {
          setAdvisory(a.output);
          setAdvisoryMeta({ model: a.model, validator_passed: a.validator_passed });
        }
      })
      .catch(() => undefined);
  }, [caseRecord.evaluation_id]);

  if (!out) {
    return (
      <div className="p-4 text-xs text-slate-600">
        {mr ? "या प्रकरणाचे मूल्यांकन अजून झालेले नाही." : "This case has not been evaluated yet."}
      </div>
    );
  }

  const s = out.summary;
  const v = out.viability;
  const m = out.market;
  const top = s.top_packages;
  const best = top[0];

  const recalc = async (pct: number) => {
    setRecalcBusy(true);
    setRecalcError("");
    try {
      await api.evaluate(caseRecord.id, { udhar_pct: (pct / 100).toFixed(2) });
      onCaseUpdated(await api.getCase(caseRecord.id));
    } catch (e) {
      setRecalcError((e as Error).message);
    } finally {
      setRecalcBusy(false);
    }
  };

  const loadAdvisory = async () => {
    if (!caseRecord.evaluation_id) return;
    setAdvisoryBusy(true);
    setAdvisoryError("");
    try {
      const a = await api.generateAdvisory(caseRecord.evaluation_id, lang);
      setAdvisory(a.output);
      setAdvisoryMeta({ model: a.model, validator_passed: a.validator_passed });
    } catch (e) {
      setAdvisoryError((e as Error).message);
    } finally {
      setAdvisoryBusy(false);
    }
  };

  const speak = () => {
    if (!("speechSynthesis" in window)) return;
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    const biz = mr ? s.business_name_mr : s.business_name_en;
    let text: string;
    if (!best) {
      text = mr
        ? `${caseRecord.beneficiary.first_name} यांच्या ${biz} व्यवसायासाठी सध्या कोणतीही योजना पात्र दिसत नाही.`
        : `No scheme is currently eligible for ${caseRecord.beneficiary.first_name}'s ${biz}.`;
    } else {
      const emi = Math.round(Number(best.emi));
      text = mr
        ? `${caseRecord.beneficiary.first_name} यांच्या ${biz} व्यवसायासाठी सर्वोत्तम योजना ${schemeName(best, lang)}. कर्ज ${Math.round(Number(best.loan_amount))} रुपये. हप्ता ${emi} रुपये ${emiLabel(best.emi_frequency_months, lang)}. स्वतःचे पैसे ${Math.round(Number(best.own_margin_required))} रुपये.`
        : `Best option for ${caseRecord.beneficiary.first_name}: ${schemeName(best, lang)}. Loan ${Math.round(Number(best.loan_amount))} rupees. Instalment ${emi} rupees ${emiLabel(best.emi_frequency_months, lang)}. Own money ${Math.round(Number(best.own_margin_required))} rupees.`;
    }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang === "mr" ? "mr-IN" : lang === "hi" ? "hi-IN" : "en-IN";
    u.rate = 0.95;
    u.onend = () => setIsSpeaking(false);
    u.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.cancel();
    setIsSpeaking(true);
    window.speechSynthesis.speak(u);
  };

  const sat = m.saturation_level;
  const satStyle: Record<string, string> = {
    low: "bg-emerald-100 text-emerald-800 border-emerald-300",
    medium: "bg-amber-100 text-amber-800 border-amber-300",
    high: "bg-red-100 text-red-800 border-red-300",
    needs_info: "bg-slate-100 text-slate-700 border-slate-300",
  };
  const satText: Record<string, string> = {
    low: t.satLow,
    medium: t.satMed,
    high: t.satHigh,
    needs_info: mr ? "माहिती अपूर्ण — स्पर्धक संख्या टाका" : "Needs info — enter competitor count",
  };

  const tabs: Array<{ id: typeof activeTab; icon: React.ReactNode; label: string }> = [
    { id: "financing", icon: <Award className="w-3.5 h-3.5" />, label: t.tabFinancing.split(" ")[0] },
    { id: "market", icon: <PieChart className="w-3.5 h-3.5" />, label: t.tabMarket.split(" ")[0] },
    { id: "viability", icon: <TrendingUp className="w-3.5 h-3.5" />, label: t.tabViability.split(" ")[0] },
    { id: "advisory", icon: <Lightbulb className="w-3.5 h-3.5" />, label: t.tabAdvisory.split(" ")[0] },
  ];

  return (
    <div className="p-3 sm:p-4 space-y-3.5 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 rounded-2xl p-4 text-white shadow-md space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-[10px] font-bold text-indigo-200 tracking-wider uppercase block">
              {t.evaluationResultsTitle}
            </span>
            <h2 className="text-base font-black text-white mt-0.5">{caseRecord.beneficiary.first_name}</h2>
            <p className="text-xs text-indigo-200 font-medium">
              {mr ? s.business_name_mr : s.business_name_en} ·{" "}
              {caseRecord.village ? (mr ? caseRecord.village.name_mr : caseRecord.village.name_en) : s.village_name}
            </p>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-indigo-300 block">{mr ? "प्रकल्प खर्च" : "Project cost"}</span>
            <span className="text-sm font-black text-emerald-400">{inr(best ? best.project_cost : s.project_cost)}</span>
          </div>
        </div>
        <div className="pt-2 border-t border-indigo-700/60 flex items-center justify-between text-[11px]">
          <div className="grid grid-cols-3 gap-2 text-center flex-1">
            <div>
              <span className="text-[10px] text-indigo-300 block">{mr ? "सर्वोत्तम हप्ता" : "Best EMI"}</span>
              <span className="font-bold text-white">{best ? inr(best.emi) : "—"}</span>
              {best && <span className="text-[9px] text-indigo-300 block">{emiLabel(best.emi_frequency_months, lang)}</span>}
            </div>
            <div>
              <span className="text-[10px] text-indigo-300 block">DSCR</span>
              <span className={`font-bold ${v.dscr_passed ? "text-emerald-300" : "text-amber-300"}`}>
                {v.average_dscr ? `${v.average_dscr}x` : "—"}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-indigo-300 block">{mr ? "स्पर्धा" : "Competition"}</span>
              <span className="font-bold text-teal-300 uppercase">{sat === "needs_info" ? "?" : sat}</span>
            </div>
          </div>
          <div className="pl-2 border-l border-indigo-700/60 shrink-0">
            <button
              type="button"
              onClick={speak}
              aria-label="Read aloud results summary"
              className={`p-2 rounded-xl border flex flex-col items-center gap-0.5 min-w-[44px] min-h-[44px] ${
                isSpeaking ? "bg-rose-500 text-white border-rose-400" : "bg-indigo-700/80 text-indigo-100 border-indigo-600"
              }`}
            >
              {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              <span className="text-[9px] font-bold">{isSpeaking ? (mr ? "थांबवा" : "Stop") : mr ? "ऐका" : "Listen"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-4 gap-1 p-1 bg-slate-100 rounded-xl text-xs font-bold border border-slate-200" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`py-2 rounded-lg transition min-h-[44px] flex items-center justify-center gap-1 ${
              activeTab === tab.id ? "bg-white text-indigo-700 shadow-2xs font-extrabold" : "text-slate-600"
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* FINANCING */}
      {activeTab === "financing" && (
        <div className="space-y-3">
          {top.length === 0 && (
            <div className="p-4 bg-amber-50 border border-amber-300 rounded-2xl text-xs text-amber-900 space-y-1">
              <strong className="block">{mr ? "सध्या कोणतीही योजना पात्र नाही" : "No scheme is currently eligible"}</strong>
              <span>
                {mr
                  ? "खालील कारणे व आवश्यक माहिती पहा. माहिती पूर्ण करून पुन्हा मूल्यांकन करा."
                  : "See the reasons and missing information below, then re-evaluate."}
              </span>
            </div>
          )}

          {top.map((pkg, idx) => (
            <PackageCard key={pkg.scheme_code} pkg={pkg} idx={idx} lang={lang} onSchedule={() => setSchedulePkg(pkg)} />
          ))}

          {out.rules.other_eligible.length > 0 && (
            <div className="text-[11px] text-slate-600 px-1">
              {mr ? "इतर पात्र योजना" : "Other eligible schemes"}: {out.rules.other_eligible.join(", ")}
            </div>
          )}

          {out.rules.confirm_with_agency.length > 0 && (
            <div className="p-3 bg-sky-50 border border-sky-200 rounded-xl space-y-1.5">
              <span className="text-xs font-bold text-sky-900 flex items-center gap-1">
                <HelpCircle className="w-3.5 h-3.5" />
                {mr ? "पात्र असू शकता — संस्थेकडे खात्री करा (नियम पडताळलेले नाहीत)" : "May qualify — confirm with the agency (rules not verified)"}
              </span>
              {out.rules.confirm_with_agency.map((p) => (
                <div key={p.scheme_code} className="text-[11px] text-sky-900">
                  <strong>{schemeName(p, lang)}</strong> · {mr ? "कर्ज" : "loan"} {inr(p.loan_amount)} · {p.annual_rate_pct}% ·{" "}
                  {p.apply_at}
                </div>
              ))}
            </div>
          )}

          {out.rules.needs_info.length > 0 && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="text-xs font-bold text-slate-700 block">{mr ? "आणखी माहिती हवी" : "More information needed"}</span>
              {out.rules.needs_info.map((r) => (
                <div key={r.code} className="text-[11px] text-slate-600">
                  <strong className="text-slate-800">{r.name?.[lang] || r.name?.en || r.code}:</strong>{" "}
                  {r.missing_fields.map(humanize).join(", ")}
                </div>
              ))}
            </div>
          )}

          {out.rules.not_eligible.length > 0 && (
            <details className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
              <summary className="text-xs font-bold text-slate-700 cursor-pointer min-h-[32px]">
                {t.ineligibleSchemesTitle} ({out.rules.not_eligible.length})
              </summary>
              <div className="space-y-1 mt-1.5">
                {out.rules.not_eligible.map((r) => (
                  <div key={r.code} className="text-[11px] text-slate-600">
                    <strong className="text-slate-800">{r.name?.[lang] || r.name?.en || r.code}:</strong>{" "}
                    {r.reasons.map(humanize).join(", ")}
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}

      {/* MARKET */}
      {activeTab === "market" && (
        <div className="space-y-3">
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900">{t.marketCardTitle}</h3>
            <div className={`p-3 rounded-xl border text-xs font-black ${satStyle[sat]}`}>{satText[sat]}</div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <Stat label={t.catchmentPopLabel} value={`${formatNumberIN(Math.round(Number(m.catchment_population.value)))}`}
                hint={`${formatNumberIN(Math.round(Number(m.catchment_population.min)))} – ${formatNumberIN(Math.round(Number(m.catchment_population.max)))}`} />
              <Stat label={t.monthlyDemandLabel} value={inr(m.category_demand_monthly.value)}
                hint={`${inr(m.category_demand_monthly.min)} – ${inr(m.category_demand_monthly.max)}`} />
              <Stat label={t.reportedCompetitorsLabel} value={m.competitor_count ? m.competitor_count.value : "—"} />
              <Stat label={t.bepMarketShareLabel} value={`${Number(m.be_market_share.value).toFixed(1)}%`} />
            </div>
            {m.warnings.length > 0 && <Warnings items={m.warnings} />}
            {m.explanation && <p className="text-[11px] text-slate-500">{m.explanation}</p>}
          </div>
          {m.complementary_suggestions.length > 0 && (
            <div className="p-4 bg-indigo-50/60 rounded-2xl border border-indigo-200 space-y-2">
              <h4 className="text-xs font-bold text-indigo-950 flex items-center gap-1.5">
                <Lightbulb className="w-3.5 h-3.5 text-indigo-600" />
                {t.complementaryTitle}
              </h4>
              {m.complementary_suggestions.map((cb) => (
                <div key={cb.business_code} className="p-2.5 bg-white rounded-xl border border-indigo-100 text-xs">
                  <span className="font-bold text-slate-900 block">{mr ? cb.name_mr : cb.name_en}</span>
                  <span className="text-[11px] text-slate-600">
                    {mr ? "आवश्यक बाजार हिस्सा" : "Break-even market share"}: {Number(cb.be_market_share).toFixed(1)}% · {cb.saturation_level}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* VIABILITY */}
      {activeTab === "viability" && (
        <div className="space-y-3">
          {v.income_timing_mismatch && (
            <div className="p-3.5 bg-amber-50 border-2 border-amber-400 rounded-2xl flex items-start gap-2.5 text-xs text-amber-950">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block text-sm">{t.incomeTimingWarningTitle}</span>
                <span className="text-[11px]">
                  {mr ? "राखीव निधी ठेवा" : "Keep a reserve of"}: <strong>{inr(v.recommended_reserve)}</strong>
                </span>
              </div>
            </div>
          )}
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900">{t.viabilityCardTitle}</h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <Stat label={t.dscrLabel} value={v.average_dscr ? `${v.average_dscr}x` : "—"}
                hint={`${mr ? "लक्ष्य" : "target"} ≥ ${v.dscr_target}x${v.average_dscr ? "" : mr ? " · कर्ज योजना नाही" : " · no loan package"}`} />
              <Stat label={t.bepLabel} value={`${Number(s.breakeven_capacity_pct).toFixed(0)}%`} />
              <Stat label={t.nayakWorkingCapitalLabel} value={inr(s.nayak_working_capital.total)}
                hint={`${mr ? "स्वतः" : "own"} ${inr(s.nayak_working_capital.promoter_margin_5)}`} />
              <Stat label="FOIR" value={v.foir_pct ? `${Number(v.foir_pct).toFixed(0)}%` : "—"}
                hint={v.foir_passed ? "≤ 50% ✓" : "> 50%"} />
            </div>

            <div className="p-3.5 bg-amber-50/70 border border-amber-200 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="udhar-r" className="text-xs font-bold text-amber-950 flex items-center gap-1">
                  <Sliders className="w-3.5 h-3.5 text-amber-700" />
                  {t.udharSliderLabel}
                </label>
                <span className="text-xs font-black text-amber-900 bg-amber-200 px-2 py-0.5 rounded">{udharPct}%</span>
              </div>
              <input
                id="udhar-r"
                type="range"
                min={0}
                max={50}
                step={5}
                value={udharPct}
                disabled={recalcBusy}
                onChange={(e) => setUdharPct(parseInt(e.target.value) || 0)}
                onMouseUp={() => recalc(udharPct)}
                onTouchEnd={() => recalc(udharPct)}
                onKeyUp={() => recalc(udharPct)}
                className="w-full h-2 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />
              <div className="flex items-center justify-between text-[11px] text-amber-900">
                <span>
                  {mr ? "अडकलेले खेळते भांडवल" : "Extra working capital"}: {inr(s.udhar_stress.extra_wc_needed)}
                </span>
                {recalcBusy && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
              </div>
              {recalcError && <div className="text-[11px] text-red-700">{recalcError}</div>}
            </div>
            {v.warnings.length > 0 && <Warnings items={v.warnings} />}
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2">
            <h4 className="text-xs font-bold text-slate-900">{t.projections5yrTitle}</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-100 text-[10px] uppercase text-slate-600">
                  <tr>
                    <th className="py-1.5 px-2">{t.yearCol}</th>
                    <th className="py-1.5 px-2 text-right">{t.revenueCol}</th>
                    <th className="py-1.5 px-2 text-right">{mr ? "रोख नफा" : "Cash accrual"}</th>
                    <th className="py-1.5 px-2 text-right">{mr ? "कर्ज फेड" : "Debt service"}</th>
                    <th className="py-1.5 px-2 text-right">DSCR</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {v.projections.map((row) => (
                    <tr key={row.year}>
                      <td className="py-1.5 px-2 font-bold text-slate-700">{row.year}</td>
                      <td className="py-1.5 px-2 text-right">{inr(row.gross_revenue)}</td>
                      <td className="py-1.5 px-2 text-right text-emerald-700 font-bold">{inr(row.cash_accrual)}</td>
                      <td className="py-1.5 px-2 text-right">{inr(row.debt_service)}</td>
                      <td className="py-1.5 px-2 text-right">{row.dscr ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-[10px] text-slate-500">
              {mr ? "स्थानिक/मानक आकडे" : "Local vs default inputs"}:{" "}
              {Object.entries(v.inputs_used)
                .map(([k, src]) => `${humanize(k)}=${src === "local" ? (mr ? "स्थानिक" : "local") : mr ? "मानक" : "default"}`)
                .join(", ")}
            </p>
          </div>
        </div>
      )}

      {/* ADVISORY */}
      {activeTab === "advisory" && (
        <div className="space-y-3">
          {!advisory && (
            <div className="p-4 bg-white rounded-2xl border border-slate-200 text-xs space-y-2">
              <p className="text-slate-600">
                {mr
                  ? "सल्ला केवळ वरील गणलेल्या आकड्यांवर आधारित तयार होतो. आकडे तपासले जातात."
                  : "Advice is written only from the numbers above, and every number is checked."}
              </p>
              <button
                type="button"
                onClick={loadAdvisory}
                disabled={advisoryBusy || !caseRecord.evaluation_id}
                className="w-full py-3 rounded-xl bg-indigo-600 text-white font-bold min-h-[48px] disabled:bg-slate-300"
              >
                {advisoryBusy ? t.loading : mr ? "सल्ला तयार करा" : "Generate advice"}
              </button>
              {advisoryError && <div className="text-red-700">{advisoryError}</div>}
            </div>
          )}
          {advisory && (
            <>
              {advisoryMeta && (
                <div className="text-[10px] text-slate-500 px-1">
                  {advisoryMeta.model === "template_fallback"
                    ? mr ? "साचा आधारित सल्ला (AI उपलब्ध नाही)" : "Template advice (AI unavailable)"
                    : `AI · ${mr ? "आकडे तपासले" : "numbers checked"} ${advisoryMeta.validator_passed ? "✓" : "✗"}`}
                </div>
              )}
              <Card title={t.marketReachTitle}><p className="text-xs text-slate-700">{advisory.market_reach}</p></Card>
              {advisory.opportunities?.length > 0 && (
                <Card title={t.opportunitiesTitle}><Bullets items={advisory.opportunities} /></Card>
              )}
              {advisory.swot && (
                <Card title="SWOT">
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div><strong>{t.swotStrengths}</strong><Bullets items={advisory.swot.s} /></div>
                    <div><strong>{t.swotWeaknesses}</strong><Bullets items={advisory.swot.w} /></div>
                    <div><strong>{t.swotOpportunities}</strong><Bullets items={advisory.swot.o} /></div>
                    <div><strong>{t.swotThreats}</strong><Bullets items={advisory.swot.t} /></div>
                  </div>
                </Card>
              )}
              {advisory.threats?.length > 0 && (
                <Card title={mr ? "धोके व उपाय" : "Risks & mitigations"}>
                  {advisory.threats.map((th, i) => (
                    <div key={i} className="text-[11px] text-slate-700">
                      <strong>{th.risk}</strong> → {th.mitigation}
                    </div>
                  ))}
                </Card>
              )}
              {advisory.pricing && (
                <Card title={t.pricingTitle}>
                  <p className="text-xs text-slate-700">{advisory.pricing.strategy}</p>
                  {advisory.pricing.items?.map((it, i) => (
                    <div key={i} className="text-[11px] text-slate-600">
                      {it.item}: {it.benchmark_price} {it.unit} — {it.rationale}
                    </div>
                  ))}
                </Card>
              )}
              {advisory.next_steps?.length > 0 && (
                <Card title={mr ? "पुढील पावले" : "Next steps"}><Bullets items={advisory.next_steps} /></Card>
              )}
            </>
          )}
        </div>
      )}

      <div className="pt-2">
        <button
          type="button"
          onClick={onGoToDpr}
          disabled={!best}
          className="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold text-xs shadow-md flex items-center justify-center gap-2 min-h-[48px]"
        >
          <FileCheck className="w-4 h-4" />
          <span>{mr ? "बँकेसाठी डीपीआर (PDF) तयार करा →" : "Create bank DPR (PDF) →"}</span>
        </button>
      </div>

      <AmortizationModal pkg={schedulePkg} isOpen={Boolean(schedulePkg)} onClose={() => setSchedulePkg(null)} lang={lang} />
    </div>
  );
};

const PackageCard: React.FC<{ pkg: SchemePackage; idx: number; lang: Language; onSchedule: () => void }> = ({
  pkg,
  idx,
  lang,
  onSchedule,
}) => {
  const t = translations[lang];
  const mr = lang === "mr";
  const indicative = pkg.indicative_fields.includes("interest");
  return (
    <div
      className={`p-4 rounded-2xl border space-y-3 ${
        idx === 0 ? "bg-emerald-50/70 border-emerald-400 ring-1 ring-emerald-400" : "bg-white border-slate-200"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded ${idx === 0 ? "bg-emerald-600 text-white" : "bg-slate-200 text-slate-700"}`}>
            #{idx + 1}
          </span>
          <h4 className="text-xs font-bold text-slate-900 leading-tight mt-1">{schemeName(pkg, lang)}</h4>
          <span className="text-[10px] text-slate-500 block">{pkg.agency}</span>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-slate-500 block">{mr ? "हप्ता" : "EMI"}</span>
          <span className="text-sm font-black text-emerald-800">{inr(pkg.emi)}</span>
          <span className="text-[10px] text-slate-500 block">{emiLabel(pkg.emi_frequency_months, lang)}</span>
          {pkg.emi_after_subsidy_adjustment && (
            <span className="text-[10px] text-emerald-700 block">
              {mr ? "३ वर्षांनंतर" : "after 3 yrs"}: {inr(pkg.emi_after_subsidy_adjustment)}
            </span>
          )}
        </div>
      </div>

      {!pkg.is_affordable && (
        <div className="p-2 rounded-lg bg-red-50 border border-red-200 text-[11px] text-red-800">
          {mr ? "स्वतःचे पैसे कमी" : "Own money short by"}: <strong>{inr(pkg.margin_shortfall)}</strong>
          {pkg.affordable_alternative && (
            <>
              {" · "}
              {mr ? "शक्य प्रकल्प" : "Affordable project"}: <strong>{inr(pkg.affordable_alternative.project_cost)}</strong>
            </>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 bg-white/80 p-2.5 rounded-xl border border-slate-200/80 text-xs">
        <MiniStat label={mr ? "प्रकल्प खर्च" : "Project cost"} value={inr(pkg.project_cost)} />
        <MiniStat label={mr ? "स्वतःचे पैसे" : "Own money"} value={`${inr(pkg.own_margin_required)} (${Number(pkg.own_share_pct).toFixed(0)}%)`} />
        <MiniStat label={mr ? "कर्ज" : "Loan"} value={inr(pkg.loan_amount)} />
        <MiniStat
          label={mr ? "अनुदान" : "Subsidy"}
          value={`${inr(pkg.subsidy_amount)}${Number(pkg.subsidy_rate_pct) > 0 ? ` (${Number(pkg.subsidy_rate_pct).toFixed(0)}%)` : ""}`}
        />
        <MiniStat label={mr ? "व्याज दर" : "Interest"} value={`${Number(pkg.annual_rate_pct).toFixed(2)}%${indicative ? "*" : ""}`} />
        <MiniStat label={mr ? "एकूण परतफेड" : "Total repaid"} value={inr(pkg.total_repayment)} />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-1 text-[11px] text-slate-600 px-1">
        <span>{mr ? "मुदत" : "Tenure"}: <strong>{pkg.tenure_months} {mr ? "महिने" : "months"}</strong></span>
        <span>{mr ? "मोरेटोरियम" : "Moratorium"}: <strong>{pkg.moratorium_months} {mr ? "महिने" : "months"}</strong></span>
        {pkg.subsidy_treatment === "fdr_3yr" && (
          <span className="text-emerald-700">{mr ? "अनुदान ३ वर्ष FDR मध्ये" : "Subsidy held in FDR for 3 yrs"}</span>
        )}
      </div>

      {indicative && (
        <p className="text-[10px] text-slate-500 px-1">
          * {mr ? "व्याज दर बँक ठरवते; दाखवलेला दर अंदाजित." : "Interest rate is set by the bank; shown rate is indicative."}
        </p>
      )}
      {pkg.notes.map((note, i) => (
        <p key={i} className="text-[10px] text-slate-600 px-1">• {note}</p>
      ))}
      {pkg.warnings.length > 0 && <Warnings items={pkg.warnings} />}

      <div className="flex items-center justify-between pt-1 border-t border-slate-200/60">
        <button type="button" onClick={onSchedule} className="text-xs font-bold text-indigo-700 flex items-center gap-1 min-h-[40px]">
          <FileText className="w-3.5 h-3.5" />
          {t.viewScheduleBtn}
        </button>
        <a href={pkg.source_url} target="_blank" rel="noreferrer" className="text-[10px] text-slate-500 underline">
          {mr ? "स्रोत" : "Source"} ({pkg.source_date})
        </a>
      </div>
      <p className="text-[10px] text-slate-500 px-1">
        {mr ? "अर्ज कुठे" : "Apply at"}: {pkg.apply_at}
      </p>
    </div>
  );
};

const Stat: React.FC<{ label: string; value: string; hint?: string }> = ({ label, value, hint }) => (
  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
    <span className="text-[10px] text-slate-500 block">{label}</span>
    <span className="text-base font-black text-slate-900">{value}</span>
    {hint && <span className="text-[9px] text-slate-500 block mt-0.5">{hint}</span>}
  </div>
);

const MiniStat: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div>
    <span className="text-[10px] text-slate-500 block">{label}</span>
    <span className="font-bold text-slate-900">{value}</span>
  </div>
);

const Warnings: React.FC<{ items: string[] }> = ({ items }) => (
  <ul className="space-y-1">
    {items.map((w, i) => (
      <li key={i} className="text-[11px] text-amber-900 bg-amber-50 border border-amber-200 rounded-lg p-2 flex gap-1.5">
        <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
        <span>{w}</span>
      </li>
    ))}
  </ul>
);

const Card: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-1.5">
    <h4 className="text-xs font-bold text-slate-900">{title}</h4>
    {children}
  </div>
);

const Bullets: React.FC<{ items: string[] }> = ({ items }) => (
  <ul className="space-y-0.5 text-[11px] text-slate-700">
    {items.map((x, i) => (
      <li key={i}>• {x}</li>
    ))}
  </ul>
);
