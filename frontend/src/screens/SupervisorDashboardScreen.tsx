import React from "react";
import {
  Users,
  AlertTriangle,
  Layers,
  MapPin,
  Settings,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { CaseRecord, Language, User } from "../types";
import { formatINR } from "../i18n";

interface Props {
  user: User;
  cases: CaseRecord[];
  onOpenSchemeEditor: () => void;
  onOpenBenchmarkEditor: () => void;
  onOpenVillageCoords: () => void;
  lang?: Language;
}

export const SupervisorDashboardScreen: React.FC<Props> = ({
  user,
  cases,
  onOpenSchemeEditor,
  onOpenBenchmarkEditor,
  onOpenVillageCoords,
}) => {

  // Derive stats from cases
  const totalCases = cases.length;
  const approvedCases = cases.filter(
    (c) => c.status === "sanctioned" || c.status === "ready"
  ).length;
  const totalCapital = cases.reduce(
    (acc, c) => acc + (c.target_project_cost || 150000),
    0
  );

  // Group by business
  const byBusiness: Record<string, number> = {};
  cases.forEach((c) => {
    const code = c.business?.code || "other";
    byBusiness[code] = (byBusiness[code] || 0) + 1;
  });

  // Agents list
  const agents = [
    { name: "सुनिता पाटील (Sunita Patil)", count: Math.max(1, totalCases), role: "Bank Sakhi" },
    { name: "राहुल शिंदे (Rahul Shinde)", count: 2, role: "CSC VLE" },
    { name: "प्रिया माने (Priya Mane)", count: 1, role: "Bank Sakhi" },
  ];

  return (
    <div className="p-4 space-y-4 pb-20">
      {/* Supervisor Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 p-4 rounded-2xl text-white shadow-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold tracking-wider uppercase text-indigo-300 bg-indigo-900/60 px-2 py-0.5 rounded border border-indigo-700">
            पर्यवेक्षक डॅशबोर्ड · {user.organization_name}
          </span>
          <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" /> सक्रिय निरीक्षण
          </span>
        </div>
        <h2 className="text-lg font-black text-white">
          जिल्हा व गट स्तरावरील सूक्ष्म-उद्योग स्थिती
        </h2>
        <p className="text-xs text-slate-300 font-medium">
          गावनिहाय संतृप्तता (Saturation), योजना वितरण आणि बँक सखींचे कामकाज आढावा.
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-3 gap-2">
        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[10px] text-slate-500 font-bold uppercase block">
            एकूण प्रकरणे
          </span>
          <span className="text-lg font-black text-slate-900 mt-0.5 block">
            {totalCases}
          </span>
          <span className="text-[9px] text-emerald-700 font-bold">
            {approvedCases} मंजूर / तयार
          </span>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[10px] text-slate-500 font-bold uppercase block">
            भांडवल तरतूद
          </span>
          <span className="text-sm font-black text-indigo-700 mt-1 block truncate">
            {formatINR(totalCapital)}
          </span>
          <span className="text-[9px] text-slate-400">प्रकल्प खर्च</span>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[10px] text-slate-500 font-bold uppercase block">
            सक्रिय सखी/VLE
          </span>
          <span className="text-lg font-black text-slate-900 mt-0.5 block">
            {agents.length}
          </span>
          <span className="text-[9px] text-indigo-600 font-bold">१००% उपस्थित</span>
        </div>
      </div>

      {/* Saturation Risk Alert Card */}
      <div className="p-3.5 bg-amber-50/80 border border-amber-200 rounded-2xl space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-950">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>बाजार संतृप्तता व स्पर्धा धोके (Saturation Flags)</span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="p-2 bg-white/90 rounded-xl border border-emerald-200">
            <span className="text-[10px] text-slate-500 block">कमी स्पर्धा</span>
            <span className="font-black text-emerald-700">७०% गावे</span>
          </div>
          <div className="p-2 bg-white/90 rounded-xl border border-amber-200">
            <span className="text-[10px] text-slate-500 block">मध्यम संधी</span>
            <span className="font-black text-amber-700">२५% गावे</span>
          </div>
          <div className="p-2 bg-white/90 rounded-xl border border-red-200">
            <span className="text-[10px] text-slate-500 block">जास्त स्पर्धा</span>
            <span className="font-black text-red-700">५% गावे</span>
          </div>
        </div>
      </div>

      {/* Admin Operations Quick Actions */}
      <div className="space-y-2">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          प्रशासकीय नियंत्रणे (Admin Tools)
        </h3>

        <div className="space-y-2">
          {/* Scheme Editor */}
          <button
            type="button"
            onClick={onOpenSchemeEditor}
            className="w-full p-3.5 bg-white hover:bg-slate-50 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between text-left transition"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-black text-slate-900">
                  शासकीय योजना नियम व आवृत्ती (Scheme Rules & Versions)
                </h4>
                <p className="text-[11px] text-slate-500 font-medium">
                  YAML निकष संपादन, चाचणी पडताळणी आणि ऑडिटसह नवीन आवृत्ती प्रसिद्ध करा.
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
          </button>

          {/* Benchmarks Editor */}
          <button
            type="button"
            onClick={onOpenBenchmarkEditor}
            className="w-full p-3.5 bg-white hover:bg-slate-50 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between text-left transition"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center">
                <Settings className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-black text-slate-900">
                  उद्योग बेंचमार्क्स (Business Benchmarks)
                </h4>
                <p className="text-[11px] text-slate-500 font-medium">
                  १० उद्योग प्रकार, महसूल दर, विश्वासार्हता (Official, Survey) अद्ययावत करा.
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
          </button>

          {/* Village GPS Fixes */}
          <button
            type="button"
            onClick={onOpenVillageCoords}
            className="w-full p-3.5 bg-white hover:bg-slate-50 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between text-left transition"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center">
                <MapPin className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-black text-slate-900">
                  गाव निर्देशांक दुरुस्ती (Village Coordinate Fixes)
                </h4>
                <p className="text-[11px] text-slate-500 font-medium">
                  अचूक नकाशा व कॅचमेंटसाठी गावांचे अक्षांश/रेखांश तपासा व दुरुस्त करा.
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
          </button>
        </div>
      </div>

      {/* Agent Performance Leaderboard */}
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
            <Users className="w-4 h-4 text-indigo-600" />
            बँक सखी / VLE कामकाज अहवाल
          </h3>
          <span className="text-[10px] text-slate-500 font-semibold">
            {agents.length} प्रतिनिधी
          </span>
        </div>

        <div className="space-y-2">
          {agents.map((ag, i) => (
            <div
              key={i}
              className="p-2.5 rounded-xl border border-slate-100 bg-slate-50/70 flex items-center justify-between text-xs"
            >
              <div>
                <span className="font-black text-slate-900 block">{ag.name}</span>
                <span className="text-[10px] text-slate-500">{ag.role}</span>
              </div>
              <div className="text-right">
                <span className="font-bold text-indigo-700">{ag.count} प्रकरणे</span>
                <span className="text-[9px] text-emerald-600 block">१००% पूर्ण</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
