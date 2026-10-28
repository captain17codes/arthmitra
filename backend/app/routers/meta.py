from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from engines.viability.loader import load_all_benchmarks
from models.business_type import BusinessType
from models.scheme import Scheme

from ..deps import DbSession

router = APIRouter(prefix="/meta", tags=["Metadata"])


@router.get("/businesses")
async def list_businesses(db: DbSession) -> list[dict[str, Any]]:
    """Catalog of all 10 supported micro-enterprise business types with multilingual metadata."""
    res = await db.execute(select(BusinessType))
    businesses = res.scalars().all()
    benchmarks = load_all_benchmarks()
    return [
        {
            "code": b.code,
            "name_en": b.name_en,
            "name_mr": b.name_mr,
            "name_hi": b.name_hi,
            "sector": b.sector.value,
            "hces_category": b.hces_category,
            "decay_lambda": b.decay_lambda,
            "icon": b.icon,
            "viable_range": (benchmarks.get(b.code) or {}).get("viable_range"),
        }
        for b in businesses
    ]


@router.get("/businesses/{code}/parameters")
async def business_parameters(code: str) -> dict[str, Any]:
    """Benchmark parameters (defaults + source + confidence) the agent can override with local values."""
    bm = load_all_benchmarks().get(code)
    if not bm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    def _params(section: str) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in (bm.get(section) or {}).items():
            if isinstance(v, dict) and "value" in v:
                out[k] = {
                    "value": v["value"],
                    "unit": v.get("unit"),
                    "confidence": v.get("confidence"),
                    "source_title": v.get("source_title"),
                    "source_year": v.get("source_year"),
                }
        return out

    return {
        "code": code,
        "viable_range": bm.get("viable_range"),
        "revenue_parameters": _params("revenue_parameters"),
        "cost_parameters": _params("cost_parameters"),
    }


@router.get("/schemes")
async def list_schemes(db: DbSession) -> list[dict[str, Any]]:
    """Catalog of all supported credit and subsidy schemes."""
    res = await db.execute(select(Scheme))
    schemes = res.scalars().all()
    return [
        {
            "code": s.code,
            "name_en": s.name_en,
            "name_mr": s.name_mr,
            "agency": s.agency,
            "channel": s.channel,
            "portal_url": s.portal_url,
        }
        for s in schemes
    ]
