import React, { useState } from "react";
import { Sparkles } from "lucide-react";
import { BusinessType, CalibrationData, Language } from "../types";
import { translations } from "../i18n";

interface Props {
  business: BusinessType;
  initialCalibration?: Partial<CalibrationData>;
  onEvaluate: (calibration: CalibrationData) => void;
  onBack: () => void;
  lang: Language;
}

export const CalibrationScreen: React.FC<Props> = ({
  business,
  initialCalibration,
  onEvaluate,
  onBack,
  lang,
}) => {
  const t = translations[lang];

  const [competitors, setCompetitors] = useState<number>(
    initialCalibration?.competitor_count !== undefined
      ? initialCalibration.competitor_count
      : 3
  );
  const [dailyCustomers, setDailyCustomers] = useState<number>(
    initialCalibration?.daily_volume_or_customers || 40
  );
  const [rent, setRent] = useState<number>(
    initialCalibration?.rent_monthly !== undefined
      ? initialCalibration.rent_monthly
      : 2000
  );
  const [ownPremises, setOwnPremises] = useState<boolean>(
    initialCalibration?.own_premises || false
  );
  const [milkRate, setMilkRate] = useState<number>(
    initialCalibration?.unit_price_or_rate || 38
  );
  const [animalsCount] = useState<number>(
    initialCalibration?.special_asset_count || 2
  );
  const [fodderAvailable, setFodderAvailable] = useState<boolean>(true);
  const [udharPct, setUdharPct] = useState<number>(
    initialCalibration?.udhar_pct !== undefined ? initialCalibration.udhar_pct : 15
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onEvaluate({
      competitor_count: competitors,
      daily_volume_or_customers: dailyCustomers,
      rent_monthly: ownPremises ? 0 : rent,
      own_premises: ownPremises,
      unit_price_or_rate: business.code === "dairy" ? milkRate : undefined,
      special_asset_count:
        business.code === "dairy" || business.code === "goat"
          ? animalsCount
          : undefined,
      fodder_available: fodderAvailable,
      udhar_pct: udharPct,
    });
  };

  return (
    <div className="p-4 space-y-4">
      {/* Step Header */}
      <div>
        <span className="text-[10px] uppercase font-bold text-emerald-700 tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          पायरी ५ / ५ · स्थानिक बाजार कॅलिब्रेशन
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1">
          {t.calibrationTitle}
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          {lang === "mr" ? business.name_mr : business.name_en} —{" "}
          {t.calibrationSubtitle}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Competitor Count */}
        <div className="p-3.5 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-start justify-between gap-2">
            <label className="text-xs font-bold text-slate-800">
              {t.competitorsNearLabel}
            </label>
            <span className="text-xs font-black px-2 py-0.5 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
              {competitors} दुकाने / स्पर्धक
            </span>
          </div>

          <div className="grid grid-cols-5 gap-2 pt-1">
            {[0, 1, 2, 3, 5, 8, 12].slice(0, 5).map((num) => (
              <button
                key={num}
                type="button"
                onClick={() => setCompetitors(num)}
                className={`py-2 px-1 rounded-xl text-xs font-bold border transition min-h-[44px] ${
                  competitors === num
                    ? "bg-indigo-600 text-white border-indigo-700 shadow-xs"
                    : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
                }`}
              >
                {num}
              </button>
            ))}
          </div>
          <span className="text-[10px] text-slate-400 block">
            * बँक सखीने स्थानिक पाहणीनुसार नोंदवलेली खरी संख्या.
          </span>
        </div>

        {/* Business-Specific Questions */}
        {business.code === "dairy" ? (
          <div className="p-3.5 bg-blue-50/60 rounded-2xl border border-blue-200 space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                {t.milkRateLabel}
              </label>
              <input
                type="number"
                min={25}
                max={60}
                value={milkRate}
                onChange={(e) => setMilkRate(parseInt(e.target.value) || 38)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-bold text-slate-900 bg-white min-h-[44px]"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                {t.fodderAvailableLabel}
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setFodderAvailable(true)}
                  className={`flex-1 py-2 px-2 rounded-xl text-xs font-bold border min-h-[44px] ${
                    fodderAvailable
                      ? "bg-blue-600 text-white border-blue-700"
                      : "bg-white text-slate-700 border-slate-300"
                  }`}
                >
                  {t.yes}
                </button>
                <button
                  type="button"
                  onClick={() => setFodderAvailable(false)}
                  className={`flex-1 py-2 px-2 rounded-xl text-xs font-bold border min-h-[44px] ${
                    !fodderAvailable
                      ? "bg-white text-slate-900 border-slate-400 shadow-2xs"
                      : "bg-white text-slate-700 border-slate-300"
                  }`}
                >
                  {t.no}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-3.5 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                {t.dailyCustomersLabel}
              </label>
              <input
                type="number"
                min={5}
                max={500}
                value={dailyCustomers}
                onChange={(e) => setDailyCustomers(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-slate-900 min-h-[48px]"
                required
              />
            </div>

            {/* Own premises & Rent */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-bold text-slate-800">
                  {t.ownPremisesLabel}
                </label>
                <button
                  type="button"
                  onClick={() => setOwnPremises(!ownPremises)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold border transition ${
                    ownPremises
                      ? "bg-emerald-600 text-white border-emerald-700"
                      : "bg-slate-100 text-slate-700 border-slate-300"
                  }`}
                >
                  {ownPremises ? t.yes : t.no}
                </button>
              </div>

              {!ownPremises && (
                <div className="pt-2">
                  <label className="block text-xs font-medium text-slate-600 mb-1">
                    {t.monthlyRentLabel}
                  </label>
                  <input
                    type="number"
                    step={500}
                    value={rent}
                    onChange={(e) => setRent(parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs font-semibold text-slate-900 min-h-[44px]"
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Initial Udhar Stress Calibration */}
        <div className="p-3.5 bg-amber-50/60 rounded-2xl border border-amber-200 space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-amber-950">
              {t.udharSliderLabel}
            </label>
            <span className="text-xs font-black text-amber-800 bg-amber-100 px-2 py-0.5 rounded-md border border-amber-300">
              {udharPct}%
            </span>
          </div>

          <input
            type="range"
            min={0}
            max={50}
            step={5}
            value={udharPct}
            onChange={(e) => setUdharPct(parseInt(e.target.value) || 0)}
            className="w-full h-2 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />

          <span className="text-[10px] text-amber-800 block leading-tight">
            * ग्रामीण भागात सरासरी १०% ते २५% विक्री उधारीवर चालते.
          </span>
        </div>

        {/* Buttons */}
        <div className="pt-2 flex items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="flex-1 py-3 px-4 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition min-h-[48px]"
          >
            {t.back}
          </button>
          <button
            type="submit"
            className="flex-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition min-h-[48px] flex items-center justify-center gap-1.5"
          >
            <Sparkles className="w-4 h-4" />
            {t.calculateViabilityBtn}
          </button>
        </div>
      </form>
    </div>
  );
};
