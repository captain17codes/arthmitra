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
