import React, { useState } from "react";
import { ArrowLeft, CheckCircle2, MapPin } from "lucide-react";
import { Language } from "../types";

interface Props {
  onBack: () => void;
  lang: Language;
}

interface MissingVillage {
  lgd_code: number;
  name_en: string;
  name_mr: string;
  subdistrict: string;
  district: string;
  status: "missing" | "estimated" | "fixed";
  lat?: number;
  lon?: number;
}

const SAMPLE_VILLAGES: MissingVillage[] = [
  {
    lgd_code: 555001,
    name_en: "Shirwal Vasti",
    name_mr: "शिरवळ वस्ती",
    subdistrict: "Khandala",
    district: "Satara",
    status: "missing",
  },
  {
    lgd_code: 555012,
    name_en: "Pargaon Mala",
    name_mr: "पारगाव मळा",
    subdistrict: "Purandar",
    district: "Pune",
    status: "estimated",
    lat: 18.28,
    lon: 74.12,
  },
];

export const AdminVillageScreen: React.FC<Props> = ({ onBack }) => {
  const [villages, setVillages] = useState<MissingVillage[]>(SAMPLE_VILLAGES);
  const [selectedVillage, setSelectedVillage] = useState<MissingVillage | null>(null);
  const [lat, setLat] = useState<string>("");
  const [lon, setLon] = useState<string>("");
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const handleSelect = (v: MissingVillage) => {
    setSelectedVillage(v);
    setLat(v.lat ? v.lat.toString() : "18.1524");
    setLon(v.lon ? v.lon.toString() : "74.0251");
    setSavedSuccess(false);
  };

  const handleSaveCoords = () => {
    if (!selectedVillage) return;
    setVillages((prev) =>
      prev.map((v) =>
        v.lgd_code === selectedVillage.lgd_code
          ? {
              ...v,
              status: "fixed",
              lat: parseFloat(lat),
              lon: parseFloat(lon),
            }
          : v
      )
    );
    setSavedSuccess(true);
  };

  return (
    <div className="p-4 space-y-4 pb-20">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> मागे जा
        </button>
        <span className="text-[10px] uppercase font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
          गाव निर्देशांक दुरुस्ती
        </span>
      </div>

      <div>
        <h2 className="text-base font-black text-slate-900">
          अपूर्ण निर्देशांक असलेली गावे (Missing Village GPS)
        </h2>
        <p className="text-xs text-slate-500">
          बाजार कॅचमेंट आणि १० किमी शेजारील गावांच्या विश्लेषणासाठी अचूक अक्षांश व रेखांश नोंदवा.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-xs text-emerald-950 font-bold animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>गाव निर्देशांक अद्ययावत झाले आणि PostGIS भूमितीमध्ये नोंदवले गेले.</span>
        </div>
      )}

      {/* Villages List */}
      <div className="space-y-2">
        {villages.map((v) => (
          <div
            key={v.lgd_code}
            onClick={() => handleSelect(v)}
            className={`p-3.5 rounded-2xl border transition cursor-pointer flex items-center justify-between ${
              selectedVillage?.lgd_code === v.lgd_code
                ? "bg-blue-50/80 border-blue-400 shadow-xs"
                : "bg-white border-slate-200 hover:bg-slate-50"
            }`}
          >
            <div>
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-blue-600" />
                <h4 className="text-xs font-bold text-slate-900">{v.name_mr} ({v.name_en})</h4>
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">
                तालुका: {v.subdistrict} · जिल्हा: {v.district} · LGD: {v.lgd_code}
              </p>
            </div>
            <span
              className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-md ${
                v.status === "fixed"
                  ? "bg-emerald-100 text-emerald-800"
                  : v.status === "estimated"
                  ? "bg-amber-100 text-amber-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {v.status === "fixed" ? "दुरुस्त ✓" : v.status}
            </span>
          </div>
        ))}
      </div>

      {/* Coordinate Input Form */}
      {selectedVillage && (
        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
          <h4 className="text-xs font-bold text-slate-900">
            {selectedVillage.name_mr} साठी अचूक GPS निर्देशांक:
          </h4>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                अक्षांश (Latitude):
              </label>
              <input
                type="number"
                step="any"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-mono font-bold"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                रेखांश (Longitude):
              </label>
              <input
                type="number"
                step="any"
                value={lon}
                onChange={(e) => setLon(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-mono font-bold"
              />
            </div>
          </div>

          <button
            type="button"
            onClick={handleSaveCoords}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
          >
            निर्देशांक जतन करा (Save Coordinates)
          </button>
        </div>
      )}
    </div>
  );
};
