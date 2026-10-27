from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.security import hash_pin
from app.seed import seed_business_types, seed_schemes
from models.enums import CoordSource, OrgType, SchemeStatus, UserRole
from models.organization import Organization, User
from models.scheme import SchemeVersion
from models.village import Village, VillageNeighbour


async def init_and_seed_database():
    """Initializes schema and seeds demo organizations, agents, schemes, and villages."""
    print(f"Connecting to database: {settings.database_url}")
    engine = create_async_engine(settings.database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        # 1. Organizations
        res_org = await session.execute(select(Organization).where(Organization.id == 1))
        if res_org.scalar_one_or_none() is None:
            org1 = Organization(id=1, name="UMED Pune District (MSRLM)", type=OrgType.NRLM, district_lgd=490)
            org2 = Organization(id=2, name="CSC E-Governance Satara", type=OrgType.CSC, district_lgd=491)
            session.add_all([org1, org2])
            await session.flush()
            print("Seeded organizations: UMED Pune and CSC Satara.")

        # 2. Users (Agents, Supervisor, Admin)
        res_user = await session.execute(select(User).where(User.id == 1))
        if res_user.scalar_one_or_none() is None:
            agent1 = User(
                id=1,
                org_id=1,
                role=UserRole.AGENT,
                name="Sunita Patil (Bank Sakhi)",
                phone="9876543210",
                pin_hash=hash_pin("1234"),
                lang="mr",
            )
            agent2 = User(
                id=2,
                org_id=2,
                role=UserRole.AGENT,
                name="Rahul Shinde (CSC VLE)",
                phone="9123456789",
                pin_hash=hash_pin("5678"),
                lang="mr",
            )
            supervisor = User(
                id=3,
                org_id=1,
                role=UserRole.SUPERVISOR,
                name="Prakash Deshmukh (District Coordinator)",
                phone="9999999999",
                pin_hash=hash_pin("9999"),
                lang="mr",
            )
            admin_user = User(
                id=4,
                org_id=1,
                role=UserRole.ADMIN,
                name="System Administrator",
                phone="9000000000",
                pin_hash=hash_pin("1111"),
                lang="en",
            )
            session.add_all([agent1, agent2, supervisor, admin_user])
            await session.flush()
            print("Seeded users (Agent: 9876543210 / 1234 | Supervisor: 9999999999 / 9999 | Admin: 9000000000 / 1111).")

        # 3. Catalog Seed
        await seed_business_types(session)
        await seed_schemes(session)
        print("Seeded 10 business types and scheme catalog.")

        # 4. Villages & Demographics
        res_vil = await session.execute(select(Village).where(Village.lgd_code == 555001))
        if res_vil.scalar_one_or_none() is None:
            v1 = Village(
                lgd_code=555001,
                name_en="Shirwal",
                name_mr="शिरवळ",
                subdistrict_lgd=4201,
                subdistrict_name="Haveli",
                district_lgd=490,
                district_name="Pune",
                census2011_code="555001",
                lat=18.1342,
                lon=73.9856,
                coord_source=CoordSource.OSM,
                pop_2011=14250,
                households_2011=3120,
                sc_pop_2011=2100,
                st_pop_2011=420,
                literacy_rate=84.5,
                ma_has_market=True,
                ma_has_haat=True,
                ma_haat_day="Wednesday",
                ma_bank_branch=True,
                ma_bc_point=True,
            )
            v2 = Village(
                lgd_code=555011,
                name_en="Khed Shivapur",
                name_mr="खेड शिवापूर",
                subdistrict_lgd=4201,
                subdistrict_name="Haveli",
                district_lgd=490,
                district_name="Pune",
                census2011_code="555011",
                lat=18.3512,
                lon=73.8541,
                coord_source=CoordSource.OSM,
                pop_2011=2800,
                households_2011=610,
                sc_pop_2011=380,
                st_pop_2011=45,
                literacy_rate=82.0,
                ma_has_market=True,
                ma_has_haat=False,
                ma_bank_branch=False,
                ma_bc_point=True,
            )
            v3 = Village(
                lgd_code=555012,
                name_en="Wing",
                name_mr="विंग",
                subdistrict_lgd=4201,
                subdistrict_name="Haveli",
                district_lgd=490,
                district_name="Pune",
                census2011_code="555012",
                lat=18.1022,
                lon=73.9214,
                coord_source=CoordSource.OSM,
                pop_2011=3400,
                households_2011=730,
                sc_pop_2011=490,
                st_pop_2011=60,
                literacy_rate=80.5,
                ma_has_market=False,
                ma_has_haat=False,
                ma_bank_branch=False,
                ma_bc_point=False,
            )
            session.add_all([v1, v2, v3])
            await session.flush()

            vn1 = VillageNeighbour(lgd_code=555001, neighbour_lgd=555011, dist_km=3.52)
            vn2 = VillageNeighbour(lgd_code=555001, neighbour_lgd=555012, dist_km=4.17)
            session.add_all([vn1, vn2])
            print("Seeded villages (Shirwal, Khed Shivapur, Wing) and spatial neighbours.")

        # 5. Seed Scheme Versions from YAMLs
        schemes_dir = Path(__file__).resolve().parent / ".." / "data" / "schemes"
        if schemes_dir.exists():
            for yaml_path in schemes_dir.glob("*.yaml"):
                if yaml_path.name == "stacking.yaml":
                    continue
                try:
                    with open(yaml_path, encoding="utf-8") as f:
                        content = f.read()
                        data = yaml.safe_load(content)
                        code = data.get("scheme_code") or data.get("code")
                        if not code:
                            continue
                        ver = str(data.get("version", "1.0"))

                        res_sv = await session.execute(
                            select(SchemeVersion).where(SchemeVersion.scheme_code == code, SchemeVersion.version == ver)
                        )
                        if res_sv.scalar_one_or_none() is None:
                            status_val = SchemeStatus.VERIFIED
                            raw_st = str(data.get("status", "VERIFIED")).upper()
                            if "CONFLICT" in raw_st or "AGENCY" in raw_st:
                                status_val = SchemeStatus.CONFLICT
                            elif "UNVERIFIED" in raw_st or "STUB" in raw_st:
                                status_val = SchemeStatus.UNVERIFIED

                            sv = SchemeVersion(
                                scheme_code=code,
                                version=ver,
                                status=status_val,
                                rules_yaml=content,
                                source_url=str(data.get("source_url", "")),
                                source_date=str(data.get("source_date", "")),
                                published_by="System Admin",
                            )
                            session.add(sv)
                except Exception as e:
                    print(f"Warning parsing {yaml_path.name}: {type(e).__name__}")

        await session.commit()
        print("Database seeding completed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_and_seed_database())
