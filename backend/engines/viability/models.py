"""
Data models and type definitions for Enterprise Viability Engine.
Strictly implements TECH_SPEC §5 with pure Decimal arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class ViabilityInput:
    business_code: str
    capex_total: Decimal
    annual_debt_service: list[Decimal]   # Principal + Interest due in Year 1..5
    annual_interest_due: list[Decimal]   # Interest portion due in Year 1..5
    calibration_overrides: dict[str, Any] = field(default_factory=dict)
    udhar_pct: Decimal = Decimal("0.20")  # Default 20%
    credit_months: Decimal = Decimal("2.0")
    moratorium_months: int = 6
    new_monthly_emi: Decimal = Decimal("0.00")
    existing_monthly_emi: Decimal = Decimal("0.00")
    household_monthly_income: Decimal | None = None


@dataclass
class YearlyProjection:
    year: int
    capacity_utilization: Decimal
    gross_revenue: Decimal
    variable_costs: Decimal
    fixed_costs: Decimal
    depreciation: Decimal
    interest_expense: Decimal
    profit_before_tax: Decimal
    tax: Decimal
    profit_after_tax: Decimal
    cash_accrual: Decimal  # PAT + Depreciation
    debt_service: Decimal
    dscr: Decimal


@dataclass
class ViabilityResult:
    business_code: str
    projections: list[YearlyProjection]
    average_dscr: Decimal
    dscr_target: Decimal
    dscr_passed: bool
    breakeven_revenue_yr1: Decimal
    breakeven_capacity_pct_yr1: Decimal
    nayak_total_wc: Decimal
    nayak_bank_finance: Decimal
    nayak_promoter_margin: Decimal
    udhar_extra_wc_needed: Decimal
    udhar_cash_buffer_months: Decimal
    income_timing_mismatch: bool
    recommended_reserve: Decimal
    seasonality_lowest_month_cash: Decimal
    seasonality_lowest_month_idx: int
    foir_pct: Decimal | None
    foir_passed: bool
    warnings: list[str] = field(default_factory=list)
