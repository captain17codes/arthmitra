"""
Stacking and combination validation engine.
Enforces non-negotiable rule: NEVER two capital subsidies on the same asset.
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

CAPITAL_SUBSIDY_SCHEMES: set[str] = {
    "PMEGP",
    "CMEGP",
    "MPBCDC_SEED",
    "PMFME",
}


def load_stacking_rules(config_path: Path | None = None) -> dict:
    """Load stacking rules from YAML configuration."""
    if config_path is None:
        config_path = Path(__file__).resolve().parents[3] / "data" / "schemes" / "stacking.yaml"
    if not config_path.exists():
        return {
            "capital_subsidy_schemes": list(CAPITAL_SUBSIDY_SCHEMES),
            "allowed_combinations": [],
        }
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_stacking(scheme_codes: list[str]) -> tuple[bool, str | None]:
    """
    Validate whether a combination of schemes can legally be packaged together.
    Returns (is_valid, error_reason).
    """
    if not scheme_codes:
        return True, None

    # Invariant: Count capital subsidy schemes in the candidate package
    cap_subsidies_present = [c for c in scheme_codes if c in CAPITAL_SUBSIDY_SCHEMES]
    if len(cap_subsidies_present) > 1:
        return False, f"Cannot stack multiple capital subsidies ({', '.join(cap_subsidies_present)}) on the same asset."

    return True, None
