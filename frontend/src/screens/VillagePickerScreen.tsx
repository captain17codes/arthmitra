import React, { useEffect, useState } from "react";
import { Check, MapPin, Search, Users } from "lucide-react";
import { Language, Village } from "../types";
import { formatNumberIN, translations } from "../i18n";
import { api } from "../services/api";

interface Props {
  selectedVillage?: Village;
  onSelectVillage: (village: Village) => void;
  onBack: () => void;
  lang: Language;
}

export const VillagePickerScreen: React.FC<Props> = ({
  selectedVillage,
  onSelectVillage,
  onBack,
  lang,
}) => {
  const t = translations[lang];
  const [query, setQuery] = useState("");
  const [villages, setVillages] = useState<Village[]>([]);
  const [loading, setLoading] = useState(false);
  const [chosen, setChosen] = useState<Village | undefined>(selectedVillage);

  useEffect(() => {
    let active = true;
    const fetchVillages = async () => {
      setLoading(true);
      try {
        const results = await api.searchVillages(query);
        if (active) {
          setVillages(results);
          if (!chosen && results.length > 0) {
            setChosen(results[0]);
          }
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchVillages();
    return () => {
      active = false;
    };
  }, [query]);

  const handleConfirm = () => {
    if (chosen) {
      onSelectVillage(chosen);
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Step Header */}
      <div>
        <span className="text-[10px] uppercase font-bold text-indigo-700 tracking-wider bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
          पायरी ३ / ५ · भौगोलिक स्थान
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1 flex items-center gap-1.5">
          <MapPin className="w-4 h-4 text-indigo-600" />
          {t.villagePickerTitle}
        </h2>
      </div>

      {/* Search Input */}
      <div className="relative">
        <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
          <Search className="w-4 h-4" />
        </span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t.searchVillagePlaceholder}
          className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-900 bg-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 min-h-[48px]"
        />
      </div>

      {/* Village Cards List */}
      <div className="space-y-2.5 max-h-[50vh] overflow-y-auto pr-1">
        {loading ? (
          <div className="p-6 text-center text-xs text-slate-500">
            {t.loading}
          </div>
        ) : villages.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-500 bg-white rounded-xl border border-dashed border-slate-200">
            गावे सापडली नाहीत. इतर नाव शोधून पहा.
          </div>
        ) : (
          villages.map((v) => {
            const isSelected = chosen?.id === v.id;
            return (
              <div
                key={v.id}
                onClick={() => setChosen(v)}
                className={`p-3.5 rounded-2xl border transition cursor-pointer flex items-center justify-between gap-3 ${
                  isSelected
                    ? "bg-indigo-50/80 border-indigo-500 shadow-xs"
                    : "bg-white border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-slate-900">
                      {lang === "mr" ? v.name_mr : v.name_en}
                    </h3>
                    <span className="text-[11px] text-slate-500 font-medium">
                      ({lang === "mr" ? v.name_en : v.name_mr})
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-600">
                    तालुका:{" "}
                    <strong>
                      {lang === "mr" ? v.subdistrict_mr : v.subdistrict_en}
                    </strong>{" "}
                    · जिल्हा:{" "}
                    <strong>
                      {lang === "mr" ? v.district_mr : v.district_en}
                    </strong>
                  </p>

                  <div className="flex items-center gap-3 text-[10px] text-slate-500 pt-0.5">
                    <span className="flex items-center gap-1 font-semibold text-emerald-800">
                      <Users className="w-3 h-3 text-emerald-600" />
                      {t.populationLabel}: {formatNumberIN(v.population)}
                    </span>
                    <span>LGD: {v.lgd_code}</span>
                  </div>
                </div>

                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 border ${
                    isSelected
                      ? "bg-indigo-600 border-indigo-600 text-white"
                      : "border-slate-300 bg-white"
                  }`}
                >
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                </div>
              </div>
            );
          })
        )}
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
          type="button"
          onClick={handleConfirm}
          disabled={!chosen}
          className="flex-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition min-h-[48px] disabled:opacity-50"
        >
          {t.selectVillageBtn} →
        </button>
      </div>
    </div>
  );
};
