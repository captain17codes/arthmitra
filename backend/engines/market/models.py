from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SaturationLevel(str, Enum):
    """Market saturation classification based on break-even market share."""
    LOW = "low"         # S <= 15%: strong local demand headroom
    MEDIUM = "medium"   # 15% < S <= 35%: moderate headroom, viability depends on differentiation
    HIGH = "high"       # S > 35%: saturated / high barrier, single unit needs excessive share


class MarketMetric(BaseModel):
    """A numerical market metric with point estimate, uncertainty range, and confidence."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: Decimal
    min_value: Decimal
    max_value: Decimal
    unit: str = ""
    confidence: str = "high"  # "high", "medium", "low"


class NeighbourInput(BaseModel):
    """Neighbouring village in catchment area."""
    lgd_code: int
    name_en: str
    pop_2011: int
    dist_km: float


class MarketInput(BaseModel):
    """Input payload for the market engine."""
    village_lgd: int
    village_name: str
    village_pop_2011: int
    business_code: str
    agent_competitor_count: int = Field(ge=0, description="Agent-observed active competitors in village catchment")
    neighbours: list[NeighbourInput] = Field(default_factory=list)
    calc_year: int = 2026
    district_name: str | None = "Pune"
    custom_growth_rate: Decimal | None = None
    custom_mpce: Decimal | None = None
    be_revenue_monthly: Decimal | None = None  # If passed from viability engine


class ComplementarySuggestion(BaseModel):
    """Complementary business alternative with lower saturation in catchment."""
    business_code: str
    name_en: str
    name_mr: str
    hces_category: str
    be_market_share: Decimal
    saturation_level: SaturationLevel
    monthly_demand: Decimal
    be_revenue_monthly: Decimal


class MarketResult(BaseModel):
    """Comprehensive output of the market sizing and saturation engine."""
    business_code: str
    village_lgd: int
    village_name: str
    calc_year: int

    # Demographic & Catchment
    population_now: MarketMetric
    catchment_population: MarketMetric

    # Category demand (₹/month)
    category_demand_monthly: MarketMetric

    # Competition (Agent observed, never OSM)
    competitor_count: MarketMetric
    demand_per_shop_monthly: MarketMetric

    # Viability & Saturation
    be_revenue_monthly: Decimal
    be_market_share: MarketMetric
    saturation_level: SaturationLevel

    # Complementary suggestions (populated especially when saturation is HIGH)
    complementary_suggestions: list[ComplementarySuggestion] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)
    explanation: str = ""
