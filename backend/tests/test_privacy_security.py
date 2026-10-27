from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.privacy.deletion import execute_beneficiary_deletion
from app.privacy.retention import purge_expired_processing_logs
from app.security import hash_pin
from models.beneficiary import Beneficiary, Consent
from models.case import Advisory, Case, CaseInput, DprDocument, Evaluation
from models.enums import ConsentMethod, OrgType, UserRole
from models.governance import DeletionRequest, ProcessingLog
from models.organization import Organization, User


@pytest.fixture
async def privacy_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session_factory() as session:
        # Org & User
        org = Organization(id=1, name="District Advisory Unit", type=OrgType.NRLM, district_lgd=490)
        user = User(
            id=1,
            org_id=1,
            role=UserRole.AGENT,
            name="Bank Sakhi",
            phone="9876543210",
            pin_hash=hash_pin("1234"),
            lang="mr",
        )
        session.add_all([org, user])
        await session.flush()

        # Beneficiary with Consent
        b = Beneficiary(
            id=10,
            org_id=1,
            first_name="Sunita Shinde",
            gender="female",
            age=32,
            category="SC",
            income_band="below_1.5L",
            education_band="secondary_10th",
            created_by=1,
        )
        session.add(b)
        await session.flush()

        c = Consent(
            id=10,
            beneficiary_id=10,
            notice_version="1.0",
            language="mr",
            method=ConsentMethod.VOICE,
            audio_object_key="audio/consent_10.wav",
            audio_sha256="sha256_mock_audio_hash_1234",
            agent_id=1,
        )
        session.add(c)

        # Case with CaseInput, Evaluation, Advisory, DPR
        case = Case(
            id=20,
            beneficiary_id=10,
            village_lgd=555001,
            business_code="kirana",
            margin_available=Decimal("15000.00"),
            target_project_cost=Decimal("150000.00"),
            language="mr",
            created_by=1,
        )
        session.add(case)
        await session.flush()

        inp = CaseInput(
            case_id=20,
            key="monthly_turnover",
            value="45000",
            source="voice",
            transcript="पंचेचाळीस हजार",
        )
        session.add(inp)

        eval_rec = Evaluation(
            id=30,
            case_id=20,
            engine_version="1.0.0",
            scheme_versions={"PMEGP": "1.0.0"},
            benchmarks_version="1.0.0",
            input_snapshot={"project_cost": 150000},
            output={"dscr": 1.8},
        )
        session.add(eval_rec)
        await session.flush()

        adv = Advisory(
            id=40,
            evaluation_id=30,
            language="mr",
            model="gemini-2.0-flash",
            prompt_version="1.0",
            output={"market_reach": "चांगली मागणी आहे"},
            validator_passed=True,
        )
        dpr = DprDocument(
            id=50,
            evaluation_id=30,
            language="mr",
            object_key="dpr/case_20_mr.pdf",
            sha256="dpr_sha256_abcdef123456",
        )
        session.add_all([adv, dpr])

        # Processing Logs (must be preserved)
        plog = ProcessingLog(
            id=1,
            actor_id=1,
            purpose="CASE_EVALUATION",
            entity="beneficiary",
            entity_id="10",
        )
        session.add(plog)

        # Deletion Request
        d_req = DeletionRequest(
            id=1,
            beneficiary_id=10,
            by=1,
        )
        session.add(d_req)

        await session.commit()

    yield async_session_factory
    await engine.dispose()


@pytest.mark.asyncio
async def test_dpdp_deletion_workflow(privacy_db):
    """
    TECH_SPEC §2 acceptance test:
    Proves PII, consent audio, transcripts, advisories and DPRs are purged
    while statutory processing logs remain intact.
    """
    async with privacy_db() as session:
        # Execute deletion
        res = await execute_beneficiary_deletion(session, beneficiary_id=10, actor_id=1)
        assert res["pii_redacted"] is True
        assert res["consents_withdrawn"] == 1
        assert res["inputs_deleted"] >= 1
        assert res["advisories_deleted"] >= 1
        assert res["dprs_deleted"] >= 1

        # 1. Check Beneficiary PII
        b = (await session.execute(select(Beneficiary).where(Beneficiary.id == 10))).scalar_one()
        assert b.first_name == "REDACTED"
        assert b.deleted_at is not None

        # 2. Check Consent audio
        c = (await session.execute(select(Consent).where(Consent.beneficiary_id == 10))).scalar_one()
        assert c.audio_object_key is None
        assert c.audio_sha256 is None
        assert c.withdrawn_at is not None

        # 3. Check CaseInputs (transcripts) deleted
        inputs = (await session.execute(select(CaseInput).where(CaseInput.case_id == 20))).scalars().all()
        assert len(inputs) == 0

        # 4. Check Advisories & DPRs deleted
        advisories = (await session.execute(select(Advisory).where(Advisory.evaluation_id == 30))).scalars().all()
        assert len(advisories) == 0

        dprs = (await session.execute(select(DprDocument).where(DprDocument.evaluation_id == 30))).scalars().all()
        assert len(dprs) == 0

        # 5. Check DeletionRequest is marked completed
        del_req = (await session.execute(select(DeletionRequest).where(DeletionRequest.id == 1))).scalar_one()
        assert del_req.completed_at is not None

        # 6. CRUCIAL: Check processing_log is STILL PRESERVED (no content, purely metadata for 1 year)
        plogs = (await session.execute(select(ProcessingLog).where(ProcessingLog.entity_id == "10"))).scalars().all()
        assert len(plogs) == 1
        assert plogs[0].purpose == "CASE_EVALUATION"


@pytest.mark.asyncio
async def test_processing_log_retention_purge(privacy_db):
    """Confirm retention purge deletes logs > 365 days old and preserves newer logs."""
    async with privacy_db() as session:
        now = datetime.now(UTC)
        # Add old log (400 days old)
        old_log = ProcessingLog(
            id=100,
            actor_id=1,
            purpose="OLD_PURPOSE",
            entity="case",
            entity_id="999",
            at=now - timedelta(days=400),
        )
        # Add recent log (30 days old)
        recent_log = ProcessingLog(
            id=101,
            actor_id=1,
            purpose="RECENT_PURPOSE",
            entity="case",
            entity_id="999",
            at=now - timedelta(days=30),
        )
        session.add_all([old_log, recent_log])
        await session.commit()

        # Purge older than 365 days
        purged = await purge_expired_processing_logs(session, retention_days=365)
        assert purged >= 1

        # Verify old log is gone, recent log remains
        remaining = (await session.execute(select(ProcessingLog.id))).scalars().all()
        assert 100 not in remaining
        assert 101 in remaining


@pytest.mark.asyncio
async def test_security_headers_enforcement():
    """Verify security headers: X-Content-Type-Options, X-Frame-Options, HSTS."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        headers = resp.headers
        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "DENY"
        assert "max-age=63072000" in headers.get("strict-transport-security", "")
        assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
