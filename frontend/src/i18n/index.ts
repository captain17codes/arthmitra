import { Language } from "../types";

export interface Translations {
  appName: string;
  tagline: string;
  schemeBasis: string;
  healthStatus: string;
  dpdpNotice: string;
  languageSelect: string;
  back: string;
  next: string;
  save: string;
  submit: string;
  cancel: string;
  retry: string;
  loading: string;
  error: string;
  success: string;
  all: string;
  search: string;
  filter: string;
  online: string;
  offline: string;
  offlineNotice: string;
  yes: string;
  no: string;

  // Auth
  loginTitle: string;
  loginSubtitle: string;
  phoneLabel: string;
  phonePlaceholder: string;
  pinLabel: string;
  pinPlaceholder: string;
  loginBtn: string;
  logoutBtn: string;
  agentRole: string;
  agentOrg: string;

  // Case List
  casesTitle: string;
  newCaseBtn: string;
  searchCasesPlaceholder: string;
  emptyCases: string;
  emptyCasesSub: string;
  beneficiary: string;
  village: string;
  business: string;
  status: string;
  createdOn: string;
  viewDetails: string;
  statusDraft: string;
  statusReady: string;
  statusDpr: string;
  statusApplied: string;
  statusSanctioned: string;
  statusRejected: string;
  statusDisbursed: string;
  statusClosed: string;

  // Consent Screen
  consentTitle: string;
  statutoryHeader: string;
  statutoryBody: string;
  statutoryVoicePrompt: string;
  voiceConsentBtn: string;
  paperConsentBtn: string;
  otpConsentBtn: string;
  consentGrantedNotice: string;
  dpdpProtectedBadge: string;
  zeroPiiNotice: string;
  proceedToProfile: string;

  // Beneficiary Profile
  profileTitle: string;
  firstNameLabel: string;
  firstNamePlaceholder: string;
  genderLabel: string;
  genderFemale: string;
  genderMale: string;
  genderOther: string;
  ageLabel: string;
  categoryLabel: string;
  disabilityLabel: string;
  occupationFlagsLabel: string;
  sanitationWorker: string;
  traditionalArtisan: string;
  streetVendor: string;
  noneOccupation: string;
  annualIncomeLabel: string;
  educationLabel: string;
  educationIlliterate: string;
  educationPrimary: string;
  educationMiddle: string;
  educationSecondary: string;
  educationHigherSec: string;
  educationGraduate: string;
  priorSubsidyLabel: string;
  existingEmiLabel: string;
  creditDefaultLabel: string;
  creditDefaultNo: string;
  creditDefaultYes: string;
  creditDefaultUnknown: string;
  shgMemberLabel: string;

  // Village Picker
  villagePickerTitle: string;
  searchVillagePlaceholder: string;
  populationLabel: string;
  amenitiesLabel: string;
  selectVillageBtn: string;

  // Business Picker
  businessPickerTitle: string;
  selectBusinessHint: string;
  targetCostLabel: string;
  marginAvailableLabel: string;
  marginHint: string;

  // Calibration
  calibrationTitle: string;
  calibrationSubtitle: string;
  competitorsNearLabel: string;
  dailyCustomersLabel: string;
  monthlyRentLabel: string;
  ownPremisesLabel: string;
  milchAnimalsLabel: string;
  milkRateLabel: string;
  fodderAvailableLabel: string;
  goatHerdLabel: string;
  tailoringMachinesLabel: string;
  calculateViabilityBtn: string;

  // Results Screen
  evaluationResultsTitle: string;
  tabMarket: string;
  tabFinancing: string;
  tabViability: string;
  tabAdvisory: string;
  tabDpr: string;

  // Market Card
  marketCardTitle: string;
  catchmentPopLabel: string;
  monthlyDemandLabel: string;
  reportedCompetitorsLabel: string;
  bepMarketShareLabel: string;
  saturationBandLabel: string;
  satLow: string;
  satMed: string;
  satHigh: string;
  complementaryTitle: string;

  // Financing Card
  financingCardTitle: string;
  topSchemesSubtitle: string;
  projectCostLabel: string;
  ownMarginLabel: string;
  loanLabel: string;
  subsidyLabel: string;
  interestRateLabel: string;
  tenureLabel: string;
  moratoriumLabel: string;
  monthlyEmiLabel: string;
  firstEmiDateLabel: string;
  totalRepaymentLabel: string;
  viewScheduleBtn: string;
  ineligibleSchemesTitle: string;
  scheduleModalTitle: string;
  scheduleMonth: string;
  schedulePrincipal: string;
  scheduleInterest: string;
  scheduleTotal: string;
  scheduleBalance: string;

  // Viability Card
  viabilityCardTitle: string;
  dscrLabel: string;
  dscrBenchmarkHint: string;
  bepLabel: string;
  nayakWorkingCapitalLabel: string;
  udharSliderLabel: string;
  udharAdjustedDscrHint: string;
  incomeTimingWarningTitle: string;
  projections5yrTitle: string;
  yearCol: string;
  revenueCol: string;
  surplusCol: string;

  // Advisory Card
  advisoryCardTitle: string;
  marketReachTitle: string;
  opportunitiesTitle: string;
  swotStrengths: string;
  swotWeaknesses: string;
  swotOpportunities: string;
  swotThreats: string;
  pricingTitle: string;
  nextStepsTitle: string;

  // DPR Screen
  dprCardTitle: string;
  dprSubtitle: string;
  downloadMarathiPdfBtn: string;
  downloadEnglishPdfBtn: string;
  sha256Label: string;
  bankChecklistTitle: string;
  bankChecklistDoc1: string;
  bankChecklistDoc2: string;
  bankChecklistDoc3: string;
  bankChecklistDoc4: string;
  portalToApplyTitle: string;
  portalHint: string;
  updateStatusBtn: string;
}

export const translations: Record<Language, Translations> = {
  mr: {
    appName: "अर्थमित्र",
    tagline: "ग्रामीण सूक्ष्म उद्योजकांसाठी एआय स्थानिक व्यवसाय सल्ला व वित्तीय रचना",
    schemeBasis: "सामाजिक न्याय व सक्षमीकरण मंत्रालय · शासकीय सवलत योजना",
    healthStatus: "प्रणाली कार्यरत आहे",
    dpdpNotice: "डीपीडीपी कायदा २०२३ नुसार डेटा गोपनीयता व संमती सुरक्षित",
    languageSelect: "भाषा",
    back: "मागे",
    next: "पुढे",
    save: "जतन करा",
    submit: "प्रस्तुत करा",
    cancel: "रद्द करा",
    retry: "पुन्हा प्रयत्न करा",
    loading: "प्रक्रिया सुरू आहे...",
    error: "त्रुटी आढळली",
    success: "यशस्वी झाले",
    all: "सर्व",
    search: "शोधा",
    filter: "गाळणी",
    online: "ऑनलाइन",
    offline: "ऑफलाइन",
    offlineNotice: "इंटरनेट उपलब्ध नाही. माहिती स्थानिक मेमरीमध्ये सुरक्षित ठेवली जाईल.",
    yes: "होय",
    no: "नाही",

    // Auth
    loginTitle: "लॉगिन",
    loginSubtitle: "आपला मोबाईल क्रमांक व ४ अंकी पिन प्रविष्ट करा",
    phoneLabel: "मोबाईल क्रमांक",
    phonePlaceholder: "१० अंकी मोबाईल क्रमांक",
    pinLabel: "सुरक्षित पिन",
    pinPlaceholder: "४ अंकी पिन",
    loginBtn: "लॉगिन करा",
    logoutBtn: "लॉगआउट",
    agentRole: "माझे खाते",
    agentOrg: "अर्थमित्र · वैयक्तिक खाते",

    // Cases
    casesTitle: "माझे व्यवसाय प्लॅन",
    newCaseBtn: "+ नवीन व्यवसाय प्लॅन",
    searchCasesPlaceholder: "व्यवसाय किंवा गावानुसार शोधा...",
    emptyCases: "अजून कोणताही प्लॅन नाही",
    emptyCasesSub: "तुमच्या व्यवसायासाठी योजना, कर्ज व हप्ता पाहण्यासाठी वरील बटन दाबा",
    beneficiary: "उद्योजक",
    village: "गाव",
    business: "व्यवसाय",
    status: "स्थिती",
    createdOn: "तारीख",
    viewDetails: "तपशील पहा",
    statusDraft: "मसुदा (Draft)",
    statusReady: "तयार (Ready)",
    statusDpr: "डीपीआर तयार (DPR Ready)",
    statusApplied: "बँकेत सादर (Applied)",
    statusSanctioned: "मंजूर (Sanctioned)",
    statusRejected: "नाकारले (Rejected)",
    statusDisbursed: "वितरित (Disbursed)",
    statusClosed: "बंद (Closed)",

    // Consent
    consentTitle: "डीपीडीपी वैधानिक संमती (DPDP Consent)",
    statutoryHeader: "वैयक्तिक डेटा संमती सूचना (कलम ५, डीपीडीपी कायदा २०२३)",
    statutoryBody:
      "मी याद्वारे अर्थमित्रला माझी शासकीय योजना पात्रता, सूक्ष्म व्यवसाय व्यवहार्यता आणि बँक कर्ज डीपीआर तयार करण्यासाठी आवश्यक माहिती गोळा व प्रक्रिया करण्याची संमती देत आहे. मला समजले आहे की माझा आधार, पॅन किंवा बँक खाते क्रमांक येथे साठवला जात नाही.",
    statutoryVoicePrompt: "सूचना वाचा किंवा ऐका, आणि सहमत असल्यास खाली टिक करा:",
    voiceConsentBtn: "🎙️ 'होय, मी सहमत आहे' आवाजी संमती",
    paperConsentBtn: "स्वाक्षरी / अंगठा संमती फॉर्म",
    otpConsentBtn: "एसएमएस ओटीपी संमती",
    consentGrantedNotice: "कायदेशीर संमती यशस्वीरीत्या नोंदवली गेली आहे.",
    dpdpProtectedBadge: "डीपीडीपी कायदा २०२३ अंतर्गत सुरक्षित",
    zeroPiiNotice: "शून्य आधार · शून्य पॅन · संपूर्ण डेटा एन्क्रिप्टेड",
    proceedToProfile: "पुढे: माझी माहिती →",

    // Profile
    profileTitle: "तुमची माहिती",
    firstNameLabel: "तुमचे नाव",
    firstNamePlaceholder: "उदा. अनिता कांबळे",
    genderLabel: "लिंग",
    genderFemale: "स्त्री (Female)",
    genderMale: "पुरुष (Male)",
    genderOther: "इतर (Other)",
    ageLabel: "वय (वर्षे)",
    categoryLabel: "सामाजिक प्रवर्ग",
    disabilityLabel: "दिव्यांगत्व (४०% किंवा अधिक)",
    occupationFlagsLabel: "विशेष व्यवसाय प्रवर्ग (लागू असल्यास)",
    sanitationWorker: "सफाई कामगार / वारसदार",
    traditionalArtisan: "पारंपारिक कारागीर / हस्तकला",
    streetVendor: "फेरीवाला / पथविक्रेता",
    noneOccupation: "सामान्य / लागू नाही",
    annualIncomeLabel: "कौटुंबिक वार्षिक उत्पन्न",
    educationLabel: "शिक्षण",
    educationIlliterate: "अशिक्षित / निरक्षर",
    educationPrimary: "प्राथमिक (१ ली ते ४ थी)",
    educationMiddle: "माध्यमिक (८ वी उत्तीर्ण)",
    educationSecondary: "१० वी उत्तीर्ण",
    educationHigherSec: "१२ वी उत्तीर्ण",
    educationGraduate: "पदवीधर व पुढे",
    priorSubsidyLabel: "पूर्वी शासकीय अनुदानाचा लाभ घेतला आहे का?",
    existingEmiLabel: "सध्याचे चालू मासिक कर्ज हप्ते (EMI रु.)",
    creditDefaultLabel: "पूर्वीच्या कर्जाची थकबाकी / डिफॉल्ट",
    creditDefaultNo: "नाही (स्वच्छ इतिहास)",
    creditDefaultYes: "होय (थकबाकी आहे)",
    creditDefaultUnknown: "माहित नाही / नवीन ग्राहक",
    shgMemberLabel: "महिला बचत गट (SHG) सदस्य आहात का?",

    // Village Picker
    villagePickerTitle: "उद्योगाचे कार्यक्षेत्र / गाव निवडा",
    searchVillagePlaceholder: "गावाचे नाव टाईप करा (मराठी किंवा English)...",
    populationLabel: "लोकसंख्या",
    amenitiesLabel: "नागरी सुविधा",
    selectVillageBtn: "हे गाव निवडा",

    // Business Picker
    businessPickerTitle: "सूक्ष्म व्यवसायाचा प्रकार निवडा",
    selectBusinessHint: "स्थानिक मागणी व कौशल्य यानुसार खालीलपैकी एका व्यवसायाची निवड करा:",
    targetCostLabel: "अपेक्षित प्रकल्प खर्च (रु.)",
    marginAvailableLabel: "स्वतःचे उपलब्ध भांडवल / मार्जिन (रु.)",
    marginHint: "किमान ५% ते १५% स्वतःचे भांडवल आवश्यक असते.",

    // Calibration
    calibrationTitle: "स्थानिक बाजार व क्षमता तपासणी",
    calibrationSubtitle: "अचूक व्यवहार्यता व बाजार विश्लेषण करण्यासाठी खालील स्थानिक माहिती नोंदवा:",
    competitorsNearLabel: "गावात किंवा चालण्याच्या अंतरात अस्तित्वात असलेली अशीच दुकाने/स्पर्धक",
    dailyCustomersLabel: "अपेक्षित दैनंदिन ग्राहक / कामाचे प्रमाण",
    monthlyRentLabel: "दुकान / जागेचे मासिक भाडे (रु., स्वतःची असल्यास ०)",
    ownPremisesLabel: "जागा स्वतःच्या मालकीची आहे का?",
    milchAnimalsLabel: "दुभती जनावरे संख्या (गायी/म्हशी)",
    milkRateLabel: "डेअरीचा सरासरी दूध खरेदी दर (रु./लिटर)",
    fodderAvailableLabel: "स्वतःच्या शेतात चारा उपलब्ध आहे का?",
    goatHerdLabel: "शेळ्यांची संख्या (उदा. १०+१)",
    tailoringMachinesLabel: "शिलाई मशिन संख्या",
    calculateViabilityBtn: "व्यवहार्यता व कर्ज योजना तपासा →",

    // Results
    evaluationResultsTitle: "व्यवसाय व्यवहार्यता व कर्ज रचना अहवाल",
    tabMarket: "बाजारपेठ (Market)",
    tabFinancing: "कर्ज योजना (Financing)",
    tabViability: "व्यवहार्यता (Viability)",
    tabAdvisory: "एआय सल्ला (Advisory)",
    tabDpr: "डीपीआर (Bank DPR)",

    // Market Card
    marketCardTitle: "स्थानिक बाजार मागणी व स्पर्धा विश्लेषण",
    catchmentPopLabel: "कवर होणारी स्थानिक लोकसंख्या",
    monthlyDemandLabel: "गावातील या वस्तूंचा मासिक खर्च",
    reportedCompetitorsLabel: "नोंदवलेले स्थानिक स्पर्धक",
    bepMarketShareLabel: "नफा मिळवण्यासाठी आवश्यक बाजार हिस्सा",
    saturationBandLabel: "बाजार संपृक्तता पातळी (Saturation)",
    satLow: "कमी स्पर्धा · व्यवसायासाठी उत्तम संधी",
    satMed: "मध्यम स्पर्धा · विशिष्ट सेवा दिल्यास फायदा",
    satHigh: "उच्च स्पर्धा · बाजार संपृक्त · अतिरिक्त सेवा आवश्यक",
    complementaryTitle: "पर्यायी व पूरक व्यवसाय शिफारसी",

    // Financing Card
    financingCardTitle: "सर्वोत्तम शासकीय कर्ज व अनुदान योजना (Top 3)",
    topSchemesSubtitle: "शासकीय नियमांनुसार क्रमवारी लावलेली कर्ज रचना:",
    projectCostLabel: "एकूण प्रकल्प खर्च",
    ownMarginLabel: "स्वतःचे भांडवल (मार्जिन)",
    loanLabel: "बँक कर्ज रक्कम",
    subsidyLabel: "शासकीय अनुदान (Subsidy)",
    interestRateLabel: "व्याज दर (वार्षिक)",
    tenureLabel: "कर्ज परतफेड मुदत",
    moratoriumLabel: "सवलतीचा काळ (Moratorium)",
    monthlyEmiLabel: "मासिक हप्ता (EMI)",
    firstEmiDateLabel: "पहिला हप्ता देय तारीख",
    totalRepaymentLabel: "एकूण परतफेड रक्कम",
    viewScheduleBtn: "हप्ते तक्ता (Schedule) पहा",
    ineligibleSchemesTitle: "पात्र नसलेल्या योजना व कारणे",
    scheduleModalTitle: "मासिक हप्ता परतफेड तक्ता (Amortization Schedule)",
    scheduleMonth: "महिना",
    schedulePrincipal: "मुद्दल (रु.)",
    scheduleInterest: "व्याज (रु.)",
    scheduleTotal: "एकूण हप्ता (रु.)",
    scheduleBalance: "शिल्लक मुद्दल (रु.)",

    // Viability Card
    viabilityCardTitle: "आर्थिक व्यवहार्यता व ताण चाचणी (Stress Test)",
    dscrLabel: "कर्ज परतफेड क्षमता (DSCR)",
    dscrBenchmarkHint: "बँक निकष: १.५०x किंवा अधिक सुरक्षित मानले जाते.",
    bepLabel: "ब्रेक-इव्हन क्षमता (BEP)",
    nayakWorkingCapitalLabel: "नायक समिती खेळते भांडवल शिफारस",
    udharSliderLabel: "उधारीचे प्रमाण ताण चाचणी (Udhar / Credit %):",
    udharAdjustedDscrHint: "उधारी वाढल्यास रोख प्रवाह व DSCR वर होणारा परिणाम तपासा.",
    incomeTimingWarningTitle: "उत्पन्न कालावधी चेतावणी (Income-Timing Alert)",
    projections5yrTitle: "५ वर्षांचे अंदाजित उत्पन्न व नफा तक्ता",
    yearCol: "वर्ष",
    revenueCol: "वार्षिक उत्पन्न",
    surplusCol: "निव्वळ शिल्लक",

    // Advisory Card
    advisoryCardTitle: "स्थानिक व्यवसाय वाढ व मार्गदर्शक सल्ला",
    marketReachTitle: "बाजारपेठ विस्तार रणनीती",
    opportunitiesTitle: "स्थानिक संधी",
    swotStrengths: "जमेच्या बाजू (Strengths)",
    swotWeaknesses: "कमकुवत बाबी (Weaknesses)",
    swotOpportunities: "संधी (Opportunities)",
    swotThreats: "धोके (Threats)",
    pricingTitle: "किंमत व नफा मार्गदर्शन",
    nextStepsTitle: "पुढील कृती आराखडा",

    // DPR Screen
    dprCardTitle: "बँकेसाठी प्रकल्प अहवाल (Detailed Project Report)",
    dprSubtitle: "बँक व्यवस्थापकास सादर करण्यासाठी १२ कलमी अधिकृत अहवाल तयार आहे.",
    downloadMarathiPdfBtn: "📄 मराठी डीपीआर डाऊनलोड करा (PDF)",
    downloadEnglishPdfBtn: "📄 इंग्रजी डीपीआर डाऊनलोड करा (Bank Copy)",
    sha256Label: "डिजिटल सुरक्षितता कोड (SHA-256)",
    bankChecklistTitle: "बँकेत सादर करावयाची कागदपत्रे सूची:",
    bankChecklistDoc1: "१. आधार कार्ड व ओळखपत्र प्रत (फोटोकॉपी)",
    bankChecklistDoc2: "२. जातीचा दाखला (लागू असल्यास - SC/ST/OBC)",
    bankChecklistDoc3: "३. रहिवासी दाखला व रेशन कार्ड",
    bankChecklistDoc4: "४. प्रकल्प खर्च कोटेशन / साधनसामग्री बिल",
    portalToApplyTitle: "अर्ज सादर करण्याचे ठिकाण / पोर्टल:",
    portalHint: "जिल्हा उद्योग केंद्र (DIC) किंवा अग्रणी बँक (Bank of Maharashtra)",
    updateStatusBtn: "प्रकरणाची स्थिती अद्ययावत करा",
  },

  hi: {
    appName: "अर्थमित्र",
    tagline: "ग्रामीण सूक्ष्म उद्यमियों के लिए एआई हाइपर-लोकल व्यापार परामर्श एवं वित्तीय संरचना",
    schemeBasis: "सामाजिक न्याय और अधिकारिता मंत्रालय · सरकारी रियायती योजनाएं",
    healthStatus: "सिस्टम सक्रिय है",
    dpdpNotice: "डीपीडीपी अधिनियम 2023 के तहत डेटा गोपनीयता एवं सहमति सुरक्षित",
    languageSelect: "भाषा",
    back: "पीछे",
    next: "आगे",
    save: "सुरक्षित करें",
    submit: "जमा करें",
    cancel: "रद्द करें",
    retry: "पुनः प्रयास करें",
    loading: "प्रक्रिया जारी है...",
    error: "त्रुटि",
    success: "सफल",
    all: "सभी",
    search: "खोजें",
    filter: "फ़िल्टर",
    online: "ऑनलाइन",
    offline: "ऑफलाइन",
    offlineNotice: "इंटरनेट उपलब्ध नहीं है। डेटा स्थानीय मेमोरी में सुरक्षित रहेगा।",
    yes: "हाँ",
    no: "नहीं",

    loginTitle: "लॉगिन",
    loginSubtitle: "अपना मोबाइल नंबर और 4 अंकों का पिन दर्ज करें",
    phoneLabel: "मोबाइल नंबर",
    phonePlaceholder: "10 अंकों का मोबाइल नंबर",
    pinLabel: "सुरक्षित पिन",
    pinPlaceholder: "4 अंकों का पिन",
    loginBtn: "लॉगिन करें",
    logoutBtn: "लॉगआउट",
    agentRole: "मेरा खाता",
    agentOrg: "अर्थमित्र · व्यक्तिगत खाता",

    casesTitle: "मेरे व्यवसाय प्लान",
    newCaseBtn: "+ नया व्यवसाय प्लान",
    searchCasesPlaceholder: "व्यवसाय या गाँव से खोजें...",
    emptyCases: "अभी कोई प्लान नहीं",
    emptyCasesSub: "अपने व्यवसाय के लिए योजना, लोन और किस्त देखने के लिए ऊपर का बटन दबाएँ",
    beneficiary: "उद्यमी",
    village: "गाँव",
    business: "व्यवसाय",
    status: "स्थिति",
    createdOn: "तारीख",
    viewDetails: "विवरण देखें",
    statusDraft: "प्रारूप (Draft)",
    statusReady: "तैयार (Ready)",
    statusDpr: "डीपीआर तैयार (DPR Ready)",
    statusApplied: "बैंक में प्रस्तुत (Applied)",
    statusSanctioned: "स्वीकृत (Sanctioned)",
    statusRejected: "अस्वीकृत (Rejected)",
    statusDisbursed: "संवितरित (Disbursed)",
    statusClosed: "बंद (Closed)",

    consentTitle: "डीपीडीपी वैधानिक सहमति (DPDP Consent)",
    statutoryHeader: "व्यक्तिगत डेटा सहमति सूचना (धारा 5, डीपीडीपी अधिनियम 2023)",
    statutoryBody:
      "मैं एतद्द्वारा अर्थमित्र को मेरी सरकारी योजना पात्रता, सूक्ष्म व्यापार व्यवहार्यता और बैंक ऋण डीपीआर तैयार करने हेतु आवश्यक जानकारी एकत्र व संसाधित करने की सहमति देता/देती हूँ। मुझे ज्ञात है कि मेरा आधार, पैन या बैंक खाता नंबर यहाँ संग्रहीत नहीं किया जाता है।",
    statutoryVoicePrompt: "सूचना पढ़ें या सुनें, और सहमत हों तो नीचे टिक करें:",
    voiceConsentBtn: "🎙️ 'हाँ, मैं सहमत हूँ' वॉइस सहमति",
    paperConsentBtn: "हस्ताक्षर / अंगूठा सहमति फॉर्म",
    otpConsentBtn: "एसएमएस ओटीपी सहमति",
    consentGrantedNotice: "कानूनी सहमति सफलतापूर्वक दर्ज कर ली गई है।",
    dpdpProtectedBadge: "डीपीडीपी अधिनियम 2023 के तहत सुरक्षित",
    zeroPiiNotice: "शून्य आधार · शून्य पैन · संपूर्ण डेटा एन्क्रिप्टेड",
    proceedToProfile: "आगे: मेरी जानकारी →",

    profileTitle: "आपकी जानकारी",
    firstNameLabel: "आपका नाम",
    firstNamePlaceholder: "उदा. अनिता कांबळे",
    genderLabel: "लिंग",
    genderFemale: "महिला (Female)",
    genderMale: "पुरुष (Male)",
    genderOther: "अन्य (Other)",
    ageLabel: "आयु (वर्ष)",
    categoryLabel: "सामाजिक श्रेणी",
    disabilityLabel: "दिव्यांगता (40% या अधिक)",
    occupationFlagsLabel: "विशेष व्यवसाय श्रेणी",
    sanitationWorker: "सफाई कर्मचारी / आश्रित",
    traditionalArtisan: "पारंपरिक कारीगर / शिल्पकार",
    streetVendor: "स्ट्रीट वेंडर / फेरीवाला",
    noneOccupation: "सामान्य / लागू नहीं",
    annualIncomeLabel: "पारिवारिक वार्षिक आय",
    educationLabel: "शिक्षा",
    educationIlliterate: "अशिक्षित",
    educationPrimary: "प्राथमिक (1-4)",
    educationMiddle: "माध्यमिक (8वीं)",
    educationSecondary: "10वीं उत्तीर्ण",
    educationHigherSec: "12वीं उत्तीर्ण",
    educationGraduate: "स्नातक या अधिक",
    priorSubsidyLabel: "क्या पहले सरकारी सब्सिडी का लाभ लिया है?",
    existingEmiLabel: "वर्तमान मासिक ऋण किस्त (EMI रु.)",
    creditDefaultLabel: "ऋण चूक / डिफॉल्ट इतिहास",
    creditDefaultNo: "नहीं (स्वच्छ रिकॉर्ड)",
    creditDefaultYes: "हाँ (बकाया है)",
    creditDefaultUnknown: "पता नहीं / नया ग्राहक",
    shgMemberLabel: "क्या आप स्वयं सहायता समूह (SHG) सदस्य हैं?",

    villagePickerTitle: "व्यवसाय का गाँव चुनें",
    searchVillagePlaceholder: "गाँव का नाम टाइप करें...",
    populationLabel: "जनसंख्या",
    amenitiesLabel: "सुविधाएं",
    selectVillageBtn: "यह गाँव चुनें",

    businessPickerTitle: "सूक्ष्म व्यवसाय का प्रकार चुनें",
    selectBusinessHint: "स्थानीय मांग व रुचि के अनुसार नीचे से एक व्यवसाय चुनें:",
    targetCostLabel: "अपेक्षित परियोजना लागत (रु.)",
    marginAvailableLabel: "उपलब्ध स्वयं का मार्जिन (रु.)",
    marginHint: "न्यूनतम 5% से 15% स्वयं का मार्जिन आवश्यक है।",

    calibrationTitle: "स्थानीय बाज़ार एवं क्षमता सत्यापन",
    calibrationSubtitle: "सटीक वित्तीय विश्लेषण के लिए स्थानीय जानकारी भरें:",
    competitorsNearLabel: "गाँव में पैदल दूरी पर स्थित समान दुकानें/प्रतिस्पर्धी",
    dailyCustomersLabel: "अपेक्षित दैनिक ग्राहक संख्या",
    monthlyRentLabel: "दुकान का मासिक किराया (रु., यदि अपनी है तो 0)",
    ownPremisesLabel: "क्या जगह अपनी है?",
    milchAnimalsLabel: "दुधारू पशु संख्या (गाय/भैंस)",
    milkRateLabel: "दूध का बिक्री मूल्य (रु./लीटर)",
    fodderAvailableLabel: "क्या अपने खेत में चारा उपलब्ध है?",
    goatHerdLabel: "बकरियों की संख्या (उदा. 10+1)",
    tailoringMachinesLabel: "सिलाई मशीनों की संख्या",
    calculateViabilityBtn: "व्यवहार्यता एवं ऋण योजनाएं जांचें →",

    evaluationResultsTitle: "व्यवसाय व्यवहार्यता एवं ऋण संरचना रिपोर्ट",
    tabMarket: "बाज़ार (Market)",
    tabFinancing: "ऋण योजनाएं (Financing)",
    tabViability: "व्यवहार्यता (Viability)",
    tabAdvisory: "एआई परामर्श (Advisory)",
    tabDpr: "डीपीआर (Bank DPR)",

    marketCardTitle: "स्थानीय बाज़ार मांग एवं प्रतिस्पर्धा विश्लेषण",
    catchmentPopLabel: "कैचमेंट जनसंख्या",
    monthlyDemandLabel: "गाँव का इस श्रेणी पर मासिक खर्च",
    reportedCompetitorsLabel: "रिपोर्ट किए गए प्रतिस्पर्धी",
    bepMarketShareLabel: "लाभ हेतु आवश्यक न्यूनतम बाज़ार हिस्सा",
    saturationBandLabel: "बाज़ार संतृप्ति स्तर (Saturation)",
    satLow: "कम प्रतिस्पर्धा · व्यवसाय के लिए उत्तम अवसर",
    satMed: "मध्यम प्रतिस्पर्धा · अच्छी गुणवत्ता आवश्यक",
    satHigh: "उच्च प्रतिस्पर्धा · बाज़ार संतृप्त",
    complementaryTitle: "वैकल्पिक एवं पूरक व्यवसाय सुझाव",

    financingCardTitle: "शीर्ष सरकारी ऋण एवं सब्सिडी योजनाएं (Top 3)",
    topSchemesSubtitle: "शासकीय नियमों अनुसार सर्वश्रेष्ठ वित्तपोषण संरचना:",
    projectCostLabel: "कुल परियोजना लागत",
    ownMarginLabel: "स्वयं का मार्जिन",
    loanLabel: "बैंक ऋण राशि",
    subsidyLabel: "सरकारी सब्सिडी राशि",
    interestRateLabel: "ब्याज दर (वार्षिक)",
    tenureLabel: "ऋण पुनर्भुगतान अवधि",
    moratoriumLabel: "रियायती अवधि (Moratorium)",
    monthlyEmiLabel: "मासिक किस्त (EMI)",
    firstEmiDateLabel: "प्रथम किस्त देय तिथि",
    totalRepaymentLabel: "कुल पुनर्भुगतान राशि",
    viewScheduleBtn: "किस्त अनुसूची देखें",
    ineligibleSchemesTitle: "अपात्र योजनाएं एवं कारण",
    scheduleModalTitle: "मासिक ऋण पुनर्भुगतान अनुसूची (Amortization)",
    scheduleMonth: "माह",
    schedulePrincipal: "मूलधन (रु.)",
    scheduleInterest: "ब्याज (रु.)",
    scheduleTotal: "कुल किस्त (रु.)",
    scheduleBalance: "शेष ऋण (रु.)",

    viabilityCardTitle: "वित्तीय व्यवहार्यता एवं स्ट्रेस टेस्ट",
    dscrLabel: "ऋण सेवा कवरेज अनुपात (DSCR)",
    dscrBenchmarkHint: "बैंक मानक: 1.50x या अधिक सुरक्षित माना जाता है।",
    bepLabel: "ब्रेक-इवेन क्षमता (BEP)",
    nayakWorkingCapitalLabel: "नायक समिति कार्यशील पूंजी मानदंड",
    udharSliderLabel: "उधार प्रतिशत तनाव परीक्षण (Udhar %):",
    udharAdjustedDscrHint: "उधार बढ़ने पर नकदी प्रवाह और DSCR पर प्रभाव देखें।",
    incomeTimingWarningTitle: "आय समय-सारणी चेतावनी (Income-Timing Alert)",
    projections5yrTitle: "5 वर्षों का अनुमानित आय व लाभ विवरण",
    yearCol: "वर्ष",
    revenueCol: "वार्षिक राजस्व",
    surplusCol: "शुद्ध अधिशेष",

    advisoryCardTitle: "व्यापार विकास एवं मार्गदर्शन सलाह",
    marketReachTitle: "बाज़ार पहुंच रणनीति",
    opportunitiesTitle: "स्थानीय अवसर",
    swotStrengths: "शक्तियां (Strengths)",
    swotWeaknesses: "कमजोरियां (Weaknesses)",
    swotOpportunities: "अवसर (Opportunities)",
    swotThreats: "चुनौतियां (Threats)",
    pricingTitle: "मूल्य निर्धारण मार्गदर्शन",
    nextStepsTitle: "आगामी कदम",

    dprCardTitle: "बैंक हेतु विस्तृत परियोजना रिपोर्ट (DPR)",
    dprSubtitle: "बैंक प्रबंधक को प्रस्तुत करने योग्य 12-खंडीय औपचारिक रिपोर्ट तैयार है।",
    downloadMarathiPdfBtn: "📄 मराठी डीपीआर डाउनलोड करें (PDF)",
    downloadEnglishPdfBtn: "📄 अंग्रेजी डीपीआर डाउनलोड करें (Bank Copy)",
    sha256Label: "डिजिटल सुरक्षा कोड (SHA-256)",
    bankChecklistTitle: "बैंक में प्रस्तुत करने हेतु दस्तावेज सूची:",
    bankChecklistDoc1: "1. आधार कार्ड व पहचान पत्र प्रति",
    bankChecklistDoc2: "2. जाति प्रमाण पत्र (यदि लागू हो)",
    bankChecklistDoc3: "3. निवास प्रमाण पत्र व राशन कार्ड",
    bankChecklistDoc4: "4. परियोजना उपकरण कोटेशन / बिल",
    portalToApplyTitle: "आवेदन पोर्टल / कार्यालय:",
    portalHint: "जिला उद्योग केंद्र (DIC) अथवा अग्रणी बैंक शाखा",
    updateStatusBtn: "आवेदन स्थिति अपडेट करें",
  },

  en: {
    appName: "ArthMitra",
    tagline: "AI-Driven Hyper-Local Business Advisory & Financial Structuring for Rural Micro-Entrepreneurs",
    schemeBasis: "Ministry of Social Justice and Empowerment · Government Concessionary Schemes",
    healthStatus: "System Operational",
    dpdpNotice: "DPDP Act 2023 Compliant · Zero Sensitive PII Stored",
    languageSelect: "Language",
    back: "Back",
    next: "Next",
    save: "Save",
    submit: "Submit",
    cancel: "Cancel",
    retry: "Retry",
    loading: "Processing...",
    error: "Error Occurred",
    success: "Success",
    all: "All",
    search: "Search",
    filter: "Filter",
    online: "Online",
    offline: "Offline",
    offlineNotice: "Internet disconnected. Work will be securely saved locally.",
    yes: "Yes",
    no: "No",

    loginTitle: "Login",
    loginSubtitle: "Enter your mobile number and 4-digit PIN",
    phoneLabel: "Mobile Number",
    phonePlaceholder: "10-digit mobile number",
    pinLabel: "Security PIN",
    pinPlaceholder: "4-digit PIN",
    loginBtn: "Login",
    logoutBtn: "Logout",
    agentRole: "My Account",
    agentOrg: "ArthMitra · Personal account",

    casesTitle: "My Business Plans",
    newCaseBtn: "+ New Business Plan",
    searchCasesPlaceholder: "Search by business or village...",
    emptyCases: "No plans yet",
    emptyCasesSub: "Tap the button above to see schemes, loan and EMI for your business idea",
    beneficiary: "Entrepreneur",
    village: "Village",
    business: "Business",
    status: "Status",
    createdOn: "Date",
    viewDetails: "View Details",
    statusDraft: "Draft",
    statusReady: "Ready",
    statusDpr: "DPR Ready",
    statusApplied: "Applied",
    statusSanctioned: "Sanctioned",
    statusRejected: "Rejected",
    statusDisbursed: "Disbursed",
    statusClosed: "Closed",

    consentTitle: "DPDP Statutory Consent",
    statutoryHeader: "Notice for Processing Personal Data (Section 5, DPDP Act 2023)",
    statutoryBody:
      "I hereby give consent to ArthMitra to collect and process my demographic and business details strictly for the purpose of government scheme eligibility calculation, enterprise viability assessment, and bank DPR generation. I understand that my Aadhaar, PAN, and Bank Account numbers are never stored.",
    statutoryVoicePrompt: "Read or listen to the notice, and tick below if you agree:",
    voiceConsentBtn: "🎙️ 'Yes, I agree' Voice Consent",
    paperConsentBtn: "Physical Signature / Thumbprint Consent",
    otpConsentBtn: "SMS OTP Consent",
    consentGrantedNotice: "Statutory consent recorded successfully.",
    dpdpProtectedBadge: "Protected under DPDP Act 2023",
    zeroPiiNotice: "Zero Aadhaar · Zero PAN · Encrypted Storage",
    proceedToProfile: "Next: My details →",

    profileTitle: "Your Details",
    firstNameLabel: "Your Name",
    firstNamePlaceholder: "e.g. Anita Kamble",
    genderLabel: "Gender",
    genderFemale: "Female",
    genderMale: "Male",
    genderOther: "Other",
    ageLabel: "Age (Years)",
    categoryLabel: "Social Category",
    disabilityLabel: "Disability (40% or more)",
    occupationFlagsLabel: "Special Target Occupation",
    sanitationWorker: "Sanitation Worker / Dependant",
    traditionalArtisan: "Traditional Artisan / Craftsman",
    streetVendor: "Street Vendor / Hawker",
    noneOccupation: "General / Not Applicable",
    annualIncomeLabel: "Family Annual Income",
    educationLabel: "Education Level",
    educationIlliterate: "Illiterate / Below Primary",
    educationPrimary: "Primary School (Class 1-4)",
    educationMiddle: "Middle School (Class 8 Pass)",
    educationSecondary: "Secondary (Class 10 Pass)",
    educationHigherSec: "Higher Secondary (Class 12 Pass)",
    educationGraduate: "Graduate & Above",
    priorSubsidyLabel: "Availed Government Subsidy in Past?",
    existingEmiLabel: "Existing Monthly Loan EMI (₹)",
    creditDefaultLabel: "Past Loan Default History",
    creditDefaultNo: "No (Clean Credit)",
    creditDefaultYes: "Yes (Past Default)",
    creditDefaultUnknown: "Unknown / First Time Borrower",
    shgMemberLabel: "Are you an active SHG member?",

    villagePickerTitle: "Select Business Location / Village",
    searchVillagePlaceholder: "Type village name (English or Marathi)...",
    populationLabel: "Population",
    amenitiesLabel: "Amenities",
    selectVillageBtn: "Select This Village",

    businessPickerTitle: "Choose Micro-Enterprise Category",
    selectBusinessHint: "Select one of the 10 supported micro-enterprises based on local demand:",
    targetCostLabel: "Target Project Cost (₹)",
    marginAvailableLabel: "Own Available Margin Money (₹)",
    marginHint: "Minimum 5% to 15% own contribution required.",

    calibrationTitle: "Local Catchment Calibration",
    calibrationSubtitle: "Provide hyper-local field observations to calibrate demand & break-even:",
    competitorsNearLabel: "Existing similar shops within walking distance (Competitors)",
    dailyCustomersLabel: "Expected daily footfall / customer volume",
    monthlyRentLabel: "Monthly shop rent (₹, 0 if self-owned)",
    ownPremisesLabel: "Is premises self-owned?",
    milchAnimalsLabel: "Number of milch animals (Cows/Buffaloes)",
    milkRateLabel: "Dairy collection centre milk rate (₹/Litre)",
    fodderAvailableLabel: "Fodder available on own land?",
    goatHerdLabel: "Goatery herd unit (e.g. 10+1)",
    tailoringMachinesLabel: "Number of sewing machines",
    calculateViabilityBtn: "Evaluate Viability & Schemes →",

    evaluationResultsTitle: "Viability & Financial Structuring Report",
    tabMarket: "Market",
    tabFinancing: "Financing",
    tabViability: "Viability",
    tabAdvisory: "Advisory",
    tabDpr: "Bank DPR",

    marketCardTitle: "Catchment Market Demand & Saturation",
    catchmentPopLabel: "Catchment Population",
    monthlyDemandLabel: "Monthly Catchment Spend on Category",
    reportedCompetitorsLabel: "Reported Local Competitors",
    bepMarketShareLabel: "Break-Even Market Share Required",
    saturationBandLabel: "Market Saturation Band",
    satLow: "Low Competition · Excellent Business Potential",
    satMed: "Medium Competition · Differentiation Needed",
    satHigh: "High Competition · Saturated Market",
    complementaryTitle: "Complementary Business Opportunities",

    financingCardTitle: "Top Recommended Government Loan Packages (Top 3)",
    topSchemesSubtitle: "Ranked according to statutory benefit and lowest borrowing cost:",
    projectCostLabel: "Total Project Cost",
    ownMarginLabel: "Own Margin Money",
    loanLabel: "Bank Loan Financed",
    subsidyLabel: "Government Subsidy",
    interestRateLabel: "Annual Interest Rate",
    tenureLabel: "Repayment Tenure",
    moratoriumLabel: "Moratorium Period",
    monthlyEmiLabel: "Monthly EMI",
    firstEmiDateLabel: "First EMI Due Date",
    totalRepaymentLabel: "Total Repayment Amount",
    viewScheduleBtn: "View Schedule",
    ineligibleSchemesTitle: "Ineligible Schemes & Statutory Reasons",
    scheduleModalTitle: "Monthly Amortization Schedule",
    scheduleMonth: "Month",
    schedulePrincipal: "Principal (₹)",
    scheduleInterest: "Interest (₹)",
    scheduleTotal: "EMI Total (₹)",
    scheduleBalance: "Balance (₹)",

    viabilityCardTitle: "Financial Viability & Udhar Stress Testing",
    dscrLabel: "Debt Service Coverage Ratio (DSCR)",
    dscrBenchmarkHint: "Bank Benchmark: ≥ 1.50x considered bankable and secure.",
    bepLabel: "Break-Even Capacity (BEP)",
    nayakWorkingCapitalLabel: "Nayak Committee Working Capital Norm",
    udharSliderLabel: "Customer Credit / Udhar Stress Test (%):",
    udharAdjustedDscrHint: "Inspect real-time cash flow and DSCR impact under delayed customer payments.",
    incomeTimingWarningTitle: "Income-Timing Alert",
    projections5yrTitle: "5-Year Cash Flow & Surplus Projections",
    yearCol: "Year",
    revenueCol: "Annual Revenue",
    surplusCol: "Net Surplus",

    advisoryCardTitle: "Facts-Grounded Business Strategy",
    marketReachTitle: "Catchment Reach Strategy",
    opportunitiesTitle: "Growth Opportunities",
    swotStrengths: "Strengths",
    swotWeaknesses: "Weaknesses",
    swotOpportunities: "Opportunities",
    swotThreats: "Threats",
    pricingTitle: "Pricing Guidance",
    nextStepsTitle: "Next Action Steps",

    dprCardTitle: "Bank-Ready Detailed Project Report (DPR)",
    dprSubtitle: "12-Section formal DPR generated for Bank Manager submission.",
    downloadMarathiPdfBtn: "📄 Download Marathi DPR (PDF)",
    downloadEnglishPdfBtn: "📄 Download English DPR (Bank Copy)",
    sha256Label: "Digital Integrity Hash (SHA-256)",
    bankChecklistTitle: "Document Checklist for Bank Submission:",
    bankChecklistDoc1: "1. Identity & Address Proof (Aadhaar/Voter ID)",
    bankChecklistDoc2: "2. Caste Certificate (SC/ST/OBC where applicable)",
    bankChecklistDoc3: "3. Residence Certificate & Ration Card",
    bankChecklistDoc4: "4. Quotation of Machinery / Equipment",
    portalToApplyTitle: "Application Portal / Office:",
    portalHint: "District Industries Centre (DIC) or Lead Bank Branch",
    updateStatusBtn: "Update Application Status",
  },
};

export function formatINR(val: number): string {
  if (isNaN(val)) return "₹0";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(val);
}

export function formatNumberIN(val: number): string {
  if (isNaN(val)) return "0";
  return new Intl.NumberFormat("en-IN").format(val);
}
