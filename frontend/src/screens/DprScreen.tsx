import React, { useState } from "react";
import {
  ArrowLeft,
  Building,
  CheckCircle2,
  Download,
  ExternalLink,
  FileCheck,
  Layers,
  Send,
  ShieldCheck,
} from "lucide-react";
import { CaseRecord, CaseStatus, EvaluationResult, Language } from "../types";
import { translations } from "../i18n";
import { api } from "../services/api";

interface Props {
  caseRecord: CaseRecord;
  evaluation: EvaluationResult;
  onUpdateCase: (updated: CaseRecord) => void;
  onBack: () => void;
  lang: Language;
}

export const DprScreen: React.FC<Props> = ({
  caseRecord,
  evaluation,
  onUpdateCase,
  onBack,
  lang,
}) => {
  const t = translations[lang];
  const [downloadingLang, setDownloadingLang] = useState<string | null>(null);
  const [newStatus, setNewStatus] = useState<CaseStatus>(caseRecord.status);
  const [statusReason, setStatusReason] = useState(caseRecord.status_reason || "");
  const [statusSuccess, setStatusSuccess] = useState(false);

  const handleDownload = async (language: "mr" | "en") => {
    setDownloadingLang(language);
    try {
      const res = await api.generateDpr(evaluation.id, language);
      // Simulate / open download
      const link = document.createElement("a");
      link.href = res.download_url;
      link.setAttribute("download", `DPR_${caseRecord.id}_${language}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Auto update status to dpr_generated if still ready
      if (caseRecord.status === "ready") {
        const updated = await api.updateCaseStatus(caseRecord.id, "dpr_generated");
        if (updated) onUpdateCase(updated);
      }
    } finally {
      setDownloadingLang(null);
    }
  };

  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const updated = await api.updateCaseStatus(
      caseRecord.id,
      newStatus,
      statusReason
    );
    if (updated) {
      onUpdateCase(updated);
      setStatusSuccess(true);
      setTimeout(() => setStatusSuccess(false), 2000);
    }
  };

  const sha256 =
    evaluation.dpr_documents?.[0]?.sha256 ||
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

  return (
    <div className="p-4 space-y-4 pb-20">
      {/* Top Banner */}
      <div className="flex items-center gap-2">
        <button
          onClick={onBack}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 min-w-[40px] min-h-[40px] flex items-center justify-center"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-base font-black text-slate-900">
            {t.dprCardTitle}
          </h2>
          <p className="text-xs text-slate-500">{t.dprSubtitle}</p>
        </div>
      </div>

      {/* PDF Download Action Card */}
      <div className="p-5 bg-gradient-to-tr from-emerald-800 to-teal-900 rounded-2xl text-white shadow-md space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-emerald-300 tracking-wider">
              १२ कलमी बँक प्रकल्प अहवाल
            </span>
            <h3 className="text-sm font-black">
              {caseRecord.beneficiary.first_name} —{" "}
              {lang === "mr" ? caseRecord.business.name_mr : caseRecord.business.name_en}
            </h3>
            <span className="text-xs text-emerald-200">
              {lang === "mr" ? caseRecord.village.name_mr : caseRecord.village.name_en}
            </span>
          </div>
          <FileCheck className="w-8 h-8 text-emerald-300" />
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
          <button
            type="button"
            onClick={() => handleDownload("mr")}
            disabled={downloadingLang === "mr"}
            className="py-3 px-3 rounded-xl bg-white hover:bg-emerald-50 text-emerald-950 font-bold text-xs shadow-xs transition flex items-center justify-center gap-2 min-h-[48px]"
          >
            <Download className="w-4 h-4 text-emerald-700" />
            <span>
              {downloadingLang === "mr" ? t.loading : t.downloadMarathiPdfBtn}
            </span>
          </button>

          <button
            type="button"
            onClick={() => handleDownload("en")}
            disabled={downloadingLang === "en"}
            className="py-3 px-3 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs border border-emerald-500 shadow-xs transition flex items-center justify-center gap-2 min-h-[48px]"
          >
            <Download className="w-4 h-4 text-emerald-200" />
            <span>
              {downloadingLang === "en" ? t.loading : t.downloadEnglishPdfBtn}
            </span>
          </button>
        </div>

        {/* SHA-256 Hash Verification Badge */}
        <div className="p-2.5 bg-emerald-950/60 rounded-xl border border-emerald-700/60 flex items-center gap-2 text-[10px] text-emerald-200">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <div className="truncate">
            <span className="font-bold block text-emerald-300">
              {t.sha256Label}
            </span>
            <code className="text-[9px] font-mono opacity-80">{sha256}</code>
          </div>
        </div>
      </div>

      {/* Bank Submission Checklist */}
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2.5">
        <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-indigo-600" />
          {t.bankChecklistTitle}
        </h4>
        <ul className="space-y-1.5 text-xs text-slate-700">
          <li className="flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>{t.bankChecklistDoc1}</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>{t.bankChecklistDoc2}</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>{t.bankChecklistDoc3}</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>{t.bankChecklistDoc4}</span>
          </li>
        </ul>
      </div>

      {/* Target Application Office / Portal */}
      <div className="p-4 bg-indigo-50/60 rounded-2xl border border-indigo-200 space-y-2">
        <h4 className="text-xs font-bold text-indigo-950 flex items-center gap-1.5">
          <Building className="w-4 h-4 text-indigo-700" />
          {t.portalToApplyTitle}
        </h4>
        <p className="text-xs text-indigo-900 font-semibold">{t.portalHint}</p>
        <div className="flex items-center gap-3 pt-1">
          <a
            href="https://maha-cmegp.gov.in"
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold text-indigo-700 hover:underline flex items-center gap-1"
          >
            <span>महा-रोजगार पोर्टल</span>
            <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href="https://nsfdc.nic.in"
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold text-indigo-700 hover:underline flex items-center gap-1"
          >
            <span>NSFDC अधिकृत पोर्टल</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      {/* Track & Update Status Card */}
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
        <h4 className="text-xs font-bold text-slate-900">
          प्रकरणाची सद्यस्थिती बदला (Update Status)
        </h4>

        {statusSuccess && (
          <div className="p-2 bg-emerald-50 text-emerald-800 text-xs font-bold rounded-lg border border-emerald-200">
            स्थिती यशस्वीरीत्या अद्ययावत झाली ✓
          </div>
        )}

        <form onSubmit={handleStatusSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              नवीन स्थिती निवडा
            </label>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value as CaseStatus)}
              className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs font-bold text-slate-900 bg-white min-h-[44px]"
            >
              <option value="draft">{t.statusDraft}</option>
              <option value="ready">{t.statusReady}</option>
              <option value="dpr_generated">{t.statusDpr}</option>
              <option value="applied">{t.statusApplied}</option>
              <option value="sanctioned">{t.statusSanctioned}</option>
              <option value="rejected">{t.statusRejected}</option>
              <option value="disbursed">{t.statusDisbursed}</option>
              <option value="closed">{t.statusClosed}</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              टिप्पणी / संदर्भ क्रमांक (उदा. बँक पावती क्रमांक)
            </label>
            <input
              type="text"
              value={statusReason}
              onChange={(e) => setStatusReason(e.target.value)}
              placeholder="उदा. बँक ऑफ महाराष्ट्र, शिरवळ शाखेत सादर"
              className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs font-medium text-slate-900 min-h-[44px]"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-xs transition flex items-center justify-center gap-1.5 min-h-[44px]"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{t.updateStatusBtn}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
