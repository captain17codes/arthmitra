"""
Unit tests for full data model (TECH_SPEC §2) and seed data.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.seed import seed_all, V1_BUSINESS_TYPES, V1_SCHEMES
from models import (
    Organization,
    User,
    Village,
    VillageNeighbour,
    StateParam,
    HcesShare,
    BusinessType,
    Benchmark,
    Scheme,
    SchemeVersion,
    Beneficiary,
    Consent,
    Case,
    CaseInput,
    Evaluation,
    Advisory,
    DprDocument,
    AuditLog,
    ProcessingLog,
    DeletionRequest,
    OrgType,
    UserRole,
    CaseStatus,
    TriState,
    ConsentMethod,
    BusinessSector,
)


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_seed_and_models(async_session: AsyncSession):
    # 1. Test Seed All
    counts = await seed_all(async_session)
    assert counts["business_types_seeded"] == len(V1_BUSINESS_TYPES)
    assert counts["schemes_seeded"] == len(V1_SCHEMES)

    # Idempotent re-run
    counts2 = await seed_all(async_session)
    assert counts2["business_types_seeded"] == 0
    assert counts2["schemes_seeded"] == 0

    # 2. Verify Business Types & Schemes in DB
    bts = (await async_session.execute(select(BusinessType))).scalars().all()
    assert len(bts) == 10
    bt_codes = {b.code for b in bts}
    assert "dairy" in bt_codes
    assert "kirana" in bt_codes

    schemes = (await async_session.execute(select(Scheme))).scalars().all()
    assert len(schemes) == len(V1_SCHEMES)
    scheme_codes = {s.code for s in schemes}
    assert "NSFDC_MFS" in scheme_codes
    assert "PMEGP" in scheme_codes

    # 3. Create Organization & User
    org = Organization(name="UMED Pune District", type=OrgType.NRLM, district_lgd=490)
    async_session.add(org)
    await async_session.commit()
    await async_session.refresh(org)

    user = User(
        org_id=org.id,
        role=UserRole.AGENT,
        name="Sunita Kamble",
        phone="+919876543210",
        pin_hash="hashed_pin_test",
        lang="mr",
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    assert user.phone == "+919876543210"

    # 4. Create Village
    village = Village(
        lgd_code=555001,
        name_en="Shirwal",
        name_mr="शिरवळ",
        subdistrict_lgd=4200,
        subdistrict_name="Khandala",
        district_lgd=490,
        district_name="Pune",
        pop_2011=12500,
        ma_has_market=True,
    )
    async_session.add(village)
    await async_session.commit()

    # 5. Create Beneficiary with 🔒 encrypted first_name
    beneficiary = Beneficiary(
        org_id=org.id,
        first_name="आनंदा",
        gender="male",
        age=32,
        category="SC",
        category_verified=True,
        income_band="upto_3l",
        education_band="10th_pass",
        prior_subsidy=TriState.NO,
        credit_default=TriState.NO,
        created_by=user.id,
    )
    async_session.add(beneficiary)
    await async_session.commit()
    await async_session.refresh(beneficiary)

    assert beneficiary.first_name == "आनंदा"

    # 6. Create Consent
    consent = Consent(
        beneficiary_id=beneficiary.id,
        notice_version="1.0.0",
        language="mr",
        method=ConsentMethod.VOICE,
        audio_sha256="abcdef123456",
        agent_id=user.id,
    )
    async_session.add(consent)
    await async_session.commit()

    # 7. Create Case
    case = Case(
        beneficiary_id=beneficiary.id,
        village_lgd=village.lgd_code,
        business_code="kirana",
        margin_available=25000.0,
        target_project_cost=100000.0,
        language="mr",
        status=CaseStatus.DRAFT,
        created_by=user.id,
    )
    async_session.add(case)
    await async_session.commit()
    await async_session.refresh(case)

    assert case.id is not None
    assert case.status == CaseStatus.DRAFT

    # 8. Governance Logs
    p_log = ProcessingLog(actor_id=user.id, purpose="case_evaluation", entity="cases", entity_id=str(case.id))
    async_session.add(p_log)
    await async_session.commit()
    await async_session.refresh(p_log)
    assert p_log.purpose == "case_evaluation"
