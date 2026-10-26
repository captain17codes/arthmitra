from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from .builder import build_dpr_sections
from .models import DprResult

# Font registration helper
_FONT_REGISTERED = False
_ACTIVE_FONT_NAME = "Helvetica"


def _init_pdf_fonts() -> str:
    """Register Devanagari / Unicode TTF font if available on OS."""
    global _FONT_REGISTERED, _ACTIVE_FONT_NAME
    if _FONT_REGISTERED:
        return _ACTIVE_FONT_NAME

    # Candidate Devanagari fonts on Windows and Linux
    candidate_paths = [
        ("Devanagari", "C:/Windows/Fonts/mangal.ttf"),
        ("Devanagari", "C:/Windows/Fonts/Nirmala.ttc"),
        ("Devanagari", "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"),
        ("Devanagari", "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.otf"),
    ]

    for name, f_path in candidate_paths:
        if os.path.exists(f_path):
            try:
                pdfmetrics.registerFont(TTFont(name, f_path))
                _ACTIVE_FONT_NAME = name
                _FONT_REGISTERED = True
                return name
            except Exception:
                continue

    _FONT_REGISTERED = True
    _ACTIVE_FONT_NAME = "Helvetica"
    return _ACTIVE_FONT_NAME


def render_dpr_pdf(
    case_id: int,
    eval_output: dict[str, Any],
    input_snapshot: dict[str, Any],
    output_dir: Path,
    language: str = "mr",
) -> DprResult:
    """
    Render a 12-section bank-ready DPR PDF document.
    Adheres strictly to TECH_SPEC §7.2 with verifiable SHA-256 document integrity.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    font_name = _init_pdf_fonts()

    sections = build_dpr_sections(eval_output, input_snapshot, language)
    summary = eval_output.get("summary", {})
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
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),  # Deep Navy
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "DprSubtitle",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
    )
    section_heading_style = ParagraphStyle(
        "DprSecHeading",
        parent=styles["Heading2"],
        fontName=font_name,
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
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("<b>सविस्तर प्रकल्प अहवाल (DETAILED PROJECT REPORT - DPR)</b>", title_style))
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            f"<b>{b_name_mr} ({b_name_en}) | {v_name} | योजना: {sc_code}</b>",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            f"ArthMitra Reference Case ID: #{case_id} | Language: {language.upper()} | Bank Appraisal Copy",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=12))

    # 2. Render all 12 Sections
    for sec in sections:
        # Title
        sec_title = sec.title_mr if language == "mr" else sec.title_en
        elements.append(Paragraph(f"<b>{sec_title}</b>", section_heading_style))

        # Content lines
        raw_content = sec.content_mr if language == "mr" else sec.content_en
        for line in raw_content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # Highlight bullet points or key-value rows
            elements.append(Paragraph(line_str, body_style))
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
