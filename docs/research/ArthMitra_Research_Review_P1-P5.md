## ArthMitra — Research Review (P1–P5)

Reviewed: Scheme Inventory (P1), Village Data Stack (P2), Viability & Unit Economics (P3), Rural Users (P4), Legal & Compliance (P5).
Status legend: ✅ use as-is · ⚠️ verify on the official source before coding · ❌ wrong or unreliable, don't use

---

### 1. Decisions the research already locks in

| # | Decision | Why (source) |
|---|---|---|
| D1 | **Multi-scheme rules engine, not just NSFDC.** v1 covers MoSJE corporations (NSFDC, NBCFDC, NSKFDC, NDFDC) + PMEGP + MUDRA + Stand-Up India + PM Vishwakarma + Maharashtra (CMEGP, MPBCDC, LIDCOM, LASDC, VNVJNTDC, Annasaheb Patil). | P1 gives IF/THEN rules for all of them. |
| D2 | **Rules are deterministic code, versioned as data (YAML/JSON), each rule linked to its source circular + date.** | P1. Schemes change often; rules must be updatable without code changes. |
| D3 | **Stacking guard:** never two capital subsidies on the same asset (PMEGP ✕ CMEGP ✕ PMFME ✕ caste-corp subsidy). Debt + guarantee + interest subvention can stack. | P1 stacking section. |
| D4 | **Drop OpenStreetMap as the competitor source.** Rural shop coverage in OSM is under 10%, so counts would be badly wrong. | P2. |
| D5 | **Competitor estimate = 6th Economic Census baseline × growth, then corrected by the user/agent ("how many kirana shops near you?").** Always shown as a range, never as a hard count. | P2. 7th EC microdata is unreleased; Google Places is too costly and can't be cached. |
| D6 | **LGD village code is the master key** for every table. Census 2011 code is only a legacy join key. | P2. |
| D7 | **Don't use SHRUG in the production database** (non-commercial licence). Use it offline only to calibrate coefficients. | P2. |
| D8 | **Bank-grade appraisal built in:** DSCR ≥ 1.25 (trading/service) / ≥ 1.5 (manufacturing) target, break-even %, Nayak working capital (25% of turnover: 20% bank, 5% promoter), FOIR ≤ 50% for microfinance-route loans. | P3. |
| D9 | **Output = bank-ready DPR** (promoter profile, project cost, means of finance, 5-year projections, DSCR, BEP, repayment schedule). | P3 + P4: weak DPRs are a top rejection reason. |
| D10 | **Assisted mode first.** Primary users are Bank Sakhis / CRPs (NRLM) and CSC VLEs operating ArthMitra for beneficiaries. Direct-to-user comes later. | P4: shared phones, low literacy. |
| D11 | **v1 is information + DPR + routing to official portals only.** No loan application API to lenders, no referral fees, no money flow. | P5: the moment we facilitate applications for a lender or take fees, we become an RBI Lending Service Provider. |
| D12 | **Never collect or store Aadhaar numbers or images.** Documents later via DigiLocker. Store only eligibility flags (e.g., `category=SC, verified=false`), not certificates. | P5. |
| D13 | **Consent in the user's language, by voice, logged** (who, what, when, hash). Hard delete on withdrawal. | P5 (DPDP). |
| D14 | **Accessibility (WCAG 2.1 AA) and India hosting from day one.** | P5. |
| D15 | **Repayment advice aware of crop seasons and income-start delay** (goatery, dairy, poultry). | P2, P3. |

---

### 2. Conflicts and items to verify before coding (⚠️)

| # | Item | What the reports say | Action |
|---|---|---|---|
| V1 | **NSFDC income ceiling** | P1: ₹5 L (from Jan 2026). P4: ₹3 L. | Check nsfdc.nic.in scheme page / latest circular. This changes eligibility for everyone, so it is the #1 check. |
| V2 | PM SVANidhi tranche amounts | P1: ₹10k / ₹20k / ₹50k. | Likely outdated: the scheme was restructured in 2025 with larger first tranches. Check pmsvanidhi.mohua.gov.in. |
| V3 | Stand-Up India debt share | P1 says 85% loan. | Official guideline says the loan is expected to cover 75% of project cost, unless convergence funds more than 25%. Check standupmitra.in. |
| V4 | MUDRA margins (10–15%, 15–20%) | P1 presents them as rules. | Not statutory; banks decide. Show as "bank may ask". |
| V5 | Mudra NPA 9.81% | P4 attributes it to Shishu only. | Check the source; it may be total Mudra. Don't put on a slide until checked. |
| V6 | DAY-NRLM interest subvention | P1: 7% up to ₹3 L. P3: "up to ₹20 L at 7%". | ₹20 L is the collateral-free limit, not the subvention limit. Check the RBI DAY-NRLM master circular. |
| V7 | HCES shares | P2 and P3 give different numbers (conveyance 7.55% vs 8.59%; "4.91%" used for both cereals and egg/fish/meat). | Take numbers directly from the MoSPI HCES 2023-24 factsheet (state-wise, rural). |
| V8 | FSSAI basic registration limit raised to ₹1.5 Cr | P3. | Check the FSSAI notification and whether it is in force. |
| V9 | UIDAI "Circular 14 of 2025" details | P5. | Check uidai.gov.in. The principle (don't store Aadhaar) holds either way. |
| V10 | NBCFDC General Term Loan margin and project cap | P1: 15% margin, ₹15 L cap, tiered 6/7/8%. | Check nbcfdc.gov.in (matches the earlier SIH research, so probably correct). |
| V11 | Maharashtra corporation details (MPBCDC 75/20/5 split, LIDCOM, LASDC limits) | P1 relies on secondary sites. | Check sjsa.maharashtra.gov.in and the corporations' own sites. |

### 3. Errors to fix (❌)

| # | Problem | Correct handling |
|---|---|---|
| E1 | P2 spending formula multiplies **households × per-capita MPCE**. | MPCE is per person: spending = population × MPCE × category share (or households × household size × MPCE). |
| E2 | P2 uses "district MPCE" from HCES. | HCES publishes state and rural/urban level (some NSS-region data). District values must be modelled, not looked up. |
| E3 | "88% of PMEGP applications rejected" (P4). | Source is a consultancy blog. Don't use. Use official sanction vs application data from the PMEGP portal / PIB if needed. |
| E4 | P5 says the DPDP notice must be available in all 22 languages. | The rule is that the user must be able to get the notice in English or any 8th Schedule language. We serve our launch languages well and add more on request. |
| E5 | P5 says "9×9 mm touch targets" are mandated by WCAG 2.1 AA. | Not an AA requirement. Use 48×48 dp anyway (Android guideline, good for rural users). |
| E6 | P5: DPDP Rules "notified Jan 3, 2025". | That was the draft. Final rules were notified in Nov 2025, with phased dates (Board Nov 2025, consent managers Nov 2026, main duties May 2027). The timeline table in P5 is right. |
| E7 | P5: "facilitation without commission = LSP". | LSP status comes from being engaged by a lender. Sending users to government portals (Jan Samarth, PMEGP, Maha-DISHA) with a DPR is not LSP work. This supports D11. |

---

### 4. Gaps

| Gap | Impact | Fix |
|---|---|---|
| **G1. Unit economics** (P3 Part B): 22 of 25 businesses came back "NOT FOUND". | Critical: viability, DSCR and DPRs need these numbers. | Re-run with the prompt in §5.1 (names the exact source documents). |
| G2. Fact-check of V1–V11 | Wrong eligibility = wrong advice. | Run the prompt in §5.2, or check manually (most are one official page each). |
| G3. P6–P10 not yet received | Integrations, tech stack, business model, post-loan, pitch numbers. | Send when ready. |

---

### 5. Follow-up prompts

#### 5.1 Unit economics re-run (paste with the Common Context Block)
```
Find REAL published model project data for rural micro-enterprises. Use ONLY these source types and cite document title, page and year for every number:
(a) NABARD "Model Bank Projects" / model schemes (dairy, goat, sheep, broiler, layer, backyard poultry, fishery, mushroom, vermicompost),
(b) KVIC/PMEGP "model project profiles" listed on the PMEGP e-portal (kviconline.gov.in),
(c) MSME-DI / NI-MSME project profiles,
(d) Maharashtra state agency model projects (MAVIM, MSRLM/UMED, District Industries Centre),
(e) bank SME desk model DPRs (SBI, Bank of Maharashtra) if public.

For these 15 businesses: dairy (2 and 5 animals), goatery (10+1), broiler (500 birds), layer poultry, kirana, tailoring, beauty parlour, mobile repair, flour mill, masala unit, papad/pickle, bakery, tea stall/snacks, two-wheeler repair, e-rickshaw.

For each give: project cost and item-wise capex; working capital; annual revenue (with quantity × price assumptions); itemised operating costs; net profit; DSCR; break-even %; months to first income; key physical norms (e.g., litres/animal/day, mortality %, cycles/year); and the year of the prices used.
If a value is not in a source, write NOT FOUND. Do not estimate.
Output one table per business plus one summary table, ready to convert to JSON.
```

#### 5.2 Fact-check (short, one session)
```
Verify each statement below ONLY from official sources (gov.in / nic.in / rbi.org.in / ministry PDFs). For each: TRUE / FALSE / PARTLY, the correct current value, exact source link, and its date.
1. NSFDC annual family income ceiling for loans is ₹5,00,000 (or is it ₹3,00,000?), effective from which date?
2. NSFDC Micro Credit Finance: project ≤ ₹1.40 L, loan max ₹1.25 L, 6.5%, 3 years incl. 3-month moratorium, quarterly.
3. NSFDC Term Loan: ≤ ₹50 L, loan max ₹45 L, 8%, up to 7 years incl. 6-month moratorium.
4. NSFDC Mahila Samriddhi Yojana: rate 4%, loan max ₹1.25 L (or other?).
5. NBCFDC General Loan: up to ₹15 L, loan 85%, rates 6/7/8% by slab, income ceiling ₹3 L.
6. PM SVANidhi current tranche amounts and validity period after the 2025 restructuring.
7. Stand-Up India: share of project cost the bank loan is expected to cover; margin rules.
8. DAY-NRLM: loan amount eligible for interest subvention at 7%; collateral-free limit for SHGs.
9. PMEGP: subsidy rates and project cost limits for 2025-26; education condition.
10. CMEGP Maharashtra: age limits, project limits, subsidy rates.
11. MPBCDC Seed Capital scheme: project range, bank/corporation/beneficiary shares, interest rate, income limit.
12. Mudra NPA ratio as of March 2025: overall and Shishu separately.
13. FSSAI basic registration turnover limit currently in force.
14. Final DPDP Rules notification date and phased commencement dates.
```

---

### 6. What stays the same from the hackathon build
- Finance engine approach (deterministic, tested) — extend to multi-scheme.
- Udhar stress slider and income-timing mismatch warning — both confirmed as real failure causes (P1, P3).
- "AI never does maths" — reinforced by every report.

### 7. Next step
Send P6–P10 and the results of §5.1 and §5.2. Then I'll produce: PRD (v1 scope), system architecture, data model (LGD-keyed), rules-engine spec, and the new Antigravity build plan for ArthMitra.
