from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DprSection:
    section_number: int
    title_mr: str
    title_en: str
    content_mr: str
    content_en: str
    tables: list[dict[str, Any]] | None = None


@dataclass
class DprResult:
    """Output descriptor of generated DPR PDF."""
    file_path: str
    file_sha256: str
    language: str
    page_count: int
    section_count: int = 12
