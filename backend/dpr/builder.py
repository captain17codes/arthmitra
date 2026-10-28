from __future__ import annotations

from decimal import Decimal
from typing import Any

from .models import DprSection


def format_currency_inr(val: Any) -> str:
    """Format numerical value with Indian grouping commas (e.g. ₹1,50,000.00)."""
    try:
        d = Decimal(str(val)).quantize(Decimal("0.01"))
        sign = "-" if d < 0 else ""
        whole, frac = f"{abs(d):.2f}".split(".")
        if len(whole) > 3:
            head, tail = whole[:-3], whole[-3:]
            groups = []
            while len(head) > 2:
                groups.insert(0, head[-2:])
                head = head[:-2]
            if head:
                groups.insert(0, head)
            whole = ",".join(groups) + "," + tail
        return f"{sign}₹{whole}.{frac}"
    except Exception:
        return f"₹{val}"


def build_dpr_sections(
    eval_output: dict[str, Any],
    input_snapshot: dict[str, Any],
    language: str = "mr",
    promoter_name: str | None = None,
    benchmark: dict[str, Any] | None = None,
) -> list[DprSection]:
    """
    Construct all 12 Bank-Ready Sections required by TECH_SPEC §7.2.
    Contains both Marathi and English data structures for dual-language rendering.
    """
    summary = (eval_output.get("summary") or {})
    viability = (eval_output.get("viability") or {})
    inputs = (input_snapshot.get("inputs") or {})
    beneficiary = (input_snapshot.get("beneficiary") or {})
    village = (input_snapshot.get("village") or {})

    b_name_en = summary.get("business_name_en", "Micro Enterprise")
    b_name_mr = summary.get("business_name_mr", "सूक्ष्म व्यवसाय")
    v_name = village.get("name", summary.get("village_name", "गावात"))
    proj_cost = summary.get("project_cost", "0")
    margin_avail = summary.get("margin_available", "0")

    top_pkgs = summary.get("top_packages", [])
    lead_pkg = top_pkgs[0] if top_pkgs else {}
    sc_code = lead_pkg.get("scheme_code", "-")
    sc_name = (lead_pkg.get("scheme_name") or {}).get("mr", sc_code)
    sc_name_en = (lead_pkg.get("scheme_name") or {}).get("en", sc_code)
    loan_amt = lead_pkg.get("loan_amount", "0")
    sub_amt = lead_pkg.get("subsidy_amount", "0")
    own_margin_req = lead_pkg.get("own_margin_required", margin_avail)
    rate_pct = lead_pkg.get("annual_rate_pct", "-")
    tenure_m = lead_pkg.get("tenure_months", "-")
    mora_m = lead_pkg.get("moratorium_months", "-")
    emi = lead_pkg.get("emi", lead_pkg.get("monthly_emi", "0"))
    freq_m = int(lead_pkg.get("emi_frequency_months", 1) or 1)
    emi_label_en = "per quarter" if freq_m == 3 else "per month"
    emi_label_mr = "प्रति तिमाही" if freq_m == 3 else "प्रति महिना"
    total_repay = lead_pkg.get("total_repayment", "0")

    avg_dscr = summary.get("average_dscr") or "-"
    bep_cap = summary.get("breakeven_capacity_pct") or "-"
    nayak_wc = (summary.get("nayak_working_capital") or {})
    udhar = (summary.get("udhar_stress") or {})
    sat_level = summary.get("market_saturation") or "needs_info"
    catch_pop = summary.get("effective_catchment_population", "0")
    cat_demand = summary.get("monthly_category_demand", "0")
    comp_count = summary.get("competitors_reported") or "-"
    verified_mr = "प्रमाणित" if beneficiary.get("category_verified") else "प्रमाणपत्र तपासणी बाकी"
    verified_en = "Verified" if beneficiary.get("category_verified") else "Certificate to be verified"
    income_val = beneficiary.get("annual_family_income")
    income_txt = format_currency_inr(str(income_val)) if income_val is not None else beneficiary.get("income_band", "-")
    sat_mr = {"low": "कमी स्पर्धा", "medium": "मध्यम स्पर्धा", "high": "जास्त स्पर्धा — सावधान"}.get(sat_level, "माहिती अपूर्ण")
    sat_en = {"low": "low competition", "medium": "moderate competition", "high": "high competition — caution"}.get(
        sat_level, "competitor count not yet entered"
    )

    name = promoter_name or "-"
    lead_docs = [str(d).replace("_", " ") for d in (lead_pkg.get("documents") or [])]
    apply_at = lead_pkg.get("apply_at") or "-"
    source_url = lead_pkg.get("source_url") or "-"
    subsidy_treatment = lead_pkg.get("subsidy_treatment")
    emi_after = lead_pkg.get("emi_after_subsidy_adjustment")
    dscr_passed = summary.get("dscr_passed")
    dscr_target = viability.get("dscr_target") or "1.25"
    inputs_used = viability.get("inputs_used") or {}
    warnings_all = list(dict.fromkeys(
        list(viability.get("warnings") or [])
        + list(lead_pkg.get("warnings") or [])
        + list((eval_output.get("market") or {}).get("warnings") or [])
    ))
    udhar_pct_txt = udhar.get("udhar_pct")
    try:
        udhar_pct_txt = f"{Decimal(str(udhar_pct_txt)) * 100:.0f}%"
    except Exception:
        udhar_pct_txt = "-"

    # Benchmark asset list (indicative unit costs, not quotations).
    capex_items: list[tuple[str, Decimal, str]] = []
    for k, v in ((benchmark or {}).get("capex") or {}).items():
        if isinstance(v, dict) and "value" in v:
            capex_items.append((k.replace("_", " "), Decimal(str(v["value"])), str(v.get("confidence") or "")))
    capex_sum = sum((c[1] for c in capex_items), Decimal("0"))
    balance = Decimal(str(proj_cost)) - capex_sum

    sections: list[DprSection] = []

    # Section 1: Promoter Profile
    sections.append(
        DprSection(
            section_number=1,
            title_mr="१. उद्योजक / प्रवर्तक तपशील (Promoter Profile)",
            title_en="1. Promoter Profile",
            content_mr=(
                f"प्रवर्तकाचे नाव: {name}\n"
                f"वय: {beneficiary.get('age', '-')} वर्षे | लिंग: {beneficiary.get('gender', '-')}\n"
                f"सामाजिक प्रवर्ग: {beneficiary.get('category', '-')} ({verified_mr})\n"
                f"वार्षिक कौटुंबिक उत्पन्न: {income_txt}\n"
                f"अस्तित्वात असलेले मासिक कर्ज (EMI): {format_currency_inr(beneficiary.get('existing_emi', '0'))}"
            ),
            content_en=(
                f"Promoter Name: {name}\n"
                f"Age: {beneficiary.get('age', '-')} Years | Gender: {beneficiary.get('gender', '-')}\n"
                f"Social Category: {beneficiary.get('category', '-')} ({verified_en})\n"
                f"Annual Family Income: {income_txt}\n"
                f"Existing Debt Service (EMI): {format_currency_inr(beneficiary.get('existing_emi', '0'))}/month"
            ),
        )
    )

    # Section 2: Project Description & Location
    sections.append(
        DprSection(
            section_number=2,
            title_mr="२. प्रकल्प स्वरूप व ठिकाण (Project Description & Location)",
            title_en="2. Project Description & Location",
            content_mr=(
                f"प्रस्तावित प्रकल्प: {b_name_mr} ({b_name_en})\n"
                f"प्रकल्प ठिकाण: {v_name} (LGD Code: {village.get('lgd_code', '-')})\n"
                f"गाव लोकसंख्या (जनगणना २०११): {village.get('pop_2011', '-')}"
            ),
            content_en=(
                f"Proposed Enterprise: {b_name_en}\n"
                f"Location: Village {v_name} (LGD Code: {village.get('lgd_code', '-')})\n"
                f"Village population (Census 2011): {village.get('pop_2011', '-')}"
            ),
        )
    )

    # Section 3: Market Assessment
    sections.append(
        DprSection(
            section_number=3,
            title_mr="३. बाजारपेठ पाहणी व संभाव्य मागणी (Market Assessment)",
            title_en="3. Market Assessment",
            content_mr=(
                f"प्रभावी ग्राहक कार्यक्षेत्र लोकसंख्या (Catchment): {catch_pop} व्यक्ती (१० किमी परिसर)\n"
                f"मासिक वर्गवारी मागणी (HCES २०२३-२४ नुसार): {format_currency_inr(cat_demand)} / महिना\n"
                f"गावात कार्यरत असलेले प्रतिस्पर्धी: {comp_count} दुकाने / युनिट्स\n"
                f"बाजार संपृक्तता निर्देशांक (Saturation Level): {sat_mr}"
            ),
            content_en=(
                f"Effective Catchment Population: {catch_pop} persons (within 10 km decay radius)\n"
                f"Monthly Category Demand: {format_currency_inr(cat_demand)} / month (Source: MoSPI HCES 2023-24)\n"
                f"Active Local Competitors: {comp_count} unit(s) reported\n"
                f"Market Saturation Level: {sat_en}"
            ),
        )
    )

    # Section 4: Project Cost Breakdown — benchmark items only; no invented percentage split.
    items_mr = [f"• {n}: {format_currency_inr(v)} (संदर्भ खर्च{', ' + c if c else ''})" for n, v, c in capex_items]
    items_en = [f"• {n}: {format_currency_inr(v)} (benchmark unit cost{', ' + c if c else ''})" for n, v, c in capex_items]
    if capex_items and balance >= 0:
        bal_mr = f"• उर्वरित (खेळते भांडवल / इतर, कोटेशननुसार निश्चित करावे): {format_currency_inr(balance)}"
        bal_en = f"• Balance (working capital / other, to be itemised with quotations): {format_currency_inr(balance)}"
    elif capex_items:
        bal_mr = "• प्रकल्प खर्च संदर्भ यादीपेक्षा कमी आहे — विक्रेता कोटेशननुसार घटक कमी करून निश्चित करावे."
        bal_en = "• Project cost is below the benchmark asset list — scale items to vendor quotations."
    else:
        bal_mr = "• घटकनिहाय खर्च विक्रेता कोटेशननुसार भरावा."
        bal_en = "• Item-wise costs to be filled from vendor quotations."
    sections.append(
        DprSection(
            section_number=4,
            title_mr="४. एकूण प्रकल्प खर्च रचना (Project Cost Breakdown)",
            title_en="4. Project Cost Breakdown",
            content_mr="\n".join(
                ["संदर्भ (बेंचमार्क) घटक — अंतिम रक्कम विक्रेता कोटेशननुसार:"] + items_mr + [bal_mr,
                 f"एकूण प्रकल्प खर्च: {format_currency_inr(proj_cost)}"]
            ),
            content_en="\n".join(
                ["Indicative components from the benchmark — final amounts per vendor quotations:"] + items_en + [bal_en,
                 f"Total Project Outlay: {format_currency_inr(proj_cost)}"]
            ),
        )
    )

    # Section 5: Means of Finance
    sections.append(
        DprSection(
            section_number=5,
            title_mr="५. वित्तपुरवठा साधने व योजना (Means of Finance)",
            title_en="5. Means of Finance",
            content_mr=(
                f"१. प्रवर्तकाचे स्वतःचे भांडवल (Margin): {format_currency_inr(own_margin_req)}\n"
                f"२. बँक मुदत कर्ज (Term Loan): {format_currency_inr(loan_amt)}\n"
                f"३. शासकीय भांडवली अनुदान (Subsidy): {format_currency_inr(sub_amt)}"
                f"{' — ३ वर्षे बँकेत FDR म्हणून ठेवले जाते' if subsidy_treatment == 'fdr_3yr' else ''}\n"
                f"शिफारस केलेली शासकीय योजना: {sc_name}{'' if sc_code in sc_name else f' ({sc_code})'}\n"
                f"एकूण वित्तपुरवठा: {format_currency_inr(proj_cost)}"
            ),
            content_en=(
                f"1. Promoter Own Margin: {format_currency_inr(own_margin_req)}\n"
                f"2. Bank Term Loan: {format_currency_inr(loan_amt)}\n"
                f"3. Government Capital Subsidy: {format_currency_inr(sub_amt)}"
                f"{' — held as a 3-year FDR by the bank' if subsidy_treatment == 'fdr_3yr' else ''}\n"
                f"Target Financing Scheme: {sc_name_en}{'' if sc_code in sc_name_en else f' ({sc_code})'}\n"
                f"Total Means of Finance: {format_currency_inr(proj_cost)}"
            ),
        )
    )

    # Section 6: Assumptions — say which values are local and which are benchmark estimates.
    rev_p = (benchmark or {}).get("revenue_parameters") or {}
    cost_p = (benchmark or {}).get("cost_parameters") or {}
    a_mr: list[str] = []
    a_en: list[str] = []
    for k, src in inputs_used.items():
        meta = rev_p.get(k) or cost_p.get(k) or {}
        val = inputs.get(k, meta.get("value", "-"))
        unit = meta.get("unit") or ""
        if src == "local":
            a_mr.append(f"• {k}: {val} {unit} (गावातील प्रत्यक्ष माहिती)")
            a_en.append(f"• {k}: {val} {unit} (entered locally by agent)")
        else:
            conf = meta.get("confidence") or "estimate"
            a_mr.append(f"• {k}: {val} {unit} (संदर्भ अंदाज — {conf}; क्षेत्र पडताळणी आवश्यक)")
            a_en.append(f"• {k}: {val} {unit} (benchmark {conf}; to be field-validated)")
    if "udhar_pct" in inputs:
        a_mr.append(f"• उधार विक्री: {udhar_pct_txt}")
        a_en.append(f"• Customer credit (udhar) share: {udhar_pct_txt}")
    sections.append(
        DprSection(
            section_number=6,
            title_mr="६. आर्थिक गृहीतके व स्थानिक प्रमाणीकरण (Key Assumptions)",
            title_en="6. Key Assumptions & Local Calibration",
            content_mr="अंदाज खालील मूल्यांवर आधारित आहेत:\n" + "\n".join(a_mr or ["• संदर्भ (बेंचमार्क) मूल्ये."]),
            content_en="Projections use the following values:\n" + "\n".join(a_en or ["• Benchmark values only."]),
        )
    )

    # Section 7: 5-Year P&L and Cash Flow
    projections = viability.get("projections", [])
    p_lines_mr = []
    p_lines_en = []
    for p in projections:
        yr = p.get("year", 1)
        rev = p.get("gross_revenue", "0")
        pat = p.get("pat", "0")
        ds = p.get("debt_service", "0")
        dscr_val = p.get("dscr", "0")
        p_lines_mr.append(f"वर्ष {yr}: एकूण महसूल {format_currency_inr(rev)} | निव्वळ नफा (PAT) {format_currency_inr(pat)} | कर्जफेड {format_currency_inr(ds)} | DSCR {dscr_val}")
        p_lines_en.append(f"Year {yr}: Turnover {format_currency_inr(rev)} | PAT {format_currency_inr(pat)} | Debt Service {format_currency_inr(ds)} | DSCR {dscr_val}")

    sections.append(
        DprSection(
            section_number=7,
            title_mr="७. ५-वर्षीय नफा-तोटा व रोख प्रवाह अंदाज (5-Year P&L & Cash Flow)",
            title_en="7. 5-Year Profit & Loss and Cash Flow Projections",
            content_mr="\n".join(p_lines_mr),
            content_en="\n".join(p_lines_en),
        )
    )

    # Section 8: DSCR & Break-Even — conclusion follows the computed result.
    if dscr_passed is True:
        concl_mr = f"सरासरी DSCR {avg_dscr}, बँक निकष {dscr_target} पेक्षा जास्त."
        concl_en = f"Average DSCR {avg_dscr} meets the bank threshold of {dscr_target}."
    elif dscr_passed is False:
        concl_mr = f"सरासरी DSCR {avg_dscr}, बँक निकष {dscr_target} पेक्षा कमी — प्रकल्प आकार / अटी पुन्हा तपासा."
        concl_en = f"Average DSCR {avg_dscr} is below the bank threshold of {dscr_target} — revisit project size or terms."
    else:
        concl_mr = "DSCR काढता आला नाही (कर्जफेड नाही / माहिती अपूर्ण)."
        concl_en = "DSCR could not be computed (no debt service or incomplete data)."
    sections.append(
        DprSection(
            section_number=8,
            title_mr="८. कर्ज परतफेड क्षमता व ब्रेक-इव्हन (DSCR & Break-Even Analysis)",
            title_en="8. Debt Service Coverage (DSCR) & Break-Even Analysis",
            content_mr=(
                f"{concl_mr}\n"
                f"पहिल्या वर्षाचा ब्रेक-इव्हन: {bep_cap}% क्षमता वापर."
            ),
            content_en=(
                f"{concl_en}\n"
                f"Year-1 break-even capacity utilisation: {bep_cap}%."
            ),
        )
    )

    # Section 9: Debt Financing & Repayment Schedule
    sections.append(
        DprSection(
            section_number=9,
            title_mr="९. कर्ज परतफेड वेळापत्रक व हप्ते (Repayment Schedule)",
            title_en="9. Loan Terms & Repayment Schedule",
            content_mr=(
                f"प्रस्तावित कर्ज: {format_currency_inr(loan_amt)} | अंदाजित वार्षिक व्याज दर: {rate_pct}% (बँक ठरवेल)\n"
                f"एकूण मुदत: {tenure_m} महिने | सवलत कालावधी (Moratorium): {mora_m} महिने\n"
                f"हप्ता (EMI): {format_currency_inr(emi)} {emi_label_mr}\n"
                f"एकूण परतफेड रक्कम{' (अनुदान समायोजनानंतर)' if subsidy_treatment == 'fdr_3yr' else ''}: {format_currency_inr(total_repay)}"
                + (f"\n३ वर्षांनंतर हप्ता: {format_currency_inr(emi_after)} {emi_label_mr}" if emi_after else "")
            ),
            content_en=(
                f"Proposed Loan: {format_currency_inr(loan_amt)} | Indicative Interest Rate: {rate_pct}% p.a. (set by bank)\n"
                f"Tenure: {tenure_m} months | Moratorium: {mora_m} months\n"
                f"Instalment (EMI): {format_currency_inr(emi)} {emi_label_en}\n"
                f"Total repayable{' (after subsidy adjustment)' if subsidy_treatment == 'fdr_3yr' else ''}: {format_currency_inr(total_repay)}"
                + (f"\nInstalment after year 3: {format_currency_inr(emi_after)} {emi_label_en}" if emi_after else "")
            ),
        )
    )

    # Section 10: Risks — engine warnings and computed buffers only, no boilerplate claims.
    r_mr = [
        f"• उधार {udhar_pct_txt} गृहीत: अतिरिक्त खेळते भांडवल {format_currency_inr(udhar.get('extra_wc_needed', '0'))}; "
        f"रोख बफर {udhar.get('cash_buffer_months', '-')} महिने हप्ते.",
        f"• नायक समिती खेळते भांडवल (उलाढालीच्या २५%): {format_currency_inr(nayak_wc.get('total', '0'))}.",
        f"• स्थानिक स्पर्धा: {sat_mr}.",
    ] + [f"• {w}" for w in warnings_all]
    r_en = [
        f"• Udhar assumed at {udhar_pct_txt}: extra working capital {format_currency_inr(udhar.get('extra_wc_needed', '0'))}; "
        f"cash buffer {udhar.get('cash_buffer_months', '-')} months of instalments.",
        f"• Nayak Committee working capital (25% of turnover): {format_currency_inr(nayak_wc.get('total', '0'))}.",
        f"• Local competition: {sat_en}.",
    ] + [f"• {w}" for w in warnings_all]
    sections.append(
        DprSection(
            section_number=10,
            title_mr="१०. संभाव्य जोखीम व उपाययोजना (Risks & Mitigations)",
            title_en="10. Risks & Mitigations",
            content_mr="\n".join(r_mr),
            content_en="\n".join(r_en),
        )
    )

    # Section 11: Document checklist from the recommended scheme's own list.
    docs = lead_docs or ["KYC", "caste certificate (if applicable)", "vendor quotations"]
    sections.append(
        DprSection(
            section_number=11,
            title_mr="११. आवश्यक कागदपत्रे व अर्ज प्रक्रिया (Document Checklist)",
            title_en="11. Document Checklist & Where to Apply",
            content_mr="\n".join(
                [f"{i}. {d}" for i, d in enumerate(docs, 1)]
                + ["आधार क्रमांक ॲपमध्ये साठवला जात नाही; मूळ कागदपत्रे बँकेत दाखवा.",
                   f"अर्ज कुठे करावा: {apply_at}", f"अधिकृत स्रोत: {source_url}"]
            ),
            content_en="\n".join(
                [f"{i}. {d}" for i, d in enumerate(docs, 1)]
                + ["Aadhaar is never stored by ArthMitra; show originals at the bank.",
                   f"Where to apply: {apply_at}", f"Official source: {source_url}"]
            ),
        )
    )

    # Section 12: Statutory Disclaimer
    sections.append(
        DprSection(
            section_number=12,
            title_mr="१२. वैधानिक सूचना व अस्वीकरण (Statutory Disclaimer)",
            title_en="12. Statutory Disclaimer",
            content_mr=(
                "हा सविस्तर प्रकल्प अहवाल (DPR) योजना नियम, संदर्भ (बेंचमार्क) अंदाज व स्थानिक माहितीच्या आधारे वित्तीय मूल्यमापनासाठी "
                "तयार करण्यात आला आहे. कर्ज मंजूर करणे, व्याजदर व अंतिम अटी ठरवण्याचा पूर्ण अधिकार वित्तपुरवठादार बँकेचा आहे. "
                "ArthMitra कोणत्याही कर्ज मंजुरीची किंवा अनुदानाची हमी देत नाही."
            ),
            content_en=(
                "This Detailed Project Report (DPR) is prepared for bank appraisal from published scheme rules, "
                "benchmark estimates and locally entered values (marked in section 6). Loan sanction, appraisal terms, and disbursement decisions remain "
                "at the sole discretion of the financing institution / bank. ArthMitra provides advisory estimates and "
                "does not guarantee loan sanction or subsidy approval."
            ),
        )
    )

    return sections
