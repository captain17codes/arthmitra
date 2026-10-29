import {
  AdvisoryContent,
  BeneficiaryProfile,
  BusinessParameters,
  BusinessType,
  CalibrationData,
  CaseRecord,
  CaseStatus,
  ConsentRecord,
  DprDocument,
  EvaluationOutput,
  Role,
  User,
  Village,
} from "../types";
import { storage } from "./storage";

/**
 * Real backend client. There is NO mock fallback: every number shown in the app
 * must come from the backend engines. On failure we throw an ApiError and the UI
 * shows the error instead of invented results.
 */
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) || "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(init.body ? { "Content-Type": "application/json" } : {}),
    ...((init.headers as Record<string, string>) || {}),
  };
  const token = storage.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  } catch {
    throw new ApiError("Server could not be reached. Check the internet connection and try again.", 0);
  }
  if (res.status === 401) {
    storage.clearToken();
    storage.clearUser();
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
      else if (Array.isArray(body?.detail)) detail = body.detail.map((d: { msg: string }) => d.msg).join("; ");
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail, res.status);
  }
  return (await res.json()) as T;
}

// ---------------------------------------------------------------------------
// Mappers between backend payloads and UI types
// ---------------------------------------------------------------------------

interface BackendUser {
  id: number;
  name: string;
  role: string;
  org_id: number;
  lang?: string;
}

function toUser(u: BackendUser): User {
  const role = (["citizen", "agent", "supervisor", "admin"].includes(u.role) ? u.role : "citizen") as Role;
  return {
    id: String(u.id),
    full_name: u.name,
    role,
    organization_id: String(u.org_id),
    organization_name: role === "citizen" ? "" : `Org #${u.org_id}`,
    lang: u.lang,
  };
}

interface BackendVillage {
  lgd_code: number;
  name_en: string;
  name_mr: string;
  subdistrict_name?: string | null;
  district_name?: string | null;
  pop_2011?: number | null;
}

export function toVillage(v: BackendVillage): Village {
  return {
    id: String(v.lgd_code),
    lgd_code: String(v.lgd_code),
    name_en: v.name_en,
    name_mr: v.name_mr,
    subdistrict_en: v.subdistrict_name || "",
    subdistrict_mr: v.subdistrict_name || "",
    district_en: v.district_name || "",
    district_mr: v.district_name || "",
    population: v.pop_2011 ?? null,
  };
}

interface BackendCase {
  id: number;
  beneficiary_id: number;
  beneficiary?: { first_name: string; gender?: string; age?: number; category?: string };
  beneficiary_name?: string;
  village?: BackendVillage | null;
  business?: BusinessType | null;
  business_code: string;
  margin_available: string;
  target_project_cost: string | null;
  status: CaseStatus;
  status_reason_code?: string | null;
  created_at: string;
  updated_at?: string | null;
  inputs?: CalibrationData;
  latest_evaluation?: { id: number; output: EvaluationOutput } | null;
}

function toCase(c: BackendCase): CaseRecord {
  return {
    id: String(c.id),
    beneficiary_id: String(c.beneficiary_id),
    beneficiary: c.beneficiary || { first_name: c.beneficiary_name || "—" },
    village: c.village ? toVillage(c.village) : null,
    business: c.business || null,
    business_code: c.business_code,
    target_project_cost: c.target_project_cost ? Number(c.target_project_cost) : null,
    margin_available: Number(c.margin_available),
    status: c.status,
    status_reason: c.status_reason_code,
    created_at: c.created_at,
    updated_at: c.updated_at,
    inputs: c.inputs,
    evaluation_id: c.latest_evaluation ? String(c.latest_evaluation.id) : undefined,
    output: c.latest_evaluation?.output,
  };
}

interface BackendBeneficiary {
  id: number;
  first_name: string;
  gender: string;
  age: number;
  category: string;
  disability_40: boolean;
  occupation_flags: string[] | null;
  annual_family_income: number | null;
  education_band: string;
  shg_member: boolean;
  prior_subsidy: string;
  credit_default: string;
  existing_emi_monthly: string | number;
}

const EDUCATION_LEVELS = ["illiterate", "primary", "middle_8th", "secondary_10th", "higher_secondary_12th", "graduate"];

function toProfile(b: BackendBeneficiary): Partial<BeneficiaryProfile> {
  const flags = b.occupation_flags || [];
  return {
    first_name: b.first_name,
    gender: (["female", "male", "other"].includes(b.gender) ? b.gender : "female") as BeneficiaryProfile["gender"],
    age: b.age,
    category: b.category as BeneficiaryProfile["category"],
    disability_40: b.disability_40,
    sanitation_worker: flags.includes("sanitation_worker"),
    traditional_artisan: flags.includes("traditional_artisan"),
    street_vendor: flags.includes("street_vendor"),
    annual_income: b.annual_family_income ?? undefined,
    education: (EDUCATION_LEVELS.includes(b.education_band) ? b.education_band : undefined) as BeneficiaryProfile["education"],
    prior_subsidy: b.prior_subsidy === "yes",
    existing_emi: Number(b.existing_emi_monthly) || 0,
    credit_default: (["no", "yes", "unknown"].includes(b.credit_default) ? b.credit_default : "unknown") as BeneficiaryProfile["credit_default"],
    shg_member: b.shg_member,
  };
}

function toBeneficiaryPayload(p: BeneficiaryProfile, consent: ConsentRecord) {
  const occupation_flags: string[] = [];
  if (p.sanitation_worker) occupation_flags.push("sanitation_worker");
  if (p.traditional_artisan) occupation_flags.push("traditional_artisan");
  if (p.street_vendor) occupation_flags.push("street_vendor");
  return {
    first_name: p.first_name,
    gender: p.gender,
    age: p.age,
    category: p.category,
    disability_40: p.disability_40,
    occupation_flags,
    annual_family_income: Math.round(p.annual_income),
    income_band: "exact",
    education_band: p.education,
    shg_member: p.shg_member,
    prior_subsidy: p.prior_subsidy ? "yes" : "no",
    credit_default: p.credit_default,
    existing_emi_monthly: p.existing_emi,
    consent: {
      language: consent.language,
      method: consent.method,
      audio_sha256: consent.audio_sha256,
    },
  };
}

// ---------------------------------------------------------------------------
// API surface
// ---------------------------------------------------------------------------

export interface OtpVerifyResult {
  setup_token: string;
  is_new_user: boolean;
  name: string | null;
}

export const api = {
  /** Sends an OTP. `dev_otp` is only present while no SMS provider is configured (demo mode). */
  async requestOtp(phone: string): Promise<{ sent: boolean; dev_otp?: string }> {
    return request("/auth/otp/request", { method: "POST", body: JSON.stringify({ phone }) });
  },

  /** Server OTP mode: "firebase" | "dev" | "msg91". */
  async authConfig(): Promise<{ otp_provider: string }> {
    return request("/auth/config");
  },

  /** Exchange a Firebase phone-auth ID token for the same result as verifyOtp. */
  async verifyFirebase(idToken: string): Promise<OtpVerifyResult> {
    return request("/auth/firebase", { method: "POST", body: JSON.stringify({ id_token: idToken }) });
  },

  async verifyOtp(phone: string, otp: string): Promise<OtpVerifyResult> {
    return request("/auth/otp/verify", { method: "POST", body: JSON.stringify({ phone, otp }) });
  },

  /** Create the account (new number) or reset the PIN, and sign in. */
  async setPin(setupToken: string, pin: string, name: string | null, lang: string): Promise<User> {
    const data = await request<{ access_token: string; user: BackendUser }>("/auth/pin", {
      method: "POST",
      body: JSON.stringify({ setup_token: setupToken, pin, name, lang }),
    });
    storage.setToken(data.access_token);
    const user = toUser(data.user);
    storage.setUser(user);
    return user;
  },

  async deleteMyAccount(): Promise<void> {
    await request("/auth/me", { method: "DELETE" });
    storage.clearToken();
    storage.clearUser();
    storage.clearCases();
  },

  /** The person's saved profile (one per account), or null before the first plan. */
  async getMyProfile(): Promise<{ id: string; profile: Partial<BeneficiaryProfile> } | null> {
    const rows = await request<BackendBeneficiary[]>("/beneficiaries");
    if (!rows.length) return null;
    return { id: String(rows[0].id), profile: toProfile(rows[0]) };
  },

  async login(phone: string, pin: string): Promise<User> {
    const data = await request<{ access_token: string; user: BackendUser }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ phone, pin }),
    });
    storage.setToken(data.access_token);
    const user = toUser(data.user);
    storage.setUser(user);
    return user;
  },

  async getBusinesses(): Promise<BusinessType[]> {
    return request<BusinessType[]>("/meta/businesses");
  },

  async getBusinessParameters(code: string): Promise<BusinessParameters> {
    return request<BusinessParameters>(`/meta/businesses/${encodeURIComponent(code)}/parameters`);
  },

  async searchVillages(query: string): Promise<Village[]> {
    const q = query.trim();
    const rows = await request<BackendVillage[]>(
      `/geo/villages?limit=25${q ? `&q=${encodeURIComponent(q)}` : ""}`
    );
    return rows.map(toVillage);
  },

  async getCases(): Promise<CaseRecord[]> {
    const rows = await request<BackendCase[]>("/cases");
    const cases = rows.map(toCase);
    storage.saveCases(cases); // offline read-only cache of the list
    return cases;
  },

  async getCase(id: string): Promise<CaseRecord> {
    return toCase(await request<BackendCase>(`/cases/${id}`));
  },

  /**
   * Full new-case flow: beneficiary (+consent) → case → local inputs → evaluation.
   * Each step is a real API call; nothing is computed in the browser.
   */
  async createAndEvaluateCase(args: {
    profile: BeneficiaryProfile;
    consent: ConsentRecord;
    village: Village;
    business: BusinessType;
    margin: number;
    targetProjectCost: number | null;
    calibration: CalibrationData;
    language: string;
    existingBeneficiaryId?: string | null;
  }): Promise<CaseRecord> {
    let ben: { id: number };
    if (args.existingBeneficiaryId) {
      // Saved profile: update it with any changes (consent was recorded with the first plan).
      const fields: Record<string, unknown> = { ...toBeneficiaryPayload(args.profile, args.consent) };
      delete fields.consent;
      delete fields.income_band;
      ben = await request<{ id: number }>(`/beneficiaries/${args.existingBeneficiaryId}`, {
        method: "PATCH",
        body: JSON.stringify(fields),
      });
    } else {
      ben = await request<{ id: number }>("/beneficiaries", {
        method: "POST",
        body: JSON.stringify(toBeneficiaryPayload(args.profile, args.consent)),
      });
    }
    const created = await request<{ id: number }>("/cases", {
      method: "POST",
      body: JSON.stringify({
        beneficiary_id: ben.id,
        village_lgd: Number(args.village.lgd_code),
        business_code: args.business.code,
        margin_available: args.margin,
        target_project_cost: args.targetProjectCost,
        language: args.language,
      }),
    });
    await api.evaluate(String(created.id), args.calibration);
    return api.getCase(String(created.id));
  },

  async evaluate(caseId: string, inputs: CalibrationData): Promise<{ evaluation_id: number; output: EvaluationOutput }> {
    const udhar = inputs.udhar_pct;
    return request(`/cases/${caseId}/evaluate`, {
      method: "POST",
      body: JSON.stringify({
        inputs,
        udhar_pct: udhar !== undefined && udhar !== "" ? Number(udhar) : undefined,
      }),
    });
  },

  async generateDpr(evaluationId: string, language: string): Promise<DprDocument> {
    return request<DprDocument>(`/evaluations/${evaluationId}/dpr?language=${encodeURIComponent(language)}`, {
      method: "POST",
    });
  },

  /** Fetch the PDF with the auth header and hand it to the browser as a file. */
  async downloadDpr(doc: DprDocument, filename: string): Promise<void> {
    const token = storage.getToken();
    let res: Response;
    try {
      res = await fetch(`${API_BASE}${doc.download_url}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
    } catch {
      throw new ApiError("Server could not be reached.", 0);
    }
    if (!res.ok) throw new ApiError(`Download failed (${res.status})`, res.status);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  },

  async getAdvisory(evaluationId: string): Promise<{ output: AdvisoryContent; validator_passed: boolean; model: string } | null> {
    try {
      return await request(`/evaluations/${evaluationId}/advisory`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) return null;
      throw e;
    }
  },

  async generateAdvisory(evaluationId: string, language: string): Promise<{ output: AdvisoryContent; validator_passed: boolean; model: string }> {
    return request(`/evaluations/${evaluationId}/advisory?language=${encodeURIComponent(language)}`, {
      method: "POST",
    });
  },

  async updateCaseStatus(id: string, status: CaseStatus, reason?: string): Promise<void> {
    await request(`/cases/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, status_reason_code: reason || null }),
    });
  },
};
