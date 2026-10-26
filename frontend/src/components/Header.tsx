import React from "react";
import { Globe, LogOut, ShieldCheck, Wifi, WifiOff } from "lucide-react";
import { Language, User } from "../types";
import { translations } from "../i18n";

interface Props {
  lang: Language;
  onSelectLang: (l: Language) => void;
  user: User | null;
  onLogout: () => void;
  isOnline: boolean;
}

export const Header: React.FC<Props> = ({
  lang,
  onSelectLang,
  user,
  onLogout,
  isOnline,
}) => {
  const t = translations[lang];

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-xs border-b border-slate-200 px-3 py-2.5 shadow-2xs">
      <div className="flex items-center justify-between gap-2">
        {/* Brand */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-600 to-indigo-600 flex items-center justify-center text-white font-black text-base shadow-xs">
            अ
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-black text-slate-900 tracking-tight">
                {t.appName}
              </span>
              {/* DPDP Pill */}
              <span className="hidden sm:inline-flex items-center gap-0.5 text-[9px] bg-emerald-50 text-emerald-800 px-1.5 py-0.2 rounded border border-emerald-200 font-medium">
                <ShieldCheck className="w-2.5 h-2.5 text-emerald-600" />
                DPDP
              </span>
            </div>
            <p className="text-[10px] text-slate-500 font-medium truncate max-w-[140px]">
              {user ? user.full_name : t.agentRole}
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          {/* Online/Offline status */}
          <div
            className={`flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-md border ${
              isOnline
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-amber-50 text-amber-700 border-amber-300"
            }`}
            title={isOnline ? t.online : t.offlineNotice}
          >
            {isOnline ? (
              <Wifi className="w-3 h-3 text-emerald-600" />
            ) : (
              <WifiOff className="w-3 h-3 text-amber-600" />
            )}
            <span className="font-bold hidden xs:inline">
              {isOnline ? t.online : t.offline}
            </span>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <Globe className="w-3 h-3 text-slate-400 ml-1 hidden xs:inline" />
            {(["mr", "hi", "en"] as Language[]).map((l) => (
              <button
                key={l}
                onClick={() => onSelectLang(l)}
                className={`px-1.5 py-0.5 rounded text-[11px] font-bold transition min-w-[28px] ${
                  lang === l
                    ? "bg-white text-indigo-700 shadow-2xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
                aria-label={`Switch to ${l}`}
              >
                {l === "mr" ? "मराठी" : l === "hi" ? "हिंदी" : "EN"}
              </button>
            ))}
          </div>

          {/* Logout */}
          {user && (
            <button
              onClick={onLogout}
              className="p-1.5 text-slate-500 hover:text-red-600 rounded-lg border border-slate-200 hover:bg-red-50 transition"
              title={t.logoutBtn}
              aria-label="Logout"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
