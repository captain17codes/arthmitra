export type Language = "mr" | "hi" | "en";

export type Role = "bank_sakhi" | "vle" | "supervisor" | "admin";

export interface User {
  id: string;
  phone: string;
  full_name: string;
  role: Role;
  organization_id: string;
  organization_name: string;
}

export type Gender = "female" | "male" | "other";

export type SocialCategory = "SC" | "ST" | "OBC" | "VJNT" | "SBC" | "General";

export type EducationLevel =
  | "illiterate"
  | "primary"
  | "middle_8th"
  | "secondary_10th"
  | "higher_secondary_12th"
  | "graduate";

export type IncomeBand = "below_1.5L" | "1.5L_to_3.0L" | "3.0L_to_6.0L" | "above_6.0L";

export interface BeneficiaryProfile {
  id?: string;
  first_name: string;
  gender: Gender;
  age: number;
  category: SocialCategory;
  disability_40: boolean;
  sanitation_worker: boolean;
  traditional_artisan: boolean;
  street_vendor: boolean;
  annual_income: number;
  education: EducationLevel;
  prior_subsidy: boolean;
  existing_emi: number;
  credit_default: "no" | "yes" | "unknown";
  shg_member: boolean;
}

export interface Village {
  id: string;
  name_en: string;
  name_mr: string;
  subdistrict_en: string;
  subdistrict_mr: string;
  district_en: string;
  district_mr: string;
  lgd_code: string;
  census_code: string;
  population: number;
  amenities_count: number;
}

export interface BusinessType {
  code: string;
  name_en: string;
  name_mr: string;
  name_hi: string;
  sector: string;
  category_hces: string;
  default_project_cost: number;
  min_margin_pct: number;
  decay_lambda: number;
  description_mr: string;
  description_en: string;
}

export interface CalibrationData {
  competitor_count: number;
  daily_volume_or_customers?: number;
  unit_price_or_rate?: number;
  rent_monthly?: number;
  own_premises?: boolean;
  special_asset_count?: number; // animals, machines, birds
  udhar_pct?: number; // 0 to 50%
  [key: string]: any;
}

export type CaseStatus =
  | "draft"
  | "ready"
  | "dpr_generated"
  | "applied"
  | "sanctioned"
  | "rejected"
  | "disbursed"
  | "closed";

export interface CaseRecord {
  id: string;
  beneficiary_id: string;
  beneficiary: BeneficiaryProfile;
  village_id: string;
  village: Village;
  business_code: string;
  business: BusinessType;
  target_project_cost: number;
  margin_available: number;
  calibration: CalibrationData;
  status: CaseStatus;
  status_reason?: string;
  created_at: string;
  updated_at: string;
  evaluation?: EvaluationResult;
}

export interface SchemePackage {
  scheme_code: string;
  scheme_name_en: string;
  scheme_name_mr: string;
  rank: number;
  project_cost: number;
  margin_amount: number;
  margin_pct: number;
  loan_amount: number;
  subsidy_amount: number;
  subsidy_pct: number;
  annual_interest_rate: number;
  tenure_months: number;
  moratorium_months: number;
  monthly_emi: number;
  total_interest_paid: number;
  total_amount_paid: number;
  first_emi_date: string;
  portal_url: string;
  amortization_schedule: Array<{
    month: number;
    principal_payment: number;
    interest_payment: number;
    total_payment: number;
    remaining_balance: number;
  }>;
}

export interface MarketMetrics {
  catchment_population: number;
  monthly_category_spend: number;
  competitors_reported: number;
  breakeven_market_share_pct: number;
  saturation_band: "low" | "medium" | "high";
  saturation_reason_mr: string;
  saturation_reason_en: string;
  complementary_businesses: Array<{
    code: string;
    name_mr: string;
    name_en: string;
    rationale_mr: string;
    rationale_en: string;
  }>;
}

export interface ViabilityMetrics {
  dscr: number;
  breakeven_capacity_pct: number;
  nayak_working_capital: number;
  nayak_margin_required: number;
  year1_revenue: number;
  year1_net_profit: number;
  year1_cash_flow: number;
  projections_5yr: Array<{
    year: number;
    revenue: number;
    expenses: number;
    loan_repayment: number;
    net_surplus: number;
  }>;
  income_timing_warning: boolean;
  income_timing_text_mr?: string;
  income_timing_text_en?: string;
  udhar_pct: number;
  udhar_adjusted_dscr: number;
}

export interface AdvisoryContent {
  market_reach: string;
  opportunities: string[];
  swot: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
  threats_mitigations: Array<{
    threat: string;
    mitigation: string;
  }>;
  pricing_guidance: string;
  next_steps: string[];
}

export interface EvaluationResult {
  id: string;
  case_id: string;
  evaluated_at: string;
  market: MarketMetrics;
  top_schemes: SchemePackage[];
  ineligible_schemes: Array<{
    scheme_code: string;
    scheme_name: string;
    rejection_reasons: string[];
  }>;
  viability: ViabilityMetrics;
  advisory?: AdvisoryContent;
  dpr_documents?: Array<{
    id: string;
    language: string;
    filename: string;
    sha256: string;
    download_url: string;
  }>;
}
