import React, { useState } from "react";
import {
  Briefcase,
  CheckCircle2,
  Coins,
  Cpu,
  Flame,
  Hammer,
  Milk,
  Scissors,
  ShoppingBag,
  Sparkles,
  Store,
  Truck,
  Wrench,
} from "lucide-react";
import { BusinessType, Language } from "../types";
import { formatINR, translations } from "../i18n";
import { MOCK_BUSINESS_TYPES } from "../services/mockData";

interface Props {
  selectedBusinessCode?: string;
  initialProjectCost?: number;
  initialMargin?: number;
  onConfirmBusiness: (
    business: BusinessType,
    cost: number,
    margin: number
  ) => void;
  onBack: () => void;
  lang: Language;
}

export const BusinessPickerScreen: React.FC<Props> = ({
  selectedBusinessCode = "kirana",
  initialProjectCost,
  initialMargin,
  onConfirmBusiness,
  onBack,
  lang,
}) => {
  const t = translations[lang];
  const businesses = MOCK_BUSINESS_TYPES;

  const [selectedCode, setSelectedCode] = useState(selectedBusinessCode);
  const currentBusiness =
    businesses.find((b) => b.code === selectedCode) || businesses[0];

  const [targetCost, setTargetCost] = useState<number>(
    initialProjectCost || currentBusiness.default_project_cost
  );
  const [marginAvailable, setMarginAvailable] = useState<number>(
    initialMargin || Math.round((initialProjectCost || currentBusiness.default_project_cost) * 0.1)
  );

  const handleSelectBusiness = (b: BusinessType) => {
    setSelectedCode(b.code);
    setTargetCost(b.default_project_cost);
    setMarginAvailable(Math.round(b.default_project_cost * 0.1));
  };

  const getBusinessIcon = (code: string) => {
    switch (code) {
      case "kirana":
        return <Store className="w-5 h-5 text-emerald-600" />;
      case "dairy":
        return <Milk className="w-5 h-5 text-blue-600" />;
      case "goat":
        return <Flame className="w-5 h-5 text-amber-600" />;
      case "tailoring":
        return <Scissors className="w-5 h-5 text-purple-600" />;
      case "beauty_parlour":
        return <Sparkles className="w-5 h-5 text-pink-600" />;
      case "two_wheeler_repair":
        return <Wrench className="w-5 h-5 text-orange-600" />;
      case "flour_mill":
        return <Cpu className="w-5 h-5 text-teal-600" />;
      case "vegetable_vending":
        return <Truck className="w-5 h-5 text-green-600" />;
      case "poultry_broiler":
        return <ShoppingBag className="w-5 h-5 text-red-600" />;
      case "welding_fabrication":
        return <Hammer className="w-5 h-5 text-slate-700" />;
      default:
        return <Briefcase className="w-5 h-5 text-indigo-600" />;
    }
  };

  const marginPct = Math.round((marginAvailable / (targetCost || 1)) * 100);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirmBusiness(currentBusiness, targetCost, marginAvailable);
  };

  return (
    <div className="p-4 space-y-4">
      {/* Step Header */}
      <div>
        <span className="text-[10px] uppercase font-bold text-indigo-700 tracking-wider bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
          पायरी ४ / ५ · व्यवसाय व भांडवल
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1">
          {t.businessPickerTitle}
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">{t.selectBusinessHint}</p>
      </div>

      {/* Business Cards Grid (10 Businesses) */}
      <div className="grid grid-cols-2 gap-2.5 max-h-[42vh] overflow-y-auto pr-1">
        {businesses.map((b) => {
          const isSelected = selectedCode === b.code;
          return (
            <div
              key={b.code}
              onClick={() => handleSelectBusiness(b)}
              className={`p-3 rounded-2xl border transition cursor-pointer flex flex-col justify-between gap-1.5 ${
                isSelected
                  ? "bg-indigo-50/90 border-indigo-500 shadow-xs ring-1 ring-indigo-500"
                  : "bg-white border-slate-200 hover:border-slate-300"
              }`}
            >
              <div className="flex items-start justify-between gap-1">
                <div className="p-1.5 rounded-xl bg-white border border-slate-100 shadow-2xs">
                  {getBusinessIcon(b.code)}
                </div>
                {isSelected && (
                  <CheckCircle2 className="w-4 h-4 text-indigo-600" />
                )}
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-900 leading-tight">
                  {lang === "mr" ? b.name_mr : b.name_en}
                </h3>
                <span className="text-[10px] text-slate-500 font-medium block mt-0.5">
                  {b.sector}
                </span>
              </div>

              <div className="text-[11px] font-extrabold text-emerald-800 pt-1 border-t border-slate-100">
                {formatINR(b.default_project_cost)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Financial Sizing Form */}
      <form onSubmit={handleSubmit} className="space-y-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">
            {t.targetCostLabel}
          </label>
          <input
            type="number"
            step={5000}
            min={20000}
            max={5000000}
            value={targetCost}
            onChange={(e) => {
              const val = parseInt(e.target.value) || 0;
              setTargetCost(val);
              setMarginAvailable(Math.round(val * 0.1));
            }}
            className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-slate-900 min-h-[48px]"
            required
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700">
              {t.marginAvailableLabel}
            </label>
            <span className="text-xs font-black text-indigo-600">
              {marginPct}% ({formatINR(marginAvailable)})
            </span>
          </div>

          <input
            type="range"
            min={Math.round(targetCost * 0.05)}
            max={Math.round(targetCost * 0.35)}
            step={1000}
            value={marginAvailable}
            onChange={(e) => setMarginAvailable(parseInt(e.target.value) || 0)}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />

          <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1">
            <span>किमान ५% ({formatINR(Math.round(targetCost * 0.05))})</span>
            <span>कमाल ३५% ({formatINR(Math.round(targetCost * 0.35))})</span>
          </div>
        </div>

        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center gap-2 text-[11px] text-slate-600">
          <Coins className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>
            कर्ज रक्कम: <strong>{formatINR(targetCost - marginAvailable)}</strong>{" "}
            (बँक वित्तपुरवठा: {100 - marginPct}%)
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
            className="flex-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition min-h-[48px]"
          >
            स्थानिक तपासणी करा →
          </button>
        </div>
      </form>
    </div>
  );
};
