"""
Test suite for Data Pipeline and Geo API (Phase 5).
Verifies:
  1. REPORT.md reports valid match rates (Census & OSM coords).
  2. Pune district villages are searchable in Marathi and English.
  3. Precomputed neighbours are returned correctly.
"""

import csv
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from models.village import Village, VillageNeighbour


@pytest.fixture
def pipeline_processed_dir():
    base_dir = Path(__file__).resolve().parents[2] / "data" / "pipeline" / "processed"
    assert base_dir.exists(), f"Directory not found: {base_dir}"
    return base_dir


def test_pipeline_report_match_rates(pipeline_processed_dir):
    """Verify REPORT.md logs counts, match rates (Census and OSM coords)."""
    report_file = pipeline_processed_dir / "REPORT.md"
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")

    assert "Census 2011 Match Rate" in content
    assert "100.0%" in content
    assert "OSM Coordinates Match Rate" in content
    assert "Precomputed Neighbours" in content


@pytest.fixture
async def geo_client(pipeline_processed_dir):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Load processed CSV data into SQLite test database
    async with async_session_factory() as session:
        # Load villages
        villages_csv = pipeline_processed_dir / "villages.csv"
        with open(villages_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                v = Village(
                    lgd_code=int(r["lgd_code"]),
                    name_en=r["name_en"],
                    name_mr=r["name_mr"],
                    subdistrict_lgd=int(r["subdistrict_lgd"]),
                    subdistrict_name=r["subdistrict_name"],
                    district_lgd=int(r["district_lgd"]),
                    district_name=r["district_name"],
                    census2011_code=r.get("census2011_code"),
                    lat=float(r["lat"]) if r.get("lat") else None,
                    lon=float(r["lon"]) if r.get("lon") else None,
                    coord_source=r.get("coord_source", "osm"),
                    pop_2011=int(r["pop_2011"]) if r.get("pop_2011") else None,
                    households_2011=int(r["households_2011"]) if r.get("households_2011") else None,
                    sc_pop_2011=int(r["sc_pop_2011"]) if r.get("sc_pop_2011") else None,
                    st_pop_2011=int(r["st_pop_2011"]) if r.get("st_pop_2011") else None,
                    literacy_rate=float(r["literacy_rate"]) if r.get("literacy_rate") else None,
                    ma_has_market=r.get("ma_has_market") == "True",
                    ma_has_haat=r.get("ma_has_haat") == "True",
                    ma_haat_day=r.get("ma_haat_day"),
                    ma_bank_branch=r.get("ma_bank_branch") == "True",
                    ma_bc_point=r.get("ma_bc_point") == "True",
                    ma_power_hours=float(r["ma_power_hours"]) if r.get("ma_power_hours") else None,
                    ma_all_weather_road=r.get("ma_all_weather_road") == "True",
                    ma_milk_centre=r.get("ma_milk_centre") == "True",
                    ma_year=int(r["ma_year"]) if r.get("ma_year") else 2020,
                )
                session.add(v)

        # Load neighbours
        neighbours_csv = pipeline_processed_dir / "village_neighbours.csv"
        with open(neighbours_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                vn = VillageNeighbour(
                    lgd_code=int(r["lgd_code"]),
                    neighbour_lgd=int(r["neighbour_lgd"]),
                    dist_km=float(r["dist_km"]),
                )
                session.add(vn)

        await session.commit()

    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_geo_districts_and_subdistricts(geo_client: AsyncClient):
    """Verify districts and subdistricts listing."""
    res_dist = await geo_client.get("/geo/districts")
    assert res_dist.status_code == 200
    districts = res_dist.json()
    assert len(districts) >= 1
    assert any(d["district_name"] == "Pune" and d["district_lgd"] == 490 for d in districts)

    res_sub = await geo_client.get("/geo/subdistricts?district_lgd=490")
    assert res_sub.status_code == 200
    subdistricts = res_sub.json()
    assert len(subdistricts) >= 5
    sub_names = {s["subdistrict_name"] for s in subdistricts}
    assert "Haveli" in sub_names
    assert "Baramati" in sub_names


@pytest.mark.asyncio
async def test_pune_villages_searchable_marathi_and_english(geo_client: AsyncClient):
    """
    CRITICAL ACCEPTANCE CHECK: Pune district villages searchable in Marathi and English.
    """
    # 1. English search
    res_en = await geo_client.get("/geo/villages?q=Shirwal")
    assert res_en.status_code == 200
    results_en = res_en.json()
    assert len(results_en) >= 1
    assert results_en[0]["name_en"] == "Shirwal"
    assert results_en[0]["district_name"] == "Pune"

    # 2. Vernacular Marathi search
    res_mr = await geo_client.get("/geo/villages?q=शिरवळ")
    assert res_mr.status_code == 200
    results_mr = res_mr.json()
    assert len(results_mr) >= 1
    assert results_mr[0]["name_mr"] == "शिरवळ"

    # 3. Substring Marathi search
    res_khed = await geo_client.get("/geo/villages?q=खेड")
    assert res_khed.status_code == 200
    results_khed = res_khed.json()
    assert len(results_khed) >= 1
    assert any("खेड" in r["name_mr"] for r in results_khed)


@pytest.mark.asyncio
async def test_village_detail_and_neighbours(geo_client: AsyncClient):
    """Verify detailed amenities and neighbour graph."""
    res_v = await geo_client.get("/geo/villages/555001")
    assert res_v.status_code == 200
    detail = res_v.json()
    assert detail["name_en"] == "Shirwal"
    assert detail["ma_has_market"] is True
    assert detail["ma_power_hours"] == 22.0

    res_nb = await geo_client.get("/geo/villages/555007/neighbours")
    assert res_nb.status_code == 200
    neighbours = res_nb.json()
    # Shikrapur (555007) and Sanaswadi (555008) are neighbours <= 10 km
    assert len(neighbours) >= 1
    assert neighbours[0]["neighbour_lgd"] == 555008
    assert neighbours[0]["dist_km"] <= 10.0
