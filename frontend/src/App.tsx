import React, { useEffect, useState } from "react";
import {
  BeneficiaryProfile,
  BusinessType,
  CalibrationData,
  CaseRecord,
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
  const [, setDraftConsent] = useState<any>(null);
  const [draftProfile, setDraftProfile] = useState<BeneficiaryProfile | null>(null);
  const [draftVillage, setDraftVillage] = useState<Village | null>(null);
  const [draftBusiness, setDraftBusiness] = useState<BusinessType | null>(null);
  const [draftCost, setDraftCost] = useState<number>(150000);
  const [draftMargin, setDraftMargin] = useState<number>(15000);

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

  const handleConsentGranted = (c: any) => {
    setDraftConsent(c);
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

  const handleConfirmBusiness = (b: BusinessType, cost: number, margin: number) => {
    setDraftBusiness(b);
    setDraftCost(cost);
    setDraftMargin(margin);
    setWizardStep("calibration");
  };

  const handleCompleteCalibration = async (calib: CalibrationData) => {
    if (!draftProfile || !draftVillage || !draftBusiness) return;

    const newRecord: CaseRecord = {
      id: `case_${Date.now()}`,
      beneficiary_id: `ben_${Date.now()}`,
      beneficiary: draftProfile,
      village_id: draftVillage.id,
      village: draftVillage,
      business_code: draftBusiness.code,
      business: draftBusiness,
      target_project_cost: draftCost,
      margin_available: draftMargin,
      calibration: calib,
      status: "ready",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Evaluate
    const evalRes = await api.evaluateCase(newRecord, calib.udhar_pct || 15);
    newRecord.evaluation = evalRes;
    const saved = await api.saveCase(newRecord);

    setCases(storage.getCases());
    setSelectedCase(saved);
    setCurrentTab("cases");
  };

  const handleCaseUpdated = (updated: CaseRecord) => {
    setSelectedCase(updated);
    setCases(storage.getCases());
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
              />
            )}
          </div>
        ) : selectedCase ? (
          viewingDpr ? (
            <DprScreen
              caseRecord={selectedCase}
              evaluation={selectedCase.evaluation!}
              onUpdateCase={handleCaseUpdated}
              onBack={() => setViewingDpr(false)}
              lang={lang}
            />
          ) : (
            <ResultsScreen
              caseRecord={selectedCase}
              evaluation={selectedCase.evaluation!}
              onUpdateCase={handleCaseUpdated}
              onGoToDpr={() => setViewingDpr(true)}
              onBack={() => setSelectedCase(null)}
              lang={lang}
            />
          )
        ) : (
          <CaseListScreen
            cases={cases}
            onSelectCase={(c) => {
              setSelectedCase(c);
              setViewingDpr(false);
            }}
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
