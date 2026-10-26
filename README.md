# ArthMitra (अर्थमित्र)

> **AI-Driven Hyper-Local Business Advisory & Financial Structuring for Rural Micro-Entrepreneurs**  
> **Ministry:** Ministry of Social Justice and Empowerment (MoSJE)  
> **Apex Scheme Basis:** National Scheduled Castes Finance and Development Corporation (NSFDC) — Micro Credit Finance & Term Loan

---

## 1. Architecture & Non-Negotiable Invariants

- **AI Never Computes Numbers or Eligibility:** 100% of money, eligibility, schedules, DSCR and market figures come from pure Python engines in `backend/engines/`. LLM output is text-only and validated.
- **Versioned YAML Scheme Data:** Scheme rules and business benchmarks live in `data/` as versioned YAML with source URL and verification date. Never hard-code scheme terms in Python.
- **Golden Test Vectors (§4):** Golden test vectors pass to $\pm\text{₹}1$.
- **Data Privacy & DPDP Act 2023:** Zero Aadhaar, PAN or bank account fields anywhere. PII columns encrypted. Consent before any profile data is saved.
- **Adapter Resilience:** Every external call (LLM, ASR, OSM) goes through an adapter with timeout, retry, and fallback.
- **Mobile-First UX:** Calibrated for a 360×640 Android viewport. Multi-lingual i18n (`mr` Marathi, `hi` Hindi, `en` English) and Indian currency format (`₹10,00,000`).

---

## 2. Monorepo Layout

```
arthmitra/
├── .github/workflows/ci.yml   # CI pipeline: lint, type-check & test
├── backend/                  # Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
│   ├── app/                  # FastAPI routes, /health, config, database
│   ├── engines/              # Pure Python calculation engines (0% AI math)
│   ├── adapters/             # External adapters with timeout, retry, fallback
│   ├── worker/               # RQ background worker
│   ├── tests/                # Pytest suite with golden vectors
│   └── migrations/           # Alembic database migrations
├── data/                     # Versioned YAML rules & benchmarks
│   ├── schemes/              # Scheme parameters (NSFDC, etc.)
│   └── benchmarks/           # 8 enterprise model benchmark profiles
├── frontend/                 # React, Vite, TypeScript, Tailwind, vite-plugin-pwa
│   ├── src/                  # Mobile-first components, i18n (mr, hi, en)
│   ├── tests/                # Vitest unit & component tests
│   └── e2e/                  # Playwright 360×640 mobile viewport tests
├── docker-compose.yml        # postgis/postgis:16, redis, api, worker (RQ), web
├── Makefile                  # make up, make test, make lint
├── docs/                     # PRD.md, TECH_SPEC.md
├── .env.example
└── PLAN.md
```

---

## 3. Quick Start

### Method A: Docker Compose (Production Stack)
```bash
cp .env.example .env
make up
```
- Web Application: http://localhost:3000
- Backend Health Check: http://localhost:8000/health (`{"status": "ok"}`)
- API Documentation (Swagger): http://localhost:8000/docs
- Stop containers: `make down`

### Method B: Local Development

#### 1. Backend
```bash
cd backend
cp ../.env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 on a mobile or simulated 360×640 screen.

---

## 4. Verification & Testing

```bash
# Run lint, type-check & tests across both stacks
make lint
make test
```

Or individually:
```bash
# Backend lint & tests
cd backend
ruff check .
mypy app engines adapters
pytest -v

# Frontend lint & tests
cd frontend
npm run lint
npm test
```
