from __future__ import annotations

import difflib
import logging
from pathlib import Path
from typing import Annotated, Any

import yaml  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from engines.rules.evaluator import evaluate_scheme
from engines.rules.models import SchemeDefinition
from models.business_type import Benchmark
from models.enums import BenchmarkConfidence, CoordSource, SchemeStatus, UserRole
from models.scheme import Scheme, SchemeVersion
from models.village import Village

from ..deps import DbSession, log_audit, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin & Supervisor"])

AdminUser = Annotated[
    Any,
    Depends(require_role([UserRole.SUPERVISOR, UserRole.ADMIN])),
]


class ValidateYamlRequest(BaseModel):
    rules_yaml: str


class PublishSchemeRequest(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    rules_yaml: str
    source_url: str | None = None
    source_date: str | None = None
    status: SchemeStatus = SchemeStatus.VERIFIED


class BenchmarkUpdateRequest(BaseModel):
    value: float
    unit: str
    region: str
    source_title: str
    source_url: str | None = None
    source_year: int
    confidence: BenchmarkConfidence
    version: str = "1.0.1"


class BenchmarkCreateRequest(BenchmarkUpdateRequest):
    business_code: str
    key: str


class VillageCoordsUpdateRequest(BaseModel):
    lat: float = Field(..., ge=8.0, le=37.0)
    lon: float = Field(..., ge=68.0, le=97.0)
    source_note: str | None = "manual_verified"


# ==========================================
# 1. Scheme Rule Management & Versioning
# ==========================================

@router.get("/schemes")
async def list_admin_schemes(
    user: AdminUser,
    db: DbSession,
) -> list[dict[str, Any]]:
    """List all schemes with their latest version, status, and published date."""
    stmt = (
        select(Scheme, SchemeVersion)
        .outerjoin(
            SchemeVersion,
            (SchemeVersion.scheme_code == Scheme.code),
        )
        .order_by(Scheme.code, SchemeVersion.id.desc())
    )
    res = await db.execute(stmt)
    rows = res.all()

    seen_codes: set[str] = set()
    result = []
    for scheme, version in rows:
        if scheme.code in seen_codes:
            continue
        seen_codes.add(scheme.code)
        result.append(
            {
                "code": scheme.code,
                "name_en": scheme.name_en,
                "name_mr": scheme.name_mr,
                "agency": scheme.agency,
                "channel": scheme.channel,
                "portal_url": scheme.portal_url,
                "current_version": version.version if version else "1.0.0",
                "status": version.status.value if version else "verified",
                "published_at": version.published_at.isoformat() if version else None,
                "published_by": version.published_by if version else None,
            }
        )
    return result


@router.get("/schemes/{code}")
async def get_admin_scheme_detail(
    code: str,
    user: AdminUser,
    db: DbSession,
) -> dict[str, Any]:
    """Get scheme details including current active YAML rules and version history."""
    scheme_res = await db.execute(select(Scheme).where(Scheme.code == code))
    scheme = scheme_res.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{code}' not found")

    versions_res = await db.execute(
        select(SchemeVersion)
        .where(SchemeVersion.scheme_code == code)
        .order_by(SchemeVersion.id.desc())
    )
    versions = versions_res.scalars().all()

    current_yaml = ""
    # Try reading from latest DB version or fallback to data/schemes/{code}.yaml
    if versions and versions[0].rules_yaml:
        current_yaml = str(versions[0].rules_yaml)
    else:
        file_path = Path(__file__).resolve().parents[3] / "data" / "schemes" / f"{code}.yaml"
        if file_path.exists():
            current_yaml = file_path.read_text(encoding="utf-8")

    return {
        "code": scheme.code,
        "name_en": scheme.name_en,
        "name_mr": scheme.name_mr,
        "agency": scheme.agency,
        "current_rules_yaml": current_yaml,
        "versions": [
            {
                "id": v.id,
                "version": v.version,
                "status": v.status.value,
                "source_url": v.source_url,
                "source_date": v.source_date,
                "published_by": v.published_by,
                "published_at": v.published_at.isoformat(),
            }
            for v in versions
        ],
    }


@router.post("/schemes/{code}/validate")
async def validate_scheme_yaml(
    code: str,
    payload: ValidateYamlRequest,
    user: AdminUser,
    db: DbSession,
) -> dict[str, Any]:
    """
    Validate proposed YAML string against Pydantic schema and execute embedded test vectors.
    Returns test run summary without mutating database or active rules.
    """
    errors: list[str] = []
    tests_run = 0
    tests_passed = 0

    # 1. Parse YAML syntax
    try:
        data = yaml.safe_load(payload.rules_yaml)
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"YAML syntax error: {str(e)}"],
            "tests_run": 0,
            "tests_passed": 0,
            "diff": [],
        }

    # 2. Validate against SchemeDefinition model
    try:
        scheme_def = SchemeDefinition.model_validate(data)
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Schema validation error: {str(e)}"],
            "tests_run": 0,
            "tests_passed": 0,
            "diff": [],
        }

    # 3. Execute embedded test vectors
    if scheme_def.tests:
        for i, test_vector in enumerate(scheme_def.tests):
            tests_run += 1
            eval_res = evaluate_scheme(scheme_def, test_vector.input)
            expected_status = test_vector.expect.get("status")
            if expected_status and eval_res.status.value != expected_status:
                errors.append(
                    f"Test #{i + 1} failed: expected status '{expected_status}', got '{eval_res.status.value}'"
                )
            else:
                tests_passed += 1

    # Compute diff against current rules if existing
    active_yaml = ""
    latest_ver = await db.execute(
        select(SchemeVersion)
        .where(SchemeVersion.scheme_code == code)
        .order_by(SchemeVersion.id.desc())
        .limit(1)
    )
    row = latest_ver.scalar_one_or_none()
    if row and row.rules_yaml:
        active_yaml = str(row.rules_yaml)

    diff_lines = list(
        difflib.unified_diff(
            active_yaml.splitlines(),
            payload.rules_yaml.splitlines(),
            fromfile="current.yaml",
            tofile="proposed.yaml",
            lineterm="",
        )
    )

    is_valid = len(errors) == 0
    return {
        "valid": is_valid,
        "errors": errors,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "diff": diff_lines,
    }


@router.post("/schemes/{code}/publish", status_code=status.HTTP_201_CREATED)
async def publish_scheme_version(
    code: str,
    payload: PublishSchemeRequest,
    user: AdminUser,
    db: DbSession,
) -> dict[str, Any]:
    """
    Publish new version of a scheme.
    TECH_SPEC §3: Re-runs all test vectors, saves version to database,
    records audit_log, and guarantees reproducibility of old evaluations.
    """
    scheme_res = await db.execute(select(Scheme).where(Scheme.code == code))
    scheme = scheme_res.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{code}' not found")

    # Validate and test before publish
    try:
        data = yaml.safe_load(payload.rules_yaml)
        scheme_def = SchemeDefinition.model_validate(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot publish invalid scheme YAML: {e}",
        ) from e

    # Re-run all tests
    if scheme_def.tests:
        for i, test_vector in enumerate(scheme_def.tests):
            eval_res = evaluate_scheme(scheme_def, test_vector.input)
            expected_status = test_vector.expect.get("status")
            if expected_status and eval_res.status.value != expected_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Test #{i + 1} failed during publication check: expected '{expected_status}', got '{eval_res.status.value}'",
                )

    # Create new immutable SchemeVersion record
    new_version = SchemeVersion(
        scheme_code=code,
        version=payload.version,
        status=payload.status,
        rules_yaml=payload.rules_yaml,
        source_url=payload.source_url or str(scheme_def.source.url),
        source_date=payload.source_date or scheme_def.source.date,
        published_by=user.name or f"User-{user.id}",
    )
    db.add(new_version)
    await db.flush()

    # Log to audit trail
    await log_audit(
        db,
        actor_id=user.id,
        action="publish_scheme_version",
        entity="scheme",
        entity_id=code,
        diff={
            "version": payload.version,
            "status": payload.status.value,
            "tests_run": len(scheme_def.tests or []),
        },
    )

    await db.commit()
    await db.refresh(new_version)

    return {
        "scheme_code": code,
        "version": new_version.version,
        "status": new_version.status.value,
        "published_at": new_version.published_at.isoformat(),
        "published_by": new_version.published_by,
        "tests_passed": len(scheme_def.tests or []),
    }


# ==========================================
# 2. Benchmarks Management
# ==========================================

@router.get("/benchmarks")
async def list_admin_benchmarks(
    user: AdminUser,
    db: DbSession,
    business_code: str | None = None,
) -> list[dict[str, Any]]:
    """List benchmark metrics with sources, years, and confidence labels."""
    stmt = select(Benchmark).where(Benchmark.active == True)  # noqa: E712
    if business_code:
        stmt = stmt.where(Benchmark.business_code == business_code)
    stmt = stmt.order_by(Benchmark.business_code, Benchmark.key)

    res = await db.execute(stmt)
    benchmarks = res.scalars().all()

    return [
        {
            "id": b.id,
            "business_code": b.business_code,
            "key": b.key,
            "value": float(b.value),
            "unit": b.unit,
            "region": b.region,
            "source_title": b.source_title,
            "source_url": b.source_url,
            "source_year": b.source_year,
            "confidence": b.confidence.value,
            "version": b.version,
        }
        for b in benchmarks
    ]


@router.put("/benchmarks/{benchmark_id}")
async def update_benchmark(
    benchmark_id: int,
    payload: BenchmarkUpdateRequest,
    user: AdminUser,
    db: DbSession,
) -> dict[str, Any]:
    """Edit benchmark with source, year, and confidence level; records audit log."""
    res = await db.execute(select(Benchmark).where(Benchmark.id == benchmark_id))
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    old_val = float(b.value)
    setattr(b, "value", payload.value)
    setattr(b, "unit", payload.unit)
    setattr(b, "region", payload.region)
    setattr(b, "source_title", payload.source_title)
    setattr(b, "source_url", payload.source_url)
    setattr(b, "source_year", payload.source_year)
    setattr(b, "confidence", payload.confidence)
    setattr(b, "version", payload.version)

    await log_audit(
        db,
        actor_id=user.id,
        action="update_benchmark",
        entity="benchmark",
        entity_id=str(benchmark_id),
        diff={
            "key": b.key,
            "old_value": old_val,
            "new_value": payload.value,
            "source_title": payload.source_title,
            "confidence": payload.confidence.value,
        },
    )

    await db.commit()
    return {"id": b.id, "success": True, "updated_key": b.key}


# ==========================================
# 3. Village Coordinate Fixes
# ==========================================

@router.get("/villages/missing-coords")
async def list_villages_missing_coords(
    user: AdminUser,
    db: DbSession,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List villages needing manual coordinate verification or fixes."""
    stmt = (
        select(Village)
        .where(
            (Village.lat.is_(None))
            | (Village.lon.is_(None))
            | (Village.coord_source == CoordSource.OTHER)
        )
        .limit(limit)
    )
    res = await db.execute(stmt)
    villages = res.scalars().all()

    return [
        {
            "lgd_code": v.lgd_code,
            "name_en": v.name_en,
            "name_mr": v.name_mr,
            "subdistrict_name": v.subdistrict_name,
            "district_name": v.district_name,
            "lat": v.lat,
            "lon": v.lon,
            "coord_source": v.coord_source.value if v.coord_source else None,
        }
        for v in villages
    ]


@router.patch("/villages/{lgd_code}/coords")
async def update_village_coords(
    lgd_code: int,
    payload: VillageCoordsUpdateRequest,
    user: AdminUser,
    db: DbSession,
) -> dict[str, Any]:
    """Fix village coordinates manually with audit logging."""
    res = await db.execute(select(Village).where(Village.lgd_code == lgd_code))
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Village not found")

    old_lat = v.lat
    old_lon = v.lon

    setattr(v, "lat", payload.lat)
    setattr(v, "lon", payload.lon)
    setattr(v, "coord_source", CoordSource.MANUAL)

    await log_audit(
        db,
        actor_id=user.id,
        action="update_village_coords",
        entity="village",
        entity_id=str(lgd_code),
        diff={
            "old_coords": [old_lat, old_lon],
            "new_coords": [payload.lat, payload.lon],
            "source_note": payload.source_note,
        },
    )

    await db.commit()
    return {
        "lgd_code": v.lgd_code,
        "name_en": v.name_en,
        "lat": v.lat,
        "lon": v.lon,
        "coord_source": v.coord_source.value,
        "success": True,
    }
