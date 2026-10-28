"""
Pydantic v2 schemas and validation models for Scheme Rule definitions.
Strictly implements TECH_SPEC §3.1.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class OperatorType(StrEnum):
    EQ = "eq"
    IN = "in"
    NOT_IN = "not_in"
    LTE = "lte"
    LT = "lt"
    GTE = "gte"
    GT = "gt"
    BETWEEN = "between"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    UNKNOWN_OK = "unknown_ok"


class EligibilityStatus(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    NEEDS_INFO = "NEEDS_INFO"
    CONFIRM_WITH_AGENCY = "CONFIRM_WITH_AGENCY"


class SchemeStatusType(StrEnum):
    VERIFIED = "verified"
    CONFLICT = "conflict"
    UNVERIFIED = "unverified"
    RETIRED = "retired"


class Condition(BaseModel):
    field: str
    op: OperatorType
    value: Any = None


class EligibilityRule(BaseModel):
    """A single eligibility rule.

    Either `field`/`op`/`value` (simple rule) or `any` (passes if ANY sub-condition passes).
    `when` makes the rule conditional: it is only checked if ALL `when` conditions hold.
    """

    field: str | None = None
    op: OperatorType | None = None
    value: Any = None
    any: list[Condition] | None = None
    when: list[Condition] | None = None
    reason: str


class SpecialCategoryConfig(BaseModel):
    """Who counts as 'special category' for this scheme (lower own share / higher subsidy)."""

    categories: list[str] = Field(default_factory=list)
    female: bool = False
    disability: bool = False


class TrancheConfig(BaseModel):
    """One loan tranche of a multi-lender package (e.g. bank 75% + corporation 20%)."""

    name: str
    share: Decimal
    interest: InterestConfig
    tenure_months: int
    moratorium_months: int = 0
    repayment_frequency_months: int = 1
    grant_amount: Decimal = Decimal("0")  # non-repayable part inside this tranche


class SourceMetadata(BaseModel):
    url: str
    date: str


class ChannelConfig(BaseModel):
    via: list[str]
    apply_at: str


class InterestConfig(BaseModel):
    type: str  # "fixed", "slab", "bank_rate"
    rate: Decimal | None = None
    slabs: list[dict[str, Any]] | None = None


class SubsidyRule(BaseModel):
    treatment: str  # "upfront", "fdr_3yr"
    adjust_month: int | None = 36
    # keys: general_urban, general_rural, special_urban, special_rural
    rate_by: dict[str, Decimal] | None = None
    cap: Decimal | None = None


class FinanceConfig(BaseModel):
    loan_share: Decimal
    loan_cap: Decimal | None = None
    min_own_share: Decimal
    min_own_share_special: Decimal | None = None
    # If true, loan = project - own share (subsidy sits inside the loan, e.g. PMEGP FDR)
    loan_share_is_remainder: bool = False
    max_project_cost: Decimal | None = None
    max_project_cost_by_sector: dict[str, Decimal] | None = None
    min_project_cost: Decimal | None = None
    tranches: list[TrancheConfig] | None = None
    bank_decides: list[str] = Field(default_factory=list)  # fields that are indicative only
    subsidy: SubsidyRule | None | None = None
    interest: InterestConfig
    tenure_months: int
    moratorium_months: int = 0
    moratorium_interest: str = "simple"
    moratorium_mode_default: str = "capitalise"
    repayment_frequency_months: int = 1


class SchemeTestVector(BaseModel):
    input: dict[str, Any]
    expect: dict[str, Any]


class SchemeDefinition(BaseModel):
    code: str
    name: dict[str, str]
    agency: str
    status: SchemeStatusType
    source: SourceMetadata
    channel: ChannelConfig
    notes: list[str] = Field(default_factory=list)  # shown to the agent with the package
    special: SpecialCategoryConfig | None = None
    capital_subsidy: bool = False
    eligibility: list[EligibilityRule] = Field(default_factory=list)
    negative_list: list[str] | None = Field(default_factory=list)
    finance: FinanceConfig
    documents: list[str] = Field(default_factory=list)
    tests: list[SchemeTestVector] | None = Field(default_factory=list)


class SchemeEvaluationResult(BaseModel):
    scheme_code: str
    status: EligibilityStatus
    reasons: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    warning_messages: list[str] = Field(default_factory=list)
    source_url: str
    source_date: str


TrancheConfig.model_rebuild()
