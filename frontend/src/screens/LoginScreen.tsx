import React, { useState } from "react";
import { Lock, Phone, ShieldCheck, Sparkles } from "lucide-react";
import { Language, User } from "../types";
import { translations } from "../i18n";
import { api, ApiError } from "../services/api";

interface Props {
  lang: Language;
  onLoginSuccess: (user: User) => void;
}

export const LoginScreen: React.FC<Props> = ({ lang, onLoginSuccess }) => {
  const t = translations[lang];
  const [phone, setPhone] = useState("9876543210");
  const [pin, setPin] = useState("1234");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    if (phone.length < 10) {
      setErrorMsg(lang === "mr" ? "कृपया वैध १० अंकी मोबाईल नंबर टाका." : "Enter valid 10-digit phone number.");
      return;
    }
    if (pin.length !== 4) {
      setErrorMsg(lang === "mr" ? "कृपया ४ अंकी पिन प्रविष्ट करा." : "Enter 4-digit PIN.");
      return;
    }

    setLoading(true);
    try {
      const user = await api.login(phone, pin);
      onLoginSuccess(user);
    } catch (err) {
      if (err instanceof ApiError && err.status === 0) {
        setErrorMsg(
          lang === "mr"
            ? "सर्व्हरशी संपर्क झाला नाही. इंटरनेट तपासा (पहिल्यांदा सर्व्हर सुरू होण्यास १ मिनिट लागू शकतो)."
            : "Could not reach the server. Check internet (first start can take ~1 minute)."
        );
      } else {
        setErrorMsg(lang === "mr" ? "लॉगिन अयशस्वी. कृपया पिन तपासा." : "Login failed. Please verify credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 flex flex-col justify-center min-h-[80vh]">
      {/* Brand Hero */}
      <div className="text-center mb-6">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-emerald-600 via-teal-600 to-indigo-600 flex items-center justify-center text-white font-black text-2xl shadow-md mb-3">
          अ
        </div>
        <h2 className="text-xl font-black text-slate-900 tracking-tight">
          {t.appName}
        </h2>
        <p className="text-xs text-indigo-700 font-semibold mt-1 max-w-[280px] mx-auto">
          {t.schemeBasis}
        </p>
      </div>

      {/* Login Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">{t.loginTitle}</h3>
          <p className="text-xs text-slate-500 mt-0.5">{t.loginSubtitle}</p>
        </div>

        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-medium">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Phone Field */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.phoneLabel}
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Phone className="w-4 h-4" />
              </span>
              <input
                type="tel"
                maxLength={10}
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
                placeholder={t.phonePlaceholder}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 min-h-[48px]"
                required
              />
            </div>
          </div>

          {/* PIN Field */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.pinLabel}
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type="password"
                inputMode="numeric"
                maxLength={4}
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
                placeholder={t.pinPlaceholder}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold tracking-widest text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 min-h-[48px]"
                required
              />
            </div>
          </div>

          {/* Quick Demo Pre-fill */}
          <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-[11px] text-slate-600">
            <span className="flex items-center gap-1 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              डेमो पिन (Demo PIN): 1234
            </span>
            <button
              type="button"
              onClick={() => {
                setPhone("9876543210");
                setPin("1234");
              }}
              className="font-bold text-indigo-600 hover:text-indigo-800 underline"
            >
              Fill Demo
            </button>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-bold text-sm shadow-sm transition flex items-center justify-center gap-2 min-h-[48px] disabled:opacity-60"
          >
            {loading ? t.loading : t.loginBtn}
          </button>
        </form>
      </div>

      {/* DPDP Legal Note */}
      <div className="mt-6 text-center space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-800 rounded-full text-[11px] font-medium border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          {t.dpdpNotice}
        </div>
      </div>
    </div>
  );
};
