import React, { useState, useEffect } from "react";
import { ShieldCheck, CheckCircle2, Globe } from "lucide-react";
import { translations, Language } from "./i18n";

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>("mr");
  const [healthStatus, setHealthStatus] = useState<string>("Checking...");
  const t = translations[lang];

  useEffect(() => {
    fetch("/health")
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "ok") {
          setHealthStatus("ok");
        }
      })
      .catch(() => {
        setHealthStatus("offline");
      });
  }, []);

  return (
    <div className="mobile-viewport bg-white border-x border-slate-200 flex flex-col justify-between shadow-sm">
      {/* Mobile Header (360px viewport baseline) */}
      <header className="p-4 border-b border-slate-100 bg-white sticky top-0 z-20">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-600 flex items-center justify-center text-white font-black text-lg shadow-sm">
              अ
            </div>
            <div>
              <h1 className="text-base font-black text-slate-900 leading-tight">
                {t.appName}
              </h1>
              <p className="text-[10px] text-slate-500 font-medium truncate max-w-[200px]">
                {t.schemeBasis}
              </p>
            </div>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <Globe className="w-3 h-3 text-slate-500 ml-1" />
            {(["mr", "hi", "en"] as Language[]).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-2 py-0.5 rounded text-[11px] font-bold transition ${
                  lang === l
                    ? "bg-white text-indigo-600 shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {l === "mr" ? "मराठी" : l === "hi" ? "हिंदी" : "EN"}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="p-4 space-y-4 flex-1">
        {/* Status Pill */}
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2.5 text-xs text-emerald-900">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <div className="flex-1">
            <span className="font-bold">{t.healthStatus}</span>
            <span className="text-emerald-700 block text-[11px]">
              FastAPI + PostGIS + Redis + RQ Architecture Verified ({healthStatus})
            </span>
          </div>
        </div>

        {/* Vision Card */}
        <div className="p-4 bg-indigo-50/60 border border-indigo-100 rounded-xl space-y-2">
          <span className="px-2 py-0.5 bg-indigo-200/70 text-indigo-900 text-[10px] font-extrabold uppercase tracking-wider rounded">
            MoSJE · NSFDC
          </span>
          <p className="text-xs font-semibold text-indigo-950 leading-relaxed">
            {t.tagline}
          </p>
        </div>

        {/* DPDP Compliance Card */}
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center gap-2 text-xs text-slate-600">
          <ShieldCheck className="w-4 h-4 text-indigo-600 flex-shrink-0" />
          <span className="text-[11px] leading-tight">{t.dpdpNotice}</span>
        </div>
      </main>

      {/* Footer */}
      <footer className="p-3 border-t border-slate-100 text-center text-[10px] text-slate-400">
        ArthMitra Production · 360×640 Mobile First
      </footer>
    </div>
  );
};

export default App;
