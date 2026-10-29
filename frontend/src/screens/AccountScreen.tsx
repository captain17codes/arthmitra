import React, { useState } from "react";
import { FileText, LogOut, ShieldCheck, Trash2 } from "lucide-react";
import { CaseRecord, Language, User } from "../types";
import { translations } from "../i18n";
import { api } from "../services/api";

interface Props {
  user: User;
  cases: CaseRecord[];
  onLogout: () => void;
  onAccountDeleted: () => void;
  lang: Language;
}

const TXT = {
  mr: {
    plans: "व्यवसाय प्लॅन",
    privacyTitle: "तुमचा डेटा",
    privacy:
      "तुमची माहिती फक्त तुम्हाला दिसते व एन्क्रिप्ट करून ठेवली जाते. आधार, पॅन किंवा बँक खाते क्रमांक साठवले जात नाहीत.",
    del: "माझे खाते व सर्व माहिती कायमची हटवा",
    delWarn: "हे परत आणता येणार नाही. तुमचे सर्व प्लॅन, अहवाल व माहिती कायमची हटवली जाईल.",
    delConfirm: "होय, कायमचे हटवा",
    cancel: "रद्द करा",
  },
  hi: {
    plans: "व्यवसाय प्लान",
    privacyTitle: "आपका डेटा",
    privacy:
      "आपकी जानकारी सिर्फ आपको दिखती है और एन्क्रिप्ट करके रखी जाती है। आधार, पैन या बैंक खाता नंबर संग्रहीत नहीं किए जाते।",
    del: "मेरा खाता और सारी जानकारी हमेशा के लिए हटाएँ",
    delWarn: "यह वापस नहीं होगा। आपके सारे प्लान, रिपोर्ट और जानकारी हमेशा के लिए हट जाएगी।",
    delConfirm: "हाँ, हमेशा के लिए हटाएँ",
    cancel: "रद्द करें",
  },
  en: {
    plans: "Business plans",
    privacyTitle: "Your data",
    privacy:
      "Only you can see your information and it is stored encrypted. Aadhaar, PAN and bank account numbers are never stored.",
    del: "Delete my account and all my data",
    delWarn: "This cannot be undone. All your plans, reports and details will be permanently deleted.",
    delConfirm: "Yes, delete permanently",
    cancel: "Cancel",
  },
};

export const AccountScreen: React.FC<Props> = ({ user, cases, onLogout, onAccountDeleted, lang }) => {
  const t = translations[lang];
  const L = TXT[lang];
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const doDelete = async () => {
    setBusy(true);
    setError("");
    try {
      await api.deleteMyAccount();
      onAccountDeleted();
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  };

  return (
    <div className="p-4 space-y-4 lg:max-w-2xl">
      <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-2xs flex items-center gap-3">
        <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 font-black text-xl">
          {user.full_name.charAt(0)}
        </div>
        <div className="flex-1">
          <h2 className="text-base font-black text-slate-900">{user.full_name}</h2>
          <p className="text-xs text-slate-500 flex items-center gap-1">
            <FileText className="w-3.5 h-3.5" /> {cases.length} {L.plans}
          </p>
        </div>
      </div>

      <div className="p-4 bg-emerald-50 rounded-2xl border border-emerald-200 space-y-1">
        <h3 className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4" /> {L.privacyTitle}
        </h3>
        <p className="text-xs text-emerald-900">{L.privacy}</p>
      </div>

      <button
        type="button"
        onClick={onLogout}
        className="w-full py-3 rounded-xl border border-slate-300 bg-white text-slate-800 font-bold text-sm flex items-center justify-center gap-2 min-h-[48px] hover:bg-slate-50"
      >
        <LogOut className="w-4 h-4" /> {t.logoutBtn}
      </button>

      <div className="pt-2 border-t border-slate-200">
        {!confirming ? (
          <button
            type="button"
            onClick={() => setConfirming(true)}
            className="w-full py-3 rounded-xl text-red-700 font-bold text-sm flex items-center justify-center gap-2 min-h-[48px] hover:bg-red-50"
          >
            <Trash2 className="w-4 h-4" /> {L.del}
          </button>
        ) : (
          <div className="p-4 rounded-2xl bg-red-50 border border-red-200 space-y-3" role="alertdialog">
            <p className="text-xs text-red-900 font-semibold">{L.delWarn}</p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setConfirming(false)}
                disabled={busy}
                className="flex-1 py-2.5 rounded-xl border border-slate-300 bg-white text-slate-800 font-bold text-xs min-h-[44px]"
              >
                {L.cancel}
              </button>
              <button
                type="button"
                onClick={doDelete}
                disabled={busy}
                className="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 disabled:bg-slate-300 text-white font-bold text-xs min-h-[44px]"
              >
                {busy ? t.loading : L.delConfirm}
              </button>
            </div>
            {error && <p className="text-xs text-red-800">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
};
