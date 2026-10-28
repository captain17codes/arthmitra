import { CaseRecord, User } from "../types";

/**
 * Browser storage for per-device conveniences only: auth token, the signed-in user,
 * language, and a read-only cache of the case list for viewing while offline.
 * The server is always the source of truth; nothing here is ever invented.
 */
const STORAGE_KEYS = {
  AUTH_TOKEN: "arthmitra_auth_token",
  AUTH_USER: "arthmitra_auth_user",
  CASES: "arthmitra_cases_cache_v2",
  LANGUAGE: "arthmitra_language",
};

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    /* storage unavailable (private mode etc.) */
  }
}

export const storage = {
  getToken(): string | null {
    return read(STORAGE_KEYS.AUTH_TOKEN);
  },
  setToken(token: string): void {
    write(STORAGE_KEYS.AUTH_TOKEN, token);
  },
  clearToken(): void {
    write(STORAGE_KEYS.AUTH_TOKEN, null);
  },

  getUser(): User | null {
    const data = read(STORAGE_KEYS.AUTH_USER);
    if (!data || !read(STORAGE_KEYS.AUTH_TOKEN)) return null;
    try {
      return JSON.parse(data) as User;
    } catch {
      return null;
    }
  },
  setUser(user: User): void {
    write(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));
  },
  clearUser(): void {
    write(STORAGE_KEYS.AUTH_USER, null);
  },

  getCases(): CaseRecord[] {
    const data = read(STORAGE_KEYS.CASES);
    if (!data) return [];
    try {
      const parsed = JSON.parse(data);
      return Array.isArray(parsed) ? (parsed as CaseRecord[]) : [];
    } catch {
      return [];
    }
  },
  saveCases(cases: CaseRecord[]): void {
    // Cache list fields only (no evaluation payloads) to keep storage small.
    const slim = cases.map((c) => ({ ...c, output: undefined }));
    write(STORAGE_KEYS.CASES, JSON.stringify(slim));
  },
  clearCases(): void {
    write(STORAGE_KEYS.CASES, null);
  },

  getLanguage(): string {
    return read(STORAGE_KEYS.LANGUAGE) || "mr";
  },
  setLanguage(lang: string): void {
    write(STORAGE_KEYS.LANGUAGE, lang);
  },
};
