from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

DEVANAGARI_DIGITS_MAP = {
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
}

# Base number names (0 to 100) mapped to numeric values
BASE_NUMBERS: dict[str, Decimal] = {
    # 0 - 10
    "शून्य": Decimal("0"),
    "shunya": Decimal("0"),
    "zero": Decimal("0"),
    "एक": Decimal("1"),
    "ek": Decimal("1"),
    "one": Decimal("1"),
    "दोन": Decimal("2"),
    "दो": Decimal("2"),
    "don": Decimal("2"),
    "do": Decimal("2"),
    "two": Decimal("2"),
    "तीन": Decimal("3"),
    "teen": Decimal("3"),
    "tin": Decimal("3"),
    "three": Decimal("3"),
    "चार": Decimal("4"),
    "char": Decimal("4"),
    "chaar": Decimal("4"),
    "four": Decimal("4"),
    "पाच": Decimal("5"),
    "पांच": Decimal("5"),
    "paach": Decimal("5"),
    "panch": Decimal("5"),
    "five": Decimal("5"),
    "सहा": Decimal("6"),
    "छह": Decimal("6"),
    "छः": Decimal("6"),
    "saha": Decimal("6"),
    "chhe": Decimal("6"),
    "chhah": Decimal("6"),
    "six": Decimal("6"),
    "सात": Decimal("7"),
    "saat": Decimal("7"),
    "seven": Decimal("7"),
    "आठ": Decimal("8"),
    "aath": Decimal("8"),
    "ath": Decimal("8"),
    "eight": Decimal("8"),
    "नऊ": Decimal("9"),
    "नौ": Decimal("9"),
    "nau": Decimal("9"),
    "nav": Decimal("9"),
    "nine": Decimal("9"),
    "दहा": Decimal("10"),
    "दस": Decimal("10"),
    "daha": Decimal("10"),
    "das": Decimal("10"),
    "ten": Decimal("10"),
    # 11 - 20
    "अकरा": Decimal("11"),
    "ग्यारह": Decimal("11"),
    "gyarah": Decimal("11"),
    "eleven": Decimal("11"),
    "बारा": Decimal("12"),
    "बारह": Decimal("12"),
    "bara": Decimal("12"),
    "baarah": Decimal("12"),
    "twelve": Decimal("12"),
    "तेरा": Decimal("13"),
    "तेरह": Decimal("13"),
    "tera": Decimal("13"),
    "terah": Decimal("13"),
    "thirteen": Decimal("13"),
    "चौदा": Decimal("14"),
    "चौदह": Decimal("14"),
    "chauda": Decimal("14"),
    "chaudah": Decimal("14"),
    "fourteen": Decimal("14"),
    "पंधरा": Decimal("15"),
    "पंद्रह": Decimal("15"),
    "pandhra": Decimal("15"),
    "pandrah": Decimal("15"),
    "fifteen": Decimal("15"),
    "सोळा": Decimal("16"),
    "सोलह": Decimal("16"),
    "sola": Decimal("16"),
    "solah": Decimal("16"),
    "sixteen": Decimal("16"),
    "सतरा": Decimal("17"),
    "सत्रह": Decimal("17"),
    "satra": Decimal("17"),
    "satrah": Decimal("17"),
    "seventeen": Decimal("17"),
    "अठरा": Decimal("18"),
    "अठारह": Decimal("18"),
    "athra": Decimal("18"),
    "athaarah": Decimal("18"),
    "eighteen": Decimal("18"),
    "एकोणीस": Decimal("19"),
    "उन्नीस": Decimal("19"),
    "ekonis": Decimal("19"),
    "unnis": Decimal("19"),
    "nineteen": Decimal("19"),
    "वीस": Decimal("20"),
    "बीस": Decimal("20"),
    "vees": Decimal("20"),
    "vis": Decimal("20"),
    "bees": Decimal("20"),
    "twenty": Decimal("20"),
    # Tens and common 21-99
    "एकवीस": Decimal("21"),
    "इक्कीस": Decimal("21"),
    "बावीस": Decimal("22"),
    "बाईस": Decimal("22"),
    "तेवीस": Decimal("23"),
    "तेईस": Decimal("23"),
    "चोवीस": Decimal("24"),
    "चौबीस": Decimal("24"),
    "पंचवीस": Decimal("25"),
    "पच्चीस": Decimal("25"),
    "panchvees": Decimal("25"),
    "pachchees": Decimal("25"),
    "twenty five": Decimal("25"),
    "तीस": Decimal("30"),
    "tees": Decimal("30"),
    "thirty": Decimal("30"),
    "पस्तीस": Decimal("35"),
    "पैंतीस": Decimal("35"),
    "thirty five": Decimal("35"),
    "चाळीस": Decimal("40"),
    "चालीस": Decimal("40"),
    "chalis": Decimal("40"),
    "chalees": Decimal("40"),
    "forty": Decimal("40"),
    "पंचेचाळीस": Decimal("45"),
    "पैंतालीस": Decimal("45"),
    "forty five": Decimal("45"),
    "पन्नास": Decimal("50"),
    "पचास": Decimal("50"),
    "pannas": Decimal("50"),
    "pachas": Decimal("50"),
    "fifty": Decimal("50"),
    "साठ": Decimal("60"),
    "saath": Decimal("60"),
    "sath": Decimal("60"),
    "sixty": Decimal("60"),
    "सत्तर": Decimal("70"),
    "sattar": Decimal("70"),
    "seventy": Decimal("70"),
    "पंच्याहत्तर": Decimal("75"),
    "पचहत्तर": Decimal("75"),
    "seventy five": Decimal("75"),
    "ऐंशी": Decimal("80"),
    "अस्सी": Decimal("80"),
    "aishi": Decimal("80"),
    "assi": Decimal("80"),
    "eighty": Decimal("80"),
    "नव्वद": Decimal("90"),
    "नब्बे": Decimal("90"),
    "navvad": Decimal("90"),
    "nabbe": Decimal("90"),
    "ninety": Decimal("90"),
    "शंभर": Decimal("100"),
    "सौ": Decimal("100"),
    "shambhar": Decimal("100"),
    "sau": Decimal("100"),
    "hundred": Decimal("100"),
}

# Special fused words (e.g. दीडशे -> 150)
FUSED_WORDS: dict[str, Decimal] = {
    "दीडशे": Decimal("150"),
    "dedh sau": Decimal("150"),
    "dedhsau": Decimal("150"),
    "अडीचशे": Decimal("250"),
    "dhai sau": Decimal("250"),
    "dhaisau": Decimal("250"),
    "सव्वाशे": Decimal("125"),
    "savva sau": Decimal("125"),
    "paune don she": Decimal("175"),
    "पावणेदोनशे": Decimal("175"),
    "पावणे दोनशे": Decimal("175"),
    "पौने दो सौ": Decimal("175"),
    "साडेतीनशे": Decimal("350"),
    "साडे तीनशे": Decimal("350"),
    "साढ़े तीन सौ": Decimal("350"),
    "साडेचारशे": Decimal("450"),
    "साडे चारशे": Decimal("450"),
    "साढ़े चार सौ": Decimal("450"),
    "साडेपाचशे": Decimal("550"),
    "साडे पाचशे": Decimal("550"),
}

# Large scale units
SCALE_UNITS: dict[str, Decimal] = {
    # Crore: 1,00,00,000 (10^7)
    "कोटी": Decimal("10000000"),
    "करोड": Decimal("10000000"),
    "करोड़": Decimal("10000000"),
    "crore": Decimal("10000000"),
    "crores": Decimal("10000000"),
    "cr": Decimal("10000000"),
    "koti": Decimal("10000000"),
    # Lakh: 1,00,000 (10^5)
    "लाख": Decimal("100000"),
    "लक्ष": Decimal("100000"),
    "lakh": Decimal("100000"),
    "lakhs": Decimal("100000"),
    "lac": Decimal("100000"),
    "lacs": Decimal("100000"),
    "l": Decimal("100000"),
    # Thousand: 1,000
    "हजार": Decimal("1000"),
    "हज़ार": Decimal("1000"),
    "hazar": Decimal("1000"),
    "hazaar": Decimal("1000"),
    "thousand": Decimal("1000"),
    "thousands": Decimal("1000"),
    "k": Decimal("1000"),
    # Hundred: 100
    "शे": Decimal("100"),
    "शंभर": Decimal("100"),
    "सौ": Decimal("100"),
    "hundred": Decimal("100"),
    "sau": Decimal("100"),
}


class IndianNumberParser:
    """
    Deterministic Indian-number parser supporting Marathi, Hindi, English and Hinglish.
    Parses spoken idioms:
      - 'दीड लाख' -> 150000
      - 'साडे तीन हजार' -> 3500
      - 'पावणे दोन लाख' -> 175000
      - 'सव्वा लाख' -> 125000
      - 'अडीच लाख' -> 250000
      - 'दोन लाख पन्नास हजार' -> 250000
      - '1.5 lakh' -> 150000
    """

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Replace devanagari numerals, remove currency symbols and strip punctuation."""
        if not text:
            return ""
        s = text.strip()
        # Convert Devanagari numerals
        for dev, lat in DEVANAGARI_DIGITS_MAP.items():
            s = s.replace(dev, lat)

        # Remove currency symbols and common words
        s = re.sub(r"[₹$]|rs\.?|inr|rupees?|रुपये|रुपया", " ", s, flags=re.IGNORECASE)
        # Remove trailing '/-' or '/'
        s = re.sub(r"/-\s*", " ", s)
        # Remove commas inside digits (e.g. 1,50,000 -> 150000)
        s = re.sub(r"(?<=\d),(?=\d)", "", s)
        # Replace remaining punctuation
        s = re.sub(r"[,/\\()\-]+", " ", s)
        # Collapse whitespace
        s = re.sub(r"\s+", " ", s).strip().lower()
        return s

    @classmethod
    def format_inr(cls, amount: Decimal | int | float) -> str:
        """Format number into standard Indian numbering system (e.g., ₹1,50,000)."""
        dec = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        s = str(abs(int(dec)))
        sign = "-" if dec < 0 else ""
        if len(s) <= 3:
            return f"{sign}₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        # Group pairs from right to left
        pairs: list[str] = []
        while len(remaining) > 2:
            pairs.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            pairs.insert(0, remaining)
        formatted = ",".join(pairs) + "," + last_three
        return f"{sign}₹{formatted}"

    @classmethod
    def parse(cls, text: str) -> Decimal | None:
        """Main parsing method returning Decimal value or None if no number found."""
        clean = cls.normalize_text(text)
        if not clean:
            return None

        # Check fused special words first
        for fused_phrase, val in FUSED_WORDS.items():
            if fused_phrase in clean:
                return val

        # 1. Check direct numeric expressions with optional scale (e.g., '1.5 lakh', '150000', '50k')
        direct_match = cls._try_direct_numeric(clean)
        if direct_match is not None:
            return direct_match

        # 2. Check fractional prefix idioms (दीड, अडीच, सव्वा, साडे, पावणे, अर्धा, पाऊण, पाव)
        fractional_match = cls._try_fractional_idioms(clean)
        if fractional_match is not None:
            return fractional_match

        # 3. Check multi-word compound scale phrases (e.g., 'दोन लाख पन्नास हजार', 'two lakh fifty thousand')
        compound_match = cls._try_compound_phrase(clean)
        if compound_match is not None:
            return compound_match

        # 4. Single base number (e.g. 'पन्नास' -> 50, 'वीस' -> 20)
        if clean in BASE_NUMBERS:
            return BASE_NUMBERS[clean]

        return None

    @classmethod
    def _try_direct_numeric(cls, s: str) -> Decimal | None:
        """Handles patterns like '1.5 lakh', '2.5 crore', '50k', '150000', '2500'."""
        # Pattern: number followed optionally by scale
        # Example: '1.5 lakh', '50 thousand', '2 cr', '150000'
        # Check scale keywords
        pattern = r"^(\d+(?:\.\d+)?)\s*([a-z\u0900-\u097f]+)?$"
        m = re.match(pattern, s)
        if m:
            num_part = Decimal(m.group(1))
            scale_part = m.group(2)
            if not scale_part:
                return num_part
            if scale_part in SCALE_UNITS:
                return (num_part * SCALE_UNITS[scale_part]).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            return None

        # Also check if pure number is embedded: '150000'
        if re.fullmatch(r"^\d+$", s):
            return Decimal(s)

        return None

    @classmethod
    def _try_fractional_idioms(cls, s: str) -> Decimal | None:
        """
        Parses classic Indian fractional forms:
          - 'दीड लाख' / 'dedh lakh' -> 1.5 * 100,000 = 150000
          - 'अडीच लाख' / 'dhai lakh' / 'adhai crore' -> 2.5 * scale
          - 'सव्वा लाख' / 'sawa lakh' -> 1.25 * scale
          - 'सव्वा दोन लाख' / 'sawa do lakh' -> 2.25 * scale
          - 'साडे तीन हजार' / 'sade teen hazar' -> 3.5 * 1000 = 3500
          - 'साडे चार लाख' / 'saade char lakh' -> 4.5 * 100000 = 450000
          - 'पावणे दोन लाख' / 'paune do lakh' -> 1.75 * 100000 = 175000
          - 'पावणे तीन लाख' -> 2.75 * 100000 = 275000
          - 'अर्धा लाख' / 'aadha lakh' -> 0.5 * 100000 = 50000
          - 'पाऊण लाख' / 'paun lakh' -> 0.75 * 100000 = 75000
          - 'पाव लाख' -> 0.25 * 100000 = 25000
        """
        tokens = s.split()
        if not tokens:
            return None

        # Check for fractional prefixes
        first = tokens[0]

        # Case 1: 'दीड' / 'dedh' / 'deed' (1.5)
        if first in ("दीड", "डेढ़", "dedh", "deed"):
            if len(tokens) == 1:
                return Decimal("1.5")
            target_scale = cls._find_scale(tokens[1:])
            if target_scale:
                return (Decimal("1.5") * target_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 2: 'अडीच' / 'ढाई' / 'adhai' / 'dhai' (2.5)
        if first in ("अडीच", "ढाई", "adhai", "dhai"):
            if len(tokens) == 1:
                return Decimal("2.5")
            target_scale = cls._find_scale(tokens[1:])
            if target_scale:
                return (Decimal("2.5") * target_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 3: 'पाव' / 'paav' (0.25)
        if first in ("पाव", "paav", "paaon"):
            if len(tokens) == 1:
                return Decimal("0.25")
            target_scale = cls._find_scale(tokens[1:])
            if target_scale:
                return (Decimal("0.25") * target_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 4: 'अर्धा' / 'आधा' / 'ardha' / 'aadha' (0.5)
        if first in ("अर्धा", "आधा", "ardha", "aadha", "half"):
            if len(tokens) == 1:
                return Decimal("0.5")
            target_scale = cls._find_scale(tokens[1:])
            if target_scale:
                return (Decimal("0.5") * target_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 5: 'पाऊण' / 'पौन' / 'paun' / 'paaun' (0.75)
        if first in ("पाऊण", "पौन", "paun", "paaun"):
            if len(tokens) == 1:
                return Decimal("0.75")
            target_scale = cls._find_scale(tokens[1:])
            if target_scale:
                return (Decimal("0.75") * target_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 6: 'सव्वा' / 'सवा' / 'savva' / 'sawa'
        if first in ("सव्वा", "सवा", "savva", "sawa"):
            if len(tokens) == 1:
                return Decimal("1.25")
            # If directly followed by a scale: 'सव्वा लाख' -> 1.25 * 100000
            scale = cls._find_scale([tokens[1]])
            if scale:
                return (Decimal("1.25") * scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            # Or followed by a base number: 'सव्वा दोन लाख' -> (2 + 0.25) * 100000
            base_val = cls._get_base_num(tokens[1])
            if base_val is not None:
                multiplier = base_val + Decimal("0.25")
                found_scale = cls._find_scale(tokens[2:]) if len(tokens) > 2 else None
                rest_scale = found_scale if found_scale is not None else Decimal("1")
                return (multiplier * rest_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 7: 'साडे' / 'साढ़े' / 'sade' / 'saade' (+0.5)
        if first in ("साडे", "साढ़े", "sade", "saade"):
            if len(tokens) > 1:
                base_val = cls._get_base_num(tokens[1])
                if base_val is not None:
                    multiplier = base_val + Decimal("0.5")
                    found_scale = cls._find_scale(tokens[2:]) if len(tokens) > 2 else None
                    scale = found_scale if found_scale is not None else Decimal("1")
                    return (multiplier * scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # Case 8: 'पावणे' / 'पौने' / 'paune' / 'paaune' (-0.25)
        if first in ("पावणे", "पौने", "paune", "paaune"):
            if len(tokens) > 1:
                # If directly followed by a scale: 'पावणे लाख' -> 0.75 * 100000 = 75000
                direct_scale = cls._find_scale([tokens[1]])
                if direct_scale:
                    return (Decimal("0.75") * direct_scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                base_val = cls._get_base_num(tokens[1])
                if base_val is not None:
                    multiplier = base_val - Decimal("0.25")
                    found_scale = cls._find_scale(tokens[2:]) if len(tokens) > 2 else None
                    scale = found_scale if found_scale is not None else Decimal("1")
                    return (multiplier * scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        return None

    @classmethod
    def _try_compound_phrase(cls, s: str) -> Decimal | None:
        """
        Parses additive compound phrases across scales:
          - 'दोन लाख पन्नास हजार' -> 250,000
          - 'एक लाख वीस हजार' -> 120,000
          - 'तीन लाख पंचवीस हजार' -> 325,000
          - 'एक कोटी पन्नास लाख' -> 15,000,000
          - 'two lakh fifty thousand' -> 250,000
          - 'three lakh' -> 300,000
        """
        # Split tokens and find scale boundaries (crore, lakh, thousand, hundred)
        tokens = s.split()
        if not tokens:
            return None

        total = Decimal("0")
        current_segment: list[str] = []
        found_any_scale = False

        for token in tokens:
            if token in SCALE_UNITS:
                scale_val = SCALE_UNITS[token]
                segment_str = " ".join(current_segment).strip()
                if not segment_str:
                    # e.g., 'लाख' alone means 1 lakh
                    total += scale_val
                else:
                    sub_val = cls.parse(segment_str)
                    if sub_val is None:
                        # try base num
                        sub_val = cls._get_base_num(segment_str)
                    if sub_val is not None:
                        total += sub_val * scale_val
                    else:
                        return None
                current_segment = []
                found_any_scale = True
            else:
                current_segment.append(token)

        # Trailing segment (e.g. 'दोनशे पन्नास' or 'one hundred twenty')
        if current_segment:
            rem_str = " ".join(current_segment).strip()
            # If we had preceding scales, add remainder
            if found_any_scale:
                rem_val = cls.parse(rem_str)
                if rem_val is not None:
                    total += rem_val
            else:
                # No scales found, maybe just multi-word base like 'twenty five'
                if rem_str in BASE_NUMBERS:
                    return BASE_NUMBERS[rem_str]
                return None

        if found_any_scale and total > 0:
            return total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        return None

    @classmethod
    def _find_scale(cls, tokens: list[str]) -> Decimal | None:
        """Detect any scale unit within tokens."""
        for t in tokens:
            if t in SCALE_UNITS:
                return SCALE_UNITS[t]
        return None

    @classmethod
    def _get_base_num(cls, token: str) -> Decimal | None:
        """Parse token as a digit, decimal or base word."""
        if re.fullmatch(r"^\d+(?:\.\d+)?$", token):
            return Decimal(token)
        return BASE_NUMBERS.get(token)


def parse_indian_number(text: str, default: int | float | Decimal | None = None) -> Decimal | None:
    """Convenience helper to parse an Indian spoken/written number."""
    val = IndianNumberParser.parse(text)
    if val is not None:
        return val
    if default is not None:
        return Decimal(str(default))
    return None
