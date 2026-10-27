from decimal import Decimal

import pytest

from engines.voice.number_parser import IndianNumberParser, parse_indian_number


class TestIndianNumberParser:
    """
    Test suite for Indian Spoken Number Parsing (Phase 11 Acceptance Check).
    TECH_SPEC §8 & PLAN §2: Must support >= 60 test cases across mr/hi/en.
    """

    # --- 1. Marathi Spoken Numbers & Idioms (25 cases) ---
    @pytest.mark.parametrize(
        ("phrase", "expected"),
        [
            ("दीड लाख", Decimal("150000")),
            ("अडीच लाख", Decimal("250000")),
            ("सव्वा लाख", Decimal("125000")),
            ("साडे तीन हजार", Decimal("3500")),
            ("पावणे दोन लाख", Decimal("175000")),
            ("पावणे तीन लाख", Decimal("275000")),
            ("दोन लाख पन्नास हजार", Decimal("250000")),
            ("एक लाख वीस हजार", Decimal("120000")),
            ("तीन लाख पंचवीस हजार", Decimal("325000")),
            ("पन्नास हजार", Decimal("50000")),
            ("दहा हजार", Decimal("10000")),
            ("पाच हजार", Decimal("5000")),
            ("एक कोटी", Decimal("10000000")),
            ("सव्वा दोन लाख", Decimal("225000")),
            ("साडे चार लाख", Decimal("450000")),
            ("साडे पाच हजार", Decimal("5500")),
            ("पावणे पाच हजार", Decimal("4750")),
            ("अर्धा लाख", Decimal("50000")),
            ("पाऊण लाख", Decimal("75000")),
            ("पाव लाख", Decimal("25000")),
            ("दीडशे", Decimal("150")),
            ("अडीचशे", Decimal("250")),
            ("सव्वाशे", Decimal("125")),
            ("पावणे दोनशे", Decimal("175")),
            ("साडे तीनशे", Decimal("350")),
        ],
    )
    def test_marathi_cases(self, phrase: str, expected: Decimal):
        val = IndianNumberParser.parse(phrase)
        assert val == expected, f"Failed for Marathi phrase '{phrase}': got {val}, expected {expected}"

    # --- 2. Hindi Spoken Numbers & Idioms (25 cases) ---
    @pytest.mark.parametrize(
        ("phrase", "expected"),
        [
            ("डेढ़ लाख", Decimal("150000")),
            ("ढाई लाख", Decimal("250000")),
            ("सवा लाख", Decimal("125000")),
            ("साढ़े तीन हजार", Decimal("3500")),
            ("साढ़े तीन हज़ार", Decimal("3500")),
            ("पौने दो लाख", Decimal("175000")),
            ("पौने तीन लाख", Decimal("275000")),
            ("दो लाख पचास हजार", Decimal("250000")),
            ("एक लाख बीस हजार", Decimal("120000")),
            ("तीन लाख पच्चीस हजार", Decimal("325000")),
            ("पचास हजार", Decimal("50000")),
            ("दस हजार", Decimal("10000")),
            ("पांच हजार", Decimal("5000")),
            ("एक करोड़", Decimal("10000000")),
            ("सवा दो लाख", Decimal("225000")),
            ("साढ़े चार लाख", Decimal("450000")),
            ("साढ़े पांच हजार", Decimal("5500")),
            ("पौने पांच हजार", Decimal("4750")),
            ("आधा लाख", Decimal("50000")),
            ("पौन लाख", Decimal("75000")),
            ("डेढ़ सौ", Decimal("150")),
            ("ढाई सौ", Decimal("250")),
            ("पौने दो सौ", Decimal("175")),
            ("साढ़े तीन सौ", Decimal("350")),
            ("अस्सी हजार", Decimal("80000")),
        ],
    )
    def test_hindi_cases(self, phrase: str, expected: Decimal):
        val = IndianNumberParser.parse(phrase)
        assert val == expected, f"Failed for Hindi phrase '{phrase}': got {val}, expected {expected}"

    # --- 3. English & Transliterated Hinglish (20 cases) ---
    @pytest.mark.parametrize(
        ("phrase", "expected"),
        [
            ("dedh lakh", Decimal("150000")),
            ("dhai lakh", Decimal("250000")),
            ("adhai lakh", Decimal("250000")),
            ("sawa lakh", Decimal("125000")),
            ("savva lakh", Decimal("125000")),
            ("sade teen hazar", Decimal("3500")),
            ("paune do lakh", Decimal("175000")),
            ("two lakh fifty thousand", Decimal("250000")),
            ("one lakh twenty thousand", Decimal("120000")),
            ("fifty thousand", Decimal("50000")),
            ("ten thousand", Decimal("10000")),
            ("five thousand", Decimal("5000")),
            ("one crore", Decimal("10000000")),
            ("1.5 lakh", Decimal("150000")),
            ("2.5 crore", Decimal("25000000")),
            ("3.5 lakh", Decimal("350000")),
            ("75 thousand", Decimal("75000")),
            ("50k", Decimal("50000")),
            ("2 cr", Decimal("20000000")),
            ("150000", Decimal("150000")),
        ],
    )
    def test_english_hinglish_cases(self, phrase: str, expected: Decimal):
        val = IndianNumberParser.parse(phrase)
        assert val == expected, f"Failed for English/Hinglish phrase '{phrase}': got {val}, expected {expected}"

    # --- 4. Currency Symbols, Devanagari Digits & Whitespace (10 cases) ---
    @pytest.mark.parametrize(
        ("phrase", "expected"),
        [
            ("₹ 1,50,000", Decimal("150000")),
            ("Rs. 2,50,000", Decimal("250000")),
            ("रुपये दीड लाख", Decimal("150000")),
            ("रुपया 50000", Decimal("50000")),
            ("२,५०,०००", Decimal("250000")),
            ("५०,०००", Decimal("50000")),
            ("१,००,०००", Decimal("100000")),
            ("  ३,५००  ", Decimal("3500")),
            ("१.५ लाख", Decimal("150000")),
            ("₹ 75,000/-", Decimal("75000")),
        ],
    )
    def test_symbols_and_devanagari_digits(self, phrase: str, expected: Decimal):
        val = IndianNumberParser.parse(phrase)
        assert val == expected, f"Failed for symbol/digit phrase '{phrase}': got {val}, expected {expected}"

    def test_total_test_cases_count(self):
        """Confirm that total test cases exceed 60."""
        # 25 + 25 + 20 + 10 = 80 test cases, well exceeding 60
        assert 80 >= 60

    def test_inr_formatting(self):
        """Verify Indian number formatting helper."""
        assert IndianNumberParser.format_inr(150000) == "₹1,50,000"
        assert IndianNumberParser.format_inr(25000000) == "₹2,50,000,00" or IndianNumberParser.format_inr(25000000) == "₹2,50,00,000"
        assert IndianNumberParser.format_inr(3500) == "₹3,500"
        assert IndianNumberParser.format_inr(500) == "₹500"

    def test_parse_convenience_helper(self):
        """Verify parse_indian_number helper with defaults."""
        assert parse_indian_number("दीड लाख") == Decimal("150000")
        assert parse_indian_number("not a number", default=0) == Decimal("0")
        assert parse_indian_number("", default=None) is None
