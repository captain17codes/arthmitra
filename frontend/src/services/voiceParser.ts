/**
 * Deterministic Indian-number parser in TypeScript for client-side instant preview.
 * Supports spoken phrases across Marathi, Hindi, and English:
 *   "दीड लाख" / "dedh lakh" -> 150000
 *   "साडे तीन हजार" / "sade teen hazar" -> 3500
 *   "सव्वा लाख" / "sawa lakh" -> 125000
 *   "पावणे दोन लाख" / "paune do lakh" -> 175000
 *   "अडीच लाख" / "dhai lakh" -> 250000
 *   "दोन लाख पन्नास हजार" -> 250000
 */

const DEVANAGARI_DIGITS_MAP: Record<string, string> = {
  "०": "0",
  "१": "1",
  "२": "2",
  "३": "3",
  "४": "4",
  "५": "5",
  "६": "6",
  "७": "7",
  "८": "8",
  "९": "9",
};

const BASE_WORDS: Record<string, number> = {
  // 0 - 10
  शून्य: 0,
  shunya: 0,
  zero: 0,
  एक: 1,
  ek: 1,
  one: 1,
  दोन: 2,
  दो: 2,
  don: 2,
  do: 2,
  two: 2,
  तीन: 3,
  teen: 3,
  three: 3,
  चार: 4,
  char: 4,
  chaar: 4,
  four: 4,
  पाच: 5,
  पांच: 5,
  paach: 5,
  panch: 5,
  five: 5,
  सहा: 6,
  छह: 6,
  छः: 6,
  saha: 6,
  six: 6,
  सात: 7,
  saat: 7,
  seven: 7,
  आठ: 8,
  aath: 8,
  eight: 8,
  नऊ: 9,
  नौ: 9,
  nau: 9,
  nav: 9,
  nine: 9,
  दहा: 10,
  दस: 10,
  daha: 10,
  das: 10,
  ten: 10,
  // 11 - 20
  अकरा: 11,
  ग्यारह: 11,
  eleven: 11,
  बारा: 12,
  बारह: 12,
  bara: 12,
  twelve: 12,
  तेरा: 13,
  तेरह: 13,
  thirteen: 13,
  चौदा: 14,
  चौदह: 14,
  fourteen: 14,
  पंधरा: 15,
  पंद्रह: 15,
  fifteen: 15,
  सोळा: 16,
  सोलह: 16,
  sixteen: 16,
  सतरा: 17,
  सत्रह: 17,
  seventeen: 17,
  अठरा: 18,
  अठारह: 18,
  eighteen: 18,
  एकोणीस: 19,
  उन्नीस: 19,
  nineteen: 19,
  वीस: 20,
  बीस: 20,
  vees: 20,
  bees: 20,
  twenty: 20,
  // 21 - 99
  पंचवीस: 25,
  पच्चीस: 25,
  तीस: 30,
  tees: 30,
  thirty: 30,
  पस्तीस: 35,
  पैंतीस: 35,
  चाळीस: 40,
  चालीस: 40,
  chalis: 40,
  forty: 40,
  पन्नास: 50,
  पचास: 50,
  pannas: 50,
  pachas: 50,
  fifty: 50,
  साठ: 60,
  saath: 60,
  sixty: 60,
  सत्तर: 70,
  sattar: 70,
  seventy: 70,
  पंच्याहत्तर: 75,
  पचहत्तर: 75,
  ऐंशी: 80,
  अस्सी: 80,
  eighty: 80,
  नव्वद: 90,
  नब्बे: 90,
  ninety: 90,
  शंभर: 100,
  सौ: 100,
  hundred: 100,
};

const SCALE_WORDS: Record<string, number> = {
  कोटी: 10000000,
  करोड: 10000000,
  करोड़: 10000000,
  crore: 10000000,
  cr: 10000000,
  koti: 10000000,
  लाख: 100000,
  लक्ष: 100000,
  lakh: 100000,
  lac: 100000,
  l: 100000,
  हजार: 1000,
  हज़ार: 1000,
  hazar: 1000,
  hazaar: 1000,
  thousand: 1000,
  k: 1000,
  शे: 100,
  शंभर: 100,
  सौ: 100,
  sau: 100,
  hundred: 100,
};

export function normalizeSpokenText(text: string): string {
  if (!text) return "";
  let s = text.trim();
  for (const [dev, lat] of Object.entries(DEVANAGARI_DIGITS_MAP)) {
    s = s.split(dev).join(lat);
  }
  s = s.replace(/[₹$]|rs\.?|inr|rupees?|रुपये|रुपया/gi, " ");
  s = s.replace(/\/-\s*/g, " ");
  s = s.replace(/(?<=\d),(?=\d)/g, "");
  s = s.replace(/[,/\\()\-]+/g, " ");
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

export function formatInrCurrency(amount: number): string {
  const rounded = Math.round(amount);
  const s = Math.abs(rounded).toString();
  const sign = rounded < 0 ? "-" : "";
  if (s.length <= 3) return `${sign}₹${s}`;
  const lastThree = s.slice(-3);
  let rem = s.slice(0, -3);
  const pairs: string[] = [];
  while (rem.length > 2) {
    pairs.unshift(rem.slice(-2));
    rem = rem.slice(0, -2);
  }
  if (rem.length > 0) pairs.unshift(rem);
  return `${sign}₹${pairs.join(",")},${lastThree}`;
}

export function parseIndianSpokenNumber(text: string): number | null {
  const clean = normalizeSpokenText(text);
  if (!clean) return null;

  // Direct digits with optional scale (e.g., '1.5 lakh', '150000', '50k')
  const directMatch = clean.match(/^(\d+(?:\.\d+)?)\s*([a-z\u0900-\u097f]+)?$/);
  if (directMatch) {
    const num = parseFloat(directMatch[1]);
    const scaleStr = directMatch[2];
    if (!scaleStr) return num;
    if (SCALE_WORDS[scaleStr]) {
      return Math.round(num * SCALE_WORDS[scaleStr]);
    }
  }

  // Fused words
  if (clean === "दीडशे" || clean === "dedh sau") return 150;
  if (clean === "अडीचशे" || clean === "dhai sau") return 250;
  if (clean === "सव्वाशे") return 125;
  if (clean === "पावणेदोनशे" || clean === "पावणे दोनशे") return 175;
  if (clean === "साडेतीनशे" || clean === "साडे तीनशे") return 350;

  const tokens = clean.split(" ");
  if (tokens.length === 0) return null;

  const first = tokens[0];

  // 1.5 multiplier (दीड, डेढ़, dedh)
  if (["दीड", "डेढ़", "dedh", "deed"].includes(first)) {
    if (tokens.length === 1) return 1.5;
    const scale = findScale(tokens.slice(1));
    if (scale) return Math.round(1.5 * scale);
  }

  // 2.5 multiplier (अडीच, ढाई, adhai, dhai)
  if (["अडीच", "ढाई", "adhai", "dhai"].includes(first)) {
    if (tokens.length === 1) return 2.5;
    const scale = findScale(tokens.slice(1));
    if (scale) return Math.round(2.5 * scale);
  }

  // 0.25 (पाव, paav)
  if (["पाव", "paav"].includes(first)) {
    if (tokens.length === 1) return 0.25;
    const scale = findScale(tokens.slice(1));
    if (scale) return Math.round(0.25 * scale);
  }

  // 0.5 (अर्धा, आधा, ardha, aadha)
  if (["अर्धा", "आधा", "ardha", "aadha"].includes(first)) {
    if (tokens.length === 1) return 0.5;
    const scale = findScale(tokens.slice(1));
    if (scale) return Math.round(0.5 * scale);
  }

  // 0.75 (पाऊण, पौन, paun)
  if (["पाऊण", "पौन", "paun"].includes(first)) {
    if (tokens.length === 1) return 0.75;
    const scale = findScale(tokens.slice(1));
    if (scale) return Math.round(0.75 * scale);
  }

  // 1.25 (सव्वा, सवा, savva, sawa)
  if (["सव्वा", "सवा", "savva", "sawa"].includes(first)) {
    if (tokens.length === 1) return 1.25;
    const scale = findScale([tokens[1]]);
    if (scale) return Math.round(1.25 * scale);
    const base = getBaseNumber(tokens[1]);
    if (base !== null) {
      const restScale = findScale(tokens.slice(2)) || 1;
      return Math.round((base + 0.25) * restScale);
    }
  }

  // +0.5 (साडे, साढ़े, sade, saade)
  if (["साडे", "साढ़े", "sade", "saade"].includes(first)) {
    if (tokens.length > 1) {
      const base = getBaseNumber(tokens[1]);
      if (base !== null) {
        const scale = findScale(tokens.slice(2)) || 1;
        return Math.round((base + 0.5) * scale);
      }
    }
  }

  // -0.25 (पावणे, पौने, paune)
  if (["पावणे", "पौने", "paune"].includes(first)) {
    if (tokens.length > 1) {
      const directScale = findScale([tokens[1]]);
      if (directScale) return Math.round(0.75 * directScale);
      const base = getBaseNumber(tokens[1]);
      if (base !== null) {
        const scale = findScale(tokens.slice(2)) || 1;
        return Math.round((base - 0.25) * scale);
      }
    }
  }

  // Multi-scale compound (e.g. 'दोन लाख पन्नास हजार')
  let total = 0;
  let currentSegment: string[] = [];
  let foundAnyScale = false;

  for (const token of tokens) {
    if (SCALE_WORDS[token]) {
      const scaleVal = SCALE_WORDS[token];
      const segStr = currentSegment.join(" ").trim();
      if (!segStr) {
        total += scaleVal;
      } else {
        const sub = parseIndianSpokenNumber(segStr) ?? getBaseNumber(segStr);
        if (sub !== null) {
          total += sub * scaleVal;
        } else {
          return null;
        }
      }
      currentSegment = [];
      foundAnyScale = true;
    } else {
      currentSegment.push(token);
    }
  }

  if (currentSegment.length > 0) {
    const remStr = currentSegment.join(" ").trim();
    if (foundAnyScale) {
      const rem = parseIndianSpokenNumber(remStr) ?? getBaseNumber(remStr);
      if (rem !== null) total += rem;
    } else {
      if (BASE_WORDS[remStr] !== undefined) return BASE_WORDS[remStr];
      return null;
    }
  }

  if (foundAnyScale && total > 0) {
    return Math.round(total);
  }

  if (BASE_WORDS[clean] !== undefined) {
    return BASE_WORDS[clean];
  }

  return null;
}

function findScale(tokens: string[]): number | null {
  for (const t of tokens) {
    if (SCALE_WORDS[t]) return SCALE_WORDS[t];
  }
  return null;
}

function getBaseNumber(token: string): number | null {
  if (/^\d+(?:\.\d+)?$/.test(token)) {
    return parseFloat(token);
  }
  return BASE_WORDS[token] !== undefined ? BASE_WORDS[token] : null;
}
