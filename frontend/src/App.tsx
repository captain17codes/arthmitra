import React, { useEffect, useState } from "react";
import {
  BeneficiaryProfile,
  BusinessType,
  CalibrationData,
  CaseRecord,
  ConsentRecord,
  Language,
  User,
  Village,
} from "./types";
import { storage } from "./services/storage";
import { api } from "./services/api";
import { Header } from "./components/Header";
import { BottomNav, NavTab } from "./components/BottomNav";
import { LoginScreen } from "./screens/LoginScreen";
import { CaseListScreen } from "./screens/CaseListScreen";
import { ConsentScreen } from "./screens/ConsentScreen";
import { ProfileScreen } from "./screens/ProfileScreen";
import { VillagePickerScreen } from "./screens/VillagePickerScreen";
import { BusinessPickerScreen } from "./screens/BusinessPickerScreen";
import { CalibrationScreen } from "./screens/CalibrationScreen";
import { ResultsScreen } from "./screens/ResultsScreen";
import { DprScreen } from "./screens/DprScreen";
import { AgentProfileScreen } from "./screens/AgentProfileScreen";
import { SupervisorDashboardScreen } from "./screens/SupervisorDashboardScreen";
import { AdminSchemeEditorScreen } from "./screens/AdminSchemeEditorScreen";
import { AdminBenchmarkScreen } from "./screens/AdminBenchmarkScreen";
import { AdminVillageScreen } from "./screens/AdminVillageScreen";

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>(
    (storage.getLanguage() as Language) || "mr"
  );
  const [user, setUser] = useState<User | null>(storage.getUser());
  const [currentTab, setCurrentTab] = useState<NavTab>("cases");
  const [cases, setCases] = useState<CaseRecord[]>(storage.getCases());
  const [casesError, setCasesError] = useState<string>("");
  const [evalBusy, setEvalBusy] = useState<boolean>(false);
  const [evalError, setEvalError] = useState<string>("");
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);

  // Active view states
  const [selectedCase, setSelectedCase] = useState<CaseRecord | null>(null);
  const [viewingDpr, setViewingDpr] = useState<boolean>(false);
  const [adminSubView, setAdminSubView] = useState<
    "none" | "schemes" | "benchmarks" | "villages"
  >("none");

  // Wizard state for new case
  const [wizardStep, setWizardStep] = useState<
    "consent" | "profile" | "village" | "business" | "calibration"
  >("consent");
  const [draftConsent, setDraftConsent] = useState<ConsentRecord | null>(null);
  const [draftProfile, setDraftProfile] = useState<BeneficiaryProfile | null>(null);
  const [draftVillage, setDraftVillage] = useState<Village | null>(null);
  const [draftBusiness, setDraftBusiness] = useState<BusinessType | null>(null);
  const [draftCost, setDraftCost] = useState<number | null>(null);
  const [draftMargin, setDraftMargin] = useState<number | undefined>(undefined);

  const refreshCases = async () => {
    try {
      setCases(await api.getCases());
      setCasesError("");
    } catch (e) {
      setCasesError((e as Error).message);
      if (!storage.getToken()) setUser(null);
    }
  };

  useEffect(() => {
    if (user) refreshCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleSelectLang = (l: Language) => {
    setLang(l);
    storage.setLanguage(l);
  };

  const handleLoginSuccess = (u: User) => {
    setUser(u);
    setCurrentTab("cases");
  };

  const handleLogout = () => {
    storage.clearToken();
    storage.clearUser();
    storage.clearCases();
    setCases([]);
    setSelectedCase(null);
    setUser(null);
  };

  const startNewCase = () => {
    setSelectedCase(null);
    setViewingDpr(false);
    setDraftConsent(null);
    setDraftProfile(null);
    setDraftVillage(null);
    setDraftBusiness(null);
    setWizardStep("consent");
    setCurrentTab("new_case");
  };

  const handleConsentGranted = (c: { method?: string; audio_sha256?: string }) => {
    setDraftConsent({
      language: lang,
      method: c.method === "voice" ? "voice" : "tap",
      audio_sha256: c.audio_sha256,
    });
    setWizardStep("profile");
  };

  const handleSaveProfile = (p: BeneficiaryProfile) => {
    setDraftProfile(p);
    setWizardStep("village");
  };

  const handleSelectVillage = (v: Village) => {
    setDraftVillage(v);
    setWizardStep("business");
  };

  const handleConfirmBusiness = (b: BusinessType, cost: number | null, margin: number) => {
    setDraftBusiness(b);
    setDraftCost(cost);
    setDraftMargin(margin);
    setWizardStep("calibration");
  };

  const handleCompleteCalibration = async (calib: CalibrationData) => {
    if (!draftProfile || !draftVillage || !draftBusiness || !draftConsent || draftMargin === undefined) return;
    setEvalBusy(true);
    setEvalError("");
    try {
      const created = await api.createAndEvaluateCase({
        profile: draftProfile,
        consent: draftConsent,
        village: draftVillage,
        business: draftBusiness,
        margin: draftMargin,
        targetProjectCost: draftCost,
        calibration: calib,
        language: lang,
      });
      await refreshCases();
      setSelectedCase(created);
      setViewingDpr(false);
      setCurrentTab("cases");
    } catch (e) {
      // Stay on the wizard with all entered data so the agent can retry.
      setEvalError((e as Error).message);
    } finally {
      setEvalBusy(false);
    }
  };

  const openCase = async (c: CaseRecord) => {
    setViewingDpr(false);
    setSelectedCase(c);
    try {
      setSelectedCase(await api.getCase(c.id));
    } catch (e) {
      setCasesError((e as Error).message);
    }
  };

  const handleCaseUpdated = (updated: CaseRecord) => {
    setSelectedCase(updated);
    refreshCases();
  };

  return (
    <div className="mobile-viewport bg-slate-50 border-x border-slate-200 flex flex-col min-h-screen shadow-lg">
      {/* Header */}
      <Header
        lang={lang}
        onSelectLang={handleSelectLang}
        user={user}
        onLogout={handleLogout}
        isOnline={isOnline}
      />

      {/* Main Container */}
      <main className="flex-1 overflow-y-auto">
        {!user ? (
          <LoginScreen lang={lang} onLoginSuccess={handleLoginSuccess} />
        ) : currentTab === "profile" ? (
          <AgentProfileScreen
            user={user}
            cases={cases}
            onLogout={handleLogout}
            lang={lang}
          />
        ) : currentTab === "supervisor" ? (
          adminSubView === "schemes" ? (
            <AdminSchemeEditorScreen
              onBack={() => setAdminSubView("none")}
              lang={lang}
            />
          ) : adminSubView === "benchmarks" ? (
            <AdminBenchmarkScreen
              onBack={() => setAdminSubView("none")}
              lang={lang}
            />
          ) : adminSubView === "villages" ? (
            <AdminVillageScreen
              onBack={() => setAdminSubView("none")}
              lang={lang}
            />
          ) : (
            <SupervisorDashboardScreen
              user={user}
              cases={cases}
              onOpenSchemeEditor={() => setAdminSubView("schemes")}
              onOpenBenchmarkEditor={() => setAdminSubView("benchmarks")}
              onOpenVillageCoords={() => setAdminSubView("villages")}
              lang={lang}
            />
          )
        ) : currentTab === "new_case" ? (
          /* New Case Wizard */
          <div>
            {wizardStep === "consent" && (
              <ConsentScreen
                lang={lang}
                onConsentGranted={handleConsentGranted}
                onBack={() => setCurrentTab("cases")}
              />
            )}
            {wizardStep === "profile" && (
              <ProfileScreen
                lang={lang}
                initialProfile={draftProfile || undefined}
                onSaveProfile={handleSaveProfile}
                onBack={() => setWizardStep("consent")}
              />
            )}
            {wizardStep === "village" && (
              <VillagePickerScreen
                lang={lang}
                selectedVillage={draftVillage || undefined}
                onSelectVillage={handleSelectVillage}
                onBack={() => setWizardStep("profile")}
              />
            )}
            {wizardStep === "business" && (
              <BusinessPickerScreen
                lang={lang}
                selectedBusinessCode={draftBusiness?.code}
                initialProjectCost={draftCost}
                initialMargin={draftMargin}
                onConfirmBusiness={handleConfirmBusiness}
                onBack={() => setWizardStep("village")}
              />
            )}
            {wizardStep === "calibration" && draftBusiness && (
              <CalibrationScreen
                lang={lang}
                business={draftBusiness}
                onEvaluate={handleCompleteCalibration}
                onBack={() => setWizardStep("business")}
                busy={evalBusy}
                error={evalError}
              />
            )}
          </div>
        ) : selectedCase ? (
          viewingDpr ? (
            <DprScreen
              caseRecord={selectedCase}
              onUpdateCase={handleCaseUpdated}
              onBack={() => setViewingDpr(false)}
              lang={lang}
            />
          ) : (
            <ResultsScreen
              caseRecord={selectedCase}
              onCaseUpdated={handleCaseUpdated}
              onGoToDpr={() => setViewingDpr(true)}
              lang={lang}
            />
          )
        ) : (
          <CaseListScreen
            cases={cases}
            error={casesError}
            onRefresh={refreshCases}
            onSelectCase={openCase}
            onNewCase={startNewCase}
            lang={lang}
          />
        )}
      </main>

      {/* Persistent Bottom Nav (when logged in) */}
      {user && (
        <BottomNav
          currentTab={currentTab}
          onSelectTab={(tab) => {
            if (tab === "new_case") {
              startNewCase();
            } else {
              setSelectedCase(null);
              setViewingDpr(false);
              setAdminSubView("none");
              setCurrentTab(tab);
            }
          }}
          lang={lang}
        />
      )}
    </div>
  );
};

export default App;
