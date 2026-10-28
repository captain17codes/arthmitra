export type Language = "mr" | "hi" | "en";

export type Role = "agent" | "supervisor" | "admin";

export interface User {
  id: string;
  full_name: string;
  role: Role;
  organization_id: string;
  organization_name: string;
  lang?: string;
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

/** What the agent enters in the profile step (sent to POST /beneficiaries). */
export interface BeneficiaryProfile {
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

export interface ConsentRecord {
  language: Language;
  method: "voice" | "tap";
  audio_sha256?: string;
}

export interface Village {
  id: string; // LGD code as string
  lgd_code: string;
  name_en: string;
  name_mr: string;
  subdistrict_en: string;
  subdistrict_mr: string;
  district_en: string;
  district_mr: string;
  population: number | null;
}

export interface ViableRange {
  min: number;
  max: number;
}

export interface BusinessType {
  code: string;
  name_en: string;
  name_mr: string;
  name_hi: string;
  sector: string;
  viable_range?: ViableRange | null;
}

export interface BenchmarkParam {
  value: number;
  unit?: string | null;
  confidence?: string | null;
  source_title?: string | null;
  source_year?: number | null;
}

export interface BusinessParameters {
  code: string;
  viable_range?: ViableRange | null;
  revenue_parameters: Record<string, BenchmarkParam>;
  cost_parameters: Record<string, BenchmarkParam>;
}

/** Local values entered by the agent. Keys are benchmark parameter names (e.g. daily_customers). */
export type CalibrationData = Record<string, number | string>;

export type CaseStatus =
  | "draft"
  | "ready"
  | "dpr_generated"
  | "applied"
  | "sanctioned"
  | "rejected"
  | "disbursed"
  | "closed";

// ---------------------------------------------------------------------------
// Evaluation output — mirrors backend app/services/evaluation.py exactly.
// All numbers arrive as decimal strings and are only formatted, never computed, in the UI.
// ---------------------------------------------------------------------------

export interface ScheduleRow {
  period: number;
  due_month: number;
  opening_balance: string;
  interest: string;
  principal: string;
  payment: string;
  subsidy_credit: string;
  closing_balance: string;
  is_moratorium: boolean;
}

export interface Tranche {
  name: string;
  principal: string;
  annual_rate_pct: string;
  tenure_months: number;
  moratorium_months: number;
  frequency_months: number;
  emi: string;
  instalments: number;
  schedule: ScheduleRow[];
}

export interface SchemePackage {
  rank?: number;
  scheme_code: string;
  scheme_name: Record<string, string>;
  agency: string;
  scheme_status: string;
  source_url: string;
  source_date: string;
  apply_at: string;
  documents: string[];
  notes: string[];
  indicative_fields: string[];
  is_special_category: boolean;
  own_share_pct: string;
  project_cost: string;
  own_margin_required: string;
  own_margin_available: string;
  margin_shortfall: string;
  is_affordable: boolean;
  loan_amount: string;
  subsidy_amount: string;
  subsidy_rate_pct: string;
  subsidy_treatment: string | null;
  annual_rate_pct: string;
  tenure_months: number;
  moratorium_months: number;
  emi: string;
  emi_frequency_months: number;
  monthly_equivalent_emi: string;
  emi_after_subsidy_adjustment: string | null;
  moratorium_interest: string;
  total_repayment: string;
  net_cost_to_beneficiary: string;
  net_cost_per_lakh: string;
  warnings: string[];
  eligibility_warnings?: string[];
  affordable_alternative?: {
    project_cost: string;
    own_margin_required: string;
    loan_amount: string;
  };
  tranches: Tranche[];
}

export interface Metric {
  value: string;
  min: string;
  max: string;
}

export interface EvaluationOutput {
  summary: {
    business_code: string;
    business_name_en: string;
    business_name_mr: string;
    village_lgd: number;
    village_name: string;
    project_cost: string;
    margin_available: string;
    top_packages: SchemePackage[];
    financing_basis: string | null;
    average_dscr: string | null;
    dscr_passed: boolean | null;
    breakeven_capacity_pct: string;
    nayak_working_capital: { total: string; bank_finance_20: string; promoter_margin_5: string };
    udhar_stress: { udhar_pct: string; extra_wc_needed: string; cash_buffer_months: string };
    market_saturation: "low" | "medium" | "high" | "needs_info";
    effective_catchment_population: string;
    monthly_category_demand: string;
    competitors_reported: string | null;
  };
  viability: {
    dscr_target: string;
    average_dscr: string | null;
    dscr_passed: boolean | null;
    income_timing_mismatch: boolean;
    recommended_reserve: string;
    foir_pct: string | null;
    foir_passed: boolean;
    revenue_share_of_local_demand_pct: string | null;
    warnings: string[];
    inputs_used: Record<string, "local" | "default">;
    projections: Array<{
      year: number;
      capacity_utilization: string;
      gross_revenue: string;
      variable_costs: string;
      fixed_costs: string;
      depreciation: string;
      interest: string;
      pbt: string;
      pat: string;
      cash_accrual: string;
      debt_service: string;
      dscr: string | null;
    }>;
  };
  market: {
    population_now: Metric;
    catchment_population: Metric;
    category_demand_monthly: Metric;
    competitor_count: Metric | null;
    demand_per_shop_monthly: Metric | null;
    be_market_share: Metric;
    saturation_level: "low" | "medium" | "high" | "needs_info";
    complementary_suggestions: Array<{
      business_code: string;
      name_en: string;
      name_mr: string;
      be_market_share: string;
      saturation_level: string;
      monthly_demand: string;
    }>;
    warnings: string[];
    explanation: string;
  };
  rules: {
    eligible_schemes_count: number;
    other_eligible: string[];
    confirm_with_agency: SchemePackage[];
    needs_info: Array<{ code: string; name: Record<string, string>; missing_fields: string[] }>;
    not_eligible: Array<{ code: string; name: Record<string, string>; reasons: string[] }>;
  };
}

/** Mirrors backend engines/advisory/models.py AdvisoryOutput. */
export interface AdvisoryContent {
  market_reach: string;
  opportunities: string[];
  swot: { s: string[]; w: string[]; o: string[]; t: string[] };
  threats: Array<{ risk: string; type: string; mitigation: string }>;
  pricing: {
    strategy: string;
    items: Array<{ item: string; benchmark_price: string; unit: string; rationale: string }>;
  };
  complementary: string[];
  next_steps: string[];
}

export interface CaseRecord {
  id: string;
  beneficiary_id: string;
  beneficiary: { first_name: string; gender?: string; age?: number; category?: string };
  village: Village | null;
  business: BusinessType | null;
  business_code: string;
  target_project_cost: number | null;
  margin_available: number;
  status: CaseStatus;
  status_reason?: string | null;
  created_at: string;
  updated_at?: string | null;
  inputs?: CalibrationData;
  evaluation_id?: string;
  output?: EvaluationOutput;
}

export interface DprDocument {
  dpr_id: number;
  language: string;
  file_sha256: string;
  download_url: string;
}
