import React, { useState } from "react";
import { KeyRound, Lock, MessageSquareText, Phone, ShieldCheck, UserRound } from "lucide-react";
import { Language, User } from "../types";
import { translations } from "../i18n";
import { api, ApiError } from "../services/api";
import { firebaseConfirmOtp, firebaseEnabled, firebaseSendOtp } from "../services/firebaseOtp";

interface Props {
  lang: Language;
  onLoginSuccess: (user: User) => void;
}

type Mode = "login" | "otp_phone" | "otp_code" | "set_pin";

const TXT = {
  mr: {
    login: "लॉगिन",
    loginSub: "मोबाईल नंबर व ४ अंकी पिन टाका",
    newHere: "पहिल्यांदाच? नवीन खाते बनवा",
    forgot: "पिन विसरलात?",
    otpTitle: "मोबाईल नंबर पडताळणी",
    otpSub: "या नंबरवर ६ अंकी OTP पाठवला जाईल",
    sendOtp: "OTP पाठवा",
    codeTitle: "OTP टाका",
    codeSub: (p: string) => `${p} वर पाठवलेला ६ अंकी कोड`,
    verify: "पडताळा",
    resend: "OTP पुन्हा पाठवा",
    devOtp: "डेमो मोड: SMS सेवा अजून जोडलेली नाही. तुमचा OTP आहे",
    newTitle: "नवीन खाते",
    resetTitle: "नवीन पिन बनवा",
    welcomeBack: (n: string) => `नमस्कार ${n}, नवीन पिन बनवा`,
    name: "तुमचे नाव",
    namePh: "उदा. अनिता कांबळे",
    newPin: "४ अंकी पिन",
    confirmPin: "पिन पुन्हा टाका",
    create: "खाते बनवा",
    savePin: "पिन जतन करा",
    back: "← मागे",
    badPhone: "कृपया योग्य १० अंकी मोबाईल नंबर टाका.",
    badPin: "पिन ४ अंकी असावा.",
    pinMismatch: "दोन्ही पिन सारखे नाहीत.",
    needName: "कृपया तुमचे नाव टाका.",
    needOtp: "कृपया ६ अंकी OTP टाका.",
    wrongLogin: "मोबाईल नंबर किंवा पिन चुकीचा आहे.",
    offline: "सर्व्हरशी संपर्क झाला नाही. इंटरनेट तपासा (पहिल्यांदा सर्व्हर सुरू होण्यास १ मिनिट लागू शकतो).",
  },
  hi: {
    login: "लॉगिन",
    loginSub: "मोबाइल नंबर और 4 अंकों का पिन डालें",
    newHere: "पहली बार? नया खाता बनाएँ",
    forgot: "पिन भूल गए?",
    otpTitle: "मोबाइल नंबर सत्यापन",
    otpSub: "इस नंबर पर 6 अंकों का OTP भेजा जाएगा",
    sendOtp: "OTP भेजें",
    codeTitle: "OTP डालें",
    codeSub: (p: string) => `${p} पर भेजा गया 6 अंकों का कोड`,
    verify: "सत्यापित करें",
    resend: "OTP फिर से भेजें",
    devOtp: "डेमो मोड: SMS सेवा अभी जुड़ी नहीं है। आपका OTP है",
    newTitle: "नया खाता",
    resetTitle: "नया पिन बनाएँ",
    welcomeBack: (n: string) => `नमस्ते ${n}, नया पिन बनाएँ`,
    name: "आपका नाम",
    namePh: "जैसे अनीता कांबले",
    newPin: "4 अंकों का पिन",
    confirmPin: "पिन दोबारा डालें",
    create: "खाता बनाएँ",
    savePin: "पिन सेव करें",
    back: "← पीछे",
    badPhone: "कृपया सही 10 अंकों का मोबाइल नंबर डालें।",
    badPin: "पिन 4 अंकों का होना चाहिए।",
    pinMismatch: "दोनों पिन एक जैसे नहीं हैं।",
    needName: "कृपया अपना नाम डालें।",
    needOtp: "कृपया 6 अंकों का OTP डालें।",
    wrongLogin: "मोबाइल नंबर या पिन गलत है।",
    offline: "सर्वर से संपर्क नहीं हुआ। इंटरनेट जाँचें (पहली बार सर्वर शुरू होने में 1 मिनट लग सकता है)।",
  },
  en: {
    login: "Login",
    loginSub: "Enter your mobile number and 4-digit PIN",
    newHere: "First time? Create an account",
    forgot: "Forgot PIN?",
    otpTitle: "Verify mobile number",
    otpSub: "We will send a 6-digit OTP to this number",
    sendOtp: "Send OTP",
    codeTitle: "Enter OTP",
    codeSub: (p: string) => `6-digit code sent to ${p}`,
    verify: "Verify",
    resend: "Resend OTP",
    devOtp: "Demo mode: SMS service not connected yet. Your OTP is",
    newTitle: "New account",
    resetTitle: "Set a new PIN",
    welcomeBack: (n: string) => `Hello ${n}, set a new PIN`,
    name: "Your name",
    namePh: "e.g. Anita Kamble",
    newPin: "4-digit PIN",
    confirmPin: "Re-enter PIN",
    create: "Create account",
    savePin: "Save PIN",
    back: "← Back",
    badPhone: "Please enter a valid 10-digit mobile number.",
    badPin: "PIN must be 4 digits.",
    pinMismatch: "The two PINs do not match.",
    needName: "Please enter your name.",
    needOtp: "Please enter the 6-digit OTP.",
    wrongLogin: "Wrong mobile number or PIN.",
    offline: "Could not reach the server. Check internet (first start can take ~1 minute).",
  },
};

const digitsOnly = (v: string, max: number) => v.replace(/\D/g, "").slice(0, max);
const validPhone = (p: string) => /^[6-9]\d{9}$/.test(p);

const inputCls =
  "w-full pl-10 pr-3 py-3 rounded-xl border border-slate-300 text-base font-semibold text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 min-h-[52px] bg-white";

export const LoginScreen: React.FC<Props> = ({ lang, onLoginSuccess }) => {
  const t = translations[lang];
  const L = TXT[lang];
  const [mode, setMode] = useState<Mode>("login");
  const [phone, setPhone] = useState("");
  const [pin, setPin] = useState("");
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [setupToken, setSetupToken] = useState("");
  const [isNewUser, setIsNewUser] = useState(true);
  const [existingName, setExistingName] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [newPin, setNewPin] = useState("");
  const [newPin2, setNewPin2] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fail = (e: unknown, fallback?: string) => {
    if (e instanceof ApiError && e.status === 0) setError(L.offline);
    else if (fallback && e instanceof ApiError && e.status === 401) setError(fallback);
    else setError((e as Error).message);
  };

  const run = async (fn: () => Promise<void>) => {
    setError("");
    setLoading(true);
    try {
      await fn();
    } finally {
      setLoading(false);
    }
  };

  const go = (m: Mode) => {
    setError("");
    setMode(m);
  };

  const doLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validPhone(phone)) return setError(L.badPhone);
    if (pin.length !== 4) return setError(L.badPin);
    run(async () => {
      try {
        onLoginSuccess(await api.login(phone, pin));
      } catch (err) {
        fail(err, L.wrongLogin);
      }
    });
  };

  const sendOtp = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!validPhone(phone)) return setError(L.badPhone);
    run(async () => {
      try {
        if (firebaseEnabled()) {
          await firebaseSendOtp(phone, "otp-send-btn");
          setDevOtp(null);
        } else {
          const r = await api.requestOtp(phone);
          setDevOtp(r.dev_otp ?? null);
        }
        setOtp("");
        setMode("otp_code");
      } catch (err) {
        fail(err);
      }
    });
  };

  const verifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.length !== 6) return setError(L.needOtp);
    run(async () => {
      try {
        const r = firebaseEnabled()
          ? await api.verifyFirebase(await firebaseConfirmOtp(otp))
          : await api.verifyOtp(phone, otp);
        setSetupToken(r.setup_token);
        setIsNewUser(r.is_new_user);
        setExistingName(r.name);
        setNewPin("");
        setNewPin2("");
        setMode("set_pin");
      } catch (err) {
        fail(err);
      }
    });
  };

  const savePin = (e: React.FormEvent) => {
    e.preventDefault();
    if (isNewUser && !name.trim()) return setError(L.needName);
    if (newPin.length !== 4) return setError(L.badPin);
    if (newPin !== newPin2) return setError(L.pinMismatch);
    run(async () => {
      try {
        onLoginSuccess(await api.setPin(setupToken, newPin, isNewUser ? name.trim() : null, lang));
      } catch (err) {
        fail(err);
      }
    });
  };

  const PhoneField = (
    <div className="relative">
      <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
      <input
        id="phone"
        type="tel"
        inputMode="numeric"
        autoComplete="tel-national"
        value={phone}
        onChange={(e) => setPhone(digitsOnly(e.target.value, 10))}
        placeholder={t.phonePlaceholder}
        className={inputCls}
        aria-label={t.phoneLabel}
      />
    </div>
  );

  const PinField = (id: string, value: string, set: (v: string) => void, label: string) => (
    <div className="relative">
      <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
      <input
        id={id}
        type="password"
        inputMode="numeric"
        autoComplete={id === "pin" ? "current-password" : "new-password"}
        value={value}
        onChange={(e) => set(digitsOnly(e.target.value, 4))}
        placeholder={label}
        className={`${inputCls} tracking-[0.4em]`}
        aria-label={label}
      />
    </div>
  );

  const primaryBtn =
    "w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold text-sm shadow-sm transition min-h-[52px]";
  const linkBtn = "text-sm font-bold text-indigo-700 hover:underline min-h-[44px] px-1";

  return (
    <div className="p-4 sm:p-6 flex flex-col justify-center min-h-[80vh]">
      <div className="text-center mb-6">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-emerald-600 via-teal-600 to-indigo-600 flex items-center justify-center text-white font-black text-2xl shadow-md mb-3">
          अ
        </div>
        <h2 className="text-xl font-black text-slate-900 tracking-tight">{t.appName}</h2>
        <p className="text-xs text-slate-600 font-medium mt-1 max-w-[300px] mx-auto">
          {lang === "mr"
            ? "तुमच्या व्यवसायासाठी सरकारी योजना, कर्ज, अनुदान व बँक अहवाल"
            : lang === "hi"
              ? "आपके व्यवसाय के लिए सरकारी योजना, लोन, सब्सिडी और बैंक रिपोर्ट"
              : "Government schemes, loan, subsidy and a bank report for your business"}
        </p>
      </div>

      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        {mode === "login" && (
          <form onSubmit={doLogin} className="space-y-3">
            <div>
              <h3 className="text-base font-bold text-slate-900">{L.login}</h3>
              <p className="text-xs text-slate-500">{L.loginSub}</p>
            </div>
            {PhoneField}
            {PinField("pin", pin, setPin, t.pinPlaceholder)}
            <button type="submit" disabled={loading} className={primaryBtn}>
              {loading ? t.loading : L.login}
            </button>
            <div className="flex items-center justify-between pt-1">
              <button type="button" className={linkBtn} onClick={() => go("otp_phone")}>
                {L.newHere}
              </button>
              <button type="button" className={linkBtn} onClick={() => go("otp_phone")}>
                {L.forgot}
              </button>
            </div>
          </form>
        )}

        {mode === "otp_phone" && (
          <form onSubmit={sendOtp} className="space-y-3">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <MessageSquareText className="w-4 h-4 text-indigo-600" /> {L.otpTitle}
              </h3>
              <p className="text-xs text-slate-500">{L.otpSub}</p>
            </div>
            {PhoneField}
            <button id="otp-send-btn" type="submit" disabled={loading} className={primaryBtn}>
              {loading ? t.loading : L.sendOtp}
            </button>
            <button type="button" className={linkBtn} onClick={() => go("login")}>
              {L.back}
            </button>
          </form>
        )}

        {mode === "otp_code" && (
          <form onSubmit={verifyOtp} className="space-y-3">
            <div>
              <h3 className="text-base font-bold text-slate-900">{L.codeTitle}</h3>
              <p className="text-xs text-slate-500">{L.codeSub(phone)}</p>
            </div>
            {devOtp && (
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-300 text-xs text-amber-900">
                {L.devOtp}: <strong className="text-base tracking-widest">{devOtp}</strong>
              </div>
            )}
            <div className="relative">
              <KeyRound className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                id="otp"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                value={otp}
                onChange={(e) => setOtp(digitsOnly(e.target.value, 6))}
                placeholder="______"
                className={`${inputCls} tracking-[0.5em]`}
                aria-label={L.codeTitle}
              />
            </div>
            <button type="submit" disabled={loading} className={primaryBtn}>
              {loading ? t.loading : L.verify}
            </button>
            <div className="flex items-center justify-between">
              <button type="button" className={linkBtn} onClick={() => go("otp_phone")}>
                {L.back}
              </button>
              <button type="button" className={linkBtn} disabled={loading} onClick={() => sendOtp()}>
                {L.resend}
              </button>
            </div>
          </form>
        )}

        {mode === "set_pin" && (
          <form onSubmit={savePin} className="space-y-3">
            <div>
              <h3 className="text-base font-bold text-slate-900">{isNewUser ? L.newTitle : L.resetTitle}</h3>
              {!isNewUser && existingName && <p className="text-xs text-slate-500">{L.welcomeBack(existingName)}</p>}
            </div>
            {isNewUser && (
              <div className="relative">
                <UserRound className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  id="name"
                  type="text"
                  autoComplete="name"
                  value={name}
                  onChange={(e) => setName(e.target.value.slice(0, 100))}
                  placeholder={L.namePh}
                  className={inputCls}
                  aria-label={L.name}
                />
              </div>
            )}
            {PinField("new-pin", newPin, setNewPin, L.newPin)}
            {PinField("new-pin-2", newPin2, setNewPin2, L.confirmPin)}
            <button type="submit" disabled={loading} className={primaryBtn}>
              {loading ? t.loading : isNewUser ? L.create : L.savePin}
            </button>
          </form>
        )}

        {error && (
          <div role="alert" className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 font-medium">
            {error}
          </div>
        )}
      </div>

      <div className="mt-5 text-center">
        <span className="inline-flex items-center gap-1.5 text-[11px] text-emerald-800 font-semibold bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5" /> {t.dpdpProtectedBadge}
        </span>
      </div>
    </div>
  );
};
