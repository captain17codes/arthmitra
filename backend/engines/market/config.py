from __future__ import annotations

from decimal import Decimal
from typing import Any, TypedDict

# Annual population growth rate projections (Census 2011 to 2026+)
# Source: Office of the Registrar General & Census Commissioner, Population Projections Report for Maharashtra
DEFAULT_DISTRICT_GROWTH_RATES: dict[str, dict[str, Decimal]] = {
    "default": {
        "central": Decimal("0.0118"),
        "min": Decimal("0.0090"),
        "max": Decimal("0.0145"),
    },
    "pune": {
        "central": Decimal("0.0135"),
        "min": Decimal("0.0105"),
        "max": Decimal("0.0165"),
    },
    "satara": {
        "central": Decimal("0.0085"),
        "min": Decimal("0.0065"),
        "max": Decimal("0.0110"),
    },
    "solapur": {
        "central": Decimal("0.0105"),
        "min": Decimal("0.0080"),
        "max": Decimal("0.0130"),
    },
    "kolhapur": {
        "central": Decimal("0.0095"),
        "min": Decimal("0.0070"),
        "max": Decimal("0.0120"),
    },
    "ahmednagar": {
        "central": Decimal("0.0110"),
        "min": Decimal("0.0085"),
        "max": Decimal("0.0135"),
    },
    "nashik": {
        "central": Decimal("0.0125"),
        "min": Decimal("0.0095"),
        "max": Decimal("0.0155"),
    },
}

# Road circuity factor: converts straight-line Euclidean distance to road travel distance
CIRCUITY_FACTOR = {
    "central": Decimal("1.35"),
    "min": Decimal("1.20"),
    "max": Decimal("1.50"),
}

MAX_CATCHMENT_DISTANCE_KM = 10.0

class MPCERural(TypedDict):
    central: Decimal
    min: Decimal
    max: Decimal
    source: str


# MoSPI HCES 2023-24 Rural Maharashtra Monthly Per Capita Consumption Expenditure (₹/person/month)
MPCE_MAHARASHTRA_RURAL: MPCERural = {
    "central": Decimal("3322"),
    "min": Decimal("2950"),
    "max": Decimal("3850"),
    "source": "MoSPI Household Consumption Expenditure Survey (HCES) 2023-24",
}

# Business type configuration: HCES category, consumption share, decay lambda, and benchmark break-even revenue
BUSINESS_MARKET_CONFIG: dict[str, dict[str, Any]] = {
    "kirana": {
        "name_en": "Kirana / Grocery Store",
        "name_mr": "किराणा दुकान",
        "hces_category": "food_and_groceries",
        "share": Decimal("0.255"),
        "decay_lambda": Decimal("0.28"),
        "default_be_monthly": Decimal("45000"),
    },
    "flour_mill": {
        "name_en": "Flour & Masala Mill",
        "name_mr": "पिठाची व मसाल्याची गिरणी",
        "hces_category": "food_and_groceries",
        "share": Decimal("0.255"),
        "decay_lambda": Decimal("0.28"),
        "default_be_monthly": Decimal("22000"),
    },
    "papad_pickle": {
        "name_en": "Papad, Pickle & Snack Production",
        "name_mr": "पापड, लोणचे व फराळ निर्मिती",
        "hces_category": "processed_food",
        "share": Decimal("0.056"),
        "decay_lambda": Decimal("0.28"),
        "default_be_monthly": Decimal("25000"),
    },
    "tailoring": {
        "name_en": "Tailoring & Garment Making",
        "name_mr": "शिलाई व टेलरिंग",
        "hces_category": "clothing_and_bedding",
        "share": Decimal("0.054"),
        "decay_lambda": Decimal("0.18"),
        "default_be_monthly": Decimal("16000"),
    },
    "beauty_parlour": {
        "name_en": "Beauty Parlour & Grooming",
        "name_mr": "ब्युटी पार्लर",
        "hces_category": "personal_care_and_services",
        "share": Decimal("0.032"),
        "decay_lambda": Decimal("0.18"),
        "default_be_monthly": Decimal("18000"),
    },
    "dairy": {
        "name_en": "Dairy Farming (2 Animals)",
        "name_mr": "दुग्धव्यवसाय (२ जनावरे)",
        "hces_category": "milk_and_milk_products",
        "share": Decimal("0.083"),
        "decay_lambda": Decimal("0.18"),
        "default_be_monthly": Decimal("28000"),
    },
    "goatery": {
        "name_en": "Goat Rearing (10+1)",
        "name_mr": "शेळीपालन (१०+१)",
        "hces_category": "meat_and_poultry",
        "share": Decimal("0.049"),
        "decay_lambda": Decimal("0.18"),
        "default_be_monthly": Decimal("16000"),
    },
    "broiler": {
        "name_en": "Broiler Poultry Farming (Small Batch)",
        "name_mr": "कुक्कुटपालन (ब्रॉयलर)",
        "hces_category": "meat_and_poultry",
        "share": Decimal("0.049"),
        "decay_lambda": Decimal("0.18"),
        "default_be_monthly": Decimal("42000"),
    },
    "mobile_repair": {
        "name_en": "Mobile Phone Repair & Accessories",
        "name_mr": "मोबाईल दुरुस्ती",
        "hces_category": "repair_and_maintenance",
        "share": Decimal("0.042"),
        "decay_lambda": Decimal("0.12"),
        "default_be_monthly": Decimal("24000"),
    },
    "two_wheeler_repair": {
        "name_en": "Two-Wheeler Servicing & Repair",
        "name_mr": "दुचाकी दुरुस्ती गॅरेज",
        "hces_category": "repair_and_maintenance",
        "share": Decimal("0.042"),
        "decay_lambda": Decimal("0.12"),
        "default_be_monthly": Decimal("26000"),
    },
}
