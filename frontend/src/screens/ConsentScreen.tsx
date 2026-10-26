import React, { useState } from "react";
import {
  CheckCircle2,
  FileText,
  Mic,
  ShieldCheck,
  Volume2,
} from "lucide-react";
import { Language } from "../types";
import { translations } from "../i18n";

interface Props {
  lang: Language;
  onConsentGranted: (consentData: {
    notice_version: string;
    method: "voice" | "signed_paper" | "otp_sms";
  }) => void;
  onBack: () => void;
}

export const ConsentScreen: React.FC<Props> = ({
  lang,
  onConsentGranted,
  onBack,
}) => {
  const t = translations[lang];
  const [method, setMethod] = useState<"voice" | "signed_paper" | "otp_sms">("voice");
  const [isRecording, setIsRecording] = useState(false);
  const [recorded, setRecorded] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const handleVoiceTap = () => {
    setIsRecording(true);
    setTimeout(() => {
      setIsRecording(false);
      setRecorded(true);
    }, 1200);
  };

  const handlePlayNotice = () => {
    setIsPlayingAudio(true);
    setTimeout(() => {
      setIsPlayingAudio(false);
    }, 2500);
  };

  const handleProceed = () => {
    onConsentGranted({
      notice_version: "1.0",
      method,
    });
  };

  return (
    <div className="p-4 space-y-4">
      {/* Step Header */}
      <div>
        <span className="text-[10px] uppercase font-bold text-emerald-700 tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          पायरी १ / ५ · DPDP Act 2023
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1">
          {t.consentTitle}
        </h2>
      </div>

      {/* Statutory Notice Card */}
      <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-2xl space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            {t.statutoryHeader}
          </div>
          {/* Read aloud button */}
          <button
            type="button"
            onClick={handlePlayNotice}
            className={`flex items-center gap-1 text-[11px] font-bold px-2 py-1 rounded-lg border transition ${
              isPlayingAudio
                ? "bg-emerald-600 text-white border-emerald-700 animate-pulse"
                : "bg-white text-emerald-800 border-emerald-200 hover:bg-emerald-50"
            }`}
          >
            <Volume2 className="w-3.5 h-3.5" />
            {isPlayingAudio ? "वाचत आहे..." : "ऐका (Audio)"}
          </button>
        </div>

        <p className="text-xs text-emerald-900 leading-relaxed font-medium">
          {t.statutoryBody}
        </p>

        <div className="pt-2 border-t border-emerald-200/80 flex items-center justify-between text-[11px] text-emerald-800">
          <span className="font-semibold">{t.zeroPiiNotice}</span>
          <span className="text-[10px] bg-emerald-200/60 px-1.5 py-0.5 rounded font-bold">
            v1.0
          </span>
        </div>
      </div>

      {/* Consent Method Picker */}
      <div className="space-y-2">
        <label className="block text-xs font-bold text-slate-700">
          {t.statutoryVoicePrompt}
        </label>

        {/* Big Voice Consent Button */}
        <button
          type="button"
          onClick={handleVoiceTap}
          disabled={isRecording}
          className={`w-full py-4 px-4 rounded-2xl border-2 transition flex flex-col items-center justify-center gap-1.5 shadow-sm min-h-[72px] ${
            recorded
              ? "bg-emerald-100/80 border-emerald-500 text-emerald-950"
              : isRecording
              ? "bg-red-50 border-red-400 text-red-700 animate-pulse"
              : "bg-white hover:bg-emerald-50 border-emerald-300 text-emerald-900"
          }`}
        >
          <div className="flex items-center gap-2 font-bold text-sm">
            {recorded ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            ) : (
              <Mic className="w-5 h-5 text-emerald-600" />
            )}
            <span>
              {isRecording
                ? "आवाज नोंदवत आहे... (Recording)"
                : recorded
                ? "संमती ऑडिओ रेकॉर्ड झाली ✓"
                : t.voiceConsentBtn}
            </span>
          </div>
          <span className="text-[11px] text-slate-500 font-medium">
            {recorded
              ? "डिजिटल ऑडिओ हॅश: sha256_e7d2... सुरक्षित जतन"
              : "माईक टॅप करून लाभार्थ्यांचा संमती होकार नोंदवा"}
          </span>
        </button>

        {/* Alternative Consent Methods */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <button
            type="button"
            onClick={() => {
              setMethod("signed_paper");
              setRecorded(true);
            }}
            className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition min-h-[44px] ${
              method === "signed_paper" && recorded
                ? "bg-indigo-50 border-indigo-500 text-indigo-900 font-bold"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-indigo-600" />
            {t.paperConsentBtn}
          </button>

          <button
            type="button"
            onClick={() => {
              setMethod("otp_sms");
              setRecorded(true);
            }}
            className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition min-h-[44px] ${
              method === "otp_sms" && recorded
                ? "bg-indigo-50 border-indigo-500 text-indigo-900 font-bold"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-indigo-600" />
            {t.otpConsentBtn}
          </button>
        </div>
      </div>

      {/* Confirmation Badge */}
      {recorded && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-xs text-emerald-900 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span className="font-semibold">{t.consentGrantedNotice}</span>
        </div>
      )}

      {/* Actions */}
      <div className="pt-4 flex items-center gap-3">
        <button
          type="button"
          onClick={onBack}
          className="flex-1 py-3 px-4 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition min-h-[48px]"
        >
          {t.back}
        </button>

        <button
          type="button"
          onClick={handleProceed}
          disabled={!recorded}
          className="flex-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition min-h-[48px] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {t.proceedToProfile}
        </button>
      </div>
    </div>
  );
};
