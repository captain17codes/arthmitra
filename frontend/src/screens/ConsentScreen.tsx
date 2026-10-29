import React, { useState } from "react";
import { CheckSquare, ShieldCheck, Square, Volume2 } from "lucide-react";
import { Language } from "../types";
import { translations } from "../i18n";

interface Props {
  lang: Language;
  onConsentGranted: (consentData: { notice_version: string; method: "tap" }) => void;
  onBack: () => void;
}

const AGREE = {
  mr: "मी सूचना वाचली/ऐकली असून माझ्या माहितीच्या वापरास मी सहमत आहे.",
  hi: "मैंने सूचना पढ़ी/सुनी है और अपनी जानकारी के उपयोग के लिए सहमत हूँ।",
  en: "I have read / heard the notice and I agree to the use of my information.",
};

/** The person consents for themselves: notice (readable or read aloud) + an explicit tick. */
export const ConsentScreen: React.FC<Props> = ({ lang, onConsentGranted, onBack }) => {
  const t = translations[lang];
  const [agreed, setAgreed] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const listen = () => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    if (speaking) {
      setSpeaking(false);
      return;
    }
    const u = new SpeechSynthesisUtterance(t.statutoryBody);
    u.lang = lang === "mr" ? "mr-IN" : lang === "hi" ? "hi-IN" : "en-IN";
    u.rate = 0.95;
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(u);
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <span className="text-[10px] uppercase font-bold text-emerald-700 tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          {lang === "en" ? "Step 1 / 5" : lang === "hi" ? "चरण 1 / 5" : "पायरी १ / ५"} · DPDP Act 2023
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1">{t.consentTitle}</h2>
      </div>

      <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-2xl space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" /> {t.statutoryHeader}
          </h3>
          <button
            type="button"
            onClick={listen}
            className="shrink-0 px-2.5 py-1.5 rounded-lg bg-white border border-emerald-300 text-emerald-800 text-xs font-bold flex items-center gap-1 min-h-[40px]"
          >
            <Volume2 className="w-4 h-4" /> {speaking ? "■" : lang === "en" ? "Listen" : lang === "hi" ? "सुनें" : "ऐका"}
          </button>
        </div>
        <p className="text-sm text-slate-800 leading-relaxed">{t.statutoryBody}</p>
        <p className="text-[11px] text-emerald-800 font-semibold">{t.zeroPiiNotice}</p>
      </div>

      <button
        type="button"
        role="checkbox"
        aria-checked={agreed}
        onClick={() => setAgreed((a) => !a)}
        className={`w-full p-4 rounded-2xl border-2 text-left flex items-start gap-3 transition min-h-[64px] ${
          agreed ? "bg-emerald-50 border-emerald-500" : "bg-white border-slate-300"
        }`}
      >
        {agreed ? (
          <CheckSquare className="w-6 h-6 text-emerald-600 shrink-0" />
        ) : (
          <Square className="w-6 h-6 text-slate-400 shrink-0" />
        )}
        <span className="text-sm font-semibold text-slate-900">{AGREE[lang]}</span>
      </button>

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
          onClick={() => onConsentGranted({ notice_version: "1.0", method: "tap" })}
          disabled={!agreed}
          className="flex-[2] py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition min-h-[48px] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {t.proceedToProfile}
        </button>
      </div>
    </div>
  );
};
