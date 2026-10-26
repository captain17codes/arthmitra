from __future__ import annotations

import re
from typing import Any

# Devanagari numeral translation table
DEV_TO_ARABIC = str.maketrans("०१२३४५६७८९", "0123456789")

# Regex to match currency, percentages, integers, and floats with Indian formatting (e.g. ₹1,50,000.50 or 25%)
NUMBER_PATTERN = re.compile(
    r"(?:[₹₹]|Rs\.?|INR\s*)?([0-9०-९]{1,3}(?:[,][0-9०-९]{2,3})*(?:\.[0-9०-९]+)?|[0-9०-९]+(?:\.[0-9०-९]+)?)"
)


def extract_text_strings(obj: Any) -> list[str]:
    """Recursively extract all string values from an arbitrary JSON-like dictionary or list."""
    strings: list[str] = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for val in obj.values():
            strings.extend(extract_text_strings(val))
    elif isinstance(obj, list):
        for item in obj:
            strings.extend(extract_text_strings(item))
    return strings


def extract_numbers_from_text(text: str) -> list[float]:
    """Extract all numbers from text after normalising Indian commas and Devanagari digits."""
    cleaned_text = text.translate(DEV_TO_ARABIC)
    found_numbers: list[float] = []

    for match in NUMBER_PATTERN.finditer(cleaned_text):
        raw_num = match.group(1).replace(",", "").strip()
        if not raw_num:
            continue
        try:
            val = float(raw_num)
            found_numbers.append(val)
        except ValueError:
            continue

    return found_numbers


def validate_advisory_numbers(
    advisory_data: dict[str, Any],
    allowed_numbers: list[float],
    tolerance: float = 0.05,
) -> tuple[bool, list[float]]:
    """
    Validate that every single number mentioned in generated advisory text
    originates from the pre-computed engine evaluation facts.
    Strictly implements TECH_SPEC §7.1 safety invariant against LLM hallucination.
    """
    # Allowed numbers set + derived representations (e.g. 0.35 as 35, 1.5 Lakh as 1.5 and 150000)
    allowed_set: set[float] = set()
    for a in allowed_numbers:
        allowed_set.add(round(a, 2))
        allowed_set.add(round(a, 0))
        # If ratio e.g. 0.35, also allow percentage 35.0
        if 0 < a <= 1.0:
            allowed_set.add(round(a * 100.0, 2))
            allowed_set.add(round(a * 100.0, 0))
        # If Lakhs e.g. 150000, also allow 1.5
        if a >= 100000.0:
            allowed_set.add(round(a / 100000.0, 2))
            allowed_set.add(round(a / 100000.0, 1))

    # Also allow standard structural numbers: years, months (1..12), 100, 0
    allowed_set.update({0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 2011.0, 2026.0, 100.0})

    text_strings = extract_text_strings(advisory_data)
    unauthorized_numbers: list[float] = []

    for s in text_strings:
        nums = extract_numbers_from_text(s)
        for n in nums:
            # Check if n matches any allowed number within tolerance
            matched = any(abs(n - allowed) <= tolerance for allowed in allowed_set)
            if not matched:
                unauthorized_numbers.append(n)

    is_valid = len(unauthorized_numbers) == 0
    return is_valid, unauthorized_numbers
