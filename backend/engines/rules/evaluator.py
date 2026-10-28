"""
Rule Evaluator for Schemes.
Strictly implements TECH_SPEC §3.2.
"""

from __future__ import annotations

from typing import Any

from .models import (
    Condition,
    EligibilityRule,
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


def is_special_for_scheme(scheme: SchemeDefinition, facts: dict[str, Any]) -> bool:
    """Whether the applicant counts as 'special category' under this scheme's own definition."""
    sp = scheme.special
    if sp is None:
        return False
    if facts.get("category") in sp.categories:
        return True
    if sp.female and facts.get("gender") == "female":
        return True
    if sp.disability and bool(facts.get("disability_40")):
        return True
    return False


_MISSING = object()


def _check_condition(cond: Condition | EligibilityRule, facts: dict[str, Any]) -> bool | object:
    """True/False, or _MISSING when the fact is unknown (and the op is not unknown_ok)."""
    assert cond.field is not None and cond.op is not None
    val = facts.get(cond.field)
    if val is None and cond.op != OperatorType.UNKNOWN_OK:
        return _MISSING
    return evaluate_operator(val, cond.op, cond.value)


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
    is_capital_subsidy_scheme = scheme.capital_subsidy
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

    # 4. Evaluate individual eligibility rules (scheme-specific 'special' flag injected first)
    facts = {**facts, "is_special": is_special_for_scheme(scheme, facts)}
    for rule in scheme.eligibility:
        # Conditional rule: skip unless every `when` condition holds
        if rule.when:
            when_results = [_check_condition(c, facts) for c in rule.when]
            if any(r is _MISSING for r in when_results):
                missing_fields.extend(c.field for c, r in zip(rule.when, when_results, strict=True) if r is _MISSING)
                continue
            if not all(when_results):
                continue

        if rule.any:
            results = [_check_condition(c, facts) for c in rule.any]
            if any(r is True for r in results):
                continue
            if any(r is _MISSING for r in results):
                missing_fields.extend(c.field for c, r in zip(rule.any, results, strict=True) if r is _MISSING)
                continue
            reasons.append(rule.reason)
            continue

        result = _check_condition(rule, facts)
        if result is _MISSING:
            missing_fields.append(rule.field or "?")
        elif not result:
            reasons.append(rule.reason)

    # 5. Determine overall eligibility status
    if reasons:
        status = EligibilityStatus.NOT_ELIGIBLE
    elif missing_fields:
        status = EligibilityStatus.NEEDS_INFO
    elif scheme.status != SchemeStatusType.VERIFIED:
        # Status conflict or unverified stubs must be flagged for agency confirmation
        status = EligibilityStatus.CONFIRM_WITH_AGENCY
    else:
        status = EligibilityStatus.ELIGIBLE

    return SchemeEvaluationResult(
        scheme_code=scheme.code,
        status=status,
        reasons=reasons,
        missing_fields=sorted(set(missing_fields)),
        warning_messages=warnings,
        source_url=scheme.source.url,
        source_date=scheme.source.date,
    )
