import {
  BusinessType,
  CaseRecord,
  EvaluationResult,
  User,
  Village,
} from "../types";
import { storage } from "./storage";
import {
  MOCK_BUSINESS_TYPES,
  MOCK_USER,
  MOCK_VILLAGES,
  createMockEvaluation,
} from "./mockData";

const API_BASE = import.meta.env.VITE_API_BASE || "";

class ApiService {
  private getHeaders(): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const token = storage.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async login(phone: string, pin: string): Promise<{ token: string; user: User }> {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, pin }),
      });
      if (res.ok) {
        const data = await res.json();
        const token = data.access_token || "jwt_demo_token";
        storage.setToken(token);
        const user = data.user || MOCK_USER;
        storage.setUser(user);
        return { token, user };
      }
    } catch {}

    // Offline / Mock fallback (validates 4-digit PIN)
    if (pin.length === 4) {
      const mockToken = "mock_jwt_token_" + Date.now();
      storage.setToken(mockToken);
      storage.setUser(MOCK_USER);
      return { token: mockToken, user: MOCK_USER };
    }
    throw new Error("Invalid phone or PIN");
  }

  async getMe(): Promise<User> {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: this.getHeaders(),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {}
    return storage.getUser() || MOCK_USER;
  }

  async getBusinesses(): Promise<BusinessType[]> {
    try {
      const res = await fetch(`${API_BASE}/meta/businesses`, {
        headers: this.getHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) return data;
      }
    } catch {}
    return MOCK_BUSINESS_TYPES;
  }

  async searchVillages(query: string): Promise<Village[]> {
    if (!query || query.trim().length === 0) {
      return MOCK_VILLAGES;
    }
    const q = query.trim().toLowerCase();
    try {
      const res = await fetch(
        `${API_BASE}/geo/search?q=${encodeURIComponent(query)}&limit=10`,
        { headers: this.getHeaders() }
      );
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) return data;
      }
    } catch {}

    return MOCK_VILLAGES.filter(
      (v) =>
        v.name_en.toLowerCase().includes(q) ||
        v.name_mr.includes(query) ||
        v.district_en.toLowerCase().includes(q) ||
        v.district_mr.includes(query) ||
        v.subdistrict_en.toLowerCase().includes(q) ||
        v.subdistrict_mr.includes(query)
    );
  }

  async getCases(): Promise<CaseRecord[]> {
    try {
      const res = await fetch(`${API_BASE}/cases`, {
        headers: this.getHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          storage.saveCases(data);
          return data;
        }
      }
    } catch {}
    return storage.getCases();
  }

  async getCase(id: string): Promise<CaseRecord | undefined> {
    try {
      const res = await fetch(`${API_BASE}/cases/${id}`, {
        headers: this.getHeaders(),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {}
    return storage.getCaseById(id);
  }

  async saveCase(caseRecord: CaseRecord): Promise<CaseRecord> {
    try {
      const res = await fetch(`${API_BASE}/cases`, {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify(caseRecord),
      });
      if (res.ok) {
        const saved = await res.json();
        return storage.saveCase(saved);
      }
    } catch {}
    return storage.saveCase(caseRecord);
  }

  async evaluateCase(
    caseRecord: CaseRecord,
    udharPct: number = 20
  ): Promise<EvaluationResult> {
    try {
      const res = await fetch(`${API_BASE}/cases/${caseRecord.id}/evaluate`, {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({
          udhar_pct: udharPct,
          ...caseRecord.calibration,
        }),
      });
      if (res.ok) {
        const evalRes = await res.json();
        caseRecord.evaluation = evalRes;
        caseRecord.status = "ready";
        storage.saveCase(caseRecord);
        return evalRes;
      }
    } catch {}

    // Fallback to pure calculation mock evaluation
    const evalResult = createMockEvaluation(caseRecord, udharPct);
    caseRecord.evaluation = evalResult;
    caseRecord.status = "ready";
    storage.saveCase(caseRecord);
    return evalResult;
  }

  async generateDpr(
    evaluationId: string,
    language: string = "mr"
  ): Promise<{ download_url: string; sha256: string }> {
    try {
      const res = await fetch(`${API_BASE}/evaluations/${evaluationId}/dpr`, {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({ language }),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {}

    return {
      download_url: `/api/dpr/mock_${evaluationId}_${language}.pdf`,
      sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    };
  }

  async updateCaseStatus(
    id: string,
    status: CaseRecord["status"],
    reason?: string
  ): Promise<CaseRecord | undefined> {
    try {
      const res = await fetch(`${API_BASE}/cases/${id}/status`, {
        method: "PATCH",
        headers: this.getHeaders(),
        body: JSON.stringify({ status, reason }),
      });
      if (res.ok) {
        const updated = await res.json();
        return storage.saveCase(updated);
      }
    } catch {}
    return storage.updateCaseStatus(id, status, reason);
  }
}

export const api = new ApiService();
