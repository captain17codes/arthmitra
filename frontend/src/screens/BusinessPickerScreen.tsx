import React, { useEffect, useState } from "react";
import {
  Briefcase,
  CheckCircle2,
  Coins,
  Cpu,
  Egg,
  Flame,
  Milk,
  Scissors,
  Smartphone,
  Sparkles,
  Store,
  UtensilsCrossed,
  Wrench,
} from "lucide-react";
import { BusinessType, Language } from "../types";
import { formatINR, translations } from "../i18n";
import { api } from "../services/api";

interface Props {
  selectedBusinessCode?: string;
  initialProjectCost?: number | null;
  initialMargin?: number;
  onConfirmBusiness: (business: BusinessType, cost: number | null, margin: number) => void;
  onBack: () => void;
  lang: Language;
}

const ICONS: Record<string, React.ReactNode> = {
  kirana: <Store className="w-5 h-5 text-emerald-600" />,
  dairy: <Milk className="w-5 h-5 text-blue-600" />,
  goatery: <Flame className="w-5 h-5 text-amber-600" />,
  broiler: <Egg className="w-5 h-5 text-red-600" />,
  tailoring: <Scissors className="w-5 h-5 text-purple-600" />,
  beauty_parlour: <Sparkles className="w-5 h-5 text-pink-600" />,
  mobile_repair: <Smartphone className="w-5 h-5 text-sky-600" />,
  two_wheeler_repair: <Wrench className="w-5 h-5 text-orange-600" />,
  flour_mill: <Cpu className="w-5 h-5 text-teal-600" />,
  papad_pickle: <UtensilsCrossed className="w-5 h-5 text-rose-600" />,
};

export const BusinessPickerScreen: React.FC<Props> = ({
  selectedBusinessCode,
  initialProjectCost,
  initialMargin,
  onConfirmBusiness,
  onBack,
  lang,
}) => {
  const t = translations[lang];
  const mr = lang === "mr";
  const [businesses, setBusinesses] = useState<BusinessType[]>([]);
  const [loadError, setLoadError] = useState<string>("");
  const [selectedCode, setSelectedCode] = useState<string | undefined>(selectedBusinessCode);
  const [useTarget, setUseTarget] = useState<boolean>(Boolean(initialProjectCost));
  const [targetCost, setTargetCost] = useState<string>(initialProjectCost ? String(initialProjectCost) : "");
  const [margin, setMargin] = useState<string>(initialMargin !== undefined ? String(initialMargin) : "");

  useEffect(() => {
    api
      .getBusinesses()
      .then((list) => {
        setBusinesses(list);
        if (!selectedCode && list.length) setSelectedCode(list[0].code);
      })
      .catch((e: Error) => setLoadError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const current = businesses.find((b) => b.code === selectedCode);
  const range = current?.viable_range;
  const marginNum = Number(margin);
  const targetNum = Number(targetCost);
  const canSubmit =
    Boolean(current) && margin !== "" && marginNum >= 0 && (!useTarget || (targetCost !== "" && targetNum > 0));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!current || !canSubmit) return;
    onConfirmBusiness(current, useTarget ? targetNum : null, marginNum);
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <span className="text-[10px] uppercase font-bold text-indigo-700 tracking-wider bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
          {mr ? "पायरी ४ / ५ · व्यवसाय व भांडवल" : "Step 4 / 5 · Business & own money"}
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1">{t.businessPickerTitle}</h2>
        <p className="text-xs text-slate-500 mt-0.5">{t.selectBusinessHint}</p>
      </div>

      {loadError && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800">{loadError}</div>
      )}
      {!loadError && businesses.length === 0 && <div className="text-xs text-slate-500">{t.loading}</div>}

      <div className="grid grid-cols-2 gap-2.5 max-h-[42vh] overflow-y-auto pr-1">
        {businesses.map((b) => {
          const isSelected = selectedCode === b.code;
          return (
            <button
              type="button"
              key={b.code}
              onClick={() => setSelectedCode(b.code)}
              aria-pressed={isSelected}
              className={`p-3 rounded-2xl border transition text-left flex flex-col justify-between gap-1.5 min-h-[48px] ${
                isSelected
                  ? "bg-indigo-50/90 border-indigo-500 shadow-xs ring-1 ring-indigo-500"
                  : "bg-white border-slate-200 hover:border-slate-300"
              }`}
            >
              <div className="flex items-start justify-between gap-1">
                <div className="p-1.5 rounded-xl bg-white border border-slate-100 shadow-2xs">
                  {ICONS[b.code] || <Briefcase className="w-5 h-5 text-indigo-600" />}
                </div>
                {isSelected && <CheckCircle2 className="w-4 h-4 text-indigo-600" />}
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-900 leading-tight">{mr ? b.name_mr : b.name_en}</h3>
                <span className="text-[10px] text-slate-500 font-medium block mt-0.5">{b.sector}</span>
              </div>
              {b.viable_range && (
                <div className="text-[10px] font-bold text-emerald-800 pt-1 border-t border-slate-100">
                  {formatINR(b.viable_range.min)} – {formatINR(b.viable_range.max)}
                </div>
              )}
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSubmit} className="space-y-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
        <div>
          <label htmlFor="margin" className="block text-xs font-bold text-slate-700 mb-1">
            {t.marginAvailableLabel}
          </label>
          <input
            id="margin"
            type="number"
            inputMode="numeric"
            min={0}
            step={1000}
            value={margin}
            placeholder={mr ? "उदा. 10000" : "e.g. 10000"}
            onChange={(e) => setMargin(e.target.value)}
            className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-slate-900 min-h-[48px]"
            required
          />
          <p className="text-[10px] text-slate-500 mt-1">
            {mr
              ? "तुमच्याकडे प्रत्यक्ष असलेली रक्कम. प्रकल्प व कर्ज प्रत्येक योजनेनुसार गणले जाईल."
              : "Money you actually have in hand. Project and loan are sized per scheme by the engine."}
          </p>
        </div>

        <label className="flex items-center gap-2 text-xs font-semibold text-slate-700 cursor-pointer min-h-[44px]">
          <input
            type="checkbox"
            checked={useTarget}
            onChange={(e) => setUseTarget(e.target.checked)}
            className="w-5 h-5 rounded text-indigo-600"
          />
          {mr ? "ठरावीक प्रकल्प खर्च आधीच माहित आहे" : "A specific project cost is already planned"}
        </label>

        {useTarget && (
          <div>
            <label htmlFor="target" className="block text-xs font-bold text-slate-700 mb-1">
              {t.targetCostLabel}
            </label>
            <input
              id="target"
              type="number"
              inputMode="numeric"
              min={1}
              step={5000}
              value={targetCost}
              onChange={(e) => setTargetCost(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-slate-900 min-h-[48px]"
              required
            />
            {range && (
              <p className="text-[10px] text-slate-500 mt-1">
                {mr ? "या व्यवसायासाठी सामान्य गुंतवणूक" : "Typical investment for this business"}:{" "}
                {formatINR(range.min)} – {formatINR(range.max)}
              </p>
            )}
          </div>
        )}

        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center gap-2 text-[11px] text-slate-600">
          <Coins className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>
            {mr
              ? "कर्ज, अनुदान व हप्ता पुढील पायरीनंतर सर्व पात्र योजनांसाठी गणले जातील."
              : "Loan, subsidy and EMI are calculated for every eligible scheme after the next step."}
          </span>
        </div>

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
            disabled={!canSubmit}
            className="flex-[2] py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold text-xs shadow-sm transition min-h-[48px]"
          >
            {mr ? "स्थानिक तपासणी करा →" : "Local check →"}
          </button>
        </div>
      </form>
    </div>
  );
};
