import React from "react";
import {
  Building2,
  CheckCircle,
  LogOut,
  Phone,
  ShieldCheck,
  UserCheck,
} from "lucide-react";
import { CaseRecord, Language, User } from "../types";
import { translations } from "../i18n";

interface Props {
  user: User;
  cases: CaseRecord[];
  onLogout: () => void;
  lang: Language;
}

export const AgentProfileScreen: React.FC<Props> = ({
  user,
  cases,
  onLogout,
  lang,
}) => {
  const t = translations[lang];

  return (
    <div className="p-4 space-y-4">
      {/* Agent Card */}
      <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-3">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 font-black text-xl">
            {user.full_name.charAt(0)}
          </div>
          <div>
            <h2 className="text-base font-black text-slate-900">
              {user.full_name}
            </h2>
            <p className="text-xs text-indigo-700 font-semibold">{t.agentRole}</p>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 space-y-2 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-slate-400" />
            <span>
              संस्था: <strong>{user.organization_name}</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Phone className="w-4 h-4 text-slate-400" />
            <span>
              ID: <strong>{user.id}</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-slate-400" />
            <span>
              भूमिका: <strong className="uppercase">{user.role}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Case Sync & Storage Stats */}
      <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
        <h3 className="text-xs font-bold text-slate-900">
          स्थानिक डेटा व सिंक स्थिती (Offline & Storage)
        </h3>

        <div className="grid grid-cols-2 gap-2 text-center text-xs">
          <div className="p-3 bg-white rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-500 block">एकूण प्रकरणे</span>
            <span className="text-base font-black text-slate-900">
              {cases.length}
            </span>
          </div>

          <div className="p-3 bg-white rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-500 block">डीपीआर तयार</span>
            <span className="text-base font-black text-emerald-700">
              {cases.filter((c) => c.status === "dpr_generated" || c.status === "applied").length}
            </span>
          </div>
        </div>

        <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-xs text-emerald-900 font-medium">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>सर्व प्रकरणे स्थानिक मेमरीमध्ये सुरक्षित जतन आहेत.</span>
        </div>
      </div>

      {/* DPDP Statutory Safeguards */}
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-2 text-xs">
        <h4 className="font-bold text-slate-900 flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          {t.dpdpProtectedBadge}
        </h4>
        <p className="text-slate-600 leading-relaxed text-[11px]">
          अर्थमित्र अॅपमध्ये आधार कार्ड नंबर, पॅन नंबर किंवा बँक खाते क्रमांक कधीही
          स्टोअर केले जात नाहीत. सर्व वैयक्तिक माहिती कूटबद्ध (Fernet Encrypted)
          असून डीपीडीपी कायदा २०२३ नुसार संमतीशिवाय कोणत्याही त्रयस्थ संस्थेला दिली
          जात नाही.
        </p>
      </div>

      {/* Logout */}
      <button
        type="button"
        onClick={onLogout}
        className="w-full py-3 px-4 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 font-bold text-xs transition flex items-center justify-center gap-1.5 min-h-[48px]"
      >
        <LogOut className="w-4 h-4" />
        <span>{t.logoutBtn}</span>
      </button>
    </div>
  );
};
