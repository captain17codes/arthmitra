"""initial schema matching TECH_SPEC §2

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-27 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 1. organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.Enum("nrlm", "csc", "ngo", "sca", "other", name="orgtype"), nullable=False),
        sa.Column("district_lgd", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_organizations_district_lgd", "organizations", ["district_lgd"])

    # 2. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("agent", "supervisor", "admin", name="userrole"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(256), nullable=False),
        sa.Column("pin_hash", sa.String(255), nullable=False),
        sa.Column("lang", sa.String(10), nullable=False, server_default="mr"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])
    op.create_index("ix_users_role", "users", ["role"])

    # 3. villages
    op.create_table(
        "villages",
        sa.Column("lgd_code", sa.Integer(), primary_key=True),
        sa.Column("name_en", sa.String(255), nullable=False),
        sa.Column("name_mr", sa.String(255), nullable=False),
        sa.Column("subdistrict_lgd", sa.Integer(), nullable=False),
        sa.Column("subdistrict_name", sa.String(255), nullable=False),
        sa.Column("district_lgd", sa.Integer(), nullable=False),
        sa.Column("district_name", sa.String(255), nullable=False),
        sa.Column("census2011_code", sa.String(50), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("coord_source", sa.Enum("osm", "manual", "other", name="coordsource"), nullable=True),
        sa.Column("pop_2011", sa.Integer(), nullable=True),
        sa.Column("households_2011", sa.Integer(), nullable=True),
        sa.Column("sc_pop_2011", sa.Integer(), nullable=True),
        sa.Column("st_pop_2011", sa.Integer(), nullable=True),
        sa.Column("literacy_rate", sa.Float(), nullable=True),
        sa.Column("ma_has_market", sa.Boolean(), nullable=True),
        sa.Column("ma_has_haat", sa.Boolean(), nullable=True),
        sa.Column("ma_haat_day", sa.String(50), nullable=True),
        sa.Column("ma_bank_branch", sa.Boolean(), nullable=True),
        sa.Column("ma_bc_point", sa.Boolean(), nullable=True),
        sa.Column("ma_power_hours", sa.Float(), nullable=True),
        sa.Column("ma_all_weather_road", sa.Boolean(), nullable=True),
        sa.Column("ma_milk_centre", sa.Boolean(), nullable=True),
        sa.Column("ma_year", sa.Integer(), nullable=True),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326) if dialect == "postgresql" else sa.String(), nullable=True),
    )
    op.create_index("ix_villages_name_en", "villages", ["name_en"])
    op.create_index("ix_villages_name_mr", "villages", ["name_mr"])
    op.create_index("ix_villages_district_lgd", "villages", ["district_lgd"])
    op.create_index("ix_villages_subdistrict_lgd", "villages", ["subdistrict_lgd"])
    op.create_index("ix_villages_subdistrict_district", "villages", ["district_lgd", "subdistrict_lgd"])

    if dialect == "postgresql":
        op.execute("CREATE INDEX ix_villages_name_mr_trgm ON villages USING gin (name_mr gin_trgm_ops);")
        op.execute("CREATE INDEX ix_villages_name_en_trgm ON villages USING gin (name_en gin_trgm_ops);")

    # 4. village_neighbours
    op.create_table(
        "village_neighbours",
        sa.Column("lgd_code", sa.Integer(), sa.ForeignKey("villages.lgd_code", ondelete="CASCADE"), primary_key=True),
        sa.Column("neighbour_lgd", sa.Integer(), sa.ForeignKey("villages.lgd_code", ondelete="CASCADE"), primary_key=True),
        sa.Column("dist_km", sa.Float(), nullable=False),
    )

    # 5. state_params
    op.create_table(
        "state_params",
        sa.Column("state", sa.String(50), primary_key=True),
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
    )

    # 6. hces_shares
    op.create_table(
        "hces_shares",
        sa.Column("state", sa.String(50), primary_key=True),
        sa.Column("sector", sa.Enum("rural", "urban", name="sectortype"), primary_key=True),
        sa.Column("category", sa.String(100), primary_key=True),
        sa.Column("share", sa.Float(), nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
    )

    # 7. business_types
    op.create_table(
        "business_types",
        sa.Column("code", sa.String(50), primary_key=True),
        sa.Column("name_en", sa.String(255), nullable=False),
        sa.Column("name_mr", sa.String(255), nullable=False),
        sa.Column("name_hi", sa.String(255), nullable=False),
        sa.Column("sector", sa.Enum("manufacturing", "service", "trading", "agri_allied", name="businesssector"), nullable=False),
        sa.Column("hces_category", sa.String(100), nullable=False),
        sa.Column("decay_lambda", sa.Float(), nullable=False, server_default="0.18"),
        sa.Column("icon", sa.String(100), nullable=True),
    )

    # 8. benchmarks
    op.create_table(
        "benchmarks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("business_code", sa.String(50), sa.ForeignKey("business_types.code", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Numeric(14, 2), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("source_title", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("source_year", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Enum("official", "secondary", "estimate", name="benchmarkconfidence"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False, server_default="1.0.0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_benchmarks_business_code", "benchmarks", ["business_code"])
    op.create_index("ix_benchmarks_key", "benchmarks", ["key"])

    # 9. schemes
    op.create_table(
        "schemes",
        sa.Column("code", sa.String(50), primary_key=True),
        sa.Column("name_en", sa.String(255), nullable=False),
        sa.Column("name_mr", sa.String(255), nullable=False),
        sa.Column("agency", sa.String(255), nullable=False),
        sa.Column("channel", sa.String(255), nullable=False),
        sa.Column("portal_url", sa.String(500), nullable=True),
    )

    # 10. scheme_versions
    op.create_table(
        "scheme_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scheme_code", sa.String(50), sa.ForeignKey("schemes.code", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("status", sa.Enum("verified", "conflict", "unverified", "retired", name="schemestatus"), nullable=False),
        sa.Column("rules_yaml", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("source_date", sa.String(50), nullable=True),
        sa.Column("effective_from", sa.String(50), nullable=True),
        sa.Column("published_by", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scheme_versions_scheme_code", "scheme_versions", ["scheme_code"])

    # 11. beneficiaries
    op.create_table(
        "beneficiaries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("first_name", sa.String(256), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("category_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("disability_40", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("occupation_flags", sa.JSON(), nullable=True),
        sa.Column("income_band", sa.String(50), nullable=False),
        sa.Column("education_band", sa.String(50), nullable=False),
        sa.Column("shg_member", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("prior_subsidy", sa.Enum("yes", "no", "unknown", name="tristate"), nullable=False),
        sa.Column("credit_default", sa.Enum("yes", "no", "unknown", name="tristate"), nullable=False),
        sa.Column("existing_emi_monthly", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_beneficiaries_org_id", "beneficiaries", ["org_id"])

    # 12. consents
    op.create_table(
        "consents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("beneficiary_id", sa.Integer(), sa.ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notice_version", sa.String(50), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="mr"),
        sa.Column("method", sa.Enum("voice", "tap", name="consentmethod"), nullable=False),
        sa.Column("audio_object_key", sa.String(512), nullable=True),
        sa.Column("audio_sha256", sa.String(64), nullable=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_index("ix_consents_beneficiary_id", "consents", ["beneficiary_id"])

    # 13. cases
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("beneficiary_id", sa.Integer(), sa.ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("village_lgd", sa.Integer(), sa.ForeignKey("villages.lgd_code"), nullable=False),
        sa.Column("business_code", sa.String(50), sa.ForeignKey("business_types.code"), nullable=False),
        sa.Column("margin_available", sa.Numeric(14, 2), nullable=False),
        sa.Column("target_project_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="mr"),
        sa.Column("status", sa.Enum("draft", "ready", "dpr_generated", "applied", "sanctioned", "rejected", "disbursed", "closed", name="casestatus"), nullable=False),
        sa.Column("status_reason_code", sa.String(100), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_created_by", "cases", ["created_by"])
    op.create_index("ix_cases_status_created_by", "cases", ["status", "created_by"])

    # 14. case_inputs
    op.create_table(
        "case_inputs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("source", sa.Enum("agent", "default", "voice", name="inputsource"), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_case_inputs_case_id", "case_inputs", ["case_id"])
    op.create_index("ix_case_inputs_key", "case_inputs", ["key"])

    # 15. evaluations
    op.create_table(
        "evaluations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_version", sa.String(50), nullable=False),
        sa.Column("scheme_versions", sa.JSON(), nullable=False),
        sa.Column("benchmarks_version", sa.String(50), nullable=False),
        sa.Column("input_snapshot", sa.JSON(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evaluations_case_id", "evaluations", ["case_id"])

    # 16. advisories
    op.create_table(
        "advisories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("evaluation_id", sa.Integer(), sa.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="mr"),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("prompt_version", sa.String(50), nullable=False),
        sa.Column("output", sa.JSON(), nullable=False),
        sa.Column("validator_passed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_advisories_evaluation_id", "advisories", ["evaluation_id"])

    # 17. dpr_documents
    op.create_table(
        "dpr_documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("evaluation_id", sa.Integer(), sa.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(10), nullable=False),
        sa.Column("object_key", sa.String(255), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_dpr_documents_evaluation_id", "dpr_documents", ["evaluation_id"])

    # 18. audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=False),
        sa.Column("diff", sa.JSON(), nullable=True),
        sa.Column("at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])
    op.create_index("ix_audit_log_entity", "audit_log", ["entity"])
    op.create_index("ix_audit_log_at", "audit_log", ["at"])

    # 19. processing_log
    op.create_table(
        "processing_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("purpose", sa.String(255), nullable=False),
        sa.Column("entity", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_processing_log_actor_id", "processing_log", ["actor_id"])
    op.create_index("ix_processing_log_at", "processing_log", ["at"])

    # 20. deletion_requests
    op.create_table(
        "deletion_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("by", sa.Integer(), nullable=False),
    )
    op.create_index("ix_deletion_requests_beneficiary_id", "deletion_requests", ["beneficiary_id"])


def downgrade() -> None:
    op.drop_table("deletion_requests")
    op.drop_table("processing_log")
    op.drop_table("audit_log")
    op.drop_table("dpr_documents")
    op.drop_table("advisories")
    op.drop_table("evaluations")
    op.drop_table("case_inputs")
    op.drop_table("cases")
    op.drop_table("consents")
    op.drop_table("beneficiaries")
    op.drop_table("scheme_versions")
    op.drop_table("schemes")
    op.drop_table("benchmarks")
    op.drop_table("business_types")
    op.drop_table("hces_shares")
    op.drop_table("state_params")
    op.drop_table("village_neighbours")
    op.drop_table("villages")
    op.drop_table("users")
    op.drop_table("organizations")
