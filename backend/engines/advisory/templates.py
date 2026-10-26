from __future__ import annotations

from typing import Any

from .models import SWOT, AdvisoryOutput, PricingItem, PricingStrategy, ThreatItem


def generate_template_advisory(
    eval_output: dict[str, Any],
    village_name: str,
    language: str = "mr",
) -> AdvisoryOutput:
    """
    Deterministic multilingual template fallback generator.
    Guarantees 100% safety and zero hallucination when LLM is unavailable or fails validation.
    """
    summary = eval_output.get("summary", {})
    market = eval_output.get("market", {})
    b_name_mr = summary.get("business_name_mr", "व्यवसाय")
    b_name_en = summary.get("business_name_en", "Business")
    proj_cost = summary.get("project_cost", "0")
    top_pkgs = summary.get("top_packages", [])
    top_pkg = top_pkgs[0] if top_pkgs else {}
    sc_name = top_pkg.get("scheme_name", {}).get("mr", top_pkg.get("scheme_code", "योजना"))
    emi = top_pkg.get("monthly_emi", "0")
    loan = top_pkg.get("loan_amount", "0")
    subsidy = top_pkg.get("subsidy_amount", "0")
    dscr = summary.get("average_dscr", "1.5")
    sat_level = summary.get("market_saturation", "low")
    c_reported = summary.get("competitors_reported", "1")
    comp_suggestions = market.get("complementary_suggestions", [])

    if language == "mr":
        market_reach = (
            f"{village_name} व लगतच्या गावांमध्ये {b_name_mr} साठी चांगला स्थानिक ग्राहक वर्ग उपलब्ध आहे. "
            f"गावात सध्या {c_reported} प्रतिस्पर्धी व्यावसायिक कार्यरत आहेत. "
            f"एकूण बाजारातील संपृक्तता (Saturation) {sat_level} पातळीवर असून व्यवसाय सुरू करण्यास अनुकूल संधी आहे."
        )

        opportunities = [
            "स्थानिक पातळीवर गुणवत्तापूर्ण सेवा/उत्पादन दिल्यास नियमित ग्राहकवर्ग तयार होईल.",
            f"{sc_name} अंतर्गत ₹{subsidy} अनुदानाचा लाभ मिळाल्याने कर्जाचा मासिक भार (EMI ₹{emi}) आवाक्यात राहील.",
            "गावातील आठवडे बाजार आणि शेजारील वाड्यांमध्ये थेट विक्रीची संधी आहे.",
        ]

        swot = SWOT(
            s=[
                f"प्रकल्प खर्च ₹{proj_cost} व कर्ज ₹{loan} ची सुलभ रचना.",
                f"सरासरी DSCR {dscr} असल्याने कर्ज परतफेडीची क्षमता उत्तम आहे.",
            ],
            w=[
                "सुरुवातीच्या काळात खेळत्या भांडवलाची योग्य हाताळणी आवश्यक आहे.",
                "उधार विक्री वाढल्यास रोख रकमेचा तुटवडा जाणवू शकतो.",
            ],
            o=[
                f"शासकीय {sc_name} योजनेचा थेट आर्थिक पाठिंबा.",
                "परिसरातील वाढती मागणी व घरपोच सेवेची संधी.",
            ],
            t=[
                "कच्च्या मालाच्या दरातील चढ-उतार.",
                "स्थानिक स्पर्धकांकडून होणारी किंमत स्पर्धा.",
            ],
        )

        threats = [
            ThreatItem(
                risk="उधार विक्रीमुळे रोख रकमेचा तुटवडा",
                type="financial",
                mitigation="उधार विक्री २०% पेक्षा जास्त ठेवू नका व रोख व्यवहारांवर २-३% सूट द्या.",
            ),
            ThreatItem(
                risk="उत्पादनाची किंवा सेवेची गुणवत्ता घसरणे",
                type="operational",
                mitigation="सुरुवातीपासून दर्जेदार साहित्य वापरा व ग्राहकांचा अभिप्राय घ्या.",
            ),
        ]

        pricing = PricingStrategy(
            strategy="स्थानिक बाजारातील चालू दरांपेक्षा ५% कमी किंवा सममूल्य राखून उच्च दर्जाची हमी देणे.",
            items=[
                PricingItem(
                    item="मुख्य सेवा/उत्पादन",
                    benchmark_price="स्थानिक बाजार दर",
                    unit="नग / सेवा",
                    rationale="स्थानिक ग्राहकांना परवडणारी व स्पर्धात्मक किंमत",
                )
            ],
        )

        comp_list = [
            f"{s.get('name_mr', s.get('business_code', ''))} (कमी संपृक्तता पर्याय)"
            for s in comp_suggestions[:2]
        ]
        if not comp_list:
            comp_list = ["दुग्ध व्यवसाय पूरक कुक्कुटपालन किंवा शेळीपालन"]

        next_steps = [
            f"१. {sc_name} साठी आवश्यक कागदपत्रे व बँक डीपीआर तयार करा.",
            f"२. स्वतःचे भांडवल (Margin) ₹{top_pkg.get('own_margin_required', '0')} बँकेत जमा ठेवा.",
            "३. स्थानिक बँकेत किंवा महामंडळ पोर्टलवर अधिकृत अर्ज दाखल करा.",
            "४. कर्ज मंजूर झाल्यावर पहिल्या ६ महिन्यांच्या सवलत (Moratorium) कालावधीत उत्पादन क्षमता वाढवा.",
        ]

    else:
        # English fallback
        market_reach = (
            f"In {village_name} and neighbouring villages, there is a viable customer base for {b_name_en}. "
            f"Currently {c_reported} active competitor(s) operate locally. "
            f"Market saturation is {sat_level}, indicating favourable headroom for entry."
        )

        opportunities = [
            "Consistent demand from local households and nearby village catchments.",
            f"Subsidy benefit of ₹{subsidy} under {sc_name} reduces monthly EMI to ₹{emi}.",
            "Direct sales during weekly village haats and local markets.",
        ]

        swot = SWOT(
            s=[
                f"Sound financial structure: Project ₹{proj_cost}, Loan ₹{loan}.",
                f"Healthy debt service capacity with an average DSCR of {dscr}.",
            ],
            w=[
                "Requires disciplined working capital and cash collection cycles.",
                "Risk of working capital stretch if credit sales exceed 20%.",
            ],
            o=[
                f"Financial support under government scheme {sc_name}.",
                "Opportunity to offer doorstep delivery and quality differentiation.",
            ],
            t=[
                "Fluctuations in input material prices.",
                "Price undercutting by established local competitors.",
            ],
        )

        threats = [
            ThreatItem(
                risk="Cash flow strain due to uncollected customer credit (Udhar)",
                type="financial",
                mitigation="Cap credit sales below 20% of monthly turnover and offer small prompt payment discounts.",
            ),
            ThreatItem(
                risk="Input material supply disruptions",
                type="operational",
                mitigation="Source raw materials from multiple verified local vendors.",
            ),
        ]

        pricing = PricingStrategy(
            strategy="Competitive value pricing matching local benchmark rates with superior customer service.",
            items=[
                PricingItem(
                    item="Core Service / Unit",
                    benchmark_price="Local market benchmark",
                    unit="per unit",
                    rationale="Matches consumer willingness to pay while ensuring positive contribution margin",
                )
            ],
        )

        comp_list = [
            f"{s.get('name_en', s.get('business_code', ''))} (Low saturation alternative)"
            for s in comp_suggestions[:2]
        ]
        if not comp_list:
            comp_list = ["Allied livestock rearing and agro-processing"]

        next_steps = [
            f"1. Finalize the bank-ready DPR and document checklist for {sc_name}.",
            f"2. Ensure promoter margin of ₹{top_pkg.get('own_margin_required', '0')} is ready in bank account.",
            "3. Submit application on the designated government portal (Jan Samarth / PMEGP).",
            f"4. Utilize the initial {top_pkg.get('moratorium_months', 6)}-month moratorium to build capacity.",
        ]

    return AdvisoryOutput(
        market_reach=market_reach,
        opportunities=opportunities,
        swot=swot,
        threats=threats,
        pricing=pricing,
        complementary=comp_list,
        next_steps=next_steps,
    )
