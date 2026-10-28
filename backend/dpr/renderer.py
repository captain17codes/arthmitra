from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from engines.viability.loader import load_benchmark

from .builder import build_dpr_sections
from .models import DprResult

# Font registration: bundled Noto fonts so Marathi + ₹ render on any host.
_FONT_DIR = Path(__file__).resolve().parent / "fonts"
_FONTS_READY: bool | None = None
_DEVA = "NotoDeva"
_LATIN = "NotoLatin"
# Latin words (plus bullets/dashes/&, which the Devanagari font lacks) go to the Latin font.
# Whole whitespace-delimited tokens are routed, because ReportLab shapes a word with one font.
_LATIN_RUN = re.compile(r"[^\sऀ-ॿ]*[A-Za-z•&—–][^\sऀ-ॿ]*(?:\s+[^\sऀ-ॿ]*[A-Za-z•&—–][^\sऀ-ॿ]*)*")


def _init_pdf_fonts() -> bool:
    """Register Noto Sans Devanagari (shaped) + Noto Sans (Latin). Returns False if unavailable."""
    global _FONTS_READY
    if _FONTS_READY is not None:
        return _FONTS_READY
    try:
        for fam, base in ((_DEVA, "NotoSansDevanagari"), (_LATIN, "NotoSans")):
            pdfmetrics.registerFont(TTFont(fam, str(_FONT_DIR / f"{base}-Regular.ttf")))
            pdfmetrics.registerFont(TTFont(f"{fam}-Bold", str(_FONT_DIR / f"{base}-Bold.ttf")))
            registerFontFamily(fam, normal=fam, bold=f"{fam}-Bold", italic=fam, boldItalic=f"{fam}-Bold")
        _FONTS_READY = True
    except Exception:
        _FONTS_READY = False
    return _FONTS_READY


def _markup(text: str, fonts_ok: bool) -> str:
    """Escape text for Paragraph and route Latin runs to the Latin font (Devanagari font has no Latin)."""
    if not fonts_ok:
        return escape(text)
    out: list[str] = []
    pos = 0
    for m in _LATIN_RUN.finditer(text):
        out.append(escape(text[pos:m.start()]))
        out.append(f'<font name="{_LATIN}">{escape(m.group(0))}</font>')
        pos = m.end()
    out.append(escape(text[pos:]))
    return "".join(out)


def render_dpr_pdf(
    case_id: int,
    eval_output: dict[str, Any],
    input_snapshot: dict[str, Any],
    output_dir: Path,
    language: str = "mr",
    promoter_name: str | None = None,
) -> DprResult:
    """
    Render a 12-section bank-ready DPR PDF document.
    Adheres strictly to TECH_SPEC §7.2 with verifiable SHA-256 document integrity.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    fonts_ok = _init_pdf_fonts()
    font_name = _DEVA if fonts_ok else "Helvetica"
    shaping = 1 if fonts_ok else 0

    business_code = input_snapshot.get("business_code") or (eval_output.get("summary") or {}).get("business_code")
    try:
        benchmark = load_benchmark(business_code) if business_code else None
    except Exception:
        benchmark = None
    sections = build_dpr_sections(eval_output, input_snapshot, language, promoter_name=promoter_name, benchmark=benchmark)
    summary = (eval_output.get("summary") or {})
    b_name_mr = summary.get("business_name_mr", "व्यवसाय")
    b_name_en = summary.get("business_name_en", "Business")
    v_name = summary.get("village_name", "")
    top_pkgs = summary.get("top_packages", [])
    top_pkg = top_pkgs[0] if top_pkgs else {}
    sc_code = top_pkg.get("scheme_code", "MUDRA")

    filename = f"DPR_Case_{case_id}_{language}.pdf"
    file_path = output_dir / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Define custom styling with resolved font
    title_style = ParagraphStyle(
        "DprTitle",
        parent=styles["Title"],
        fontName=font_name,
        shaping=shaping,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),  # Deep Navy
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "DprSubtitle",
        parent=styles["Normal"],
        fontName=font_name,
        shaping=shaping,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
    )
    section_heading_style = ParagraphStyle(
        "DprSecHeading",
        parent=styles["Heading2"],
        fontName=font_name,
        shaping=shaping,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "DprBody",
        parent=styles["Normal"],
        fontName=font_name,
        shaping=shaping,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
    )

    elements = []

    # 1. Header Banner
    def para(text: str, style: ParagraphStyle, bold: bool = False) -> Paragraph:
        body = _markup(text, fonts_ok)
        return Paragraph(f"<b>{body}</b>" if bold else body, style)

    elements.append(para("सविस्तर प्रकल्प अहवाल (DETAILED PROJECT REPORT - DPR)", title_style, bold=True))
    elements.append(Spacer(1, 4))
    elements.append(
        para(f"{b_name_mr} ({b_name_en}) | {v_name} | योजना / Scheme: {sc_code}", subtitle_style, bold=True)
    )
    elements.append(Spacer(1, 4))
    elements.append(
        para(f"ArthMitra Reference Case ID: #{case_id} | Language: {language.upper()} | Bank Appraisal Copy", subtitle_style)
    )
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=12))

    # 2. Render all 12 Sections
    for sec in sections:
        # Title
        sec_title = sec.title_mr if language == "mr" else sec.title_en
        elements.append(para(sec_title, section_heading_style, bold=True))

        # Content lines
        raw_content = sec.content_mr if language == "mr" else sec.content_en
        for line in raw_content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # Highlight bullet points or key-value rows
            elements.append(para(line_str, body_style))
            elements.append(Spacer(1, 2))

        elements.append(Spacer(1, 6))

    # Build PDF
    doc.build(elements)

    # Compute SHA-256
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    digest = sha256.hexdigest()

    return DprResult(
        file_path=str(file_path),
        file_sha256=digest,
        language=language,
        page_count=len(sections),
        section_count=len(sections),
    )
