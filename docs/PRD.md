# ArthMitra — Product Requirements Document (PRD)

**Product Name:** ArthMitra (अर्थमित्र)  
**Vision:** Production-grade AI-assisted hyper-local business viability & financial structuring engine for rural micro-entrepreneurs under Ministry of Social Justice and Empowerment (MoSJE) apex refinance corporations.

---

## 1. Problem Statement & User Research Insights

### 1.1 The Rural Enterprise Paradox
Rural micro-entrepreneurs accessing concessional government schemes (such as NSFDC, NBCFDC, and NSKFDC) suffer high default rates within 18 months due to:
1. **Hyper-Local Market Cannibalization:** Identical copycat units open in immediate proximity without population supportable metrics.
2. **Working Capital Depletion & Udhar (Customer Credit):** Cash flow is stranded in unpaid village credit while debt service begins prematurely.
3. **Information Asymmetry:** Scheme rules, moratorium conditions, and subsidy schedules are incomprehensible to low-literacy beneficiaries.

### 1.2 User Personas
- **Primary Beneficiary:** Rural SC/ST/OBC artisan, farmer, or nano-trader (e.g., Sunita, Tailoring; Ramesh, Dairy; Kavita, Goatery).
- **Assisted Intermediary:** Bank Sakhi, Self-Help Group (SHG) leader, Common Service Centre (CSC) Village Level Entrepreneur (VLE).

---

## 2. Regulatory Compliance & DPDP Act 2023 Architecture

1. **No Sensitive PII Collection:**
   - Explicitly prohibited: No Aadhaar number, PAN, or bank account number fields anywhere.
2. **Consent-First Architecture:**
   - Explicit, multi-lingual consent modal before profile creation or business calculation caching.
3. **Data Security:**
   - Database columns storing contact info or names are AES-256 encrypted.
   - Zero biometric or financial identification storage.

---

## 3. Core Functional Modules

### 3.1 Module 1: Hyper-Local Geospatial Intelligence
- LGD (Local Government Directory) code mapping down to the village level.
- OpenStreetMap competitor mapping (5 km immediate catchment, 10 km extended trading radius).
- Algorithmic market saturation scoring with rural informal business correction factors.

### 3.2 Module 2: Deterministic Concessional Financial Engine
- Automatic scheme routing across NSFDC Micro Credit Finance (MCF) and Term Loan (TL).
- Exact quarterly amortization schedule with moratorium simple interest handling (capitalise vs. pay quarterly).
- 100% deterministic calculation; zero mathematical generation permitted by LLMs.

### 3.3 Module 3: Viability & Stress Testing
- Nayak Committee 25% working capital assessment rule.
- Customer credit (Udhar) stress slider (0% to 40%).
- Gestation-moratorium cash-flow mismatch warning.

### 3.4 Module 4: Multi-Lingual AI Advisory DPR
- Generation of bankable Detailed Project Report (DPR) narrative via Gemini 2.0 Flash in strict JSON mode.
- Marathi (`mr`), Hindi (`hi`), and English (`en`) outputs.
- Anti-copycat complementary business suggestions.
- 1-click printable DPR PDF.
