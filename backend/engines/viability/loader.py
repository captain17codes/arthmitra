"""
Benchmark YAML Loader for Enterprise Viability.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


def load_benchmark(business_code: str, benchmarks_dir: Path | None = None) -> dict[str, Any]:
    """Load benchmark configuration for a given enterprise."""
    if benchmarks_dir is None:
        benchmarks_dir = Path(__file__).resolve().parents[3] / "data" / "benchmarks"

    file_path = benchmarks_dir / f"{business_code}.yaml"
    if not file_path.exists():
        raise FileNotFoundError(f"Benchmark file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_all_benchmarks(benchmarks_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load all benchmark files."""
    if benchmarks_dir is None:
        benchmarks_dir = Path(__file__).resolve().parents[3] / "data" / "benchmarks"

    benchmarks: dict[str, dict[str, Any]] = {}
    if not benchmarks_dir.exists():
        return benchmarks

    for yaml_path in sorted(benchmarks_dir.glob("*.yaml")):
        code = yaml_path.stem
        with open(yaml_path, encoding="utf-8") as f:
            benchmarks[code] = yaml.safe_load(f) or {}

    return benchmarks
