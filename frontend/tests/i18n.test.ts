import { describe, it, expect } from "vitest";
import { translations, formatINR, formatNumberIN } from "../src/i18n";
import { Language } from "../src/types";

describe("i18n and Formatting Invariants", () => {
  const languages: Language[] = ["mr", "hi", "en"];

  it("provides complete translations across all 3 supported languages", () => {
    languages.forEach((lang) => {
      const t = translations[lang];
      expect(t.appName).toBeDefined();
      expect(t.loginTitle).toBeDefined();
      expect(t.casesTitle).toBeDefined();
      expect(t.statutoryHeader).toBeDefined();
      expect(t.statutoryBody).toBeDefined();
      expect(t.marketCardTitle).toBeDefined();
      expect(t.financingCardTitle).toBeDefined();
      expect(t.viabilityCardTitle).toBeDefined();
      expect(t.dprCardTitle).toBeDefined();
    });
  });

  it("formats currency using Indian rupee numbering (lakhs & crores)", () => {
    // ₹1,50,000 (not 150,000)
    const inr150k = formatINR(150000);
    expect(inr150k).toContain("1,50,000");

    // ₹10,00,000 (not 1,000,000)
    const inr10L = formatINR(1000000);
    expect(inr10L).toContain("10,00,000");
  });

  it("formats Indian numbers with commas", () => {
    expect(formatNumberIN(14752)).toBe("14,752");
    expect(formatNumberIN(100000)).toBe("1,00,000");
  });
});
