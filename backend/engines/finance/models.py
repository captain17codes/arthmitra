"""
Type definitions and data models for the Finance Engine.
All monetary calculations strictly use Decimal arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum, StrEnum


class MoratoriumMode(StrEnum):
    CAPITALISE = "capitalise"
    PAY = "pay"


class RepaymentFrequency(int, Enum):
    MONTHLY = 1
    QUARTERLY = 3


class SubsidyTreatment(StrEnum):
    UPFRONT = "upfront"
    FDR_3YR = "fdr_3yr"


class InterestType(StrEnum):
    FIXED = "fixed"
    SLAB = "slab"
    BANK_RATE = "bank_rate"


@dataclass(frozen=True)
class InterestSlab:
    upto: Decimal | None  # None indicates above previous slab
    rate: Decimal            # Annual rate, e.g. Decimal("0.08") for 8%


@dataclass(frozen=True)
class SubsidyConfig:
    amount: Decimal
    treatment: SubsidyTreatment = SubsidyTreatment.UPFRONT
    adjust_month: int = 36


@dataclass
class FinanceInput:
    principal: Decimal
    annual_rate: Decimal
    tenure_months: int
    moratorium_months: int = 0
    frequency_months: int = 1
    moratorium_mode: MoratoriumMode = MoratoriumMode.CAPITALISE
    subsidy: SubsidyConfig | None = None
    rate_slabs: list[InterestSlab] | None = None


@dataclass
class ScheduleRow:
    period: int
    due_month: int
    opening_balance: Decimal
    interest_payment: Decimal
    principal_payment: Decimal
    total_payment: Decimal
    closing_balance: Decimal
    is_moratorium: bool = False
    subsidy_credit: Decimal = Decimal("0.00")


@dataclass
class FinanceResult:
    principal: Decimal
    financed_principal: Decimal
    moratorium_interest: Decimal
    initial_emi: Decimal
    subsequent_emi: Decimal | None
    num_instalments: int
    total_principal_paid: Decimal
    total_interest_paid: Decimal
    total_amount_paid: Decimal
    effective_annual_cost: Decimal
    schedule: list[ScheduleRow] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
