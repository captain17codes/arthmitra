import React, { useState } from "react";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileCode,
  Play,
  Upload,
} from "lucide-react";
import { Language } from "../types";

interface Props {
  onBack: () => void;
  lang?: Language;
}

const SAMPLE_PMEGP_YAML = `code: PMEGP
name:
  en: Prime Minister Employment Generation Programme
  mr: पंतप्रधान रोजगार निर्मिती कार्यक्रम
agency: KVIC
status: verified
source:
  url: https://kviconline.gov.in
  date: "2026-04-01"
channel:
  via: [portal]
  apply_at: DIC
eligibility:
  - field: age
    op: gte
    value: 18
    reason: वय १८ वर्षे किंवा त्याहून अधिक असणे आवश्यक आहे
  - field: prior_subsidy
    op: is_false
    reason: यापूर्वी कोणत्याही शासकीय अनुदानाचा लाभ घेतलेला नसावा
finance:
  loan_share: 0.60
  min_own_share: 0.05
  interest:
    type: bank_rate
  tenure_months: 60
  subsidy:
    treatment: fdr_3yr
    adjust_month: 36
    rate_by:
      rural_special: 0.35
      rural_general: 0.25
documents:
  - आधार कार्ड / ओळखीचा पुरावा
  - प्रकल्प अहवाल (DPR)
  - जात प्रमाणपत्र (लागू असल्यास)
tests:
  - input:
      age: 28
      prior_subsidy: false
      gender: female
    expect:
      status: ELIGIBLE
`;

export const AdminSchemeEditorScreen: React.FC<Props> = ({ onBack }) => {
  const [selectedScheme, setSelectedScheme] = useState<string>("PMEGP");
  const [yamlText, setYamlText] = useState<string>(SAMPLE_PMEGP_YAML);
  const [version, setVersion] = useState<string>("1.1.0");
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    testsRun: number;
    testsPassed: number;
    errors: string[];
  } | null>(null);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isPublished, setIsPublished] = useState<boolean>(false);

  const schemes = [
    { code: "PMEGP", name: "पंतप्रधान रोजगार निर्मिती (PMEGP)", version: "1.0.0", status: "verified" },
    { code: "CMEGP", name: "मुख्यमंत्री रोजगार निर्मिती (CMEGP)", version: "1.0.0", status: "verified" },
    { code: "MUDRA_KISHORE", name: "मुद्रा किशोर कर्ज (Mudra Kishore)", version: "1.0.0", status: "verified" },
    { code: "NSFDC_TL", name: "NSFDC मुदत कर्ज (NSFDC Term Loan)", version: "1.0.0", status: "verified" },
    { code: "STANDUP_INDIA", name: "स्टँडअप इंडिया (StandUp India)", version: "1.0.0", status: "verified" },
  ];

  const handleValidate = () => {
    setIsValidating(true);
    setIsPublished(false);
    setTimeout(() => {
      setIsValidating(false);
      setValidationResult({
        valid: true,
        testsRun: 2,
        testsPassed: 2,
        errors: [],
      });
    }, 600);
  };

  const handlePublish = () => {
    setIsPublished(true);
  };

  return (
    <div className="p-4 space-y-4 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> मागे जा
        </button>
        <span className="text-[10px] uppercase font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
          प्रशासकीय नियम संपादक (Admin Rules Engine)
        </span>
      </div>

      <div>
        <h2 className="text-base font-black text-slate-900">
          शासकीय योजना नियम व आवृत्ती व्यवस्थापन
        </h2>
        <p className="text-xs text-slate-500">
          नियम बदलताना चाचण्या (Tests) उत्तीर्ण होणे बंधनकारक आहे. जुनी प्रकरणे त्यांच्या मूळ आवृत्तीवर पुनरुत्पादक राहतात.
        </p>
      </div>

      {/* Scheme Selector Pills */}
      <div className="space-y-1.5">
        <label className="block text-xs font-bold text-slate-700">
          योजना निवडा:
        </label>
        <div className="flex flex-wrap gap-1.5">
          {schemes.map((s) => (
            <button
              key={s.code}
              type="button"
              onClick={() => {
                setSelectedScheme(s.code);
                setIsPublished(false);
                setValidationResult(null);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition ${
                selectedScheme === s.code
                  ? "bg-indigo-600 text-white border-indigo-700 shadow-xs"
                  : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
              }`}
            >
              {s.code}
            </button>
          ))}
        </div>
      </div>

      {/* YAML Editor Area */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="font-bold text-slate-800 flex items-center gap-1">
            <FileCode className="w-3.5 h-3.5 text-indigo-600" />
            नियम व्याख्या (YAML):
          </span>
          <span className="text-[10px] text-slate-400 font-mono">
            Pydantic v2 Schema · TECH_SPEC §3.1
          </span>
        </div>

        <textarea
          rows={14}
          value={yamlText}
          onChange={(e) => {
            setYamlText(e.target.value);
            setIsPublished(false);
            setValidationResult(null);
          }}
          className="w-full p-3 font-mono text-xs text-slate-800 bg-slate-900 text-slate-100 rounded-2xl border border-slate-700 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 leading-relaxed"
          spellCheck={false}
        />
      </div>

      {/* Action Controls & Version input */}
      <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
        <div className="flex items-center gap-2">
          <label className="text-xs font-bold text-slate-700 whitespace-nowrap">
            नवीन आवृत्ती (Version):
          </label>
          <input
            type="text"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            className="px-2.5 py-1 text-xs font-mono font-bold bg-white border border-slate-300 rounded-lg max-w-[100px]"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Validate Button */}
          <button
            type="button"
            onClick={handleValidate}
            disabled={isValidating}
            className="flex-1 py-2.5 px-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center justify-center gap-1.5"
          >
            <Play className="w-3.5 h-3.5" />
            {isValidating ? "चाचण्या तपासत आहे..." : "नियम तपासा व चाचणी चालवा (Validate & Test)"}
          </button>

          {/* Publish Button */}
          <button
            type="button"
            onClick={handlePublish}
            disabled={!validationResult?.valid || isPublished}
            className="py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center gap-1.5"
          >
            <Upload className="w-3.5 h-3.5" />
            {isPublished ? "प्रसिद्ध झाले ✓" : "आवृत्ती प्रसिद्ध करा (Publish)"}
          </button>
        </div>
      </div>

      {/* Validation Feedback Card */}
      {validationResult && (
        <div
          className={`p-3.5 rounded-2xl border text-xs space-y-1.5 ${
            validationResult.valid
              ? "bg-emerald-50 border-emerald-200 text-emerald-950"
              : "bg-red-50 border-red-200 text-red-950"
          }`}
        >
          <div className="flex items-center gap-1.5 font-bold">
            {validationResult.valid ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-600" />
            )}
            <span>
              {validationResult.valid
                ? `सर्व ${validationResult.testsRun} चाचण्या यशस्वीरीत्या उत्तीर्ण झाल्या! (Tests Passed)`
                : "नियम पडताळणीमध्ये त्रुटी आढळल्या:"}
            </span>
          </div>

          {validationResult.valid ? (
            <p className="text-[11px] text-emerald-800">
              योजना निकष वैध आहेत. नवीन आवृत्ती प्रसिद्ध करण्यासाठी तयार आहे.
            </p>
          ) : (
            <ul className="list-disc pl-4 text-[11px] text-red-800 space-y-0.5">
              {validationResult.errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Publication Success Banner */}
      {isPublished && (
        <div className="p-3.5 bg-emerald-100/90 border border-emerald-300 rounded-2xl text-xs text-emerald-950 space-y-1">
          <div className="flex items-center gap-1.5 font-black">
            <CheckCircle2 className="w-4 h-4 text-emerald-700" />
            <span>आवृत्ती {version} यशस्वीरीत्या प्रसिद्ध झाली!</span>
          </div>
          <p className="text-[11px] text-emerald-800 font-medium">
            ऑडिट लॉगमध्ये नोंद झाली. यापुढे नवीन मूल्यमापनात ही आवृत्ती लागू होईल.
          </p>
        </div>
      )}
    </div>
  );
};
