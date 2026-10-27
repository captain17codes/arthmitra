# ArthMitra — Scheme Authoring & Version Management Guide

**Document Version:** 1.0.0  
**Effective Date:** October 2026  
**Audience:** Policy Admins, Scheme Coordinators, Data Stewards  
**Location in Repository:** `data/schemes/*.yaml` and Admin Console (`/admin/schemes`)

---

## 1. Overview & Core Principles

In ArthMitra, **all financial calculations and eligibility rules are deterministic code, never AI hallucinated or guessed.**
Every government scheme (NSFDC, PMEGP, CMEGP, MUDRA, Stand-Up India, MPBCDC, etc.) is specified as a strongly-typed, version-controlled YAML document with an official government source URL and date.

### Mandatory Rules for Scheme Updates
1. **Source & Date Obligation**: Every rule file or edit MUST include the official government circular or portal URL (`source_url`) and the gazette/circular date (`source_date`).
2. **Built-in Test Suite**: A scheme file cannot be published without passing its embedded test cases (`tests:` array in YAML).
3. **Immutability & Bit-for-Bit Reproducibility**: When a scheme is updated, existing historical evaluations and DPRs retain their snapshot of the scheme version used at evaluation time.
4. **Stacking Safeguards**: A beneficiary can never receive two capital subsidies across schemes.

---

## 2. Scheme YAML Specification

Scheme files live under `data/schemes/<SCHEME_CODE>.yaml`.

### Complete YAML Structure

```yaml
scheme_code: "NSFDC_MFS"
name:
  en: "NSFDC Micro Finance Scheme"
  mr: "एनएसएफडीसी सूक्ष्म वित्त योजना"
  hi: "एनएसएफडीसी सूक्ष्म वित्त योजना"
version: "1.1"
status: "VERIFIED" # VERIFIED | CONFIRM_WITH_AGENCY | UNVERIFIED_STUB
source_url: "https://nsfdc.nic.in/en/micro-credit-finance-scheme"
source_date: "2024-03-31"

eligibility:
  categories: ["SC"]
  min_age: 18
  max_age: 65
  family_income_ceiling_annual: 300000
  disability_min_pct: null
  occupation_flags: []
  shg_member_only: false
  prior_subsidy_disqualified: true

financial_terms:
  min_project_cost: 10000
  max_project_cost: 150000
  promoter_margin_pct: 10.0
  promoter_margin_sc_st_women_pct: 5.0
  subsidy_type: "NONE" # NONE | CAPITAL | INTEREST_SUBVENTION
  subsidy_pct: 0.0
  subsidy_max_amount: 0.0
  interest_type: "FIXED" # FIXED | SLAB | BANK_RATE
  annual_rate_pct: 6.0
  tenure_months: 36
  moratorium_months: 6
  moratorium_interest_mode: "CAPITALISE" # CAPITALISE | PAY | ZERO

tests:
  - name: "Eligible SC woman micro-enterprise"
    inputs:
      category: "SC"
      age: 28
      gender: "female"
      family_income: 180000
      project_cost: 100000
      margin_available: 10000
      prior_subsidy: false
    expected:
      status: "ELIGIBLE"
      loan_amount: 95000
      margin_required: 5000

  - name: "Disqualified General category"
    inputs:
      category: "General"
      age: 32
      family_income: 150000
      project_cost: 100000
    expected:
      status: "NOT_ELIGIBLE"
      reason_codes: ["CATEGORY_INELIGIBLE"]
```

---

## 3. Step-by-Step Update & Publication Workflow

### Step 1: Edit Scheme YAML
Admins can modify scheme terms either directly in `data/schemes/<SCHEME_CODE>.yaml` via git, or via the interactive web console at `/admin/schemes`.

### Step 2: Validate Schema
Verify that the YAML conforms strictly to the `SchemeDefinition` Pydantic model:
```bash
# Via CLI / Test
pytest arthmitra/backend/tests/test_rules_engine.py

# Or via Admin API
curl -X POST http://localhost:8000/admin/schemes/validate \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "..."}'
```

### Step 3: Run Automated Scheme Tests
The test runner executes all synthetic beneficiary fixtures listed in `tests:`:
```bash
curl -X POST http://localhost:8000/admin/schemes/test-run \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "..."}'

# Response must return:
# {
#   "valid": true,
#   "tests_run": 2,
#   "tests_passed": 2,
#   "failures": []
# }
```

### Step 4: Review Diff & Publish
1. The Admin UI renders a side-by-side colorized diff highlighting altered loan limits, interest rates, or eligibility criteria.
2. The Admin clicks **"प्रकाशित करा (Publish Version)"**.
3. The backend executes an atomic transaction:
   - Increments scheme version (e.g., `1.0` → `1.1`).
   - Inserts row into `scheme_versions` table with timestamp and admin user ID.
   - Logs entry in `audit_log` detailing who changed what and when.
   - Invalidates Redis scheme rules cache.

---

## 4. Conflict Resolution for Conflicting Schemes

When two official government sources publish contradictory guidelines (e.g., NBCFDC General Loan scheme where central ministry says 6% interest and state corporation says 8% with 10% margin):

1. **Set Status to `CONFIRM_WITH_AGENCY`**:
   Never pick one unilaterally. Set `status: "CONFIRM_WITH_AGENCY"`.
2. **Document Both In Notes**:
   Include both source URLs and conflicting parameters in the `notes:` attribute.
3. **UI Warning**:
   The field agent UI will show an amber banner instructing the Sakhi to confirm terms with the local District Social Welfare Officer / DIC before submitting bank papers.

---

## 5. Verification Checklist

- [ ] New scheme YAML contains valid source URL and publication date.
- [ ] Stacking rule in `data/schemes/stacking.yaml` verified (capital subsidy exclusivity).
- [ ] All embedded unit tests in the YAML pass 100%.
- [ ] Full backend regression suite (`pytest arthmitra/backend/tests`) passes.
- [ ] Published version is visible in Supervisor and Agent case evaluations.
