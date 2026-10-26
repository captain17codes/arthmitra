from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal

from .config import (
    BUSINESS_MARKET_CONFIG,
    CIRCUITY_FACTOR,
    DEFAULT_DISTRICT_GROWTH_RATES,
    MAX_CATCHMENT_DISTANCE_KM,
    MPCE_MAHARASHTRA_RURAL,
)
from .models import (
    ComplementarySuggestion,
    MarketInput,
    MarketMetric,
    MarketResult,
    SaturationLevel,
)


def _round_decimal(val: Decimal, places: int = 2) -> Decimal:
    """Round Decimal using standard commercial half-up rounding."""
    q = Decimal("10") ** -places
    return val.quantize(q, rounding=ROUND_HALF_UP)


def get_growth_rates(district_name: str | None, custom_growth: Decimal | None = None) -> dict[str, Decimal]:
    """Resolve annual population growth rate (central, min, max)."""
    if custom_growth is not None:
        return {
            "central": custom_growth,
            "min": _round_decimal(custom_growth * Decimal("0.80"), 4),
            "max": _round_decimal(custom_growth * Decimal("1.20"), 4),
        }
    dist_key = (district_name or "default").strip().lower()
    return DEFAULT_DISTRICT_GROWTH_RATES.get(dist_key, DEFAULT_DISTRICT_GROWTH_RATES["default"])


def project_population(pop_2011: int, year: int, growth_rate: Decimal) -> Decimal:
    """
    Project village population from Census 2011 to current year.
    Formula: P_now = P_2011 * (1 + g)^(year - 2011)
    """
    years_elapsed = year - 2011
    if years_elapsed <= 0:
        return Decimal(pop_2011)
    factor = (Decimal("1") + growth_rate) ** years_elapsed
    return _round_decimal(Decimal(pop_2011) * factor, 0)


def calculate_catchment_population(
    v0_pop: Decimal,
    neighbours: list[tuple[Decimal, float]],
    decay_lambda: Decimal,
    circuity: Decimal,
) -> Decimal:
    """
    Calculate effective population in catchment using spatial distance-decay.
    Formula: P_catch = P_now(v0) + sum(P_now(vi) * exp(-lambda * circuity * d_euclid)) for d <= 10 km
    """
    effective_pop = float(v0_pop)
    circ_factor = float(circuity)
    lam = float(decay_lambda)

    for n_pop, dist_km in neighbours:
        if dist_km <= MAX_CATCHMENT_DISTANCE_KM:
            friction = math.exp(-lam * circ_factor * dist_km)
            effective_pop += float(n_pop) * friction

    return _round_decimal(Decimal(str(effective_pop)), 0)


def calculate_category_demand(
    catchment_pop: Decimal,
    mpce: Decimal,
    share: Decimal,
) -> Decimal:
    """
    Calculate monthly category consumption demand in the catchment.
    Formula: D = P_catch * MPCE_rural * share_category (₹/month)
    """
    demand = catchment_pop * mpce * share
    return _round_decimal(demand, 2)


def determine_saturation(be_share: Decimal) -> SaturationLevel:
    """
    Classify saturation band from break-even market share.
    Thresholds: S <= 15% -> Low, 15% < S <= 35% -> Medium, S > 35% -> High.
    """
    if be_share <= Decimal("0.15"):
        return SaturationLevel.LOW
    elif be_share <= Decimal("0.35"):
        return SaturationLevel.MEDIUM
    else:
        return SaturationLevel.HIGH


def rank_complementary_businesses(
    v0_pop_now: Decimal,
    neighbours_pop_now: list[tuple[Decimal, float]],
    current_business_code: str,
    mpce_central: Decimal,
) -> list[ComplementarySuggestion]:
    """
    Rank other eligible micro-businesses in the catchment by lowest break-even market share.
    Provides actionable pivot alternatives when current business exhibits high saturation.
    """
    suggestions: list[ComplementarySuggestion] = []

    for code, cfg in BUSINESS_MARKET_CONFIG.items():
        if code == current_business_code:
            continue

        c_pop = calculate_catchment_population(
            v0_pop=v0_pop_now,
            neighbours=neighbours_pop_now,
            decay_lambda=cfg["decay_lambda"],
            circuity=CIRCUITY_FACTOR["central"],
        )
        d_monthly = calculate_category_demand(
            catchment_pop=c_pop,
            mpce=mpce_central,
            share=cfg["share"],
        )

        be_rev = cfg["default_be_monthly"]
        be_share = _round_decimal(be_rev / d_monthly, 4) if d_monthly > 0 else Decimal("1.0000")
        sat_lvl = determine_saturation(be_share)

        suggestions.append(
            ComplementarySuggestion(
                business_code=code,
                name_en=cfg["name_en"],
                name_mr=cfg["name_mr"],
                hces_category=cfg["hces_category"],
                be_market_share=be_share,
                saturation_level=sat_lvl,
                monthly_demand=d_monthly,
                be_revenue_monthly=be_rev,
            )
        )

    # Sort ascending by be_market_share (lowest share requirement = highest headroom)
    suggestions.sort(key=lambda s: s.be_market_share)
    return suggestions[:3]


def evaluate_market(market_input: MarketInput) -> MarketResult:
    """
    Execute full market analysis for a proposed enterprise in a target village.
    Follows TECH_SPEC §6 with rigorous Decimal arithmetic, uncertainty ranges,
    and agent-verified competitor reporting (never OSM shop counts).
    """
    warnings: list[str] = []

    # 1. Resolve business config
    b_code = market_input.business_code.strip().lower()
    b_cfg = BUSINESS_MARKET_CONFIG.get(b_code)
    if b_cfg is None:
        raise ValueError(f"Unknown business code: '{b_code}'. Available: {list(BUSINESS_MARKET_CONFIG.keys())}")

    # 2. Population projection (central, min, max)
    g_rates = get_growth_rates(market_input.district_name, market_input.custom_growth_rate)
    year = market_input.calc_year

    pop_central = project_population(market_input.village_pop_2011, year, g_rates["central"])
    pop_min = project_population(market_input.village_pop_2011, year, g_rates["min"])
    pop_max = project_population(market_input.village_pop_2011, year, g_rates["max"])

    pop_metric = MarketMetric(
        value=pop_central,
        min_value=pop_min,
        max_value=pop_max,
        unit="persons",
        confidence="high" if market_input.village_pop_2011 > 0 else "medium",
    )

    # 3. Project neighbours population
    neighbours_central: list[tuple[Decimal, float]] = []
    neighbours_min: list[tuple[Decimal, float]] = []
    neighbours_max: list[tuple[Decimal, float]] = []

    for n in market_input.neighbours:
        n_central = project_population(n.pop_2011, year, g_rates["central"])
        n_min = project_population(n.pop_2011, year, g_rates["min"])
        n_max = project_population(n.pop_2011, year, g_rates["max"])
        neighbours_central.append((n_central, n.dist_km))
        neighbours_min.append((n_min, n.dist_km))
        neighbours_max.append((n_max, n.dist_km))

    # 4. Catchment population with distance-decay
    decay_lambda = b_cfg["decay_lambda"]

    catch_central = calculate_catchment_population(
        v0_pop=pop_central,
        neighbours=neighbours_central,
        decay_lambda=decay_lambda,
        circuity=CIRCUITY_FACTOR["central"],
    )
    catch_min = calculate_catchment_population(
        v0_pop=pop_min,
        neighbours=neighbours_min,
        decay_lambda=decay_lambda,
        circuity=CIRCUITY_FACTOR["max"],  # higher circuity -> higher friction -> lower catchment
    )
    catch_max = calculate_catchment_population(
        v0_pop=pop_max,
        neighbours=neighbours_max,
        decay_lambda=decay_lambda,
        circuity=CIRCUITY_FACTOR["min"],  # lower circuity -> lower friction -> higher catchment
    )

    catch_metric = MarketMetric(
        value=catch_central,
        min_value=catch_min,
        max_value=catch_max,
        unit="persons",
        confidence="high" if len(market_input.neighbours) > 0 else "medium",
    )

    # 5. Category monthly demand (₹/month)
    mpce_central = market_input.custom_mpce or MPCE_MAHARASHTRA_RURAL["central"]
    mpce_min = (
        _round_decimal(market_input.custom_mpce * Decimal("0.85"), 2)
        if market_input.custom_mpce
        else MPCE_MAHARASHTRA_RURAL["min"]
    )
    mpce_max = (
        _round_decimal(market_input.custom_mpce * Decimal("1.15"), 2)
        if market_input.custom_mpce
        else MPCE_MAHARASHTRA_RURAL["max"]
    )

    share = b_cfg["share"]
    d_central = calculate_category_demand(catch_central, mpce_central, share)
    d_min = calculate_category_demand(catch_min, mpce_min, share)
    d_max = calculate_category_demand(catch_max, mpce_max, share)

    demand_metric = MarketMetric(
        value=d_central,
        min_value=d_min,
        max_value=d_max,
        unit="INR/month",
        confidence="high",
    )

    # 6. Competitor count (Agent reported primary, range +/- 1, NEVER OSM)
    c_agent = market_input.agent_competitor_count
    c_min = Decimal(max(0, c_agent - 1))
    c_max = Decimal(c_agent + 1)
    c_central = Decimal(c_agent)

    competitor_metric = MarketMetric(
        value=c_central,
        min_value=c_min,
        max_value=c_max,
        unit="shops",
        confidence="high",
    )

    # 7. Demand per shop (with new entrant = c + 1)
    active_shops_central = c_central + Decimal("1")
    active_shops_min = c_min + Decimal("1")
    active_shops_max = c_max + Decimal("1")

    d_per_shop_central = _round_decimal(d_central / active_shops_central, 2)
    d_per_shop_min = _round_decimal(d_min / active_shops_max, 2)
    d_per_shop_max = _round_decimal(d_max / active_shops_min, 2)

    demand_per_shop_metric = MarketMetric(
        value=d_per_shop_central,
        min_value=d_per_shop_min,
        max_value=d_per_shop_max,
        unit="INR/month/shop",
        confidence="high",
    )

    # 8. Break-even monthly revenue & market share
    be_monthly = market_input.be_revenue_monthly or b_cfg["default_be_monthly"]
    be_share_central = _round_decimal(be_monthly / d_central, 4) if d_central > 0 else Decimal("1.0000")
    be_share_min = _round_decimal(be_monthly / d_max, 4) if d_max > 0 else Decimal("1.0000")
    be_share_max = _round_decimal(be_monthly / d_min, 4) if d_min > 0 else Decimal("1.0000")

    sat_level = determine_saturation(be_share_central)

    be_share_metric = MarketMetric(
        value=be_share_central,
        min_value=be_share_min,
        max_value=be_share_max,
        unit="ratio",
        confidence="high",
    )

    # 9. Warnings & Saturation Explanations
    explanation = (
        f"In {market_input.village_name}, projected catchment demand for {b_cfg['name_en']} "
        f"is ₹{d_central:,.2f}/month across an effective catchment of {catch_central:,.0f} persons. "
        f"With {c_agent} existing competitor(s) and this new entrant, estimated average monthly demand "
        f"is ₹{d_per_shop_central:,.2f}/shop. Required break-even monthly revenue is ₹{be_monthly:,.2f} "
        f"({be_share_central * Decimal('100'):.1f}% of total catchment demand), indicating {sat_level.value.upper()} saturation."
    )

    if sat_level == SaturationLevel.HIGH:
        warnings.append(
            f"High market saturation: Break-even requires {be_share_central * Decimal('100'):.1f}% "
            f"of total catchment demand (>35%). Consider recommended complementary businesses."
        )
    if c_agent >= 5:
        warnings.append(
            f"Dense local competition: {c_agent} existing units reported. Strong differentiation required."
        )
    if d_per_shop_central < be_monthly:
        warnings.append(
            f"Intense competition: Average demand per shop (₹{d_per_shop_central:,.2f}) is below break-even sales (₹{be_monthly:,.2f})."
        )

    # 10. Complementary business alternatives
    complementary = rank_complementary_businesses(
        v0_pop_now=pop_central,
        neighbours_pop_now=neighbours_central,
        current_business_code=b_code,
        mpce_central=mpce_central,
    )

    return MarketResult(
        business_code=b_code,
        village_lgd=market_input.village_lgd,
        village_name=market_input.village_name,
        calc_year=year,
        population_now=pop_metric,
        catchment_population=catch_metric,
        category_demand_monthly=demand_metric,
        competitor_count=competitor_metric,
        demand_per_shop_monthly=demand_per_shop_metric,
        be_revenue_monthly=be_monthly,
        be_market_share=be_share_metric,
        saturation_level=sat_level,
        complementary_suggestions=complementary,
        warnings=warnings,
        explanation=explanation,
    )
