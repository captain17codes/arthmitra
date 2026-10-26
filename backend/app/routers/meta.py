from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from models.business_type import BusinessType
from models.scheme import Scheme

from ..deps import DbSession

router = APIRouter(prefix="/meta", tags=["Metadata"])


@router.get("/businesses")
async def list_businesses(db: DbSession) -> list[dict[str, Any]]:
    """Catalog of all 10 supported micro-enterprise business types with multilingual metadata."""
    res = await db.execute(select(BusinessType))
    businesses = res.scalars().all()
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
        }
        for b in businesses
    ]


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
