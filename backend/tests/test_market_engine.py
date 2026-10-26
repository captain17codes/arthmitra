from __future__ import annotations

from decimal import Decimal

import pytest

from engines.market import (
    BUSINESS_MARKET_CONFIG,
    MarketInput,
    NeighbourInput,
    SaturationLevel,
    calculate_catchment_population,
    calculate_category_demand,
    determine_saturation,
    evaluate_market,
    project_population,
)


def test_population_projection():
    """Verify compound growth projection from Census 2011 to 2026."""
    pop_2011 = 10000
    g = Decimal("0.0135")  # Pune rural growth rate
    # 2026 - 2011 = 15 years
    expected = round(10000 * ((1 + 0.0135) ** 15))
    result = project_population(pop_2011, 2026, g)
    assert result == Decimal(expected)

    # Base year returns original population
    assert project_population(pop_2011, 2011, g) == Decimal(10000)


def test_catchment_distance_decay():
    """Verify spatial distance-decay calculation with 1.35 circuity factor."""
    v0_pop = Decimal("10000")
    # Neighbour at 4 km with decay lambda 0.28 (convenience)
    neighbours = [(Decimal("5000"), 4.0)]
    decay_lambda = Decimal("0.28")
    circuity = Decimal("1.35")

    catch = calculate_catchment_population(v0_pop, neighbours, decay_lambda, circuity)

    # Friction = exp(-0.28 * 1.35 * 4.0) = exp(-1.512) ≈ 0.22047
    # Additional pop ≈ 5000 * 0.22047 ≈ 1102
    assert catch > v0_pop
    assert catch < v0_pop + Decimal("5000")

    # Higher decay lambda (0.28) should give LOWER catchment than lower lambda (0.12)
    catch_repair = calculate_catchment_population(v0_pop, neighbours, Decimal("0.12"), circuity)
    assert catch_repair > catch

    # Neighbour beyond 10 km must be ignored
    far_neighbours = [(Decimal("5000"), 12.0)]
    catch_far = calculate_catchment_population(v0_pop, far_neighbours, decay_lambda, circuity)
    assert catch_far == v0_pop


def test_category_demand_per_person_mpce():
    """Verify category demand uses per-person MPCE and correct category shares."""
    catch_pop = Decimal("15000")
    mpce = Decimal("3322")
    share = Decimal("0.255")  # food_and_groceries

    demand = calculate_category_demand(catch_pop, mpce, share)
    expected = catch_pop * mpce * share
    assert demand == expected
    assert demand > 0


def test_saturation_bands():
    """Verify saturation classification thresholds (<=15% Low, 15-35% Medium, >35% High)."""
    assert determine_saturation(Decimal("0.08")) == SaturationLevel.LOW
    assert determine_saturation(Decimal("0.15")) == SaturationLevel.LOW
    assert determine_saturation(Decimal("0.1501")) == SaturationLevel.MEDIUM
    assert determine_saturation(Decimal("0.25")) == SaturationLevel.MEDIUM
    assert determine_saturation(Decimal("0.35")) == SaturationLevel.MEDIUM
    assert determine_saturation(Decimal("0.3501")) == SaturationLevel.HIGH
    assert determine_saturation(Decimal("0.65")) == SaturationLevel.HIGH


def test_competitor_invariants_never_osm():
    """Verify competitor count is strictly based on agent reporting with +/- 1 range."""
    m_input = MarketInput(
        village_lgd=555001,
        village_name="Shirwal",
        village_pop_2011=14250,
        business_code="kirana",
        agent_competitor_count=3,
        neighbours=[],
    )
    result = evaluate_market(m_input)

    assert result.competitor_count.value == Decimal("3")
    assert result.competitor_count.min_value == Decimal("2")
    assert result.competitor_count.max_value == Decimal("4")
    assert result.competitor_count.unit == "shops"

    # With 0 competitors, min_value cannot be negative
    m_input_zero = MarketInput(
        village_lgd=555001,
        village_name="Shirwal",
        village_pop_2011=14250,
        business_code="kirana",
        agent_competitor_count=0,
    )
    result_zero = evaluate_market(m_input_zero)
    assert result_zero.competitor_count.value == Decimal("0")
    assert result_zero.competitor_count.min_value == Decimal("0")
    assert result_zero.competitor_count.max_value == Decimal("1")


def test_uncertainty_ranges_and_ordering():
    """Verify that all metrics have min <= central <= max."""
    m_input = MarketInput(
        village_lgd=555001,
        village_name="Shirwal",
        village_pop_2011=14250,
        business_code="flour_mill",
        agent_competitor_count=2,
        neighbours=[
            NeighbourInput(lgd_code=555011, name_en="Palashi", pop_2011=2800, dist_km=3.52),
            NeighbourInput(lgd_code=555012, name_en="Wing", pop_2011=3400, dist_km=4.17),
        ],
    )
    result = evaluate_market(m_input)

    # Population
    assert result.population_now.min_value <= result.population_now.value <= result.population_now.max_value
    # Catchment
    assert result.catchment_population.min_value <= result.catchment_population.value <= result.catchment_population.max_value
    # Demand
    assert result.category_demand_monthly.min_value <= result.category_demand_monthly.value <= result.category_demand_monthly.max_value
    # Demand per shop
    assert result.demand_per_shop_monthly.min_value <= result.demand_per_shop_monthly.value <= result.demand_per_shop_monthly.max_value
    # Break-even share (higher demand leads to lower share, so min_share <= central <= max_share)
    assert result.be_market_share.min_value <= result.be_market_share.value <= result.be_market_share.max_value


def test_high_saturation_triggers_complementary_suggestions():
    """Verify that high saturation triggers warnings and complementary suggestions."""
    # Tiny hamlet (pop 300) with small demand, trying to open high break-even business
    m_input = MarketInput(
        village_lgd=999001,
        village_name="Chhoti Vasti",
        village_pop_2011=300,
        business_code="broiler",  # high break-even revenue ₹42,000
        agent_competitor_count=4,
        neighbours=[],
    )
    result = evaluate_market(m_input)

    assert result.saturation_level == SaturationLevel.HIGH
    assert len(result.warnings) > 0
    assert any("saturation" in w.lower() for w in result.warnings)

    # Must provide complementary recommendations
    assert len(result.complementary_suggestions) == 3
    # First suggestion must have lower break-even share than current business
    assert result.complementary_suggestions[0].be_market_share < result.be_market_share.value
    # Suggestions must be sorted ascending by required share
    assert (
        result.complementary_suggestions[0].be_market_share
        <= result.complementary_suggestions[1].be_market_share
        <= result.complementary_suggestions[2].be_market_share
    )


@pytest.mark.parametrize("village_data", [
    {
        "name": "Shirwal",
        "lgd": 555001,
        "pop": 14250,
        "district": "Pune",
        "neighbours": [
            NeighbourInput(lgd_code=555011, name_en="Palashi", pop_2011=2800, dist_km=3.52),
            NeighbourInput(lgd_code=555012, name_en="Wing", pop_2011=3400, dist_km=4.17),
        ],
    },
    {
        "name": "Khed Shivapur",
        "lgd": 555002,
        "pop": 8940,
        "district": "Pune",
        "neighbours": [
            NeighbourInput(lgd_code=555013, name_en="Shindewadi Haveli", pop_2011=4100, dist_km=2.44),
            NeighbourInput(lgd_code=555014, name_en="Kondhanpur", pop_2011=3200, dist_km=3.98),
        ],
    },
    {
        "name": "Saswad Rural",
        "lgd": 555003,
        "pop": 11200,
        "district": "Pune",
        "neighbours": [
            NeighbourInput(lgd_code=555015, name_en="Dive", pop_2011=4500, dist_km=5.23),
            NeighbourInput(lgd_code=555016, name_en="Sonori", pop_2011=3100, dist_km=4.16),
        ],
    },
])
def test_reference_villages_all_ten_businesses(village_data):
    """
    Snapshot / comprehensive coverage test for the 3 reference villages
    across all 10 V1 business benchmarks.
    """
    all_codes = list(BUSINESS_MARKET_CONFIG.keys())
    assert len(all_codes) == 10

    for b_code in all_codes:
        m_input = MarketInput(
            village_lgd=village_data["lgd"],
            village_name=village_data["name"],
            village_pop_2011=village_data["pop"],
            district_name=village_data["district"],
            business_code=b_code,
            agent_competitor_count=1,
            neighbours=village_data["neighbours"],
        )
        res = evaluate_market(m_input)

        # Basic validations
        assert res.business_code == b_code
        assert res.village_lgd == village_data["lgd"]
        assert res.population_now.value > Decimal(village_data["pop"])
        assert res.catchment_population.value > res.population_now.value
        assert res.category_demand_monthly.value > Decimal("0")
        assert res.be_market_share.value > Decimal("0")
        assert res.saturation_level in [SaturationLevel.LOW, SaturationLevel.MEDIUM, SaturationLevel.HIGH]
        assert len(res.complementary_suggestions) == 3
