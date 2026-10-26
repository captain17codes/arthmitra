export type Language = "mr" | "hi" | "en";

export interface Translations {
  appName: string;
  tagline: string;
  schemeBasis: string;
  healthStatus: string;
  dpdpNotice: string;
  languageSelect: string;
}

export const translations: Record<Language, Translations> = {
  mr: {
    appName: "अर्थमित्र",
    tagline: "ग्रामीण सूक्ष्म उद्योजकांसाठी एआय स्थानिक व्यवसाय सल्ला व वित्तीय रचना",
    schemeBasis: "सामाजिक न्याय व सक्षमीकरण मंत्रालय · एनएसएफडीसी सवलत योजना",
    healthStatus: "प्रणाली कार्यरत आहे",
    dpdpNotice: "डीपीडीपी कायदा २०२३ नुसार डेटा गोपनीयता व संमती सुरक्षित",
    languageSelect: "भाषा",
  },
  hi: {
    appName: "अर्थमित्र",
    tagline: "ग्रामीण सूक्ष्म उद्यमियों के लिए एआई हाइपर-लोकल व्यापार परामर्श एवं वित्तीय संरचना",
    schemeBasis: "सामाजिक न्याय और अधिकारिता मंत्रालय · एनएसएफडीसी रियायती योजनाएं",
    healthStatus: "सिस्टम सक्रिय है",
    dpdpNotice: "डीपीडीपी अधिनियम 2023 के तहत डेटा गोपनीयता एवं सहमति सुरक्षित",
    languageSelect: "भाषा",
  },
  en: {
    appName: "ArthMitra",
    tagline: "AI-Driven Hyper-Local Business Advisory & Financial Structuring for Rural Micro-Entrepreneurs",
    schemeBasis: "Ministry of Social Justice and Empowerment · NSFDC Lending Schemes",
    healthStatus: "System Operational",
    dpdpNotice: "DPDP Act 2023 Compliant · Zero Sensitive PII Stored",
    languageSelect: "Language",
  },
};

export function formatINR(val: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(val);
}
