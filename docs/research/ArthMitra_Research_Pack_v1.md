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
