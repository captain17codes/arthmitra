from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ThreatItem(BaseModel):
    risk: str
    type: str  # market, financial, operational, climate
    mitigation: str


class PricingItem(BaseModel):
    item: str
    benchmark_price: str
    unit: str
    rationale: str


class PricingStrategy(BaseModel):
    strategy: str
    items: list[PricingItem] = Field(default_factory=list)


class SWOT(BaseModel):
    s: list[str] = Field(default_factory=list, description="Strengths")
    w: list[str] = Field(default_factory=list, description="Weaknesses")
    o: list[str] = Field(default_factory=list, description="Opportunities")
    t: list[str] = Field(default_factory=list, description="Threats")


class AdvisoryOutput(BaseModel):
    """Strict JSON schema required by TECH_SPEC §7.1."""
    market_reach: str
    opportunities: list[str] = Field(default_factory=list)
    swot: SWOT
    threats: list[ThreatItem] = Field(default_factory=list)
    pricing: PricingStrategy
    complementary: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class FactItem(BaseModel):
    id: str
    label: str
    value: Any
    unit: str | None = None
    confidence: str | None = None


class EvaluationFacts(BaseModel):
    """Structured facts extracted from Evaluation snapshot for LLM grounding."""
    case_id: int
    business_code: str
    business_name: dict[str, str]
    village_name: str
    language: str
    facts: list[FactItem]
    allowed_numbers: list[float]
