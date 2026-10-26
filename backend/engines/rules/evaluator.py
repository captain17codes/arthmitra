"""
Rule Evaluator for Schemes.
Strictly implements TECH_SPEC §3.2.
"""

from __future__ import annotations

from typing import Any

from .models import (
    EligibilityStatus,
    OperatorType,
    SchemeDefinition,
    SchemeEvaluationResult,
    SchemeStatusType,
)


def evaluate_operator(fact_val: Any, op: OperatorType, rule_val: Any) -> bool:
    """Evaluate a single rule operator against a fact value."""
    if op == OperatorType.UNKNOWN_OK:
        if fact_val is None or fact_val == "unknown":
            return True
        return bool(fact_val == rule_val)

    if fact_val is None:
        return False

    if op == OperatorType.EQ:
        return bool(fact_val == rule_val)
    elif op == OperatorType.IN:
        return bool(fact_val in rule_val)
    elif op == OperatorType.NOT_IN:
        return bool(fact_val not in rule_val)
    elif op == OperatorType.LTE:
        return bool(fact_val <= rule_val)
    elif op == OperatorType.LT:
        return bool(fact_val < rule_val)
    elif op == OperatorType.GTE:
        return bool(fact_val >= rule_val)
    elif op == OperatorType.GT:
        return bool(fact_val > rule_val)
    elif op == OperatorType.BETWEEN:
        return bool(rule_val[0] <= fact_val <= rule_val[1])
    elif op == OperatorType.IS_TRUE:
        return bool(fact_val) is True
    elif op == OperatorType.IS_FALSE:
        return bool(fact_val) is False
    return False


def evaluate_scheme(scheme: SchemeDefinition, facts: dict[str, Any]) -> SchemeEvaluationResult:
    """
    Evaluate eligibility of a beneficiary / case against a single scheme definition.
    Follows TECH_SPEC §3.2 evaluation procedure.
    """
    reasons: list[str] = []
    missing_fields: list[str] = []
    warnings: list[str] = []

    # 1. Pre-screen gate: Negative list
    business_type = facts.get("business_type")
    if business_type and scheme.negative_list and business_type in scheme.negative_list:
        return SchemeEvaluationResult(
            scheme_code=scheme.code,
            status=EligibilityStatus.NOT_ELIGIBLE,
            reasons=["business_in_negative_list"],
            source_url=scheme.source.url,
            source_date=scheme.source.date,
        )

    # 2. Pre-screen gate: Prior subsidy exclusion for capital subsidy schemes
    prior_subsidy = facts.get("prior_subsidy")
    is_capital_subsidy_scheme = scheme.code in {"PMEGP", "CMEGP", "MPBCDC_SEED"}
    if prior_subsidy == "yes" and is_capital_subsidy_scheme:
        return SchemeEvaluationResult(
            scheme_code=scheme.code,
            status=EligibilityStatus.NOT_ELIGIBLE,
            reasons=["prior_subsidy_ineligible"],
            source_url=scheme.source.url,
            source_date=scheme.source.date,
        )

    # 3. Pre-screen gate: Credit default warning
    credit_default = facts.get("credit_default")
    if credit_default == "yes":
        warnings.append("credit_default_bank_risk")

    # 4. Evaluate individual eligibility rules
    for rule in scheme.eligibility:
        field_name = rule.field
        if field_name not in facts:
            if rule.op != OperatorType.UNKNOWN_OK:
                missing_fields.append(field_name)
            continue

        fact_val = facts[field_name]
        if fact_val is None and rule.op != OperatorType.UNKNOWN_OK:
            missing_fields.append(field_name)
            continue

        passes = evaluate_operator(fact_val, rule.op, rule.value)
        if not passes:
            reasons.append(rule.reason)

    # 5. Determine overall eligibility status
    if missing_fields:
        status = EligibilityStatus.NEEDS_INFO
    elif reasons:
        status = EligibilityStatus.NOT_ELIGIBLE
    elif scheme.status != SchemeStatusType.VERIFIED:
        # Status conflict or unverified stubs must be flagged for agency confirmation
        status = EligibilityStatus.CONFIRM_WITH_AGENCY
    else:
        status = EligibilityStatus.ELIGIBLE

    return SchemeEvaluationResult(
        scheme_code=scheme.code,
        status=status,
        reasons=reasons,
        missing_fields=missing_fields,
        warning_messages=warnings,
        source_url=scheme.source.url,
        source_date=scheme.source.date,
    )
