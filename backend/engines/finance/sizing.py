"""
Project and Loan Sizing Engine per TECH_SPEC §3.3.
Pure Python deterministic logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from .amortization import round_curr


@dataclass
class SizingResult:
    project_cost: Decimal
    own_margin_required: Decimal
    own_margin_available: Decimal
    margin_shortfall: Decimal
    loan_amount: Decimal
    subsidy_amount: Decimal
    is_capped: bool
    warnings: list[str] = field(default_factory=list)


def size_project_and_loan(
    margin_available: Decimal,
    min_own_share: Decimal,
    loan_share: Decimal,
    max_project_cost: Decimal | None = None,
    loan_cap: Decimal | None = None,
    target_project_cost: Decimal | None = None,
    upfront_subsidy_share: Decimal = Decimal("0.00"),
    min_viable_cost: Decimal | None = None,
    max_viable_cost: Decimal | None = None,
    business_name: str | None = None,
) -> SizingResult:
    """
    Determine the project cost and required loan/margin breakdown.
    Supports both margin-driven sizing and user target-driven sizing.
    """
    warnings: list[str] = []
    is_capped = False

    if target_project_cost is not None and target_project_cost > Decimal("0"):
        # User specified target project cost
        project_cost = target_project_cost
        if max_project_cost and project_cost > max_project_cost:
            project_cost = max_project_cost
            is_capped = True
            warnings.append(f"Target project cost exceeds scheme maximum ₹{max_project_cost:,.2f}.")

        required_margin = round_curr(project_cost * min_own_share)
        shortfall = Decimal("0.00")
        if margin_available < required_margin:
            shortfall = required_margin - margin_available
            warnings.append(
                f"Available margin ₹{margin_available:,.2f} is short of required {min_own_share * 100:.1f}% "
                f"(₹{required_margin:,.2f}) by ₹{shortfall:,.2f}."
            )

        potential_loan = round_curr(project_cost * loan_share)
        if loan_cap and potential_loan > loan_cap:
            loan_amount = loan_cap
            is_capped = True
            warnings.append(f"Loan amount capped at scheme limit ₹{loan_cap:,.2f}.")
        else:
            loan_amount = potential_loan

        subsidy_amount = round_curr(project_cost * upfront_subsidy_share)
    else:
        # User specified margin only -> maximize project cost within scheme limits
        if min_own_share <= Decimal("0"):
            raise ValueError("min_own_share must be strictly positive for margin-driven sizing.")

        max_from_margin = round_curr(margin_available / min_own_share)

        if max_project_cost and max_from_margin > max_project_cost:
            candidate_project = max_project_cost
            is_capped = True
            warnings.append(
                f"Project cost capped at scheme maximum of ₹{max_project_cost:,.2f}."
            )
        else:
            candidate_project = max_from_margin

        # Apply loan cap
        potential_loan = round_curr(candidate_project * loan_share)
        if loan_cap and potential_loan > loan_cap:
            loan_amount = loan_cap
            is_capped = True
            warnings.append(f"Loan amount capped at scheme limit ₹{loan_cap:,.2f}.")
            # project = margin_used + loan + subsidy_upfront (TECH_SPEC §3.3)
            # margin_used cannot exceed available margin or (candidate_project - loan)
            margin_used = min(margin_available, candidate_project - loan_amount)
            project_cost = margin_used + loan_amount
            required_margin = margin_used
            if margin_available > margin_used:
                excess = margin_available - margin_used
                warnings.append(
                    f"Available margin of ₹{margin_available:,.2f} exceeds required margin ₹{margin_used:,.2f} by ₹{excess:,.2f}."
                )
        else:
            loan_amount = potential_loan
            required_margin = margin_available
            project_cost = candidate_project

        shortfall = Decimal("0.00")
        subsidy_amount = round_curr(project_cost * upfront_subsidy_share)

    # Benchmark Viable Range check
    if min_viable_cost and project_cost < min_viable_cost:
        b_label = business_name or "this enterprise"
        warnings.append(
            f"₹{project_cost:,.0f} is lower than typical viable investment for {b_label} (minimum ₹{min_viable_cost:,.0f})."
        )
    elif max_viable_cost and project_cost > max_viable_cost:
        b_label = business_name or "this enterprise"
        warnings.append(
            f"₹{project_cost:,.0f} is higher than standard scale for {b_label} (typical maximum ₹{max_viable_cost:,.0f}). "
            "Consider scaling operations or right-sizing the project cost."
        )

    return SizingResult(
        project_cost=project_cost,
        own_margin_required=required_margin,
        own_margin_available=margin_available,
        margin_shortfall=shortfall,
        loan_amount=loan_amount,
        subsidy_amount=subsidy_amount,
        is_capped=is_capped,
        warnings=warnings,
    )
