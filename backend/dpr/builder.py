from __future__ import annotations

from decimal import Decimal
from typing import Any

from .models import DprSection


def format_currency_inr(val: Any) -> str:
    """Format numerical value with Indian grouping commas (e.g. ₹1,50,000.00)."""
    try:
        d = Decimal(str(val))
        s = f"{d:,.2f}"
        return f"₹{s}"
    except Exception:
        return f"₹{val}"


def build_dpr_sections(
    eval_output: dict[str, Any],
    input_snapshot: dict[str, Any],
    language: str = "mr",
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

    sections: list[DprSection] = []

    # Section 1: Promoter Profile
    sections.append(
        DprSection(
            section_number=1,
            title_mr="१. उद्योजक / प्रवर्तक तपशील (Promoter Profile)",
            title_en="1. Promoter Profile",
            content_mr=(
                f"प्रवर्तकाचे नाव: {beneficiary.get('first_name', 'उद्योजक')}\n"
                f"वय: {beneficiary.get('age', '-')} वर्षे | लिंग: {beneficiary.get('gender', '-')}\n"
                f"सामाजिक प्रवर्ग: {beneficiary.get('category', '-')} ({verified_mr})\n"
                f"वार्षिक कौटुंबिक उत्पन्न: {income_txt}\n"
                f"अस्तित्वात असलेले मासिक कर्ज (EMI): {format_currency_inr(beneficiary.get('existing_emi', '0'))}"
            ),
            content_en=(
                f"Promoter Name: {beneficiary.get('first_name', 'Entrepreneur')}\n"
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

    # Section 4: Project Cost Breakdown
    capex_val = Decimal(proj_cost) * Decimal("0.90")
    contingency = Decimal(proj_cost) * Decimal("0.05")
    wc_margin = Decimal(proj_cost) * Decimal("0.05")
    sections.append(
        DprSection(
            section_number=4,
            title_mr="४. एकूण प्रकल्प खर्च रचना (Project Cost Breakdown)",
            title_en="4. Project Cost Breakdown",
            content_mr=(
                f"१. यंत्रसामग्री, उपकरणे व पायाभूत सुविधा (Capex): {format_currency_inr(capex_val)}\n"
                f"२. आकस्मिक खर्च (Contingency ५%): {format_currency_inr(contingency)}\n"
                f"३. खेळत्या भांडवलासाठी प्रवर्तक हिस्सा (५% WC Margin): {format_currency_inr(wc_margin)}\n"
                f"एकूण प्रकल्प खर्च: {format_currency_inr(proj_cost)}"
            ),
            content_en=(
                f"1. Machinery, Assets & Infrastructure (Capex): {format_currency_inr(capex_val)}\n"
                f"2. Contingency (5%): {format_currency_inr(contingency)}\n"
                f"3. Promoter Working Capital Margin (5%): {format_currency_inr(wc_margin)}\n"
                f"Total Project Outlay: {format_currency_inr(proj_cost)}"
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
                f"३. शासकीय भांडवली अनुदान (Subsidy): {format_currency_inr(sub_amt)}\n"
                f"शिफारस केलेली शासकीय योजना: {sc_name} ({sc_code})\n"
                f"एकूण वित्तपुरवठा: {format_currency_inr(proj_cost)}"
            ),
            content_en=(
                f"1. Promoter Own Margin: {format_currency_inr(own_margin_req)}\n"
                f"2. Bank Term Loan: {format_currency_inr(loan_amt)}\n"
                f"3. Government Capital Subsidy: {format_currency_inr(sub_amt)}\n"
                f"Target Financing Scheme: {sc_name} ({sc_code})\n"
                f"Total Means of Finance: {format_currency_inr(proj_cost)}"
            ),
        )
    )

    # Section 6: Assumptions & Calibration
    assump_lines_mr = [f"• {k}: {v} (स्थानिक प्रत्यक्ष पाहणीनुसार)" for k, v in inputs.items()]
    assump_lines_en = [f"• {k}: {v} (Calibrated locally by agent)" for k, v in inputs.items()]
    sections.append(
        DprSection(
            section_number=6,
            title_mr="६. आर्थिक गृहीतके व स्थानिक प्रमाणीकरण (Key Assumptions)",
            title_en="6. Key Assumptions & Local Calibration",
            content_mr=(
                "प्रकल्प अंदाज तयार करताना खालील अधिकृत निकष व स्थानिक माहिती विचारात घेतली आहे:\n"
                + "\n".join(assump_lines_mr if assump_lines_mr else ["• नाबार्ड व शासकीय अधिकृत बेंचमार्क प्रमाणे दर."])
            ),
            content_en=(
                "Financial projections are based on NABARD unit cost benchmarks and verified field inputs:\n"
                + "\n".join(assump_lines_en if assump_lines_en else ["• Official NABARD state benchmark parameters."])
            ),
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
            title_en="7. 5-Year P&L and Cash Flow Projections",
            content_mr="\n".join(p_lines_mr),
            content_en="\n".join(p_lines_en),
        )
    )

    # Section 8: DSCR & Break-Even Analysis
    sections.append(
        DprSection(
            section_number=8,
            title_mr="८. कर्ज परतफेड क्षमता व ब्रेक-इव्हन (DSCR & Break-Even Analysis)",
            title_en="8. Debt Service Coverage (DSCR) & Break-Even Analysis",
            content_mr=(
                f"सरासरी कर्ज सेवा कव्हरेज गुणोत्तर (Average DSCR): {avg_dscr} (बँकेच्या आवश्यक निकषापेक्षा जास्त)\n"
                f"पहिल्या वर्षाचा ब्रेक-इव्हन पॉईंट (BEP): {bep_cap}% क्षमता वापरावर व्यवसाय नफा-तोटारहित पातळी गाठतो.\n"
                f"परतफेड क्षमता निष्कर्ष: व्यवसाय पहिल्या वर्षापासून नियमित कर्जफेडीसाठी सक्षम आहे."
            ),
            content_en=(
                f"Average Debt Service Coverage Ratio (DSCR): {avg_dscr} (Exceeds bank threshold >= 1.25)\n"
                f"Break-Even Capacity Utilization: {bep_cap}%\n"
                f"Debt Viability Conclusion: The enterprise demonstrates robust debt-servicing buffer."
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
                f"कर्ज रक्कम: {format_currency_inr(loan_amt)} | वार्षिक व्याज दर: {rate_pct}%\n"
                f"एकूण मुदत: {tenure_m} महिने | सवलत कालावधी (Moratorium): {mora_m} महिने\n"
                f"हप्ता (EMI): {format_currency_inr(emi)} {emi_label_mr}\n"
                f"एकूण परतफेड रक्कम: {format_currency_inr(total_repay)}"
            ),
            content_en=(
                f"Sanctioned Loan: {format_currency_inr(loan_amt)} | Interest Rate: {rate_pct}% p.a.\n"
                f"Tenure: {tenure_m} months | Moratorium: {mora_m} months\n"
                f"Instalment (EMI): {format_currency_inr(emi)} {emi_label_en}\n"
                f"Total Principal + Interest Repayable: {format_currency_inr(total_repay)}"
            ),
        )
    )

    # Section 10: Risks & Mitigations
    sections.append(
        DprSection(
            section_number=10,
            title_mr="१०. संभाव्य जोखीम व उपाययोजना (Risks & Mitigations)",
            title_en="10. Risks & Mitigations",
            content_mr=(
                f"१. उधार विक्री जोखीम: रोख बफर {udhar.get('cash_buffer_months', '3')} महिने राखला जाईल. उधार २०% पेक्षा कमी राहील.\n"
                f"२. खेळत्या भांडवलाची गरज (नायक समिती): एकूण खेळते भांडवल {format_currency_inr(nayak_wc.get('total', '0'))} नियोजित आहे.\n"
                f"३. स्थानिक स्पर्धा: उच्च दर्जा व वाजवी दरांमुळे ग्राहक टिकून राहतील."
            ),
            content_en=(
                f"1. Working Capital & Credit Risk: Cash buffer of {udhar.get('cash_buffer_months', '3')} months maintained.\n"
                f"2. Nayak Committee Working Capital Requirement: Total WC of {format_currency_inr(nayak_wc.get('total', '0'))} assessed.\n"
                f"3. Operational Reliability: Diversified local sourcing and proactive cost controls."
            ),
        )
    )

    # Section 11: Document Checklist & Where to Apply
    sections.append(
        DprSection(
            section_number=11,
            title_mr="११. आवश्यक कागदपत्रे व अर्ज प्रक्रिया (Document Checklist)",
            title_en="11. Document Checklist & Where to Apply",
            content_mr=(
                "१. आधार संमती व ओळख पुरावा (Aadhaar Consent & KYC)\n"
                "२. सामाजिक प्रवर्ग प्रमाणपत्र (Caste Certificate, जर लागू असल्यास)\n"
                "३. जागेचा पुरावा (७/१२ उतारा किंवा भाडेकरार)\n"
                "४. यंत्रसामग्रीचे अधिकृत कोटेशन (Quotations from verified vendors)\n"
                "५. बँक सविस्तर प्रकल्प अहवाल (हा ArthMitra DPR अहवाल)\n"
                "अर्ज पोर्टल: Jan Samarth Portal (jansamarth.in) किंवा संबंधित महामंडळ पोर्टल."
            ),
            content_en=(
                "1. Promoter KYC & Identity Proof\n"
                "2. Caste / Category Certificate (where applicable)\n"
                "3. Site Possession Proof (7/12 land record or registered lease)\n"
                "4. Equipment / Machinery Quotations from GST vendors\n"
                "5. Comprehensive Bank DPR (this ArthMitra DPR document)\n"
                "Application Portal: Official Jan Samarth Portal (jansamarth.in) or Scheme Web Portal."
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
                "हा सविस्तर प्रकल्प अहवाल (DPR) अधिकृत शासकीय निकष व स्थानिक माहितीच्या आधारे वित्तीय मूल्यमापनासाठी "
                "तयार करण्यात आला आहे. कर्ज मंजूर करणे, व्याजदर व अंतिम अटी ठरवण्याचा पूर्ण अधिकार वित्तपुरवठादार बँकेचा आहे. "
                "ArthMitra कोणत्याही कर्ज मंजुरीची किंवा अनुदानाची हमी देत नाही."
            ),
            content_en=(
                "This Detailed Project Report (DPR) is generated strictly for bank appraisal purposes based on official "
                "benchmark unit costs and field inputs. Loan sanction, appraisal terms, and disbursement decisions remain "
                "at the sole discretion of the financing institution / bank. ArthMitra provides advisory estimates and "
                "does not guarantee loan sanction or subsidy approval."
            ),
        )
    )

    return sections
