"""
Enterprise revenue models for the 10 v1 micro-enterprises.
Each model is a pure Python function calculating 100% capacity annual revenue.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from typing import Any


def compute_dairy_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Dairy revenue = animals × yield × lactation days × procurement price."""
    num_animals = Decimal(str(calib.get("num_animals", params["num_animals"]["value"])))
    daily_yield = Decimal(str(calib.get("daily_milk_yield_litres", params["daily_milk_yield_litres"]["value"])))
    lactation_days = Decimal(str(calib.get("lactation_days", params["lactation_days"]["value"])))
    price_per_litre = Decimal(str(calib.get("milk_procurement_price", params["milk_procurement_price"]["value"])))
    return num_animals * daily_yield * lactation_days * price_per_litre


def compute_goatery_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Goatery revenue = does × kids/kidding × (12 / interval) × (1 - mortality) × sale price."""
    num_does = Decimal(str(calib.get("num_does", params["num_does"]["value"])))
    kids_per_kidding = Decimal(str(calib.get("kids_per_kidding", params["kids_per_kidding"]["value"])))
    interval_months = Decimal(str(calib.get("kidding_interval_months", params["kidding_interval_months"]["value"])))
    mortality = Decimal(str(calib.get("kid_mortality_rate", params["kid_mortality_rate"]["value"])))
    sale_price = Decimal(str(calib.get("average_kid_sale_price", params["average_kid_sale_price"]["value"])))

    kiddings_per_year = Decimal("12") / interval_months
    surviving_kids_annual = num_does * kids_per_kidding * kiddings_per_year * (Decimal("1") - mortality)
    return surviving_kids_annual * sale_price


def compute_broiler_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Broiler revenue = batch size × batches/yr × (1 - mortality) × weight × price/kg."""
    batch_size = Decimal(str(calib.get("batch_size", params["batch_size"]["value"])))
    batches_yr = Decimal(str(calib.get("batches_per_year", params["batches_per_year"]["value"])))
    mortality = Decimal(str(calib.get("mortality_rate", params["mortality_rate"]["value"])))
    weight_kg = Decimal(str(calib.get("bird_sale_weight_kg", params["bird_sale_weight_kg"]["value"])))
    price_per_kg = Decimal(str(calib.get("live_bird_price_per_kg", params["live_bird_price_per_kg"]["value"])))

    surviving_birds = batch_size * batches_yr * (Decimal("1") - mortality)
    return surviving_birds * weight_kg * price_per_kg


def compute_kirana_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Kirana revenue = daily customers × average bill × operating days × 12."""
    daily_cust = Decimal(str(calib.get("daily_customers", params["daily_customers"]["value"])))
    avg_bill = Decimal(str(calib.get("average_bill_inr", params["average_bill_inr"]["value"])))
    days_month = Decimal(str(calib.get("operating_days_per_month", params["operating_days_per_month"]["value"])))
    return daily_cust * avg_bill * days_month * Decimal("12")


def compute_tailoring_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Tailoring revenue = jobs/day × stitching fee × working days × 12."""
    jobs = Decimal(str(calib.get("jobs_per_day", params["jobs_per_day"]["value"])))
    fee = Decimal(str(calib.get("average_stitching_fee", params["average_stitching_fee"]["value"])))
    days = Decimal(str(calib.get("working_days_per_month", params["working_days_per_month"]["value"])))
    return jobs * fee * days * Decimal("12")


def compute_beauty_parlour_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Beauty parlour revenue = daily clients × ticket size × working days × 12."""
    clients = Decimal(str(calib.get("daily_clients", params["daily_clients"]["value"])))
    ticket = Decimal(str(calib.get("average_ticket_inr", params["average_ticket_inr"]["value"])))
    days = Decimal(str(calib.get("working_days_per_month", params["working_days_per_month"]["value"])))
    return clients * ticket * days * Decimal("12")


def compute_mobile_repair_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Mobile repair revenue = (repairs × fee + accessories profit) × working days × 12."""
    repairs = Decimal(str(calib.get("daily_repairs", params["daily_repairs"]["value"])))
    fee = Decimal(str(calib.get("average_repair_margin", params["average_repair_margin"]["value"])))
    acc_profit = Decimal(str(calib.get("daily_accessories_profit", params["daily_accessories_profit"]["value"])))
    days = Decimal(str(calib.get("working_days_per_month", params["working_days_per_month"]["value"])))
    daily_income = (repairs * fee) + acc_profit
    return daily_income * days * Decimal("12")


def compute_flour_mill_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Flour mill revenue = (flour kg × rate + masala kg × rate) × operating days × 12."""
    flour_kg = Decimal(str(calib.get("daily_flour_milling_kg", params["daily_flour_milling_kg"]["value"])))
    flour_rate = Decimal(str(calib.get("milling_rate_per_kg", params["milling_rate_per_kg"]["value"])))
    masala_kg = Decimal(str(calib.get("daily_masala_milling_kg", params["daily_masala_milling_kg"]["value"])))
    masala_rate = Decimal(str(calib.get("masala_rate_per_kg", params["masala_rate_per_kg"]["value"])))
    days = Decimal(str(calib.get("working_days_per_month", params["working_days_per_month"]["value"])))
    daily_revenue = (flour_kg * flour_rate) + (masala_kg * masala_rate)
    return daily_revenue * days * Decimal("12")


def compute_papad_pickle_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Papad & pickle revenue = daily production kg × price/kg × production days × 12."""
    prod_kg = Decimal(str(calib.get("daily_production_kg", params["daily_production_kg"]["value"])))
    price = Decimal(str(calib.get("average_selling_price_per_kg", params["average_selling_price_per_kg"]["value"])))
    days = Decimal(str(calib.get("production_days_per_month", params["production_days_per_month"]["value"])))
    return prod_kg * price * days * Decimal("12")


def compute_two_wheeler_repair_revenue(params: dict[str, Any], calib: dict[str, Any]) -> Decimal:
    """Two-wheeler repair revenue = (vehicles × labour + spares margin) × working days × 12."""
    bikes = Decimal(str(calib.get("daily_vehicles_serviced", params["daily_vehicles_serviced"]["value"])))
    labour = Decimal(str(calib.get("average_labour_charge_per_bike", params["average_labour_charge_per_bike"]["value"])))
    spares_margin = Decimal(str(calib.get("daily_spare_parts_margin", params["daily_spare_parts_margin"]["value"])))
    days = Decimal(str(calib.get("working_days_per_month", params["working_days_per_month"]["value"])))
    daily_total = (bikes * labour) + spares_margin
    return daily_total * days * Decimal("12")


REVENUE_MODELS: dict[str, Callable[[dict[str, Any], dict[str, Any]], Decimal]] = {
    "dairy": compute_dairy_revenue,
    "goatery": compute_goatery_revenue,
    "broiler": compute_broiler_revenue,
    "kirana": compute_kirana_revenue,
    "tailoring": compute_tailoring_revenue,
    "beauty_parlour": compute_beauty_parlour_revenue,
    "mobile_repair": compute_mobile_repair_revenue,
    "flour_mill": compute_flour_mill_revenue,
    "papad_pickle": compute_papad_pickle_revenue,
    "two_wheeler_repair": compute_two_wheeler_repair_revenue,
}
