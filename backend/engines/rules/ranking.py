"""
Deterministic Ranking Engine for financing packages.
Strictly implements TECH_SPEC §3.2 (Step 5).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

# Default channel reliability weights (higher is better)
CHANNEL_RELIABILITY_SCORES: dict[str, float] = {
    "SCA": 0.65,
    "PSB": 0.85,
    "RRB": 0.80,
    "Banks": 0.85,
    "Commercial Banks": 0.85,
    "Scheduled Commercial Banks": 0.85,
    "MFIs": 0.70,
}


@dataclass
class RankedPackage:
    scheme_code: str
    scheme_name: dict[str, str]
    project_cost: Decimal
    own_margin_required: Decimal
    own_margin_available: Decimal
    loan_amount: Decimal
    subsidy_amount: Decimal
    annual_rate: Decimal
    tenure_months: int
    moratorium_months: int
    emi: Decimal
    total_repayment: Decimal
    net_cost_to_beneficiary: Decimal  # total interest - subsidy
    channel_reliability_score: float
    is_affordable: bool               # own_margin_required <= own_margin_available
    rank: int = 0
    why_not_selected: str | None = None


def rank_packages(
    candidate_packages: list[RankedPackage],
    top_n: int = 3,
) -> tuple[list[RankedPackage], list[RankedPackage]]:
    """
    Deterministically rank financing packages according to TECH_SPEC §3.2:
      1. Affordability: own money required <= available (higher priority)
      2. Lowest net cost to beneficiary: (interest - subsidy) over tenure
      3. Lower EMI
      4. Higher channel reliability score
    Returns (top_n_packages, remaining_packages_with_reasons).
    """
    if not candidate_packages:
        return [], []

    def sort_key(pkg: RankedPackage) -> tuple:
        # We sort ascending:
        # - not is_affordable (0 if affordable, 1 if not)
        # - net_cost_to_beneficiary (lower is better)
        # - emi (lower is better)
        # - -channel_reliability_score (higher is better, so negate)
        return (
            0 if pkg.is_affordable else 1,
            pkg.net_cost_to_beneficiary,
            pkg.emi,
            -pkg.channel_reliability_score,
        )

    sorted_pkgs = sorted(candidate_packages, key=sort_key)

    top_packages: list[RankedPackage] = []
    remaining_packages: list[RankedPackage] = []

    for idx, pkg in enumerate(sorted_pkgs):
        pkg.rank = idx + 1
        if idx < top_n:
            top_packages.append(pkg)
        else:
            if not pkg.is_affordable:
                pkg.why_not_selected = "Requires higher own margin than currently available."
            elif pkg.net_cost_to_beneficiary > sorted_pkgs[0].net_cost_to_beneficiary:
                pkg.why_not_selected = "Higher net cost over loan tenure compared to top packages."
            else:
                pkg.why_not_selected = "Lower overall cost-efficiency compared to top ranked options."
            remaining_packages.append(pkg)

    return top_packages, remaining_packages
