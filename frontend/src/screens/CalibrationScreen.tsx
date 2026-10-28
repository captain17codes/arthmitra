import React, { useEffect, useState } from "react";
import { Info } from "lucide-react";
import { BusinessParameters, BusinessType, CalibrationData, Language } from "../types";
import { translations } from "../i18n";
import { api } from "../services/api";
import { VoiceFieldInput } from "../components/VoiceFieldInput";

interface Props {
  business: BusinessType;
  initialCalibration?: CalibrationData;
  onEvaluate: (calibration: CalibrationData) => void;
  onBack: () => void;
  lang: Language;
  busy?: boolean;
  error?: string;
}

/**
 * The 3 local numbers per business that move the result the most.
 * Keys are the benchmark parameter names the backend viability engine reads,
 * so whatever the agent enters overrides the default directly.
 */
const LOCAL_QUESTIONS: Record<string, Array<{ key: string; mr: string; en: string }>> = {
  kirana: [
    { key: "daily_customers", mr: "रोज किती ग्राहक येतील?", en: "Customers per day" },
    { key: "average_bill_inr", mr: "एका ग्राहकाचे सरासरी बिल (₹)", en: "Average bill per customer (₹)" },
    { key: "shop_rent_monthly", mr: "दुकान भाडे दरमहा (₹)", en: "Shop rent per month (₹)" },
  ],
  dairy: [
    { key: "num_animals", mr: "जनावरांची संख्या", en: "Number of animals" },
    { key: "daily_milk_yield_litres", mr: "प्रति जनावर रोज दूध (लिटर)", en: "Milk per animal per day (L)" },
    { key: "milk_procurement_price", mr: "दूध संकलन केंद्राचा दर (₹/लिटर)", en: "Collection centre milk rate (₹/L)" },
  ],
  goatery: [
    { key: "num_does", mr: "शेळ्यांची संख्या", en: "Number of does" },
    { key: "average_kid_sale_price", mr: "एका करडाची विक्री किंमत (₹)", en: "Sale price per kid (₹)" },
    { key: "kid_mortality_rate", mr: "करडे मरण्याचे प्रमाण (0–1)", en: "Kid mortality rate (0–1)" },
  ],
  broiler: [
    { key: "batch_size", mr: "एका बॅचमध्ये पक्षी", en: "Birds per batch" },
    { key: "batches_per_year", mr: "वर्षाला बॅच", en: "Batches per year" },
    { key: "live_bird_price_per_kg", mr: "जिवंत पक्षी दर (₹/किलो)", en: "Live bird price (₹/kg)" },
  ],
  tailoring: [
    { key: "jobs_per_day", mr: "रोज किती कपडे शिवाल?", en: "Jobs per day" },
    { key: "average_stitching_fee", mr: "सरासरी शिलाई (₹)", en: "Average stitching fee (₹)" },
    { key: "shop_rent_monthly", mr: "दुकान भाडे दरमहा (₹)", en: "Shop rent per month (₹)" },
  ],
  beauty_parlour: [
    { key: "daily_clients", mr: "रोज किती ग्राहक?", en: "Clients per day" },
    { key: "average_ticket_inr", mr: "एका ग्राहकाचे सरासरी बिल (₹)", en: "Average bill per client (₹)" },
    { key: "rent_monthly", mr: "भाडे दरमहा (₹)", en: "Rent per month (₹)" },
  ],
  mobile_repair: [
    { key: "daily_repairs", mr: "रोज किती दुरुस्त्या?", en: "Repairs per day" },
    { key: "average_repair_margin", mr: "एका दुरुस्तीवर नफा (₹)", en: "Margin per repair (₹)" },
    { key: "rent_monthly", mr: "भाडे दरमहा (₹)", en: "Rent per month (₹)" },
  ],
  two_wheeler_repair: [
    { key: "daily_vehicles_serviced", mr: "रोज किती गाड्या?", en: "Vehicles serviced per day" },
    { key: "average_labour_charge_per_bike", mr: "प्रति गाडी मजुरी (₹)", en: "Labour charge per bike (₹)" },
    { key: "rent_monthly", mr: "भाडे दरमहा (₹)", en: "Rent per month (₹)" },
  ],
  flour_mill: [
    { key: "daily_flour_milling_kg", mr: "रोज दळण (किलो)", en: "Flour milled per day (kg)" },
    { key: "milling_rate_per_kg", mr: "दळणाचा दर (₹/किलो)", en: "Milling rate (₹/kg)" },
    { key: "rent_monthly", mr: "भाडे दरमहा (₹)", en: "Rent per month (₹)" },
  ],
  papad_pickle: [
    { key: "daily_production_kg", mr: "रोज उत्पादन (किलो)", en: "Production per day (kg)" },
    { key: "average_selling_price_per_kg", mr: "विक्री दर (₹/किलो)", en: "Selling price (₹/kg)" },
    { key: "rent_and_power_monthly", mr: "भाडे व वीज दरमहा (₹)", en: "Rent + power per month (₹)" },
  ],
};

export const CalibrationScreen: React.FC<Props> = ({
  business,
  initialCalibration,
  onEvaluate,
  onBack,
  lang,
  busy = false,
  error,
}) => {
  const t = translations[lang];
  const mr = lang === "mr";
  const [params, setParams] = useState<BusinessParameters | null>(null);
  const [paramsError, setParamsError] = useState<string>("");
  const [values, setValues] = useState<Record<string, string>>({});
  const [competitors, setCompetitors] = useState<string>(
    initialCalibration?.competitor_count !== undefined ? String(initialCalibration.competitor_count) : ""
  );
  const [udharPct, setUdharPct] = useState<number>(
    initialCalibration?.udhar_pct !== undefined ? Math.round(Number(initialCalibration.udhar_pct) * 100) : 20
  );

  const questions = LOCAL_QUESTIONS[business.code] || [];

  useEffect(() => {
    api
      .getBusinessParameters(business.code)
      .then((p) => {
        setParams(p);
        const all = { ...p.revenue_parameters, ...p.cost_parameters };
        const init: Record<string, string> = {};
        for (const q of questions) {
          const fromCase = initialCalibration?.[q.key];
          init[q.key] = fromCase !== undefined ? String(fromCase) : all[q.key] ? String(all[q.key].value) : "";
        }
        setValues(init);
      })
      .catch((e: Error) => setParamsError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [business.code]);

  const defaults = params ? { ...params.revenue_parameters, ...params.cost_parameters } : {};

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const calib: CalibrationData = { udhar_pct: (udharPct / 100).toFixed(2) };
    if (competitors !== "") calib.competitor_count = Number(competitors);
    for (const q of questions) {
      const v = values[q.key];
      // Only send values the agent changed: unchanged values stay marked as "default" in the DPR.
      if (v !== undefined && v !== "" && defaults[q.key] && Number(v) !== Number(defaults[q.key].value)) {
        calib[q.key] = Number(v);
      }
    }
    onEvaluate(calib);
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <span className="text-[10px] uppercase font-bold text-emerald-700 tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          {mr ? "पायरी ५ / ५ · स्थानिक तपासणी" : "Step 5 / 5 · Local check"}
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1">{t.calibrationTitle}</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          {mr ? business.name_mr : business.name_en} — {t.calibrationSubtitle}
        </p>
      </div>

      {paramsError && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800">{paramsError}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-3.5 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2">
          <label htmlFor="competitors" className="text-xs font-bold text-slate-800 block">
            {t.competitorsNearLabel}
          </label>
          <div className="grid grid-cols-6 gap-2">
            {[0, 1, 2, 3, 5, 8].map((num) => (
              <button
                key={num}
                type="button"
                onClick={() => setCompetitors(String(num))}
                className={`py-2 rounded-xl text-xs font-bold border transition min-h-[44px] ${
                  competitors === String(num)
                    ? "bg-indigo-600 text-white border-indigo-700"
                    : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
                }`}
              >
                {num}
              </button>
            ))}
          </div>
          <input
            id="competitors"
            type="number"
            inputMode="numeric"
            min={0}
            value={competitors}
            onChange={(e) => setCompetitors(e.target.value)}
            placeholder={mr ? "किंवा संख्या टाका" : "or type a number"}
            className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-bold min-h-[44px]"
          />
          <span className="text-[10px] text-slate-500 block">
            {mr
              ? "स्थानिक पाहणीतील खरी संख्या. रिकामे ठेवल्यास बाजार स्पर्धा 'माहिती अपूर्ण' दाखवली जाईल."
              : "Count from the local visit. If left blank, market competition shows as 'needs info'."}
          </span>
        </div>

        <div className="p-3.5 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
          {!params && !paramsError && <div className="text-xs text-slate-500">{t.loading}</div>}
          {params &&
            questions.map((q) => {
              const d = defaults[q.key];
              return (
                <div key={q.key}>
                  <VoiceFieldInput
                    label={mr ? q.mr : q.en}
                    type="number"
                    value={values[q.key] ?? ""}
                    onChange={(val) => setValues((prev) => ({ ...prev, [q.key]: String(val) }))}
                    language={lang}
                  />
                  {d && (
                    <p className="text-[10px] text-slate-500 mt-0.5 flex items-center gap-1">
                      <Info className="w-3 h-3" />
                      {mr ? "मानक" : "Default"}: {d.value} {d.unit || ""} · {d.confidence || "estimate"}
                      {d.source_title ? ` · ${d.source_title}` : ""}
                    </p>
                  )}
                </div>
              );
            })}
        </div>

        <div className="p-3.5 bg-amber-50/70 rounded-2xl border border-amber-200 space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="udhar" className="text-xs font-bold text-amber-950">
              {t.udharSliderLabel}
            </label>
            <span className="text-xs font-black text-amber-900 bg-amber-200 px-2 py-0.5 rounded">{udharPct}%</span>
          </div>
          <input
            id="udhar"
            type="range"
            min={0}
            max={50}
            step={5}
            value={udharPct}
            onChange={(e) => setUdharPct(parseInt(e.target.value) || 0)}
            className="w-full h-2 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>

        {error && <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800">{error}</div>}

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            disabled={busy}
            className="flex-1 py-3 px-4 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition min-h-[48px]"
          >
            {t.back}
          </button>
          <button
            type="submit"
            disabled={busy || !params}
            className="flex-[2] py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold text-xs shadow-sm transition min-h-[48px]"
          >
            {busy ? (mr ? "गणना सुरू आहे…" : "Calculating…") : mr ? "मूल्यांकन करा →" : "Evaluate →"}
          </button>
        </div>
      </form>
    </div>
  );
};
