# ArthMitra — Complete Build Package (single file for Antigravity)

This file combines everything: (1) Build Plan, (2) PRD, (3) Technical Spec, (4) Verified Research Pack, (5) Research Review P1–P5.
Read it fully before writing code. Section 3 (Technical Spec) is the source of truth. When creating the repo, also save each part as its own file: PLAN.md, docs/PRD.md, docs/TECH_SPEC.md, docs/research/ArthMitra_Research_Pack_v1.md, docs/research/ArthMitra_Research_Review_P1-P5.md.


---

<!-- ===== FILE: PLAN.md ===== -->

## ArthMitra — Build Plan for Antigravity

Read order for the agent: `PLAN.md` → `docs/PRD.md` → `docs/TECH_SPEC.md` → `docs/research/ArthMitra_Research_Pack_v1.md`.

### How to use
1. Create an empty repo `arthmitra/`. Put this file at the root, and the docs in `docs/` and `docs/research/`.
2. Paste **Section 0** into Antigravity once.
3. Paste one phase prompt at a time (Section 2). Don't start the next phase until the acceptance checks pass and you've reviewed the diff.
4. Human tasks (Section 3) run in parallel — the agent can't download some government files or create accounts for you.

---

### 0. Master context (paste first)

> You are the lead engineer building **ArthMitra**, a production product. Read PLAN.md, docs/PRD.md and docs/TECH_SPEC.md completely before writing code. TECH_SPEC is the source of truth; if something is unclear or contradictory, stop and ask me instead of guessing.
>
> Non-negotiable rules:
> 1. **AI never computes numbers or eligibility.** All money, eligibility, schedules, DSCR and market figures come from the pure Python engines in `backend/engines/`. LLM output is text only and must pass the number validator.
> 2. Scheme rules and business benchmarks live in `data/` as versioned YAML with source URL and date. Never hard-code scheme terms in Python.
> 3. Golden test vectors in TECH_SPEC §4 must pass to ±₹1. Never edit a test to make it pass; fix the code or ask me.
> 4. No Aadhaar, PAN or bank account number fields anywhere. PII columns encrypted. Consent before any profile data is saved.
> 5. Every external call (LLM, ASR, OSM, any API) goes through an adapter with timeout, retry and a fallback.
> 6. Small, reviewable commits per phase. After each phase: run lint, type-check and tests, then show me the results and a short summary of what changed.
> 7. Mobile-first UI for a 360×640 Android screen; all strings through i18n (mr, hi, en); Indian number format.

---

### 1. Phase overview

| # | Phase | Output |
|---|---|---|
| 0 | Repo & tooling | Monorepo, Docker Compose (Postgres+PostGIS, Redis), CI |
| 1 | Database | Alembic migrations for TECH_SPEC §2, seed for business types & schemes |
| 2 | Finance engine | Amortization incl. moratorium modes, FDR subsidy, slabs; golden tests |
| 3 | Rules engine | YAML loader/validator, evaluator, stacking, ranking; scheme files |
| 4 | Benchmarks & viability | Benchmark library, 10 revenue models, projections, DSCR, BEP, Nayak, udhar, timing |
| 5 | Data pipeline & geo API | Maharashtra villages with population, coords, amenities; neighbour table |
| 6 | Market engine | Catchment, demand, break-even share, saturation, complements |
| 7 | Core API | Auth, beneficiaries, consent, cases, evaluate, status |
| 8 | Advisory | LLM adapter, facts builder, prompt, validator, async jobs |
| 9 | DPR | PDF in mr/hi/en, bank format |
| 10 | Agent PWA | Full agent journey, i18n |
| 11 | Voice | ASR adapter, Indian number parser, mic UI, consent recording |
| 12 | Admin & supervisor | Rule/benchmark editing with publish + diff, dashboards |
| 13 | Privacy & security | Deletion, processing log, encryption, rate limits, audit |
| 14 | Quality & deploy | E2E tests, performance budget, India-region deploy, runbooks |

---

### 2. Phase prompts

#### Phase 0 — Repo & tooling
> Create the monorepo layout from TECH_SPEC §1. Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, pytest, ruff, mypy. Frontend: React + Vite + TypeScript + Tailwind + vite-plugin-pwa, eslint, vitest, Playwright. docker-compose with postgis/postgis:16, redis, api, worker (RQ), web. Add `.env.example`, Makefile targets (`make up`, `make test`, `make lint`), and GitHub Actions CI running lint, type-check and tests. README with setup steps.
✅ `make up` starts everything; `/health` returns ok; CI passes on an empty test.

#### Phase 1 — Database
> Implement the full data model from TECH_SPEC §2 as SQLAlchemy models and Alembic migrations, including enums, indexes (village name trigram search, case status, org), PostGIS geometry column on villages, and the encryption helper for 🔒 columns. Seed `business_types` (10 v1 businesses with mr/hi/en names, sector, HCES category, λ) and `schemes` (codes only).
✅ Migrations up/down cleanly; encryption round-trip test passes; seed visible in DB.

#### Phase 2 — Finance engine
> Build `backend/engines/finance/` exactly per TECH_SPEC §4: simple-interest moratorium with capitalise/pay modes, monthly or quarterly frequency, fixed/slab/bank-rate interest, FDR subsidy credited at month 36 with EMI recompute, schedule with rounding absorbed in the last row, totals. Pure functions, Decimal arithmetic, full type hints. Write all golden vectors from §4 as tests plus property tests (sum of principal = financed amount; final balance 0).
✅ All golden tests pass to ±₹1; coverage ≥ 95% for the engine.

#### Phase 3 — Rules engine
> Build `backend/engines/rules/`: YAML schema (pydantic) for scheme files per TECH_SPEC §3.1, operators, evaluator returning ELIGIBLE / NOT_ELIGIBLE(reasons) / NEEDS_INFO / CONFIRM_WITH_AGENCY, pre-screen gates, project sizing (§3.3), stacking from `data/schemes/stacking.yaml`, deterministic ranking (§3.2). Author YAML files using ONLY values in the Research Pack §1: NSFDC_MFS, NSFDC_TL, PMEGP, CMEGP, MUDRA (4 tiers), STANDUP_INDIA, MPBCDC_SEED (status verified where the pack says ✅), NBCFDC_GL (status conflict, both versions noted), NSKFDC/NDFDC/LIDCOM/LASDC/VNVJNTDC/ANNASAHEB_PATIL as unverified stubs with source fields. Every file includes `tests:`; CI runs them.
✅ Scheme tests pass; a test proves no package has two capital subsidies; each reason code is reachable.

#### Phase 4 — Benchmarks & viability
> Create `data/benchmarks/*.yaml` for the 10 v1 businesses with keys from TECH_SPEC §5, each value carrying source, year, region and confidence. Use the Research Pack §2.1 for verified values; anything else is `confidence: estimate` with a TODO note — do not invent sources. Build `backend/engines/viability/`: one revenue model function per business, cost model, 5-year projection with ramp, DSCR, BEP, Nayak WC, udhar stress, income-timing check, seasonality, FOIR. Snapshot tests for each business.
✅ Tests pass; goatery triggers the income-timing warning; udhar 40% lowers DSCR in every business.

#### Phase 5 — Data pipeline & geo API
> Write idempotent ETL scripts in `data/pipeline/` per TECH_SPEC §10 for Maharashtra. Inputs are placed by me in `data/pipeline/raw/` (see PLAN §3). Produce processed CSVs, load them into `villages` and `village_neighbours`, and write `data/pipeline/processed/REPORT.md` with row counts and match rates (LGD↔Census, LGD↔OSM coords). Add geo endpoints from TECH_SPEC §9 with Marathi/English search.
✅ Pune district villages searchable; coordinate match rate reported; neighbours computed.

#### Phase 6 — Market engine
> Build `backend/engines/market/` per TECH_SPEC §6 (population projection, distance-decay catchment, per-person MPCE demand, agent-reported competitors, break-even market share, saturation bands, complements). Every output has value, range and confidence. Tests on 3 reference villages.
✅ Tests pass; the engine never uses OSM shop counts; ranges shown.

#### Phase 7 — Core API
> Implement auth (phone+PIN, argon2, JWT, rate limit), organizations/roles, beneficiaries (consent required before saving profile), consent endpoint (stores notice version, language, audio hash), cases, inputs, `/cases/{id}/evaluate` that snapshots inputs and versions into `evaluations`, status updates with reason codes, audit_log and processing_log on every access. OpenAPI documented.
✅ API tests cover the full case lifecycle and role restrictions.

#### Phase 8 — Advisory
> Build `adapters/llm.py` (provider-agnostic, env-configured, timeout, retry), facts builder from an evaluation, the prompt in mr/hi/en, JSON schema output, number validator (TECH_SPEC §7.1) with one regeneration then template fallback, and an RQ job + `/jobs/{id}`. Store prompt_version and validator result.
✅ Validator tests catch injected wrong numbers; fallback works with the LLM disabled.

#### Phase 9 — DPR
> Build the DPR per TECH_SPEC §7.2 with Jinja2 + WeasyPrint and Noto Sans Devanagari. Mark default vs local values. Generate both the selected language and English. Store in object storage with sha256.
✅ Sample DPRs for 3 cases render correctly in Marathi and English; numbers match the evaluation exactly.

#### Phase 10 — Agent PWA
> Build the agent journey from PRD §6: login, case list, new case, consent, profile, village picker, business tiles, margin, calibration questions (from benchmark config), results (market, top-3 packages with schedule, viability with udhar slider, advisory), DPR download/share, status update. i18n mr/hi/en, ₹ en-IN formatting, large touch targets, loading states, offline draft saving.
✅ Playwright E2E completes a case on a 360×640 viewport; JS bundle ≤ 500 KB gzipped.

#### Phase 11 — Voice
> Build `adapters/asr.py` (primary + fallback provider), `/speech/transcribe`, an Indian-number parser (e.g., "दीड लाख" → 150000, "साडे तीन हजार" → 3500) with extensive tests, a mic component on text/number fields with an editable transcript, and voice consent recording in the consent step. Optional TTS read-aloud of results.
✅ Parser tests pass (≥ 60 cases across mr/hi/en); voice works on Android Chrome; nothing is used in calculations without confirmation.

#### Phase 12 — Admin & supervisor
> Admin screens: scheme versions (edit YAML in a form, validate, run tests, show diff, publish), benchmarks (edit with source/year/confidence), village coordinate fixes. Supervisor dashboard: cases by status, scheme, business, saturation flags, per agent.
✅ Publishing a scheme version re-runs its tests and records audit_log; old evaluations stay reproducible.

#### Phase 13 — Privacy & security
> Deletion workflow (TECH_SPEC §2 note), processing-log retention job (purge after 1 year), encryption key rotation script, security headers, CORS, input validation, dependency audit, secrets scanning in CI, and an incident runbook in `docs/runbooks/`.
✅ Deletion test proves PII, audio and DPRs are gone while processing logs remain; security checks pass in CI.

#### Phase 14 — Quality & deploy
> Load test evaluate and DPR endpoints (p95 targets from PRD §8), fix hotspots. Infrastructure-as-code for an India-region deployment (managed Postgres with PostGIS, Redis, container service, object storage, backups). Write runbooks (deploy, rollback, restore backup, rotate keys, update scheme rules) and a user guide for agents in Marathi.
✅ Staging deployed; restore-from-backup rehearsed; agent guide reviewed.

---

### 3. Human tasks (do in parallel)

| # | Task | Needed by |
|---|---|---|
| H1 | Download LGD Maharashtra directory CSVs (lgdirectory.gov.in) → `data/pipeline/raw/lgd/` | Phase 5 |
| H2 | Download Census 2011 PCA Maharashtra village tables + LGD–Census mapping → `raw/census/` | Phase 5 |
| H3 | Download Geofabrik Maharashtra (western-zone India) OSM extract → `raw/osm/` | Phase 5 |
| H4 | Download Mission Antyodaya 2020 Maharashtra village data → `raw/ma/` | Phase 5 |
| H5 | Collect HCES 2023-24 Maharashtra rural MPCE & category shares → `raw/hces/` | Phase 6 |
| H6 | Download KVIC/PMEGP project profiles for the 10 businesses (PMEGP e-portal) | Phase 4 |
| H7 | Confirm NBCFDC terms with NBCFDC / Maharashtra OBC corporation (call/email) | Phase 3 |
| H8 | Get API keys: LLM provider, Sarvam (ASR/TTS); register on Bhashini | Phases 8, 11 |
| H9 | Draft consent notice text (mr/hi/en) + privacy policy; legal review | Phase 7 |
| H10 | Line up 5 Bank Sakhis / VLEs for co-design and testing | Phase 10 |
| H11 | Pilot partners: district SRLM (UMED) block, SC/OBC corporation office, lead bank | Before pilot |

### 4. Definition of done for v1.0 pilot
- All phases' acceptance checks pass in CI.
- 3 reference cases per business reviewed by a banker for DPR acceptability.
- 5 agents complete a case in ≤ 15 minutes in a field test.
- Privacy policy, consent notices and grievance contact published.

---

<!-- ===== FILE: docs/PRD.md ===== -->

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

<!-- ===== FILE: docs/TECH_SPEC.md ===== -->

## ArthMitra — Technical Specification (v1)

Companion to `docs/PRD.md`. This is the source of truth for architecture, data model, engines and APIs.

---

### 1. Architecture

```
 Agent phone (PWA, React)                    Admin / Supervisor (same web app, role-gated)
        │  HTTPS (JSON), audio upload
        ▼
 ┌──────────────────────── FastAPI (Python 3.12) ─────────────────────────┐
 │ auth · cases · consent · geo · market · rules · finance · viability    │
 │ advisory (LLM adapter) · speech (ASR/TTS adapter) · dpr · admin        │
 └───────┬───────────────┬──────────────────┬──────────────┬─────────────┘
         │               │                  │              │
   PostgreSQL 16     Object storage     Job queue        External
   + PostGIS        (DPR PDFs, consent  (Redis + RQ)     LLM API · ASR API
                    audio, encrypted)                    (behind adapters)
         ▲
   Data pipeline (offline, Python scripts): LGD, Census PCA, village coords,
   Mission Antyodaya, HCES shares, NABARD unit costs, scheme rules YAML
```

Rules:
- **Engines are pure Python packages** (`engines/finance`, `engines/rules`, `engines/viability`, `engines/market`) with no I/O. The API layer loads data and calls them. This keeps them unit-testable and reusable.
- **External AI behind adapters** (`adapters/llm.py`, `adapters/asr.py`, `adapters/tts.py`) with a config switch and a no-AI fallback.
- **Monorepo:**
```
arthmitra/
├── backend/
│   ├── app/            # FastAPI: routers, schemas, services, db
│   ├── engines/        # pure logic: rules, finance, viability, market
│   ├── adapters/       # llm, asr, tts, storage
│   ├── dpr/            # PDF templates (Jinja2 → WeasyPrint), fonts (Noto Devanagari)
│   ├── migrations/     # Alembic
│   └── tests/          # unit, golden, API
├── data/
│   ├── schemes/        # *.yaml rule files (versioned)
│   ├── benchmarks/     # *.yaml business benchmark library
│   ├── i18n/           # mr.json, hi.json, en.json (UI + DPR strings)
│   └── pipeline/       # ETL scripts + raw/ (gitignored) + processed/
├── frontend/           # React + Vite + TS PWA
├── docs/               # PRD, TECH_SPEC, research, ADRs
└── docker-compose.yml  # postgres+postgis, redis, api, worker, web
```

### 2. Data model (PostgreSQL)

> PII columns marked 🔒 are encrypted at application level (Fernet/KMS key). No Aadhaar, PAN or bank account numbers are stored anywhere.

```sql
-- Organizations & users
organizations(id, name, type ENUM('nrlm','csc','ngo','sca','other'), district_lgd, created_at)
users(id, org_id, role ENUM('agent','supervisor','admin'), name, phone🔒, pin_hash, lang, active, created_at)

-- Geography (Maharashtra in v1)
villages(lgd_code PK, name_en, name_mr, subdistrict_lgd, subdistrict_name, district_lgd, district_name,
         census2011_code, lat, lon, coord_source ENUM('osm','manual','other'),
         pop_2011, households_2011, sc_pop_2011, st_pop_2011, literacy_rate,
         ma_has_market BOOL, ma_has_haat BOOL, ma_haat_day, ma_bank_branch BOOL, ma_bc_point BOOL,
         ma_power_hours, ma_all_weather_road BOOL, ma_milk_centre BOOL, ma_year)
village_neighbours(lgd_code, neighbour_lgd, dist_km)    -- precomputed ≤ 10 km
state_params(state, key, value, unit, source, year)     -- e.g., rural MPCE, household size, growth rate
hces_shares(state, sector ENUM('rural','urban'), category, share, source, year)

-- Knowledge (versioned, sourced)
business_types(code PK, name_en, name_mr, name_hi, sector ENUM('manufacturing','service','trading','agri_allied'),
               hces_category, decay_lambda, icon)
benchmarks(id, business_code, key, value NUMERIC, unit, region, source_title, source_url, source_year,
           confidence ENUM('official','secondary','estimate'), version, active)
schemes(code PK, name_en, name_mr, agency, channel, portal_url)
scheme_versions(id, scheme_code, version, status ENUM('verified','conflict','unverified','retired'),
                rules_yaml TEXT, source_url, source_date, effective_from, published_by, published_at)

-- Cases
beneficiaries(id, org_id, first_name🔒, gender, age, category, category_verified BOOL,
              disability_40 BOOL, occupation_flags TEXT[], income_band, education_band,
              shg_member BOOL, prior_subsidy ENUM('yes','no','unknown'),
              credit_default ENUM('yes','no','unknown'), existing_emi_monthly,
              created_by, created_at, deleted_at)
consents(id, beneficiary_id, notice_version, language, method ENUM('voice','tap'),
         audio_object_key🔒, audio_sha256, granted_at, withdrawn_at, agent_id)
cases(id, beneficiary_id, village_lgd, business_code, margin_available, target_project_cost,
      language, status ENUM('draft','ready','dpr_generated','applied','sanctioned','rejected','disbursed','closed'),
      status_reason_code, created_by, created_at, updated_at)
case_inputs(case_id, key, value, source ENUM('agent','default','voice'), transcript, updated_at)
evaluations(id, case_id, engine_version, scheme_versions JSONB, benchmarks_version,
            input_snapshot JSONB, output JSONB, created_at)      -- reproducible results
advisories(id, evaluation_id, language, model, prompt_version, output JSONB, validator_passed BOOL, created_at)
dpr_documents(id, evaluation_id, language, object_key, sha256, created_at)

-- Governance
audit_log(id, actor_id, action, entity, entity_id, diff JSONB, at)
processing_log(id, actor_id, purpose, entity, entity_id, at)    -- kept ≥ 1 year, no content
deletion_requests(id, beneficiary_id, requested_at, completed_at, by)
```

**Deletion:** on withdrawal/request → delete beneficiary PII, consent audio, case inputs, advisories and DPRs; keep `processing_log` rows (no content) for ≥ 1 year, then purge (DPDP Rules).

### 3. Rules engine

#### 3.1 Scheme rule file (YAML, one per scheme version)
```yaml
code: NSFDC_TL
name: {en: "NSFDC Term Loan", mr: "एनएसएफडीसी मुदत कर्ज"}
agency: NSFDC
status: verified
source: {url: "https://devmosje.negd.in/?p=15629", date: "2026-05-25"}
channel: {via: ["SCA", "PSB", "RRB"], apply_at: "MPBCDC district office / bank branch"}
eligibility:            # all must pass; each has a reason key for the UI
  - {field: category, op: in, value: [SC], reason: needs_sc}
  - {field: annual_family_income, op: lte, value: 500000, reason: income_above_5l}
  - {field: age, op: between, value: [18, 50], reason: age_18_50}
  - {field: project_cost, op: gt, value: 140000, reason: project_above_140k}
  - {field: project_cost, op: lte, value: 5000000, reason: project_upto_50l}
finance:
  loan_share: 0.90
  loan_cap: 4500000
  min_own_share: 0.10
  subsidy: null
  interest: {type: fixed, rate: 0.08}
  tenure_months: 84
  moratorium_months: 6               # 12 if activity in [construction, plantation]
  moratorium_interest: simple        # never waived
  moratorium_mode_default: capitalise
  repayment_frequency_months: 3
documents: [caste_certificate, income_certificate, residence_proof, dpr, quotations, bank_passbook]
tests:                               # golden cases run in CI
  - {input: {margin: 100000}, expect: {project_cost: 1000000, loan: 900000, emi: 46518.48, n: 26}}
```

Supported operators: `eq, in, not_in, lte, lt, gte, gt, between, is_true, is_false, unknown_ok`.
Interest types: `fixed`, `slab` (list of `{upto, rate}` on loan or project amount), `bank_rate` (user-adjustable default, e.g., 10%).
Subsidy: `{rate_by: {category_group × area}, cap, treatment: upfront|fdr_3yr}`.

#### 3.2 Evaluation
1. Build `facts` from the case (profile + location + calibrated inputs + candidate project cost).
2. For each **published** scheme version: evaluate eligibility → `ELIGIBLE` / `NOT_ELIGIBLE(reasons)` / `NEEDS_INFO(fields)`. Schemes with `status ≠ verified` are returned as `CONFIRM_WITH_AGENCY`.
3. **Pre-screen gates:** `credit_default = yes` → warn on all bank-credit schemes; `prior_subsidy = yes` → exclude PMEGP, CMEGP, MPBCDC subsidy component; negative-list business → exclude per scheme list.
4. **Packages:** single schemes + allowed combinations from `data/schemes/stacking.yaml` (e.g., Stand-Up India + state margin support; bank loan + state interest subvention). **Never two capital subsidies on the same asset.**
5. **Ranking** (deterministic): (a) own money required ≤ available, (b) lowest total cost to beneficiary (interest − subsidy) over tenure, (c) lower EMI/expected monthly cash surplus, (d) channel reliability score (config). Return top 3 with "why not" for the rest.

#### 3.3 Project sizing
- If the user gives only margin: for each scheme, `project = min(margin / min_own_share, scheme_max)`, then apply loan cap (`loan = min(loan_share × project, loan_cap)`, `project = margin_used + loan + subsidy_upfront`).
- If the user gives a target project cost: check `margin ≥ required own share`; else show the shortfall.
- Business benchmarks give a **viable range** for project cost; if the scheme-sized project is outside it, flag ("₹10 L is more than a 2-cow dairy needs; consider 4–5 animals or a smaller loan").

### 4. Finance engine

Inputs: principal, annual rate (or slab), tenure months (incl. moratorium), moratorium months, frequency (1 or 3 months), moratorium mode (`capitalise` | `pay`), subsidy (amount, treatment, adjust month).

Algorithm:
1. Moratorium interest = principal × rate × moratorium_months / 12 (simple).
2. `capitalise` → financed = principal + moratorium interest; `pay` → interest-only instalments each period during moratorium.
3. Instalments n = (tenure − moratorium) / frequency; periodic rate r = rate × frequency / 12; EMI = P·r / (1 − (1+r)^−n).
4. Schedule rows: period, due month, opening, interest, principal, payment, closing. Last row absorbs rounding (closing = 0.00).
5. **FDR subsidy (PMEGP/CMEGP):** borrower pays on the gross loan; at month 36 the subsidy is credited to the outstanding balance and EMI is recomputed over the remaining instalments.
6. Totals: total paid, total interest, effective annual cost.

#### Golden test vectors (must pass ±₹1)
| Case | Expected |
|---|---|
| NSFDC MFS, margin ₹10,000, capitalise | project 1,00,000; loan 90,000; mor. interest 1,462.50; 11 qtrs; EMI 9,147.23; total 1,00,619.54 |
| NSFDC MFS, margin ₹10,000, pay | EMI 9,000.97; total 1,00,473.12 |
| NSFDC MFS, margin ₹14,000 (cap) | project 1,39,000; loan 1,25,000; EMI 12,704.49 |
| NSFDC TL, margin ₹1,00,000, capitalise | project 10,00,000; loan 9,00,000; mor. 36,000; 26 qtrs; EMI 46,518.48; total 12,09,480.48 |
| NSFDC TL, margin ₹1,00,000, pay | EMI 44,729.31; total 11,98,962.00 |
| NSFDC TL, margin ₹6,00,000 | capped: project 50,00,000; loan 45,00,000; EMI 2,32,592.40 + warning |
| PMEGP, SC, rural, service, project ₹10 L, bank rate 10%, 84 m incl. 6 m mor., monthly, capitalise | own 50,000; subsidy 3,50,000 (FDR); loan 9,50,000; mor. 47,500; EMI₁ 17,443.22 (78 m); balance at m36 6,87,753.97 → 3,37,753.97 after subsidy; EMI₂ 8,566.31 (48 m); total paid 9,34,479.55 |
| MUDRA Kishor ₹3 L, 11%, 60 m incl. 6 m mor., monthly, capitalise | mor. 16,500; EMI 7,457.21; total 4,02,689.38 |

### 5. Viability engine

Per business, from benchmarks + calibration:
- **Revenue model** is business-specific (e.g., dairy = animals × yield × lactation share × milk price; kirana = daily customers × avg bill × days; service = jobs/day × price × days). Each model is a small Python function with documented inputs.
- **Costs:** variable (share of revenue or per unit), fixed (rent, power, wages), depreciation (straight-line on capex).
- **5-year projection** with capacity ramp (default 60/70/80/90/90%, overridable per business).
- **DSCR** = (PAT + depreciation + interest on term loan) / (principal + interest due in year). Targets: ≥ 1.25 trading/service, ≥ 1.5 manufacturing. Show year-wise and average.
- **Break-even** = fixed costs / contribution margin → % of capacity and ₹ sales.
- **Working capital (Nayak):** 25% of projected annual turnover; bank 20%, promoter 5%.
- **Udhar stress:** extra WC = monthly revenue × udhar% × credit months (default 2); recompute DSCR and cash buffer; flag if buffer < 3 months of EMI.
- **Income-timing check:** if `income_start_month` > moratorium end → warn and suggest a reserve = EMIs until income starts, or a scheme with a longer moratorium.
- **Seasonality:** monthly multipliers per business (e.g., dairy summer dip) → show the lowest-cash month vs EMI.
- **FOIR check** for microfinance-route options: (existing EMI + new EMI) ≤ 50% of household income.

### 6. Market engine

All values carry a `confidence` and are shown as ranges.
1. **Population now:** `P_now = P_2011 × (1 + g_district)^(year − 2011)`; g from state/district projections (config).
2. **Catchment:** `P_catch = P_now(v0) + Σ P_now(vi) × exp(−λ_b × 1.35 × d_euclid)` over neighbours ≤ 10 km; λ per business (0.28 convenience, 0.18 personal services, 0.12 repair/specialised).
3. **Category demand (₹/month):** `D = P_catch × MPCE_rural_state × share_category` (MPCE is **per person**; HCES 2023-24 state rural values; category share from HCES).
4. **Competitors:** agent-reported count is primary in v1 (range ±1); Economic Census baseline added when available; never OSM shop counts.
5. **Break-even market share:** `S = BE_revenue_month / D`. Saturation: S ≤ 15% Low · 15–35% Medium · > 35% High (thresholds configurable; calibrate in pilot). Also show `D / (competitors + 1)` = average demand per shop vs break-even.
6. **Complementary suggestions** when High: rank other businesses by lowest S in the same catchment.
7. Village coordinates: OSM `place=*` nodes matched to LGD names within the taluka (OSM is reliable for place names, not for shops); unmatched villages fixed manually in the admin console.

### 7. Advisory (LLM) and DPR

#### 7.1 Advisory
- Input: a `facts` JSON (all computed numbers with IDs, scheme results, calibration values, confidence labels, language).
- Output JSON schema: `market_reach, opportunities[], swot{s,w,o,t}, threats[{risk,type,mitigation}], pricing{strategy, items[]}, complementary[], next_steps[]`.
- Rules in the prompt: use only provided facts; reference fact IDs; write simply for low-literacy readers; mark estimates as estimates.
- **Validator:** every number in the output must match a number in `facts` (after normalising Indian formatting) → else regenerate once → else fall back to a template text. Store `validator_passed`.
- Model choice behind `adapters/llm.py`; evaluate candidates on 50 pilot cases for Marathi quality and validator pass rate.

#### 7.2 DPR (PDF)
Sections (bank/KVIC format): 1) Promoter profile, 2) Project description & location, 3) Market assessment (with sources & confidence), 4) Project cost (item-wise capex, pre-operative, contingency 5%, WC margin), 5) Means of finance (own, loan, subsidy), 6) Assumptions (marked default vs local), 7) 5-year P&L and cash flow, 8) DSCR, BEP, 9) Repayment schedule, 10) Risks & mitigations, 11) Document checklist & where to apply, 12) Disclaimer (estimate, not a guarantee; lender decides).
Rendered with Jinja2 + WeasyPrint, Noto Sans Devanagari; Marathi/Hindi copy + English copy for the bank.

### 8. Speech

- `adapters/asr.py`: provider-agnostic `transcribe(audio, lang) → {text, confidence}`; primary Sarvam (best Hindi/Marathi WER in the Apr 2026 benchmark), fallback IndicConformer/Bhashini.
- Numbers spoken in words ("दीड लाख") parsed by a deterministic Indian-number parser with tests.
- The transcript is always shown and editable; nothing goes into calculations without agent confirmation.
- Audio is not stored except consent audio.

### 9. API (v1)

| Method | Path | Purpose |
|---|---|---|
| POST | /auth/login | phone + PIN → JWT |
| GET | /geo/districts, /geo/subdistricts?district=, /geo/villages?subdistrict=&q= | LGD pickers |
| GET | /meta/businesses, /meta/schemes | catalog with labels |
| POST | /beneficiaries | create (minimal profile) |
| POST | /beneficiaries/{id}/consent | upload consent audio/tap + notice version |
| POST | /cases | create case |
| PATCH | /cases/{id}/inputs | set inputs (incl. calibration) |
| POST | /cases/{id}/evaluate | run rules + finance + viability + market → evaluation |
| POST | /evaluations/{id}/advisory | generate AI text (async job) |
| POST | /evaluations/{id}/dpr | generate PDF (async job) |
| GET | /jobs/{id} | job status |
| PATCH | /cases/{id}/status | status + reason code |
| POST | /speech/transcribe | audio → text |
| POST | /beneficiaries/{id}/deletion | deletion request |
| Admin | /admin/schemes, /admin/benchmarks, /admin/villages | CRUD + publish versions |
| GET | /dashboard/summary | supervisor stats |

OpenAPI docs auto-generated. All endpoints role-checked and audit-logged.

### 10. Data pipeline (Maharashtra)

| Step | Source | Output |
|---|---|---|
| 1 | LGD directory CSV (state → district → sub-district → village) | `villages` base |
| 2 | Census 2011 PCA Maharashtra + LGD–Census crosswalk | population, households, SC/ST, literacy |
| 3 | OSM `place=*` nodes (Geofabrik Maharashtra extract) | lat/lon matched by name within sub-district |
| 4 | Mission Antyodaya 2020 village/GP data (Maharashtra) | market/haat/bank/power/road flags |
| 5 | HCES 2023-24 (MoSPI) | state rural MPCE, category shares |
| 6 | NABARD MH Unit Cost 2025-26 + other benchmark sources | `benchmarks` |
| 7 | Neighbour computation (PostGIS ST_DWithin 10 km) | `village_neighbours` |
Each script is idempotent, logs counts and match rates, and writes `data/pipeline/processed/*.csv` plus a `REPORT.md`.

### 11. Security & privacy checklist
- JWT with short expiry + refresh; PIN hashed (argon2); rate-limit login.
- PII encryption at rest; TLS everywhere; secrets in env/secret manager.
- Role checks on every route; agents see only their org's cases.
- Consent required before any profile data is saved (API enforces).
- No Aadhaar/PAN/bank numbers fields at all.
- Processing log for every read of beneficiary data.
- Hosting in an India region; backups encrypted; deletion propagates to backups within the backup retention window (documented).
- Incident playbook (CERT-In 6 h; DPDP Board/user notification).

### 12. Testing
- **Golden tests** for finance (Section 4) and every scheme YAML `tests:` block.
- Property tests: schedules sum to financed principal; closing balance = 0; EMI decreases when tenure increases.
- Rules tests: each reason code reachable.
- Market/viability: snapshot tests for 3 reference villages × 10 businesses.
- Advisory validator tests with seeded bad outputs.
- API tests (pytest + httpx); E2E (Playwright) for the agent journey on a 360×640 viewport.
- CI: lint (ruff, eslint), type-check (mypy, tsc), tests, migration check.

---

<!-- ===== FILE: docs/research/ArthMitra_Research_Pack_v1.md ===== -->

## ArthMitra — Verified Research Pack v1

Date compiled: 27 Oct 2026. Builds on the P1–P5 Gemini reports and the P1–P5 review.
Legend: ✅ verified on an official or primary source in this pass · ⚠️ conflicting or partially verified · ❓ not found / still open · 🧮 our estimate (labelled)

---

### 1. Scheme rules — fact-check results

| # | Item | Verified value | Status | Source (date) |
|---|---|---|---|---|
| 1 | NSFDC income ceiling | **Annual family income ≤ ₹5.00 L, rural and urban, effective 7 Jan 2026.** No ceiling for skill training. | ✅ | MoSJE NSFDC page (updated 25 May 2026) |
| 2 | NSFDC Micro Finance Scheme | Project ≤ ₹1.40 L; loan ≤ ₹1.25 L; 6.5%; quarterly; within 3 yrs; 3-month moratorium | ✅ | same |
| 3 | NSFDC Term Loan | > ₹1.40 L to ₹50 L; loan ≤ ₹45 L; 8%; within 7 yrs; 6-month moratorium (12 for plantation/construction) | ✅ | same |
| 3a | Other current NSFDC schemes | Aajeevika Micro-Finance Yojana (≤ ₹1.40 L, 15%, via MFIs); Udyam Nidhi (≤ ₹5 L, 13–15%, via co-op banks/SFBs); Education loan | ✅ | same |
| 4 | NSFDC Mahila Samriddhi / Mahila Adhikarita | **Not in NSFDC's current official scheme list.** Don't encode until confirmed. | ⚠️ | same (absent) |
| 5 | NBCFDC General Loan | NBCFDC's scheme page: income ≤ ₹3 L, max ₹15 L, 85% share, 6%/7%/8% by slab, 8 yrs incl. 6-month moratorium. **But** NBCFDC's own FAQ PDF (Nov 2024) says income ≤ ₹5 L, "Individual Loan" up to ₹25 L, 7% (≤ ₹1.25 L) / 8%, 4 or 7 yrs, 1-quarter moratorium. | ⚠️ conflict between two official NBCFDC sources | nbcfdc.gov.in node/358; NBCFDC FAQ PDF |
| 6 | PM SVANidhi | Restructured Aug 2025: tranches **₹15k / ₹25k / ₹50k**; lending period to 31 Mar 2030; RuPay credit card after 2nd loan; extended to census towns and peri-urban areas | ✅ (P1 was outdated) | Tribune, 27 Aug 2025 (Cabinet decision) |
| 7 | Stand-Up India | ₹10 L–₹1 Cr greenfield; loan expected to cover **~75%** of project cost (not 85%), unless convergence + own contribution exceed 25%; borrower min 10% own contribution; up to 7 yrs; moratorium up to 18 months; collateral-free via CGSSI | ✅ (P1 wrong) | Stand-Up India brochure |
| 8 | DAY-NRLM | Interest subvention for women SHGs on credit **up to ₹3 L at 7%**. Above that, normal slab rates. | ✅ (P3's "₹20 L at 7%" was wrong) | Bank SHG-NRLM page citing scheme |
| 9 | PMEGP | Mfg ≤ ₹50 L, service ≤ ₹20 L; General 10% own / 15% urban, 25% rural subsidy; Special 5% own / 25% urban, 35% rural; 8th pass for > ₹10 L mfg or > ₹5 L service; no income ceiling; new units only; **units that already got government subsidy are ineligible**; one per family; 3–7 yrs after moratorium | ✅ | Bank of Maharashtra PMEGP page |
| 10 | CMEGP (Maharashtra) | Age **18–45** (+5 years special); **Service/agro/other ≤ ₹10 L** (not ₹20 L), Mfg ≤ ₹50 L; 7th pass for ₹10–25 L, 10th pass > ₹25 L; own 10% / 5%; subsidy same slabs as PMEGP; bank 90% / 95%; CGTMSE cover | ✅ (P1 wrong on service limit) | Bank of Maharashtra CMEGP page |
| 11 | MPBCDC Seed Capital | Project up to ₹5 L (loans ₹50k–₹5 L via banks); bank 75%, corporation 20% (incl. ₹10,000 grant) at 4%, beneficiary 5%; 5-yr recovery. Income limit not stated on that page. | ✅ structure / ❓ income | mahabharti (mirror of MPBCDC info) |
| 12 | Mudra NPA | **9.81% of outstanding (all PMMY, SCBs, Mar 2025)**, 2.19% of disbursed. Not a Shishu-only number. MSME average 3.60%. | ✅ (P4 mislabelled) | Rajya Sabha reply, reported 19 Aug 2025 |
| 13 | FSSAI | Basic registration up to **₹1.5 Cr** turnover (was ₹12 L); State licence ₹1.5–50 Cr; in force from **1 Apr 2026** | ✅ | FSSAI order 13 Mar 2026 |
| 14 | DPDP Rules | Notified **14 Nov 2025**. Board: immediate. Consent managers: 14 Nov 2026. Notice/consent, breach reporting, security, children & PwD consent, rights: **14 May 2027**. **All fiduciaries must keep processing logs ≥ 1 year.** Rights requests within 90 days. | ✅ | PIB doc; AZB/Shardul alert |

#### What this changes in the product
- **Income ceiling ₹5 L** for NSFDC → more users eligible than the hackathon build assumed.
- **Store rules as versioned data with `source_url`, `source_date`, `status`** (verified / conflict / unverified). NBCFDC must ship as "conflict: confirm with SCA" until resolved by phone/letter to NBCFDC or the Maharashtra OBC corporation.
- **Prior-subsidy check is a hard gate** (PMEGP, CMEGP and state subsidy schemes all exclude previously subsidised units).
- **DPDP design correction:** "hard delete immediately" (P5) must coexist with the **1-year log retention** rule. Design: delete profile and documents on withdrawal; keep minimal processing logs (no document contents) for 1 year, then purge.

---

### 2. Unit economics — what is solid and what isn't

#### 2.1 Verified anchors
| Business | Item | Value | Source |
|---|---|---|---|
| Dairy (2 animals) | Total outlay, Maharashtra 2025-26 | HF crossbred ₹1,97,840 · Jersey ₹1,65,400 · Murrah/Jaffarabadi buffalo ₹1,88,300 · Pandharpuri buffalo ₹1,67,400 (margin 15%, bank 85%) | NABARD Maharashtra RO, Unit Cost 2025-26 (approved 21 Mar 2025) ✅ |
| Dairy | Yield norm used by NABARD MH | 12 L/day HF & Jersey; 8 L/day Murrah (2023-24 table) | NABARD MH Unit Cost 2023-24 ✅ |
| Dairy | Lactation / dry period norm | 280 days / 120 days | NABARD DEDS model (2018) ✅ (norm, old prices) |
| Dairy | Cow milk procurement price (3.5 fat / 8.5 SNF) | ₹40.80/L, Katraj Dairy (Pune district union), from 11 Sep 2026 | Free Press Journal ✅ |
| Goatery (10+1) | Total outlay, MH 2025-26 | Osmanabadi/Sangamneri etc. ₹1,51,525 · non-descript ₹1,28,425 | NABARD MH Unit Cost 2025-26 ✅ |
| Goatery | Technical norms | Kidding interval 8 months; 1.6 kids/kidding; conception 90%; kid mortality 15%; culling 20%; NABARD repayment 1+5 yrs with 1-yr grace | NABARD Model Bankable Scheme on Goat ✅ (prices in that doc are old — use norms only) |
| Layer (1,000 birds) | Outlay, MH 2023-24 | ₹9,92,000 | NABARD MH 2023-24 ✅ |
| Broiler (5,000/batch) | Outlay, MH 2023-24 | Contract ₹14,63,800 · own ₹22,92,000 (margin 17.5%) | NABARD MH 2023-24 ✅ |
| Beauty parlour | KVIC PMEGP profile | Project ₹17.07 L; Yr-1 sales ₹32.4 L at 60% capacity; BEP 33–38%; avg DSCR 2.64. **Urban-scale profile; the document has internal inconsistencies.** | KVIC PMEGP common project profile ⚠️ |
| Garments/tailoring | Tripura PMEGP profile (2012) | Project ₹4.29 L; DSCR 1.69 | Revised Project Profiles Vol II (2012) ⚠️ old |
| Flour mill (solar, small) | SELCO model | Capex ₹1.7 L (mill ₹16k + solar ₹1.54 L); ~56 kg/day; ₹5/kg | SELCO Foundation model doc ⚠️ niche |

#### 2.2 Not found (❓)
Kirana, mobile repair, two-wheeler repair, tea stall/snacks, papad/pickle, bakery, masala, e-rickshaw, broiler 500-bird village scale: no recent official model with full economics was reachable in this pass. NABARD regional PDFs (robots-blocked) and KVIC per-business profiles exist but could not be fetched.

#### 2.3 Decision: benchmark library + local calibration
This is a better design for a real product anyway, because official model DPRs are generic and quickly outdated.
1. **Library:** per business, store capex items, physical norms (yield, mortality, cycles, capacity), cost lines and price inputs. Each value carries `source`, `year`, `region` and `confidence`.
2. **Defaults:** livestock from NABARD Maharashtra unit costs (refreshed every March) + NABARD technical norms; prices from live/local feeds (dairy union rates, Agmarknet for inputs).
3. **Local calibration:** the Bank Sakhi / VLE confirms 3–5 key numbers on the spot (local selling price, daily customers or volume, rent, main input price). The DPR shows which numbers are local vs default.
4. **Gap-fill task (offline, before launch):** collect current PMEGP/KVIC profiles for the 10 launch businesses from the PMEGP e-portal manually (download PDFs), and validate with 3–5 real units per business in the pilot district.

---

### 3. Integrations (P6)

| Integration | What it gives us | Access reality | Phase |
|---|---|---|---|
| **DigiLocker (Requester)** | Pull caste, income, identity docs with user consent | No platform fee currently; onboarding by a senior authorised person with official-domain email; NeGD verifies; must not store documents beyond permitted duration; data must stay in India; **report incidents to NeGD within 24 h; annual CERT-In empanelled audit** ✅ | 2 (after company setup + audit budget) |
| Government application portals (Jan Samarth, PMEGP e-portal, Maha-CMEGP, Maha-DISHA, MahaSwayam) | Where applications actually go | No public APIs for third parties (P1). v1 = generate DPR + pre-filled checklist, the agent submits on the portal. | 1 |
| **ULI (RBI)** | Land records, milk-pouring data, satellite data for lenders | Built for lenders; launched Aug 2024; by Dec 2024 600k+ loans / ₹27,000 Cr; large banks slow to adopt; land-record digitisation slow ✅ | Not for us until we partner with a lender |
| Account Aggregator | Bank-statement data | FIU role is for regulated entities (from general knowledge — verify) | Not v1 |
| **Bhashini** | ASR/TTS/translation | Services confirmed (NMT, ASR, TTS, VAD, denoise; 3 bn+ inferences). **Developer access terms/quotas not found** ❓ → apply early, keep a commercial fallback | 1 (trial) |
| **WhatsApp Business API** | Status updates, DPR delivery, reminders | Per-template-message pricing since 1 Jul 2025; INR billing for India; user-initiated messages free; replies in 24 h window: first 1,000/month free, then utility rate (from 1 Oct 2026); marketing templates most expensive ✅ | 2 |
| UPI Autopay / e-mandate | EMI reminders → autopay | Lender-side | 3 |

**Phased roadmap**
- **Phase 1 (no permissions):** our app + DPR PDF + portal hand-off + Bhashini/commercial ASR + WhatsApp via a BSP.
- **Phase 2 (registration):** DigiLocker requester, WhatsApp verified business, NRLM/LokOS partnership (state mission MoU).
- **Phase 3 (MoU / regulated partner):** SCA or bank partnership → application data exchange; then ULI/AA via the partner lender. Becoming an LSP happens here, deliberately.

---

### 4. Tech & AI stack (P7)

#### 4.1 Speech (Voice of India benchmark, Josh Talks, Apr 2026) ✅
| Model | Hindi WER | Marathi WER |
|---|---|---|
| Sarvam Audio | **5.0%** | **9.4%** |
| Gemini 3 Pro | 6.0% | 10.7% |
| Saarika 2.5 (Sarvam) | 6.2% | 10.0% |
| Amazon Transcribe | 6.8% | 11.3% |
| IndicConformer (open source, AI4Bharat) | 8.2% | 13.1% |
| GPT-4o Transcribe | 34.0% | 55.6% |
Dialects underrepresented in training data (e.g., Bhojpuri belt) and speakers outside their home region perform much worse. Bhashini was not in this benchmark.

**Decision:** Sarvam ASR as primary for Hindi/Marathi, IndicConformer (self-hostable) as fallback/offline option, Bhashini evaluated in pilot. Always show the transcript for the agent to correct before it is used in calculations.

#### 4.2 Language model
- Sarvam 105B / 30B: open weights (Apache 2.0), free on Sarvam's API at publication, but **low on reasoning benchmarks and high hallucination** (Artificial Analysis, Apr 2026) ✅.
- **Decision:** the LLM never decides eligibility or numbers. Use a strong general model with structured JSON output for the report narrative, grounded with our computed numbers and retrieved scheme text; use an Indic model only where it measurably writes better Marathi/Hindi. Evaluate both on 50 real cases before choosing. Keep the provider behind one interface so it can be swapped.

#### 4.3 Recommended stack (🧮 recommendation)
| Layer | Choice | Why |
|---|---|---|
| Client | Android-first PWA (agent mode), large touch targets, offline drafts | Agents use low-end Android; no app-store friction |
| API | Python FastAPI | Finance/rules engine already in Python; easy testing |
| Rules engine | Scheme rules in versioned YAML + Python evaluator; golden-test suite per scheme | Auditable, updatable without deploys |
| Data | PostgreSQL + PostGIS; precomputed village features keyed by LGD code | Spatial joins done once, served as small payloads |
| Docs | Server-side PDF (DPR) in Marathi/Hindi/English | Bank-ready output |
| Hosting | India region (Mumbai/Hyderabad) on a MeitY-empanelled provider | Data localisation; government procurement readiness |
| Observability | Structured logs (1-yr retention, no document contents), error tracking, uptime | DPDP log rule + reliability |

#### 4.4 Cost per 1 lakh active users / month (🧮 estimate, assumptions stated)
Assumptions: 1 lakh users × 3 reports/month; each report ~6k input + 2k output tokens; ~2 min of speech per report.
- LLM: 1.8 bn input + 0.6 bn output tokens/month. At a fast-tier price of roughly $0.3/M in and $2.5/M out ≈ **$2,000/month (~₹1.7 L)**. Varies 3–10× by model choice.
- ASR: 6 lakh minutes/month — price ❓ (get quotes from Sarvam, Google, and Bhashini terms).
- Infra (API, DB, storage, PDFs): **~₹50k–1 L/month**.
Treat these as planning ranges, not quotes.

---

### 5. Competition & business model (P8)

| Player | What they do | Gap ArthMitra fills |
|---|---|---|
| **Haqdarshak** | Scheme discovery via ~30,000 trained (mostly women) agents in 24 states; ₹4,200 Cr+ benefits to 2.7 M families; funded via businesses and philanthropy; Pre-Series A1 led by Acumen (Mar 2023) ✅ | Broad welfare discovery, not business feasibility + DPR + loan structuring |
| Jan Samarth, PMEGP/CMEGP portals | Application intake | No feasibility, no local market view (P1) |
| PSB 59 Minutes, fintech MSME lenders | Underwriting formal businesses | Need GST/ITR/bank trails that informal rural users lack (P1) |
| NABARD/KVIC model DPRs | Static PDFs | Not interactive, not local, often outdated (§2) |

**Revenue options (in order of fit for v1, 🧮 recommendation)**
1. **B2G / programme contracts:** state SC/OBC corporations, district administrations, State Rural Livelihood Mission (UMED in Maharashtra) — per-district licence or per-DPR fee paid by the agency.
2. **CSR / philanthropy** for the pilot (same route Haqdarshak used).
3. **Agent tools:** VLEs already charge for services; a per-DPR fee paid by the VLE, not the beneficiary.
4. **Later, via a regulated partner:** lender pays for qualified applications → this makes us an LSP (RBI rules; never charge the borrower).

**Pilot design (🧮 recommendation):** one Maharashtra district; partners = State Rural Livelihood Mission block teams + the district's SC/OBC corporation office + 1 RRB/PSB lead bank; 30–50 Bank Sakhis/VLEs; 6 months; KPIs: DPRs generated, application submission rate, sanction rate vs district baseline, time to sanction, 6- and 12-month business survival, on-time repayment.

---

### 6. Post-loan survival (P9)

| Evidence | Finding | Strength | ArthMitra feature |
|---|---|---|---|
| Grace period RCT, India (J-PAL; Field, Pande et al.) | 2-month grace vs 2 weeks: ~6% more business investment, 2× more likely to start a new business, **weekly profits +57% after 3 years**, but **>3× default rate** ✅ | Strong | Recommend moratorium length to match income start; show the default-risk trade-off honestly; pair longer moratorium with a reserve buffer |
| Rule-of-thumb accounting RCT (Drexler, Fischer, Schoar) | Simple rules beat standard accounting training: +11 pp separate business/personal money, +11 pp keep records, **+18.5% sales in bad weeks**; standard training had no effect ✅ | Strong | "Ek galla, do khate" style: separate business cash, 3 simple daily entries by voice |
| NSFDC evaluation (MoSJE, 2020; 3,300 beneficiaries) | 89.2% repaying regularly; 99.3% still in activity; **61.5% cite lack of expertise/interest**, 22.8% no active market; ~3 months application→sanction; 31.4% faced access difficulty ✅ | Moderate (self-reported) | Skill-fit check before recommending a business; market check (our core); application tracker |
| Nudges (P4, J-PAL) | Social-norm messages reduce continued delinquency 4–7% among late payers; poorer borrowers respond better to concrete due-date reminders | Moderate | Voice/WhatsApp reminders with the exact amount and date |
| Udhar / working-capital squeeze (P1, P3) | Customer credit and seasonal cash dips drive collapse | Moderate (field reports) | Udhar slider; seasonal cash-flow view; reserve recommendation |

---

### 7. Hard numbers for pitch & PRD (P10)

| Fact | Number | Year | Source | Confidence |
|---|---|---|---|---|
| NSFDC disbursement | **₹775+ Cr, highest ever, +27% YoY** | FY 2025-26 | AIR / MoSJE, 10 Apr 2026 | High |
| NSFDC credit-scheme beneficiaries | 85,372 → **41,750** (NSFDC: shift to bigger loans) | FY24 → FY25 | ThePrint on Standing Committee, 12 Aug 2026 | High |
| NSFDC total beneficiaries | 1,11,309 → 1,18,002 → 61,394 | FY24 → FY26 | same | High |
| SCAs underperforming / non-performing | **14 states**; none in Telangana, Ladakh | 2026 | same | High |
| Fresh government equity to NSFDC | **None FY20–FY26**; asset base grows ~3%/yr vs 4–4.5% inflation | 2026 | same | High |
| Beneficiaries crossing poverty line | 58.8% (2022-23 evaluation) vs 99–100% earlier | 2022-23 | same | Medium |
| Committee flag | ₹5 L income cap and 15% microfinance rate may deter borrowing | 2026 | same | High |
| Mudra NPA | 9.81% of outstanding (2.19% of disbursed); MSME avg 3.60% | Mar 2025 | Rajya Sabha reply | High |
| NSFDC beneficiary outcomes | 89.2% repaying regularly; 61.5% cite lack of expertise; ~3 months to sanction | 2020 study | MoSJE evaluation | Medium |

**Implication for strategy:** SCA channels are weak in many states and NSFDC volumes are capital-constrained, so ArthMitra must route across **all** eligible channels (banks/RRBs under PMEGP, CMEGP, Mudra, Stand-Up India, NRLM) and not depend on one corporation.

---

### 8. Still open

| # | Open item | How to close |
|---|---|---|
| O1 | NBCFDC conflicting terms | Call/email NBCFDC or the Maharashtra OBC corporation; until then show both with a warning |
| O2 | Unit economics for 8+ non-farm businesses | Download KVIC/PMEGP profiles from the PMEGP e-portal manually; field-validate in pilot |
| O3 | Bhashini developer access terms | Register on the Bhashini portal; ask NeGD onboarding |
| O4 | 6th Economic Census village-level access (licence, format) | Check the MoSPI microdata portal |
| O5 | MPBCDC income limit; LIDCOM/LASDC current terms | Corporation websites / district office |
| O6 | ASR pricing (Sarvam, Google) | Vendor pricing pages / quotes |
| O7 | Account Aggregator FIU eligibility | Sahamati / RBI NBFC-AA directions |

---

### Sources
- [MoSJE — NSFDC FAQ/scheme page](https://devmosje.negd.in/?p=15629)
- [NBCFDC General Loan page](https://nbcfdc.gov.in/nbcfdc/web/node/358) · [NBCFDC FAQ PDF (Nov 2024)](https://nbcfdc.gov.in/nbcfdc/web/sites/default/files/2024-11/FAQ-NBCFDC.pdf) · [PublicServicesMap — NBCFDC GLS](https://www.publicservicesmap.in/schemes/nbcfdc-general-loan-scheme--nbcfdc-gls?lang=hi)
- [Tribune — PM SVANidhi restructuring](https://www.tribuneindia.com/news/india/street-vendors-scheme-gets-cabinet-nod-for-restructuring-lending-period-extension)
- [Stand-Up India brochure](https://www.svnit.ac.in/Unnat_Bharat/PI/pdf/Livelihood%20&%20Entreprenurship/Schemes%20by%20Government%20of%20India/Standup%20India/Annexure%20II%20Stand%20Up%20India%20-%20Brochure%20-%20English.pdf)
- [SHG under NRLM — bank page](https://agvb.bank.in/menu-content/get-content/banking-product/loans-and-advances/group-finance/shg-under-nrlm)
- [Bank of Maharashtra — PMEGP](https://bankofmaharashtra.bank.in/pmegp) · [Bank of Maharashtra — CMEGP](https://bankofmaharashtra.bank.in/cmegp)
- [MPBCDC Margin Money scheme](https://mahabharti.in/yojana/margin-money-scheme-for-backward-class/)
- [The Week — Mudra NPA](https://www.theweek.in/wire-updates/business/2025/08/19/dcm55-rsq-mudra-npa.html)
- [S.S. Rana — FSSAI thresholds](https://ssrana.in/articles/fssai-raises-turnover-limits-for-food-business-registration-and-licensing/)
- [PIB — DPDP Rules](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf) · [AZB/Shardul — DPDP commencement](https://www.amsshardul.com/insight/enforcement-of-the-dpdp-act-and-notification-of-the-dpdp-rules/)
- [NABARD MH Unit Cost 2025-26](https://www.nabard.org/auth/writereaddata/tender/pub_2105250400341558.pdf) · [NABARD MH Unit Cost 2023-24](https://bankofmaharashtra.bank.in/writereaddata/documentlibrary/9f8300e4-6e34-482e-ae20-6e4cb3a6351b.pdf) · [NABARD goat model scheme](https://www.nabard.org/auth/writereaddata/ModelBankProject/1207170156Model_scheme_on_goat_Farming.pdf) · [NABARD DEDS dairy model](https://www.pashudhanpraharee.com/wp-content/uploads/2019/08/Dairy_deds-project-report.pdf)
- [Free Press Journal — Katraj milk price](https://www.freepressjournal.in/business/milk-price-raised-before-ganeshotsav-here-why-customers-will-not-pay-more)
- [KVIC — Beauty parlour profile](https://www.kviconline.gov.in/pmegp/pmegpweb/docs/commonprojectprofile/BeautyParlour.pdf) · [Revised Project Profiles Vol II](https://www.kjffoscia.org/data/projectreport/1f35567d741e5392893c97ac584be4f1.pdf) · [SELCO flour mill model](https://selcofoundation.org/wp-content/uploads/2021/12/SF_Flour-Mill-Sector-Agri-Processing-Model-Bankable-Document.pdf)
- [DigiLocker Requester Terms (Jun 2025)](https://cf-media.api-setu.in/resources/DigiLocker-Terms-of-User-Requester-june-2025.pdf)
- [Business Standard — ULI adoption](https://www.business-standard.com/industry/news/big-banks-slow-adoption-weak-land-records-stall-uli-scale-up-bankers-125082700907_1.html) · [DT Next — ULI launch](https://www.dtnext.in/news/business/rbi-poised-to-launch-nationwide-uli-system-to-speed-up-lending-to-msmes-farm-sector-801128)
- [NeGD — Bhashini episode](https://negd.gov.in/wp-content/uploads/2025/08/AoE-Ep.-28_bhashini_compressed.pdf)
- [Baat — WhatsApp API pricing India](https://baat.ai/blog/whatsapp-api-pricing-india)
- [Josh Talks — Voice of India ASR benchmark](https://voiceofindiablogs.ai.joshtalks.com/) · [Artificial Analysis — Sarvam 105B/30B](https://artificialanalysis.ai/de/articles/sarvam-105b-Sarvam-30b-everything-you-need-to-know)
- [Outlook Startup — Haqdarshak](https://startup2.outlookindia.com/investors/haqdarshak-empowerment-solutions-private-limited-closes-pre-series-a1-investment-round-news-8274)
- [J-PAL — grace period study](https://www.povertyactionlab.org/print/pdf/node/1511?lang=en) · [J-PAL — rule-of-thumb training](https://www.povertyactionlab.org/evaluation/small-and-medium-enterprise-financing-and-mentoring-services-emerging-markets-dominican)
- [MoSJE — NSFDC evaluation summary](https://socialjustice.gov.in/public/ckeditor/upload/Summary%20Report-Evaluation%20of%20NSFDC_1648795113.pdf)
- [ThePrint — NSFDC Standing Committee](https://theprint.in/economy/dalit-finance-body-beneficiaries-nearly-halve-as-house-panel-flags-funding-drought-board-vacancies/3013066/) · [AIR — NSFDC FY26 disbursement](https://www.newsonair.gov.in/nsfdc-records-its-highest-ever-disbursement-since-inception-during-financial-year-2025-26)

---

<!-- ===== FILE: docs/research/ArthMitra_Research_Review_P1-P5.md ===== -->

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
