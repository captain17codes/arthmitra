import React, { useState } from "react";
import { UserCheck } from "lucide-react";
import {
  BeneficiaryProfile,
  EducationLevel,
  Gender,
  Language,
  SocialCategory,
} from "../types";
import { translations } from "../i18n";
import { VoiceFieldInput } from "../components/VoiceFieldInput";

interface Props {
  initialProfile?: Partial<BeneficiaryProfile>;
  onSaveProfile: (profile: BeneficiaryProfile) => void;
  onBack: () => void;
  lang: Language;
}

export const ProfileScreen: React.FC<Props> = ({
  initialProfile,
  onSaveProfile,
  onBack,
  lang,
}) => {
  const t = translations[lang];

  const [firstName, setFirstName] = useState(initialProfile?.first_name || "अनिता कांबळे");
  const [gender, setGender] = useState<Gender>(initialProfile?.gender || "female");
  const [age, setAge] = useState<number>(initialProfile?.age || 32);
  const [category, setCategory] = useState<SocialCategory>(
    initialProfile?.category || "SC"
  );
  const [disability40, setDisability40] = useState<boolean>(
    initialProfile?.disability_40 || false
  );
  const [sanitationWorker, setSanitationWorker] = useState<boolean>(
    initialProfile?.sanitation_worker || false
  );
  const [traditionalArtisan, setTraditionalArtisan] = useState<boolean>(
    initialProfile?.traditional_artisan || false
  );
  const [streetVendor, setStreetVendor] = useState<boolean>(
    initialProfile?.street_vendor || false
  );
  const [annualIncome, setAnnualIncome] = useState<number>(
    initialProfile?.annual_income || 120000
  );
  const [education, setEducation] = useState<EducationLevel>(
    initialProfile?.education || "secondary_10th"
  );
  const [priorSubsidy, setPriorSubsidy] = useState<boolean>(
    initialProfile?.prior_subsidy || false
  );
  const [existingEmi, setExistingEmi] = useState<number>(
    initialProfile?.existing_emi || 0
  );
  const [creditDefault, setCreditDefault] = useState<"no" | "yes" | "unknown">(
    initialProfile?.credit_default || "no"
  );
  const [shgMember, setShgMember] = useState<boolean>(
    initialProfile?.shg_member !== undefined ? initialProfile.shg_member : true
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveProfile({
      first_name: firstName,
      gender,
      age,
      category,
      disability_40: disability40,
      sanitation_worker: sanitationWorker,
      traditional_artisan: traditionalArtisan,
      street_vendor: streetVendor,
      annual_income: annualIncome,
      education,
      prior_subsidy: priorSubsidy,
      existing_emi: existingEmi,
      credit_default: creditDefault,
      shg_member: shgMember,
    });
  };

  return (
    <div className="p-4 space-y-4">
      {/* Step Header */}
      <div>
        <span className="text-[10px] uppercase font-bold text-indigo-700 tracking-wider bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
          पायरी २ / ५ · उद्योजक प्रोफाइल
        </span>
        <h2 className="text-base font-black text-slate-900 mt-1 flex items-center gap-1.5">
          <UserCheck className="w-4 h-4 text-indigo-600" />
          {t.profileTitle}
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">
            {t.firstNameLabel} *
          </label>
          <input
            type="text"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder={t.firstNamePlaceholder}
            className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 min-h-[48px]"
            required
          />
        </div>

        {/* Gender & Age */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.genderLabel}
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value as Gender)}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-900 bg-white min-h-[48px]"
            >
              <option value="female">{t.genderFemale}</option>
              <option value="male">{t.genderMale}</option>
              <option value="other">{t.genderOther}</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.ageLabel} (18-65)
            </label>
            <input
              type="number"
              min={18}
              max={70}
              value={age}
              onChange={(e) => setAge(parseInt(e.target.value) || 18)}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-900 min-h-[48px]"
              required
            />
          </div>
        </div>

        {/* Social Category */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">
            {t.categoryLabel} *
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(["SC", "ST", "OBC", "VJNT", "SBC", "General"] as SocialCategory[]).map(
              (cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategory(cat)}
                  className={`py-2 px-2 rounded-xl text-xs font-bold border transition min-h-[44px] ${
                    category === cat
                      ? "bg-indigo-600 text-white border-indigo-700 shadow-xs"
                      : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  {cat}
                </button>
              )
            )}
          </div>
        </div>

        {/* Special Occupation Flags */}
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
          <span className="block text-xs font-bold text-slate-800">
            {t.occupationFlagsLabel}
          </span>
          <div className="space-y-1.5">
            <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={sanitationWorker}
                onChange={(e) => setSanitationWorker(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600"
              />
              <span>{t.sanitationWorker}</span>
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={traditionalArtisan}
                onChange={(e) => setTraditionalArtisan(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600"
              />
              <span>{t.traditionalArtisan}</span>
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={streetVendor}
                onChange={(e) => setStreetVendor(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600"
              />
              <span>{t.streetVendor}</span>
            </label>
          </div>
        </div>

        {/* Disability & SHG Membership */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <span className="block text-[11px] font-bold text-slate-700">
              {t.disabilityLabel}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setDisability40(false)}
                className={`flex-1 py-1 px-2 rounded-lg text-xs font-bold border ${
                  !disability40
                    ? "bg-white text-slate-900 border-slate-400 shadow-2xs"
                    : "bg-slate-100 text-slate-500 border-transparent"
                }`}
              >
                {t.no}
              </button>
              <button
                type="button"
                onClick={() => setDisability40(true)}
                className={`flex-1 py-1 px-2 rounded-lg text-xs font-bold border ${
                  disability40
                    ? "bg-indigo-600 text-white border-indigo-700"
                    : "bg-slate-100 text-slate-500 border-transparent"
                }`}
              >
                {t.yes}
              </button>
            </div>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <span className="block text-[11px] font-bold text-slate-700">
              {t.shgMemberLabel}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShgMember(true)}
                className={`flex-1 py-1 px-2 rounded-lg text-xs font-bold border ${
                  shgMember
                    ? "bg-emerald-600 text-white border-emerald-700"
                    : "bg-slate-100 text-slate-500 border-transparent"
                }`}
              >
                {t.yes}
              </button>
              <button
                type="button"
                onClick={() => setShgMember(false)}
                className={`flex-1 py-1 px-2 rounded-lg text-xs font-bold border ${
                  !shgMember
                    ? "bg-white text-slate-900 border-slate-400 shadow-2xs"
                    : "bg-slate-100 text-slate-500 border-transparent"
                }`}
              >
                {t.no}
              </button>
            </div>
          </div>
        </div>

        {/* Annual Income & Education */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.annualIncomeLabel} (₹)
            </label>
            <input
              type="number"
              step={10000}
              value={annualIncome}
              onChange={(e) => setAnnualIncome(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-900 min-h-[48px]"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.educationLabel}
            </label>
            <select
              value={education}
              onChange={(e) => setEducation(e.target.value as EducationLevel)}
              className="w-full px-2 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-900 bg-white min-h-[48px]"
            >
              <option value="illiterate">{t.educationIlliterate}</option>
              <option value="primary">{t.educationPrimary}</option>
              <option value="middle_8th">{t.educationMiddle}</option>
              <option value="secondary_10th">{t.educationSecondary}</option>
              <option value="higher_secondary_12th">{t.educationHigherSec}</option>
              <option value="graduate">{t.educationGraduate}</option>
            </select>
          </div>
        </div>

        {/* Existing EMI & Prior Subsidy */}
        <div className="space-y-3">
          <div>
            <VoiceFieldInput
              label={t.existingEmiLabel}
              type="number"
              step={500}
              value={existingEmi}
              onChange={(val) => setExistingEmi(Number(val) || 0)}
              language={lang}
              suffix="₹/महिना"
              placeholder="0"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {t.priorSubsidyLabel}
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPriorSubsidy(false)}
                className={`flex-1 py-2 px-2 rounded-xl text-xs font-bold border min-h-[48px] ${
                  !priorSubsidy
                    ? "bg-white text-slate-900 border-slate-400 shadow-2xs"
                    : "bg-slate-100 text-slate-500 border-transparent"
                }`}
              >
                {t.no}
              </button>
              <button
                type="button"
                onClick={() => setPriorSubsidy(true)}
                className={`flex-1 py-2 px-2 rounded-xl text-xs font-bold border min-h-[48px] ${
                  priorSubsidy
                    ? "bg-amber-600 text-white border-amber-700"
                    : "bg-slate-100 text-slate-500 border-transparent"
                }`}
              >
                {t.yes}
              </button>
            </div>
          </div>
        </div>

        {/* Credit Default Status */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">
            {t.creditDefaultLabel}
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: "no", label: t.creditDefaultNo },
              { id: "yes", label: t.creditDefaultYes },
              { id: "unknown", label: t.creditDefaultUnknown },
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setCreditDefault(opt.id as any)}
                className={`py-2 px-1 rounded-xl text-xs font-bold border transition min-h-[44px] ${
                  creditDefault === opt.id
                    ? opt.id === "yes"
                      ? "bg-red-600 text-white border-red-700"
                      : "bg-indigo-600 text-white border-indigo-700"
                    : "bg-white text-slate-700 border-slate-200"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="pt-2 flex items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="flex-1 py-3 px-4 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition min-h-[48px]"
          >
            {t.back}
          </button>
          <button
            type="submit"
            className="flex-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition min-h-[48px]"
          >
            {t.next} →
          </button>
        </div>
      </form>
    </div>
  );
};
