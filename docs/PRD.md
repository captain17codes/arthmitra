## ArthMitra — Product Requirements Document (v1)

Status: Draft 1 · 27 Oct 2026 · Owner: ArthMitra team
Evidence base: `docs/research/ArthMitra_Research_Pack_v1.md` (verified) and the P1–P5 review.

---

### 1. Problem

Government gives concessional credit to marginalized micro-entrepreneurs (SC, OBC, safai karamcharis, divyang persons, women, SHG members), but:
- People pick businesses by copying neighbours, not by local demand, so villages fill up with identical shops.
- They don't know which of 20+ schemes they qualify for, how much margin they need, or what the EMI will be.
- Applications fail on weak project reports (DPRs), missing documents, and unrealistic cash flows.
- After the loan, customer credit (udhar), seasonal cash dips and lack of skills sink the business.

Evidence: NSFDC credit-scheme beneficiaries fell from 85,372 (FY24) to 41,750 (FY25); channelising agencies are weak in 14 states; NSFDC's own evaluation found 61.5% of beneficiaries cite lack of expertise and 22.8% no active market; Mudra NPA is 9.81% of outstanding (Mar 2025).

### 2. Vision

**ArthMitra is the field worker's toolkit that turns "I have ₹X and want to start Y in my village" into a viable, bank-ready, correctly-financed business plan — and then helps the business survive.**

### 3. Principles (non-negotiable)

1. **Numbers come from code, never from the AI.** Eligibility, money, schedules, DSCR, market estimates are deterministic and tested. The AI only writes explanations from those numbers.
2. **Every rule and benchmark has a source and a date.** Unverified or conflicting rules are shown as such, never as fact.
3. **Honest uncertainty.** Market estimates are ranges with a confidence label; local inputs override defaults.
4. **Assisted first.** Built for the Bank Sakhi / CRP / CSC operator sitting with the beneficiary.
5. **Privacy by design.** Minimum data; no Aadhaar; consent by voice in the user's language; user can delete.
6. **Advice, not lending (v1).** We generate the plan and route to official channels. We don't submit to lenders for a fee or touch money (keeps us outside RBI LSP rules until we choose otherwise).

### 4. Users

| Persona | Role in v1 | Key needs |
|---|---|---|
| **Agent** — Bank Sakhi / CRP (NRLM), CSC VLE, NGO field worker | Primary operator | Fast intake by voice, works on a cheap Android phone and weak network, manage many cases, print/share DPR |
| **Beneficiary** — first-time micro-entrepreneur | Subject of the case; listens, confirms, consents | Explanation in Marathi/Hindi, privacy on shared phones, clear "how much will I pay and when" |
| **Supervisor** — block/district coordinator, SCA/DIC officer | Views dashboards | Pipeline of cases, quality of DPRs, outcomes |
| **Admin** — ArthMitra team | Maintains rules and benchmarks | Edit scheme rules with sources, publish versions, audit |

### 5. Scope

#### 5.1 v1 launch boundaries
- **Geography:** Maharashtra (pilot: one district).
- **Languages:** Marathi, Hindi, English (UI, voice, DPR).
- **Businesses (10):** dairy (2 animals), goatery (10+1), broiler (small batch), kirana, tailoring, beauty parlour, mobile repair, flour/masala mill, papad/pickle/snacks, two-wheeler repair.
- **Schemes (rules engine):**
  - Verified: NSFDC Micro Finance, NSFDC Term Loan, PMEGP, CMEGP, MUDRA (Shishu/Kishor/Tarun/Tarun Plus), Stand-Up India, MPBCDC Seed Capital, DAY-NRLM SHG interest subvention (info).
  - Shown as "confirm with agency": NBCFDC (conflicting official terms), NSKFDC, NDFDC, LIDCOM, LASDC, VNVJNTDC, Annasaheb Patil (until verified).

#### 5.2 Out of scope for v1 (roadmap)
Lender integrations / application APIs, DigiLocker, WhatsApp bot, IVR, offline computation, other states, beneficiary self-serve app, post-loan bookkeeping (v1.5), payments.

### 6. User journey (agent mode)

1. **Login** (agent phone + PIN; agent belongs to an organization).
2. **New case → consent:** app plays the consent notice in the chosen language; beneficiary says/taps "yes"; recorded in the consent ledger.
3. **Profile (minimal):** first name, gender, age, category (SC/ST/OBC/VJNT/SBC/General), disability ≥40% (y/n), occupation flags (sanitation worker, traditional artisan, street vendor), family income band, education band, prior govt subsidy (y/n), existing loans/EMI, credit default (y/n/unknown), SHG member (y/n).
4. **Location:** pick district → taluka → village (LGD list, searchable in Marathi/English).
5. **Idea & money:** business type (icon tiles), available own money (margin), optional target project size.
6. **Local check (calibration, 3–5 questions per business):** e.g., kirana — "How many kirana shops within walking distance?", "Expected daily customers?", "Shop rent?"; dairy — "Milk rate at your collection centre?", "Fodder available on own land?".
7. **Results screen:**
   - **Market:** catchment population, estimated monthly spend on this category, competitors (range), and **"you need X% of local demand to break even"** with Low/Medium/High saturation.
   - **Best financing options (top 3 packages):** scheme(s), project cost, own money, loan, subsidy, rate, tenure, moratorium, EMI and first EMI date, total repayment; why other schemes don't fit.
   - **Viability:** 5-year projection, DSCR, break-even, working capital need (Nayak), **udhar slider** and **income-timing warning**.
   - **Advisory (AI text):** opportunities, SWOT, threats + mitigations, pricing guidance, complementary businesses if saturated.
8. **DPR:** generate a bank-ready PDF (chosen language + English copy for the bank), with document checklist and the exact portal/office to apply.
9. **Track:** case status (draft → DPR ready → applied → sanctioned/rejected → disbursed) with reason codes.

### 7. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| F1 | Agent auth, organizations, roles (agent, supervisor, admin) | P0 |
| F2 | Voice consent capture + consent ledger (who, notice version, language, timestamp, audio hash) | P0 |
| F3 | Voice input on every free-text/number field; transcript always editable before use | P0 |
| F4 | LGD-based village picker for Maharashtra | P0 |
| F5 | Rules engine: eligibility for all v1 schemes with reasons, rule status, and source links | P0 |
| F6 | Stacking guard (no two capital subsidies; prior-subsidy exclusion) | P0 |
| F7 | Financing packages: ranked top 3 with full terms | P0 |
| F8 | Amortization engine: monthly/quarterly, moratorium simple interest (capitalise or pay), subsidy treatment (upfront or 3-yr FDR adjustment), slab rates | P0 |
| F9 | Viability: 5-yr projections, DSCR, BEP, Nayak WC, udhar stress, income-start mismatch | P0 |
| F10 | Market engine: catchment population, category demand, competitor range, break-even market share | P0 |
| F11 | Local calibration questions per business; local values override defaults and are marked in the DPR | P0 |
| F12 | AI advisory in Marathi/Hindi/English, grounded only on computed facts; number-check guardrail | P0 |
| F13 | DPR PDF in bank format (sections in Tech Spec §7) | P0 |
| F14 | Case list, status tracking, reason codes | P0 |
| F15 | Admin: edit scheme rules & benchmarks as versioned data, publish, view diff, audit log | P0 |
| F16 | Supervisor dashboard (cases by status, schemes, businesses, saturation flags) | P1 |
| F17 | Data deletion request flow (beneficiary) | P0 |
| F18 | Read-aloud of results (TTS) | P1 |
| F19 | Draft capture while offline, sync later | P1 |
| F20 | Export case data to CSV for partner agencies (consented fields only) | P2 |

### 8. Non-functional requirements

| Area | Target |
|---|---|
| Devices | Android 9+, 2 GB RAM, Chrome; PWA first-load ≤ 500 KB JS gzipped |
| Network | Usable on 3G; report generation ≤ 20 s p95; all screens show progress |
| Accuracy | Finance engine matches golden test vectors to ±₹1; every rule has tests |
| Accessibility | WCAG 2.1 AA; touch targets ≥ 48 dp; icons + text; read-aloud |
| Privacy | DPDP-aligned: consent, purpose limitation, deletion, India hosting; processing logs kept ≥ 1 yr without document content |
| Security | OWASP ASVS L2 basics, encrypted PII columns, role-based access, rate limiting, audit log |
| Reliability | 99.5% monthly (pilot); graceful fallback if AI/ASR fail (numbers still shown) |
| Localisation | All UI strings, DPR, and AI output in mr/hi/en; Indian number format (₹10,00,000) |

### 9. Success metrics (pilot, 6 months)

| Metric | Target |
|---|---|
| Cases completed per active agent per week | ≥ 5 |
| DPRs that reach an application | ≥ 60% |
| Sanction rate vs district baseline | +25% relative |
| Median days application → sanction | track (baseline ~90 days for NSFDC) |
| Cases steered away from High-saturation businesses | track |
| 12-month business survival (follow-up sample) | ≥ 80% |
| On-time repayment (sample, with consent) | ≥ 90% |

### 10. Risks

| Risk | Mitigation |
|---|---|
| Scheme rules change or are wrong | Versioned rules with source/date; admin review; "confirm with agency" status; monthly rule audit |
| Market estimates misleading | Ranges + confidence; mandatory local calibration; never block a user — warn |
| AI writes wrong numbers or advice | Facts-only prompt; number-check validator; fallback template text |
| Agents don't adopt | Co-design with 5 Bank Sakhis; < 15 min per case; DPR saves them work |
| Privacy incident | Minimal data, encryption, no Aadhaar, incident playbook |
| Becoming an LSP by accident | No lender submission or lender fees in v1; legal review before Phase 3 |

### 11. Release plan

| Release | Contents |
|---|---|
| **v0.9 internal** | Engines + admin + agent flow in English; golden tests |
| **v1.0 pilot** | mr/hi, voice, DPR, 10 businesses, 1 district, 30–50 agents |
| **v1.5** | Post-loan: reminders, simple voice bookkeeping, survival check-ins; WhatsApp delivery |
| **v2** | DigiLocker, lender/SCA partnership (then LSP compliance), more states |

---
