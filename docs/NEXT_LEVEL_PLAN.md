# ArthMitra — Next Level Plan (for Antigravity)

**Read order for the agent:** this file → `README.md` → `docs/PRD.md` → `docs/TECH_SPEC.md` → the code. Where this file and PRD/TECH_SPEC disagree about *who the user is*, this file wins: the product is now **self-service** (see §1).

**How to use**
1. Paste **§0 Master context** into Antigravity once.
2. Paste **one phase prompt at a time** (§3). Don't start the next phase until its acceptance checks pass and you've looked at the diff.
3. Do the **human tasks** (§4) in parallel. The agent can't create accounts, sign up for providers or download some government files.

---

## 0. Master context (paste first)

> You are the lead engineer on **ArthMitra**, a live production app (frontend on Vercel, FastAPI backend + Postgres on Render). Read `docs/NEXT_LEVEL_PLAN.md`, `docs/PRD.md`, `docs/TECH_SPEC.md` and skim the code before changing anything. If something is unclear or contradictory, stop and ask me instead of guessing.
>
> **What ArthMitra is now:** a person from a village (often SC/ST/OBC, often a woman, low digital literacy, Marathi-first, cheap Android phone, patchy internet) uses the app *for themselves*. They describe their business idea and get: eligible government schemes, loan, subsidy, EMI, whether the business can repay (DSCR), local competition, and a bank-ready DPR PDF. There are **no agents**.
>
> **Non-negotiable rules:**
> 1. **AI never computes numbers or eligibility.** Money, eligibility, schedules, DSCR and market figures come only from the pure-Python engines in `backend/engines/` and `backend/app/services/evaluation.py`. LLM output is text only and must pass the number validator.
> 2. **No invented values.** If an input is unknown, show "needs info" — never a default that looks like a fact. Every benchmark/scheme value in `data/` carries a source and date; unverified values are labelled as estimates in the UI and DPR.
> 3. Scheme rules and benchmarks live in `data/` as versioned YAML. Never hard-code scheme terms in Python.
> 4. **Privacy (DPDP Act 2023):** no Aadhaar/PAN/bank-account fields; PII columns encrypted; consent before profile data; each person sees only their own data (each account has its own organisation row — keep this); "delete my data" must keep working.
> 5. Every external call (LLM, ASR, SMS, maps, any API) goes through an adapter with timeout, retry and a fallback, configured by environment variables.
> 6. Never edit a test to make it pass. Golden finance vectors must stay within ±₹1.
> 7. Mobile-first (360×640 Android) and also good on desktop; every string through i18n (mr, hi, en); Indian number format; tap targets ≥ 44 px.
> 8. Small, reviewable commits per phase. After each phase run: `ruff check`, `pytest` (backend), `tsc --noEmit`, `eslint`, `vitest` (frontend), and give me a short summary with the test results.

---

## 1. Where we are (October 2026)

| Area | State |
|---|---|
| Users | Self-service. Sign-up: mobile → OTP → name + 4-digit PIN. Daily login: mobile + PIN. Forgot PIN → OTP. PIN lockout after 5 tries. |
| OTP | `OTP_PROVIDER=dev` (OTP shown on screen, demo only) · `firebase` (real SMS via Firebase phone auth, code ready, needs config) · `msg91` (needs DLT). |
| Flow | Consent (tick + read aloud, first plan only) → profile (saved once, reused) → village → business + own money → local check (3 questions) → results (financing, market, viability, AI advisory) → DPR PDF (Marathi + English). |
| Engines | Rules (19 schemes, conditional/OR rules, special category), finance (moratorium, FDR subsidy, tranches, quarterly EMIs), viability (DSCR from benchmark costs), market (catchment, saturation), DPR builder. |
| Data | **10 businesses, benchmarks are estimates; only ~5 demo villages (synthetic).** This is the biggest gap. |
| Infra | Vercel (frontend, rewrites to API) + Render free web service + Render free Postgres (**expires 26 Nov 2026** → move to Neon). Schema changes are applied at startup; Alembic migrations exist up to `003`. |
| Tests | Backend ~198, frontend 16, all passing. |

---

## 2. Phase overview

Ordered by impact. Phases A and F are the must-haves before any real launch.

| # | Phase | Why it matters | Size |
|---|---|---|---|
| A | Real Maharashtra data | Without real villages and validated benchmarks every number is a guess | L |
| B | Low-literacy, voice-first UX | The real user can't fill a 5-step form | L |
| C | "Which business should I start?" | Most people don't arrive with a fixed idea | M |
| D | After the result: apply & track | The value is getting the loan, not reading a report | M |
| E | Grounded AI helper | Answer "why?" and "what if?" in Marathi, from computed facts only | M |
| F | Production hardening | Data safety, uptime, cost control, legal pages | M |
| G | Offline & low bandwidth | 2G / no-signal villages | M |
| H | Admin & data operations | Keep schemes/benchmarks current without code changes | M |
| I | Pilot & measurement | Prove it works with 30–50 real people | S (+ field time) |

---

## 3. Phase prompts (paste one at a time)

### Phase A — Real Maharashtra data

> Replace demo villages and estimated benchmarks with real data, without changing engine logic.
>
> 1. **Villages pipeline** in `data/pipeline/` (Python, re-runnable, idempotent):
>    - LGD village directory for Maharashtra (LGD code, names en/mr, sub-district, district) — input files in `data/raw/lgd/` (I will download them).
>    - Census 2011 Primary Census Abstract (population, households, SC/ST population, literacy) joined on Census 2011 code ↔ LGD code mapping.
>    - Village Directory amenities (market, weekly haat, bank, post office) where available.
>    - Coordinates: from the LGD/Bharat Maps file if present, else OSM Nominatim with the existing rate-limited adapter; record `coord_source`.
>    - Neighbours: villages within 10 km (PostGIS when available, haversine fallback) into `village_neighbours`.
>    - Output a load report: rows loaded, rows without coordinates, unmatched codes. Never invent coordinates or population.
> 2. **Admin import endpoint** (admin role) and a CLI to load the pipeline output into Postgres in batches.
> 3. **Village search**: trigram search on en + mr names, filter by district/taluka, show taluka and district in results; must stay < 300 ms for 44k villages.
> 4. **Benchmarks**: add `data/benchmarks/SOURCES.md`. For each of the 10 businesses record every parameter's source (NABARD unit-cost model, KVIC/PMEGP model project reports, state animal husbandry norms) with year and link; mark anything else `confidence: estimate`. Add a test that fails if any parameter lacks `source_title` or `confidence`.
> 5. **Scheme verification**: for each `data/schemes/*.yaml`, add `verified_on`, `verified_by`, and the exact source page/section. Schemes not verified in the last 180 days show "confirm with agency" in the UI.
>
> **Acceptance:** all Maharashtra villages searchable in Marathi and English; Shirwal/any test village returns real Census population; benchmark-source test passes; DPR section 6 shows each value's source and confidence.

### Phase B — Low-literacy, voice-first UX

> Make the whole flow usable by someone who reads little Marathi and has never filled an online form.
>
> 1. **Guided conversation mode** (default for new users): one question per screen, big icon + short Marathi text + 🔊 read-aloud button + 🎤 answer by voice (existing speech endpoint; Sarvam/Bhashini adapters) + tap options. Questions: name → age → category → family income (ranges with icons, then exact) → village (voice search) → business (picture grid) → "how much money do you have?" (₹ notes/coins visual) → 3 local questions.
> 2. **Plain-language result screen first**: "You can get ₹1,90,000 loan. You pay ₹3,489 every month for 7 years. Government gives ₹70,000." with read-aloud; detailed tabs below for those who want them.
> 3. **Explain every term** (subsidy, EMI, moratorium, DSCR, margin money) with a tap-to-hear tooltip in mr/hi/en.
> 4. **Share**: send the plan summary and DPR PDF via WhatsApp share sheet (Web Share API with file), and "Show at bank" full-screen QR/summary view.
> 5. **Accessibility**: font size switch, high-contrast mode, all images with alt text, screen-reader labels; test with TalkBack.
> 6. Keep the existing form mode as "Quick form" for confident users.
>
> **Acceptance:** a first-time user can complete a plan by voice + taps only (Playwright test with mocked speech); Lighthouse accessibility ≥ 95; every new string in mr/hi/en.

### Phase C — "Which business should I start?"

> Help people who don't have a fixed idea.
>
> 1. New entry on the home screen: "मी कोणता व्यवसाय करू?" Inputs: village, own money, skills/interests (tailoring, animals, repair, cooking…), time available, space (home/shop/land).
> 2. Use the existing market engine (catchment demand, competitor saturation, complementary suggestions) and viability engine to rank all businesses for that village and budget. Show top 3 with *why* (local demand, low competition, fits budget, DSCR) — all numbers from engines.
> 3. Expand the catalogue from 10 to ~25 rural businesses (e.g. mushroom farming, vermicompost, poultry layer, fishery, sewing unit, mobile canteen, cyber café/CSC-type services, solar pump servicing, bakery, dal mill). Each needs a benchmark YAML with sourced values and a revenue model with tests — **no business ships without a sourced benchmark**.
>
> **Acceptance:** recommender returns ranked results with reasons for any village; every new business has golden tests for its revenue model; recommendations change when the village changes.

### Phase D — After the result: apply & track

> The goal is getting the loan.
>
> 1. **Document checklist** per chosen scheme (from scheme YAML), with "I have it ✓" ticks saved per plan, and where to get each missing document (tehsil, Social Welfare office, Udyam portal).
> 2. **Where to apply**: nearest bank branches and DIC/corporation offices for the village (data file + map link), and the official portal link (PMEGP e-portal, JanSamarth, MahaDBT where relevant). No scraping of government portals.
> 3. **Step-by-step application guide** per scheme (screens + read-aloud).
> 4. **Status tracking by the person**: applied → bank visit → sanctioned/rejected (+ reason) → disbursed; reminders (SMS/WhatsApp when a provider is configured; in-app otherwise).
> 5. On rejection, suggest the next-best scheme from the same evaluation.
>
> **Acceptance:** a plan can move through all statuses; reminders are queued via the adapter; checklist and status survive logout/login.

### Phase E — Grounded AI helper

> 1. "विचारा" chat on the result screen. The LLM (Gemini adapter) receives only the facts JSON from the evaluation (same facts builder as advisory) and answers in the user's language. Every number in the answer must exist in the facts (reuse the number validator); otherwise answer without numbers.
> 2. "What if" questions ("if I put ₹20,000 instead?", "if 40 customers a day?") call `POST /cases/{id}/evaluate` with changed inputs and explain the difference — the engine computes, the LLM explains.
> 3. Voice in / voice out. Rate-limit per user; log prompts without PII.
>
> **Acceptance:** a test suite of 30 questions where answers never contain numbers absent from facts; what-if results equal a direct engine call.

### Phase F — Production hardening (must-have before launch)

> 1. **Database**: move to Neon (`DATABASE_URL` already supports Neon SSL params). Run `alembic upgrade head` on deploy instead of startup `ALTER`s; keep startup checks read-only. Nightly `pg_dump` backup to object storage; restore drill documented in `docs/runbooks/`.
> 2. **OTP**: switch to Firebase (`OTP_PROVIDER=firebase`, `FIREBASE_PROJECT_ID`, Vercel `VITE_FIREBASE_*`). Add per-IP rate limit on auth endpoints (slowapi). Remove `dev` mode from production config (fail startup if `OTP_PROVIDER=dev` and `ENVIRONMENT=production` unless `ALLOW_DEMO_OTP=true`).
> 3. **Secrets**: rotate `SECRET_KEY`, set a separate `ENCRYPTION_KEY` with a documented re-encryption script.
> 4. **Observability**: Sentry (frontend + backend), structured JSON logs without PII, uptime monitor on `/health`, alert on 5xx rate.
> 5. **Security**: CSP and security headers on Vercel, dependency audit in CI, OWASP ASVS L1 checklist in `docs/runbooks/security.md`, rate limits on evaluate/DPR.
> 6. **Legal pages**: Privacy Policy, Terms, Grievance Officer contact (DPDP), consent notice versioning; link from login and consent screens.
> 7. **CI/CD**: GitHub Actions running all checks on PRs; Render/Vercel deploy only from `master` after checks pass.
> 8. **Hosting**: plan for Render paid instance (no cold start) when real users start.
>
> **Acceptance:** fresh deploy from empty Neon DB works with `alembic upgrade head`; backup + restore tested; production refuses demo OTP; Sentry receives a test error; legal pages live.

### Phase G — Offline & low bandwidth

> 1. Service worker caches the app shell, business list, scheme metadata and the user's own plans (read-only offline).
> 2. Draft a new plan offline (IndexedDB); evaluate when back online with a clear "waiting for internet" state — never compute results on the device.
> 3. Payload budget: first load < 300 KB gzipped on 3G; lazy-load admin, charts and Firebase.
>
> **Acceptance:** Playwright offline test: open app, view saved plan, start a draft, reconnect, draft submits once.

### Phase H — Admin & data operations

> 1. Make the existing admin screens real: scheme YAML editor with validation + test-run against golden cases + publish as new version; benchmark editor with source fields required; village coordinate fixes.
> 2. **Scheme watcher**: monthly job fetches each scheme's source URL, stores a hash, and flags changes for review (no auto-edit).
> 3. **Anonymous impact dashboard** for the ministry/partners: plans created, schemes recommended, district split, sanction rate — aggregates only, k-anonymity ≥ 10, no PII.
>
> **Acceptance:** an admin can change a scheme rate, see which golden tests change, and publish; dashboard shows no group smaller than 10.

### Phase I — Pilot & measurement

> 1. In-app feedback (1-tap 😊/😐/☹️ + optional voice note) on result and DPR screens.
> 2. Event analytics without PII (step reached, time per step, drop-off).
> 3. A pilot report template in `docs/pilot/`: completion rate, time to result, % who visited a bank, sanction rate, top confusion points.

---

## 4. Human tasks (do in parallel)

| When | Task |
|---|---|
| Now | **Firebase** project → enable Phone sign-in → add `arthmitra-two.vercel.app` to authorized domains → Blaze plan with a budget alert → send the web config. |
| Now | **Neon** project (Singapore region) → send connection string. Then delete the Render free DB after migrating. |
| Phase A | Download LGD Maharashtra village directory, Census 2011 PCA (Maharashtra), Village Directory amenities; put them in `data/raw/`. Collect NABARD/KVIC model project reports for each business. |
| Phase A | Verify each scheme against the official page/notification; note date. Talk to 1–2 bank managers about real interest rates and margin practice. |
| Phase F | Privacy policy + terms text (use a lawyer or a reviewed template); name a grievance officer. |
| Later | DLT registration (entity + sender ID + OTP template) if moving from Firebase to MSG91 for cheaper SMS at scale. |
| Phase I | Find 30–50 pilot users in 2–3 villages (SHG federations are a good route) and a partner bank branch. |

---

## 5. Things the agent must not break

- `backend/tests/test_self_service.py` — sign-up, lockout, isolation between people, erasure.
- `backend/tests/test_evaluation_regression.py` and finance golden tests.
- One organisation per person; every query scoped by `org_id`.
- No PII in logs, analytics, LLM prompts or the advisory cache.
- The DPR states which values are local vs benchmark estimates.
