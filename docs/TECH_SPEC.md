# ArthMitra — Technical Specification (TECH_SPEC)

**Source of Truth** for the ArthMitra production system. If any requirement is unclear or contradictory, halt and consult the lead architect before guessing.

---

## Non-Negotiable System Invariants

1. **AI Never Computes Numbers or Eligibility:**
   - 100% of money, eligibility, schedules, DSCR, cash flows, and market figures come from pure Python engines in `backend/engines/`.
   - LLM output is strictly qualitative text that must pass an automated number validator ensuring zero unverified numbers are presented to the user.
2. **Versioned YAML Data (No Hard-Coded Terms):**
   - Scheme rules and business benchmarks live in `data/` as versioned YAML with source URL and verification date. Never hard-code scheme terms in Python.
3. **Golden Test Vectors (§4):**
   - Must pass to $\pm\text{₹}1$. Never edit a test to make it pass; fix the engine code.
4. **Data Privacy & DPDP Act 2023 Compliance:**
   - No Aadhaar, PAN, or bank account number fields anywhere in the application.
   - PII columns encrypted at rest. Explicit user consent required before saving any profile data.
5. **Adapter Isolation with Fallbacks:**
   - Every external call (LLM, ASR/TTS, OSM, Geocoding) must go through an adapter with an explicit timeout (8–15s), exponential retry, and guaranteed fallback response.
6. **Mobile-First UX (360×640 Android Viewport):**
   - Calibrated for low-cost Android smartphones in rural environments.
   - Multi-lingual i18n (`mr` Marathi, `hi` Hindi, `en` English).
   - Indian currency format (`₹10,00,000` via `en-IN` / `hi-IN`).

---

## §1. Monorepo Architecture & Directory Layout

```
arthmitra/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions running lint, mypy, pytest, vitest
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI entry point, /health, CORS
│   │   ├── config.py          # Pydantic v2 BaseSettings
│   │   └── database.py        # SQLAlchemy 2 async engine & session
│   ├── engines/               # Pure Python deterministic engines (0% AI math)
│   │   ├── __init__.py
│   │   ├── finance.py         # Amortization, moratorium, repayment
│   │   ├── eligibility.py     # Rule-based multi-scheme eligibility
│   │   ├── viability.py       # Nayak WC, DSCR, gestation mismatch, udhar stress
│   │   └── saturation.py      # Catchment supportable units & saturation ratio
│   ├── adapters/              # External integrations with timeout, retry & fallback
│   │   ├── __init__.py
│   │   ├── osm_adapter.py     # Nominatim & Overpass with local fallback
│   │   ├── llm_adapter.py     # Gemini JSON mode with schema validator
│   │   └── asr_adapter.py     # Web Speech / Bhashini fallback
│   ├── models/                # SQLAlchemy 2 declarative models
│   │   ├── __init__.py
│   │   ├── profile.py         # Encrypted profile store
│   │   └── audit.py           # Audit trail
│   ├── schemas/               # Pydantic v2 schemas
│   │   └── __init__.py
│   ├── worker/                # RQ background job execution
│   │   ├── __init__.py
│   │   └── tasks.py
│   ├── migrations/            # Alembic async migration suite
│   ├── tests/                 # Pytest suite with golden vectors
│   ├── Dockerfile
│   ├── pyproject.toml         # Ruff, Mypy, Pytest configurations
│   └── requirements.txt
├── data/                      # Versioned YAML rules & benchmarks
│   ├── schemes/               # NSFDC, NBCFDC, PMEGP, Mudra YAML definitions
│   │   └── nsfdc.yaml
│   └── benchmarks/            # Category benchmark profiles
│       └── enterprise_benchmarks.yaml
├── frontend/
│   ├── src/
│   │   ├── components/        # Mobile-first reusable UI widgets
│   │   ├── i18n/              # mr, hi, en translation files
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── tests/                 # Vitest component tests
│   ├── e2e/                   # Playwright mobile viewport tests
│   ├── vite.config.ts         # vite-plugin-pwa configured
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml         # postgis:16, redis, api, worker (RQ), web
├── Makefile                   # make up, make test, make lint
├── .env.example
├── .gitignore
├── PLAN.md
└── README.md
```

---

## §2. Data Layer & Scheme Specifications

### Versioned Scheme YAML Schema (`data/schemes/nsfdc.yaml`)
```yaml
schema_version: "1.0.0"
scheme_id: "nsfdc_mcf_tl"
ministry: "Ministry of Social Justice and Empowerment"
implementing_agency: "NSFDC"
source_url: "https://nsfdc.nic.in"
verified_date: "2026-10-26"
schemes:
  mcf:
    name: "Micro Credit Finance"
    max_project_cost: 140000.0
    loan_share: 0.90
    promoter_share: 0.10
    loan_ceiling: 125000.0
    interest_rate: 0.065
    tenure_months: 36
    moratorium_months: 3
    repayment_frequency: "quarterly"
  term_loan:
    name: "Term Loan"
    min_project_cost: 140000.01
    max_project_cost: 5000000.0
    loan_share: 0.90
    promoter_share: 0.10
    loan_ceiling: 4500000.0
    interest_rate: 0.080
    tenure_months: 84
    moratorium_months: 6
    repayment_frequency: "quarterly"
eligibility:
  category_sc_required: true
  annual_family_income_max: 500000.0
  age_min: 18
  age_max: 50
```

---

## §3. Deterministic Engines (`backend/engines/`)

1. **Finance Engine (`finance.py`):**
   - Derives raw project cost from margin capital: $\text{Raw} = \text{Margin} / 0.10$.
   - Applies scheme caps: MCF ceiling ₹1,25,000 (edge case where ₹14k margin $\rightarrow$ ₹1,39,000 project).
   - Simple interest moratorium: $\text{Loan} \times \text{Rate} \times \text{Moratorium} / 12$.
   - Amortization formula with quarter-end zero balance absorption.
2. **Viability Engine (`viability.py`):**
   - Nayak Committee 25% working capital assessment.
   - Live DSCR gauge: $\text{Quarterly Cash Flow} / \text{Quarterly EMI}$.
   - Gestation mismatch detector: $\text{Income Start Month} > \text{Moratorium Months}$.
   - Udhar stress impact: 2 months of delayed receivables locked in credit.
3. **Saturation Engine (`saturation.py`):**
   - Catchment capacity: $\text{Supportable} = \text{Catchment Pop} / \text{People per Unit}$.
   - Ratio: $(\text{Competitors}_{5\text{km}} + 1) / \text{Supportable}$.
   - Low ($< 0.7$), Moderate ($0.7 - 1.2$), High ($> 1.2$).

---

## §4. Golden Test Vectors (Must Pass to $\pm\text{₹}1$)

| Margin (₹) | Mode | Scheme | Project (₹) | Loan (₹) | Mor. Interest (₹) | Quarters | Quarterly EMI (₹) | Total Repaid (₹) |
|---|---|---|---|---|---|---|---|---|
| **10,000** | capitalise | MCF | 1,00,000 | 90,000 | 1,462.50 | 11 | **9,147.23** | **1,00,619.54** |
| **10,000** | pay | MCF | 1,00,000 | 90,000 | 1,462.50 | 11 | **9,000.97** | **1,00,473.12** |
| **14,000** | capitalise | MCF | 1,39,000 | 1,25,000 | 2,031.25 | 11 | **12,704.49** | **1,39,749.37** |
| **1,00,000** | capitalise | TL | 10,00,000 | 9,00,000 | 36,000.00 | 26 | **46,518.48** | **12,09,480.48** |
| **1,00,000** | pay | TL | 10,00,000 | 9,00,000 | 36,000.00 | 26 | **44,729.31** | **11,98,962.00** |
| **6,00,000** | capitalise | TL (capped) | 50,00,000 | 45,00,000 | 1,80,000.00 | 26 | **2,32,592.40** | **60,47,402.40** |

---

## §5. Adapters Layer & Fallbacks

- `osm_adapter.py`: Overpass API primary (`overpass-api.de`), fallback (`overpass.kumi.systems`), local SQLite/JSON disk cache, baseline demo fallback.
- `llm_adapter.py`: Gemini 2.0 Flash JSON mode, validated against Pydantic schema, fallbacks to static multi-lingual pre-generated templates.
- Number Validator: Rejects LLM output if any numeric value diverges from the engine's calculation.

---

## §6. Frontend Mobile Specification

- Viewport: $360 \times 640\text{ px}$ baseline, fully responsive.
- Touch Targets: Minimum $48 \times 48\text{ px}$.
- Progressive Web App: Offline service worker, installable manifest (`vite-plugin-pwa`).
- Multi-lingual: All UI strings loaded from `i18n/` bundles (`mr`, `hi`, `en`).
