"""
Geospatial and LGD Directory Endpoints.
Strictly implements TECH_SPEC §9.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from models.village import Village, VillageNeighbour

router = APIRouter(prefix="/geo", tags=["Geospatial"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/districts")
async def list_districts(db: DbSession) -> list[dict[str, Any]]:
    """List unique districts with LGD codes."""
    stmt = (
        select(Village.district_lgd, Village.district_name)
        .distinct()
        .order_by(Village.district_name)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"district_lgd": r[0], "district_name": r[1]} for r in rows]


@router.get("/subdistricts")
async def list_subdistricts(
    db: DbSession,
    district_lgd: int | None = Query(None, description="Filter by district LGD code"),
) -> list[dict[str, Any]]:
    """List talukas / sub-districts within a district."""
    stmt = select(Village.subdistrict_lgd, Village.subdistrict_name, Village.district_lgd).distinct()
    if district_lgd is not None:
        stmt = stmt.where(Village.district_lgd == district_lgd)
    stmt = stmt.order_by(Village.subdistrict_name)

    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "subdistrict_lgd": r[0],
            "subdistrict_name": r[1],
            "district_lgd": r[2],
        }
        for r in rows
    ]


@router.get("/villages")
async def list_villages(
    db: DbSession,
    subdistrict_lgd: int | None = Query(None, description="Filter by subdistrict LGD code"),
    district_lgd: int | None = Query(None, description="Filter by district LGD code"),
    q: str | None = Query(None, description="Search term in Marathi or English"),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    """
    Search villages with Marathi and English substring matching.
    """
    stmt = select(Village)

    if district_lgd is not None:
        stmt = stmt.where(Village.district_lgd == district_lgd)
    if subdistrict_lgd is not None:
        stmt = stmt.where(Village.subdistrict_lgd == subdistrict_lgd)

    if q:
        query_pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Village.name_en.ilike(query_pattern),
                Village.name_mr.like(query_pattern),
            )
        )

    stmt = stmt.order_by(Village.name_en).limit(limit)
    result = await db.execute(stmt)
    villages = result.scalars().all()

    return [
        {
            "lgd_code": v.lgd_code,
            "name_en": v.name_en,
            "name_mr": v.name_mr,
            "subdistrict_lgd": v.subdistrict_lgd,
            "subdistrict_name": v.subdistrict_name,
            "district_lgd": v.district_lgd,
            "district_name": v.district_name,
            "lat": v.lat,
            "lon": v.lon,
            "pop_2011": v.pop_2011,
            "has_market": v.ma_has_market,
            "has_haat": v.ma_has_haat,
            "bank_branch": v.ma_bank_branch,
        }
        for v in villages
    ]


@router.get("/villages/{lgd_code}")
async def get_village_detail(
    lgd_code: int,
    db: DbSession,
) -> dict[str, Any]:
    """Retrieve full demographic and amenity profile for a village."""
    stmt = select(Village).where(Village.lgd_code == lgd_code)
    result = await db.execute(stmt)
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Village not found")

    return {
        "lgd_code": v.lgd_code,
        "name_en": v.name_en,
        "name_mr": v.name_mr,
        "subdistrict_lgd": v.subdistrict_lgd,
        "subdistrict_name": v.subdistrict_name,
        "district_lgd": v.district_lgd,
        "district_name": v.district_name,
        "census2011_code": v.census2011_code,
        "lat": v.lat,
        "lon": v.lon,
        "pop_2011": v.pop_2011,
        "households_2011": v.households_2011,
        "sc_pop_2011": v.sc_pop_2011,
        "st_pop_2011": v.st_pop_2011,
        "literacy_rate": v.literacy_rate,
        "ma_has_market": v.ma_has_market,
        "ma_has_haat": v.ma_has_haat,
        "ma_haat_day": v.ma_haat_day,
        "ma_bank_branch": v.ma_bank_branch,
        "ma_bc_point": v.ma_bc_point,
        "ma_power_hours": v.ma_power_hours,
        "ma_all_weather_road": v.ma_all_weather_road,
        "ma_milk_centre": v.ma_milk_centre,
        "ma_year": v.ma_year,
    }


@router.get("/villages/{lgd_code}/neighbours")
async def get_village_neighbours(
    lgd_code: int,
    db: DbSession,
) -> list[dict[str, Any]]:
    """Retrieve precomputed neighbours within 10 km."""
    stmt = (
        select(VillageNeighbour, Village)
        .join(Village, Village.lgd_code == VillageNeighbour.neighbour_lgd)
        .where(VillageNeighbour.lgd_code == lgd_code)
        .order_by(VillageNeighbour.dist_km)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "neighbour_lgd": vn.neighbour_lgd,
            "dist_km": vn.dist_km,
            "name_en": v.name_en,
            "name_mr": v.name_mr,
            "pop_2011": v.pop_2011,
        }
        for vn, v in rows
    ]
