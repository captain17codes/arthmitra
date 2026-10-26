"""
Scheme Definition YAML Loader and Validator.
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from .models import SchemeDefinition


def load_scheme_from_yaml(file_path: Path) -> SchemeDefinition:
    """Load and validate a single scheme YAML definition."""
    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SchemeDefinition.model_validate(data)


def load_all_schemes(schemes_dir: Path | None = None) -> dict[str, SchemeDefinition]:
    """
    Load all scheme definitions from data/schemes/*.yaml.
    Excludes configuration files such as stacking.yaml.
    """
    if schemes_dir is None:
        schemes_dir = Path(__file__).resolve().parents[3] / "data" / "schemes"

    schemes: dict[str, SchemeDefinition] = {}
    if not schemes_dir.exists():
        return schemes

    for yaml_path in sorted(schemes_dir.glob("*.yaml")):
        if yaml_path.name in {"stacking.yaml", "config.yaml"}:
            continue
        scheme = load_scheme_from_yaml(yaml_path)
        schemes[scheme.code] = scheme

    return schemes
