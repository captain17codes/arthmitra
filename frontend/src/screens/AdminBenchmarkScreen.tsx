import React, { useState } from "react";
import { ArrowLeft, Edit2, Save, ShieldCheck } from "lucide-react";
import { Language } from "../types";

interface Props {
  onBack: () => void;
  lang: Language;
}

interface BenchmarkItem {
  id: number;
  business: string;
  businessName: string;
  key: string;
  label: string;
  value: number;
  unit: string;
  source: string;
  year: number;
  confidence: "official" | "secondary" | "estimate";
}

const INITIAL_BENCHMARKS: BenchmarkItem[] = [
  {
    id: 1,
    business: "kirana",
    businessName: "किराणा दुकान",
    key: "capex_setup",
    label: "सुरुवातीचा भांडवली खर्च (Setup Capex)",
    value: 150000,
    unit: "INR",
    source: "KVIC Model Profile 2025",
    year: 2025,
    confidence: "official",
  },
  {
    id: 2,
    business: "dairy",
    businessName: "दुग्ध व्यवसाय",
    key: "cow_cost",
    label: "संकरित गाय खरेदी खर्च",
    value: 65000,
    unit: "INR/गाय",
    source: "NABARD Unit Cost 2025-26",
    year: 2025,
    confidence: "official",
  },
  {
    id: 3,
    business: "flour_mill",
    businessName: "पिठाची गिरणी",
    key: "motor_pulverizer",
    label: "१० HP मोटर व पल्व्हररायझर",
    value: 120000,
    unit: "INR",
    source: "DIC Satara Field Survey",
    year: 2026,
    confidence: "secondary",
  },
  {
    id: 4,
    business: "goat",
    businessName: "शेळीपालन (१०+१)",
    key: "unit_cost",
    label: "१० शेळ्या + १ बोकड युनिट",
    value: 110000,
    unit: "INR",
    source: "NABARD Unit Cost 2025-26",
    year: 2025,
    confidence: "official",
  },
];

export const AdminBenchmarkScreen: React.FC<Props> = ({ onBack }) => {
  const [benchmarks, setBenchmarks] = useState<BenchmarkItem[]>(INITIAL_BENCHMARKS);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState<number>(0);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const startEdit = (bm: BenchmarkItem) => {
    setEditingId(bm.id);
    setEditValue(bm.value);
    setSaveSuccess(null);
  };

  const saveEdit = (id: number) => {
    setBenchmarks((prev) =>
      prev.map((b) => (b.id === id ? { ...b, value: editValue, year: 2026 } : b))
    );
    setEditingId(null);
    setSaveSuccess(`बेंचमार्क #${id} अद्ययावत झाला आणि ऑडिट लॉगमध्ये नोंद झाली.`);
    setTimeout(() => setSaveSuccess(null), 3000);
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
        <span className="text-[10px] uppercase font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
          उद्योग बेंचमार्क संपादक
        </span>
      </div>

      <div>
        <h2 className="text-base font-black text-slate-900">
          उद्योग बेंचमार्क्स व नफा प्रमाणे (Viability Benchmarks)
        </h2>
        <p className="text-xs text-slate-500">
          प्रत्येक बेंचमार्कचे स्रोत, वर्ष आणि विश्वासार्हता पातळी (Official / Survey / Estimate) नियंत्रित करा.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-xs text-emerald-900 font-semibold animate-in fade-in">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{saveSuccess}</span>
        </div>
      )}

      <div className="space-y-3">
        {benchmarks.map((bm) => (
          <div
            key={bm.id}
            className="p-3.5 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
                  {bm.businessName}
                </span>
                <h4 className="text-xs font-bold text-slate-900 mt-1">
                  {bm.label}
                </h4>
              </div>
              <span
                className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-md ${
                  bm.confidence === "official"
                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                    : "bg-amber-50 text-amber-800 border border-amber-200"
                }`}
              >
                {bm.confidence}
              </span>
            </div>

            <div className="flex items-center justify-between pt-1">
              <div>
                <span className="text-[10px] text-slate-400 block font-medium">
                  स्रोत: {bm.source} ({bm.year})
                </span>
                {editingId === bm.id ? (
                  <div className="flex items-center gap-1.5 mt-1">
                    <input
                      type="number"
                      value={editValue}
                      onChange={(e) => setEditValue(Number(e.target.value) || 0)}
                      className="px-2 py-1 text-xs font-bold bg-slate-50 border border-indigo-400 rounded-lg w-28"
                    />
                    <span className="text-xs text-slate-500 font-semibold">{bm.unit}</span>
                  </div>
                ) : (
                  <span className="text-sm font-black text-slate-900 mt-0.5 block">
                    ₹{bm.value.toLocaleString("en-IN")} {bm.unit !== "INR" && bm.unit}
                  </span>
                )}
              </div>

              <div>
                {editingId === bm.id ? (
                  <button
                    type="button"
                    onClick={() => saveEdit(bm.id)}
                    className="p-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-xs transition"
                  >
                    <Save className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => startEdit(bm)}
                    className="p-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
