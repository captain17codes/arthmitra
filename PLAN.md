# ArthMitra — Production Implementation Plan

## Phase Roadmap

### Phase 1: Monorepo Scaffold & Infrastructure (Current Phase)
- Monorepo layout matching TECH_SPEC §1.
- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, pytest, ruff, mypy.
- Frontend: React + Vite + TypeScript + Tailwind + `vite-plugin-pwa`, eslint, vitest, Playwright.
- Containerization: `docker-compose.yml` with `postgis/postgis:16`, `redis:7-alpine`, `api`, `worker` (RQ), `web`.
- Environment & Tooling: `.env.example`, `Makefile` (`make up`, `make test`, `make lint`), GitHub Actions CI (`.github/workflows/ci.yml`).
- Verification: `GET /health` returns ok; CI passes on baseline tests.

### Phase 2: Deterministic Finance Engine & Golden Test Vectors
- Pure Python financial calculations in `backend/engines/finance.py`.
- MCF vs. Term Loan auto-selection.
- Moratorium handling (Capitalise vs. Pay quarterly).
- Quarterly amortization schedule with ₹0.00 ending balance.
- All golden test vectors in TECH_SPEC §4 pass to $\pm\text{₹}1$.

### Phase 3: Versioned Scheme Data & Viability Engine
- Scheme rules in `data/schemes/nsfdc.yaml` with source URL and date.
- Category benchmarks in `data/benchmarks/enterprise_benchmarks.yaml`.
- Nayak Committee working capital evaluation, live DSCR gauge, Udhar stress slider, gestation mismatch detector.

### Phase 4: Geospatial Mapping & Saturation Engine
- `backend/adapters/osm_adapter.py` with Nominatim and Overpass integration, 10s timeout, disk caching, and offline demo fallback.
- Catchment capacity and market saturation scoring in `backend/engines/saturation.py`.

### Phase 5: AI Advisory Adapter & Number Validator
- Gemini 2.0 Flash integration in strict JSON mode with Pydantic validation.
- Number Validator ensuring zero numeric hallucinations.
- Graceful offline multi-lingual fallbacks.

### Phase 6: Mobile-First Frontend (360×640 Viewport)
- React PWA interface calibrated for Android screens.
- Multi-lingual strings in Marathi, Hindi, and English.
- Voice input via Web Speech API.

### Phase 7: One-Page DPR PDF Export & Verification
- Print stylesheet formatting clean Detailed Project Report.
- E2E Playwright tests verifying the mobile workflow.

### Phase 8: Production Polish & Review
- Small reviewable commits, clean lint and type checks, end-to-end verification.
