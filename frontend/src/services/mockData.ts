import { BusinessType, Village, CaseRecord, EvaluationResult, User } from "../types";

export const MOCK_USER: User = {
  id: "u_sakhi_01",
  phone: "9876543210",
  full_name: "सुनिता पाटील (Sunita Patil)",
  role: "bank_sakhi",
  organization_id: "org_pune_umed",
  organization_name: "उमेद (UMED) · पुणे जिल्हा",
};

export const MOCK_BUSINESS_TYPES: BusinessType[] = [
  {
    code: "kirana",
    name_en: "Kirana / Grocery Store",
    name_mr: "किराणा दुकान",
    name_hi: "किराना दुकान",
    sector: "Retail",
    category_hces: "food_beverages",
    default_project_cost: 150000,
    min_margin_pct: 10,
    decay_lambda: 0.28,
    description_mr: "दैनंदिन किराणा, डाळी, तेल, मसाले व गृहोपयोगी वस्तू विक्री",
    description_en: "Daily provisions, pulses, edible oil, spices and household staples",
  },
  {
    code: "dairy",
    name_en: "Dairy Farming (2 Animals)",
    name_mr: "दुग्ध व्यवसाय (२ जनावरे)",
    name_hi: "डेयरी व्यवसाय (2 पशु)",
    sector: "Allied Agriculture",
    category_hces: "milk_products",
    default_project_cost: 160000,
    min_margin_pct: 10,
    decay_lambda: 0.18,
    description_mr: "२ संकरित गायी किंवा म्हशी, शेड व दूध संकलन केंद्र विक्री",
    description_en: "2 crossbred cows or buffaloes with stall and dairy collection sales",
  },
  {
    code: "goat",
    name_en: "Goatery (10+1 Unit)",
    name_mr: "शेळीपालन (१०+१ युनिट)",
    name_hi: "बकरी पालन (10+1 इकाई)",
    sector: "Allied Agriculture",
    category_hces: "meat_fish_eggs",
    default_project_cost: 120000,
    min_margin_pct: 10,
    decay_lambda: 0.18,
    description_mr: "१० शेळ्या + १ बोकड (उस्मानाबादी/संगमनेरी जात)",
    description_en: "10 Does + 1 Buck unit (Osmanabadi / Sangamneri breed)",
  },
  {
    code: "tailoring",
    name_en: "Tailoring & Boutique",
    name_mr: "शिलाई व टेलरिंग व्यवसाय",
    name_hi: "सिलाई एवं टेलरिंग",
    sector: "Services",
    category_hces: "clothing_bedding",
    default_project_cost: 80000,
    min_margin_pct: 5,
    decay_lambda: 0.18,
    description_mr: "महिला व लहान मुलांचे कपडे शिलाई, फॉल-पिको व दुरुस्ती",
    description_en: "Women & children garment stitching, alterations and boutique work",
  },
  {
    code: "beauty_parlour",
    name_en: "Beauty Parlour",
    name_mr: "ब्युटी पार्लर",
    name_hi: "ब्यूटी पार्लर",
    sector: "Services",
    category_hces: "personal_care",
    default_project_cost: 75000,
    min_margin_pct: 5,
    decay_lambda: 0.18,
    description_mr: "ग्रामीण महिलांसाठी फेशियल, हेअर कट, मेहेन्दी व सौंदर्य सेवा",
    description_en: "Personal grooming, hair styling, bridal mehendi for rural women",
  },
  {
    code: "two_wheeler_repair",
    name_en: "Two-Wheeler Garage",
    name_mr: "दुचाकी दुरुस्ती गॅरेज",
    name_hi: "दोपहिया मरम्मत गैराज",
    sector: "Services",
    category_hces: "conveyance",
    default_project_cost: 110000,
    min_margin_pct: 10,
    decay_lambda: 0.12,
    description_mr: "मोटारसायकल सर्व्हिसिंग, ऑइल चेंज, पंक्चर व सुटे भाग",
    description_en: "Motorcycle servicing, oil change, tyre puncture and basic spares",
  },
  {
    code: "flour_mill",
    name_en: "Flour Mill (Chakki)",
    name_mr: "पिठाची गिरणी (चक्की)",
    name_hi: "आटा चक्की",
    sector: "Agri Processing",
    category_hces: "cereal_products",
    default_project_cost: 140000,
    min_margin_pct: 10,
    decay_lambda: 0.28,
    description_mr: "गहू, ज्वारी, बाजरी, डाळी दळणे व मिरची-हळद कांडप",
    description_en: "Grain grinding for wheat, jowar, bajra and chili pulverizer",
  },
  {
    code: "vegetable_vending",
    name_en: "Mobile Vegetable Cart",
    name_mr: "भाजीपाला विक्री गाडी",
    name_hi: "सब्जी ठेला",
    sector: "Retail",
    category_hces: "vegetables",
    default_project_cost: 40000,
    min_margin_pct: 5,
    decay_lambda: 0.28,
    description_mr: "आठवडे बाजार व घरोघरी ताजा भाजीपाला विक्री",
    description_en: "Weekly village haat and door-to-door fresh vegetable vending",
  },
  {
    code: "poultry_broiler",
    name_en: "Broiler Poultry (500 Birds)",
    name_mr: "कुक्कुटपालन (५०० पक्षी)",
    name_hi: "पोल्ट्री फार्मिंग (500 पक्षी)",
    sector: "Allied Agriculture",
    category_hces: "meat_fish_eggs",
    default_project_cost: 200000,
    min_margin_pct: 10,
    decay_lambda: 0.18,
    description_mr: "५०० बॉयलर पक्षी संगोपन, शेड व खाद्य व्यवस्था",
    description_en: "500-bird broiler cycle batch rearing with shelter and feed",
  },
  {
    code: "welding_fabrication",
    name_en: "Welding & Agri Fabrication",
    name_mr: "वेल्डिंग व कृषी फॅब्रिकेशन",
    name_hi: "वेल्डिंग एवं कृषि फैब्रिकेशन",
    sector: "Manufacturing",
    category_hces: "durable_goods",
    default_project_cost: 220000,
    min_margin_pct: 10,
    decay_lambda: 0.12,
    description_mr: "ट्रॉली, नांगर, लोखंडी दरवाजे, शेती अवजारे दुरुस्ती व निर्मिती",
    description_en: "Tractor trolley, farm implement repair, iron gates and grill work",
  },
];

export const MOCK_VILLAGES: Village[] = [
  {
    id: "v_shirwal",
    name_en: "Shirwal",
    name_mr: "शिरवळ",
    subdistrict_en: "Khandala",
    subdistrict_mr: "खंडाळा",
    district_en: "Satara",
    district_mr: "सातारा",
    lgd_code: "565012",
    census_code: "563214",
    population: 14752,
    amenities_count: 8,
  },
  {
    id: "v_khed_shivapur",
    name_en: "Khed Shivapur",
    name_mr: "खेड शिवापूर",
    subdistrict_en: "Haveli",
    subdistrict_mr: "हवेली",
    district_en: "Pune",
    district_mr: "पुणे",
    lgd_code: "556101",
    census_code: "556102",
    population: 8640,
    amenities_count: 7,
  },
  {
    id: "v_saswad",
    name_en: "Saswad Rural",
    name_mr: "सासवड ग्रामीण",
    subdistrict_en: "Purandhar",
    subdistrict_mr: "पुरंदर",
    district_en: "Pune",
    district_mr: "पुणे",
    lgd_code: "556201",
    census_code: "556202",
    population: 11200,
    amenities_count: 9,
  },
  {
    id: "v_palashi",
    name_en: "Palashi",
    name_mr: "पळशी",
    subdistrict_en: "Khandala",
    subdistrict_mr: "खंडाळा",
    district_en: "Satara",
    district_mr: "सातारा",
    lgd_code: "565014",
    census_code: "563216",
    population: 2310,
    amenities_count: 3,
  },
  {
    id: "v_wing",
    name_en: "Wing",
    name_mr: "विंग",
    subdistrict_en: "Khandala",
    subdistrict_mr: "खंडाळा",
    district_en: "Satara",
    district_mr: "सातारा",
    lgd_code: "565015",
    census_code: "563217",
    population: 3420,
    amenities_count: 4,
  },
  {
    id: "v_shindewadi",
    name_en: "Shindewadi",
    name_mr: "शिंदेवाडी",
    subdistrict_en: "Haveli",
    subdistrict_mr: "हवेली",
    district_en: "Pune",
    district_mr: "पुणे",
    lgd_code: "556103",
    census_code: "556104",
    population: 1980,
    amenities_count: 3,
  },
];

export function createMockEvaluation(
  caseRecord: CaseRecord,
  udharPct: number = 20
): EvaluationResult {
  const isGoat = caseRecord.business_code === "goat";
  const cost = caseRecord.target_project_cost || 150000;
  const margin = Math.round(cost * 0.1);
  const loan = cost - margin;

  // Calculate monthly EMI (5 years @ 5% NSFDC or 8.5% MUDRA)
  const rate = caseRecord.beneficiary.category === "SC" ? 5.0 : 8.5;
  const monthlyRate = rate / 12 / 100;
  const tenure = 60;
  const emi = Math.round(
    (loan * monthlyRate * Math.pow(1 + monthlyRate, tenure)) /
      (Math.pow(1 + monthlyRate, tenure) - 1)
  );

  const baseDscr = 1.85;
  const udharImpact = (udharPct / 100) * 0.55;
  const adjustedDscr = Math.max(1.1, +(baseDscr - udharImpact).toFixed(2));

  // Amortization schedule sample
  let balance = loan;
  const schedule = [];
  for (let m = 1; m <= 12; m++) {
    const interest = Math.round(balance * monthlyRate);
    const principal = emi - interest;
    balance = Math.max(0, balance - principal);
    schedule.push({
      month: m,
      principal_payment: principal,
      interest_payment: interest,
      total_payment: emi,
      remaining_balance: balance,
    });
  }

  return {
    id: `eval_${caseRecord.id}`,
    case_id: caseRecord.id,
    evaluated_at: new Date().toISOString(),
    market: {
      catchment_population: caseRecord.village.population || 14752,
      monthly_category_spend: Math.round((caseRecord.village.population || 14752) * 520),
      competitors_reported: caseRecord.calibration.competitor_count ?? 3,
      breakeven_market_share_pct: 12.4,
      saturation_band:
        (caseRecord.calibration.competitor_count ?? 3) > 6
          ? "high"
          : (caseRecord.calibration.competitor_count ?? 3) >= 3
          ? "medium"
          : "low",
      saturation_reason_mr:
        (caseRecord.calibration.competitor_count ?? 3) <= 2
          ? "परिसरात स्पर्धकांची संख्या कमी असून व्यवसायाची मागणी पुरेशी आहे."
          : "स्थानिक स्पर्धा मध्यम असून नियमित ग्राहक जोडल्यास चांगला नफा शक्य आहे.",
      saturation_reason_en:
        (caseRecord.calibration.competitor_count ?? 3) <= 2
          ? "Low local competition ensures high capture rate for baseline viability."
          : "Moderate competition; consistent local service will meet break-even threshold.",
      complementary_businesses: [
        {
          code: "spices_retail",
          name_mr: "घरगुती मसाले व लोणचे विक्री",
          name_en: "Home-ground Spices & Pickles",
          rationale_mr: "किराणा दुकानात विक्रीसाठी ठेवल्यास अतिरिक्त नफा मिळू शकतो.",
          rationale_en: "High margin add-on for daily footfall customers.",
        },
        {
          code: "packaged_snacks",
          name_mr: "स्थानिक बेकरी उत्पादने",
          name_en: "Local Bakery & Packaged Snacks",
          rationale_mr: "सकाळ-संध्याकाळ चहा-नाश्त्यासाठी मागणी वाढते.",
          rationale_en: "High inventory turnover item.",
        },
      ],
    },
    top_schemes: [
      {
        scheme_code: "NSFDC_TL",
        scheme_name_en: "NSFDC Term Loan Scheme",
        scheme_name_mr: "एनएसएफडीसी मुदत कर्ज योजना (कन्सशनल लोन)",
        rank: 1,
        project_cost: cost,
        margin_amount: margin,
        margin_pct: 10,
        loan_amount: loan,
        subsidy_amount: Math.round(cost * 0.15),
        subsidy_pct: 15,
        annual_interest_rate: 5.0,
        tenure_months: 60,
        moratorium_months: isGoat ? 6 : 3,
        monthly_emi: emi,
        total_interest_paid: Math.round(loan * 0.13),
        total_amount_paid: Math.round(loan * 1.13),
        first_emi_date: "10-12-2026",
        portal_url: "https://nsfdc.nic.in",
        amortization_schedule: schedule,
      },
      {
        scheme_code: "MUDRA_KISHORE",
        scheme_name_en: "Pradhan Mantri MUDRA Yojana (Kishore)",
        scheme_name_mr: "पंतप्रधान मुद्रा योजना (किशोर प्रवर्ग)",
        rank: 2,
        project_cost: cost,
        margin_amount: margin,
        margin_pct: 10,
        loan_amount: loan,
        subsidy_amount: 0,
        subsidy_pct: 0,
        annual_interest_rate: 8.5,
        tenure_months: 60,
        moratorium_months: 0,
        monthly_emi: Math.round(emi * 1.12),
        total_interest_paid: Math.round(loan * 0.23),
        total_amount_paid: Math.round(loan * 1.23),
        first_emi_date: "10-11-2026",
        portal_url: "https://www.mudra.org.in",
        amortization_schedule: schedule,
      },
      {
        scheme_code: "CMEGP",
        scheme_name_en: "Chief Minister Employment Generation Programme",
        scheme_name_mr: "मुख्यमंत्री रोजगार निर्मिती कार्यक्रम (CMEGP)",
        rank: 3,
        project_cost: cost,
        margin_amount: Math.round(cost * 0.05),
        margin_pct: 5,
        loan_amount: cost - Math.round(cost * 0.05),
        subsidy_amount: Math.round(cost * 0.25),
        subsidy_pct: 25,
        annual_interest_rate: 9.0,
        tenure_months: 60,
        moratorium_months: 3,
        monthly_emi: Math.round(emi * 1.15),
        total_interest_paid: Math.round(loan * 0.25),
        total_amount_paid: Math.round(loan * 1.25),
        first_emi_date: "10-12-2026",
        portal_url: "https://maha-cmegp.gov.in",
        amortization_schedule: schedule,
      },
    ],
    ineligible_schemes: [
      {
        scheme_code: "STANDUP_INDIA",
        scheme_name: "Stand-Up India Scheme",
        rejection_reasons: [
          "किमान प्रकल्प खर्च ₹10,00,000 आवश्यक आहे (सध्याचा खर्च: ₹" + cost + ")",
        ],
      },
      {
        scheme_code: "PMEGP",
        scheme_name: "Prime Minister Employment Generation Programme",
        rejection_reasons: [
          "कौटुंबिक उत्पन्नाचा दाखला अथवा इतर योजना जास्त फायदेशीर ठरत आहे.",
        ],
      },
    ],
    viability: {
      dscr: baseDscr,
      breakeven_capacity_pct: 42.5,
      nayak_working_capital: Math.round(cost * 0.25),
      nayak_margin_required: Math.round(cost * 0.05),
      year1_revenue: Math.round(cost * 1.8),
      year1_net_profit: Math.round(cost * 0.35),
      year1_cash_flow: Math.round(cost * 0.42),
      projections_5yr: [
        {
          year: 1,
          revenue: Math.round(cost * 1.8),
          expenses: Math.round(cost * 1.45),
          loan_repayment: emi * 12,
          net_surplus: Math.round(cost * 0.35) - emi * 12,
        },
        {
          year: 2,
          revenue: Math.round(cost * 1.98),
          expenses: Math.round(cost * 1.56),
          loan_repayment: emi * 12,
          net_surplus: Math.round(cost * 0.42) - emi * 12,
        },
        {
          year: 3,
          revenue: Math.round(cost * 2.18),
          expenses: Math.round(cost * 1.68),
          loan_repayment: emi * 12,
          net_surplus: Math.round(cost * 0.5) - emi * 12,
        },
        {
          year: 4,
          revenue: Math.round(cost * 2.4),
          expenses: Math.round(cost * 1.8),
          loan_repayment: emi * 12,
          net_surplus: Math.round(cost * 0.6) - emi * 12,
        },
        {
          year: 5,
          revenue: Math.round(cost * 2.64),
          expenses: Math.round(cost * 1.94),
          loan_repayment: emi * 12,
          net_surplus: Math.round(cost * 0.7) - emi * 12,
        },
      ],
      income_timing_warning: isGoat,
      income_timing_text_mr: isGoat
        ? "शेळीपालनात पहिल्या ६ ते ८ महिन्यांत पिल्ले विकण्यायोग्य होत नसल्याने रोख उत्पन्न उशिरा सुरू होते. सुरुवातीच्या महिन्यांसाठी मोरेटोरियम कालावधी आवश्यक आहे."
        : undefined,
      income_timing_text_en: isGoat
        ? "Goatery requires 6-8 months before kids reach saleable age. Ensure 6-month moratorium on principal repayment."
        : undefined,
      udhar_pct: udharPct,
      udhar_adjusted_dscr: adjustedDscr,
    },
    advisory: {
      market_reach:
        "स्थानिक गावातून " +
        (caseRecord.village.population || 14752) +
        " लोकसंख्येपैकी दररोज किमान ३०-४५ ग्राहक आकर्षित करून व्यवसाय शाश्वत करता येईल.",
      opportunities: [
        "स्थानिक आठवडे बाजाराच्या दिवशी विशेष विक्री सत्र आयोजित करणे",
        "नियमित ग्राहकांना सवलत व दर्जेदार माल पुरवून विश्वासार्हता निर्माण करणे",
        "शासकीय सवलतीच्या ५% व्याजदरामुळे दरमहा हप्त्याचा भार कमी राहतो",
      ],
      swot: {
        strengths: [
          "स्थानिक परिसराची माहिती व वैयक्तिक जनसंपर्क",
          "कमी भांडवलात सुरू होणारा व शाश्वत मागणी असलेला व्यवसाय",
        ],
        weaknesses: [
          "सुरुवातीस खेळते भांडवल मर्यादित असणे",
          "उधारीमुळे रोख पैशांची चणचण भासण्याची शक्यता",
        ],
        opportunities: [
          "शेजारील वाड्या-वस्त्यांवरून येणाऱ्या ग्राहकांचे जाळे तयार करणे",
          "पूरक उत्पादने (मसाले / दुग्धजन्य पदार्थ) जोडून नफा वाढवणे",
        ],
        threats: [
          "मोठ्या शहरांमधील घाऊक बाजाराशी स्पर्धा",
          "ग्राहकांकडून उधारी न मिळाल्यास खेळत्या भांडवलावर ताण",
        ],
      },
      threats_mitigations: [
        {
          threat: "उधारीचे प्रमाण वाढल्यास खेळते भांडवल अडकणे",
          mitigation: "उधारी कमाल १५ दिवसांच्या मर्यादेत ठेवावी व एकूण विक्रीच्या २०% पेक्षा जास्त उधारी देऊ नये.",
        },
        {
          threat: "किराणा मालाचे भाव चढ-उतार",
          mitigation: "हंगामात थेट शेतकऱ्यांकडून किंवा कृषी उत्पन्न बाजार समितीतून घाऊक खरेदी करावी.",
        },
      ],
      pricing_guidance: "घाऊक खरेदीवर ८% ते १२% नफा (Margin) ठेवून स्पर्धात्मक दर निश्चित करावेत.",
      next_steps: [
        "बँकेसाठी तयार केलेला डीपीआर (PDF) डाऊनलोड करा.",
        "आवश्यक कागदपत्रांची (आधार, जात प्रमाणपत्र, कोटेशन) २ प्रती तयार करा.",
        "स्थानिक बँक व्यवस्थापक किंवा उमेद सीआरपी यांच्याकडे अर्ज सादर करा.",
      ],
    },
    dpr_documents: [
      {
        id: `dpr_${caseRecord.id}_mr`,
        language: "mr",
        filename: `DPR_${caseRecord.id}_mr.pdf`,
        sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        download_url: `/api/dpr/dpr_${caseRecord.id}_mr/download`,
      },
      {
        id: `dpr_${caseRecord.id}_en`,
        language: "en",
        filename: `DPR_${caseRecord.id}_en.pdf`,
        sha256: "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
        download_url: `/api/dpr/dpr_${caseRecord.id}_en/download`,
      },
    ],
  };
}

export const INITIAL_CASES_SEED: CaseRecord[] = [
  {
    id: "case_001",
    beneficiary_id: "ben_001",
    beneficiary: {
      id: "ben_001",
      first_name: "अनिता कांबळे (Anita Kamble)",
      gender: "female",
      age: 32,
      category: "SC",
      disability_40: false,
      sanitation_worker: false,
      traditional_artisan: false,
      street_vendor: false,
      annual_income: 120000,
      education: "secondary_10th",
      prior_subsidy: false,
      existing_emi: 0,
      credit_default: "no",
      shg_member: true,
    },
    village_id: "v_shirwal",
    village: MOCK_VILLAGES[0],
    business_code: "kirana",
    business: MOCK_BUSINESS_TYPES[0],
    target_project_cost: 150000,
    margin_available: 15000,
    calibration: {
      competitor_count: 2,
      daily_volume_or_customers: 40,
      monthly_rent: 2000,
      own_premises: false,
      udhar_pct: 15,
    },
    status: "ready",
    created_at: "2026-10-24T10:30:00Z",
    updated_at: "2026-10-24T11:00:00Z",
  },
  {
    id: "case_002",
    beneficiary_id: "ben_002",
    beneficiary: {
      id: "ben_002",
      first_name: "सुरेश जाधव (Suresh Jadhav)",
      gender: "male",
      age: 28,
      category: "OBC",
      disability_40: false,
      sanitation_worker: false,
      traditional_artisan: false,
      street_vendor: false,
      annual_income: 180000,
      education: "higher_secondary_12th",
      prior_subsidy: false,
      existing_emi: 0,
      credit_default: "no",
      shg_member: false,
    },
    village_id: "v_khed_shivapur",
    village: MOCK_VILLAGES[1],
    business_code: "dairy",
    business: MOCK_BUSINESS_TYPES[1],
    target_project_cost: 160000,
    margin_available: 20000,
    calibration: {
      competitor_count: 4,
      special_asset_count: 2,
      unit_price_or_rate: 38,
      own_premises: true,
      udhar_pct: 10,
    },
    status: "dpr_generated",
    created_at: "2026-10-25T14:15:00Z",
    updated_at: "2026-10-25T15:00:00Z",
  },
];

// Attach evaluations to seed
INITIAL_CASES_SEED[0].evaluation = createMockEvaluation(INITIAL_CASES_SEED[0], 15);
INITIAL_CASES_SEED[1].evaluation = createMockEvaluation(INITIAL_CASES_SEED[1], 10);
