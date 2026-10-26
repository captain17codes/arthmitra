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
