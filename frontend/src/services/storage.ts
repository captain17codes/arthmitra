import { CaseRecord, User } from "../types";
import { INITIAL_CASES_SEED, MOCK_USER } from "./mockData";

const STORAGE_KEYS = {
  AUTH_TOKEN: "arthmitra_auth_token",
  AUTH_USER: "arthmitra_auth_user",
  CASES: "arthmitra_cases",
  LANGUAGE: "arthmitra_language",
  OFFLINE_QUEUE: "arthmitra_offline_queue",
};

export const storage = {
  getToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    } catch {
      return null;
    }
  },

  setToken(token: string): void {
    try {
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    } catch {}
  },

  clearToken(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    } catch {}
  },

  getUser(): User | null {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.AUTH_USER);
      if (data) return JSON.parse(data);
      // Auto-fallback to default Sakhi user if token exists or local mode
      return MOCK_USER;
    } catch {
      return MOCK_USER;
    }
  },

  setUser(user: User): void {
    try {
      localStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));
    } catch {}
  },

  clearUser(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.AUTH_USER);
    } catch {}
  },

  getCases(): CaseRecord[] {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CASES);
      if (data) {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    // Seed initial cases if empty
    this.saveCases(INITIAL_CASES_SEED);
    return INITIAL_CASES_SEED;
  },

  saveCases(cases: CaseRecord[]): void {
    try {
      localStorage.setItem(STORAGE_KEYS.CASES, JSON.stringify(cases));
    } catch {}
  },

  getCaseById(id: string): CaseRecord | undefined {
    const list = this.getCases();
    return list.find((c) => c.id === id);
  },

  saveCase(record: CaseRecord): CaseRecord {
    const list = this.getCases();
    const idx = list.findIndex((c) => c.id === record.id);
    if (idx >= 0) {
      list[idx] = { ...record, updated_at: new Date().toISOString() };
    } else {
      list.unshift({
        ...record,
        created_at: record.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    }
    this.saveCases(list);
    return record;
  },

  updateCaseStatus(
    id: string,
    status: CaseRecord["status"],
    reason?: string
  ): CaseRecord | undefined {
    const list = this.getCases();
    const target = list.find((c) => c.id === id);
    if (target) {
      target.status = status;
      if (reason) target.status_reason = reason;
      target.updated_at = new Date().toISOString();
      this.saveCases(list);
      return target;
    }
    return undefined;
  },

  getLanguage(): string {
    try {
      return localStorage.getItem(STORAGE_KEYS.LANGUAGE) || "mr";
    } catch {
      return "mr";
    }
  },

  setLanguage(lang: string): void {
    try {
      localStorage.setItem(STORAGE_KEYS.LANGUAGE, lang);
    } catch {}
  },
};
