"""
Seed initial knowledge base tables:
10 v1 businesses with mr/hi/en names, sector, HCES category, decay_lambda
and scheme catalog codes per TECH_SPEC §2.
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.business_type import BusinessType
from models.enums import BusinessSector
from models.scheme import Scheme

V1_BUSINESS_TYPES = [
    {
        "code": "dairy",
        "name_en": "Dairy Farming (2 Animals)",
        "name_mr": "दुग्धव्यवसाय (२ जनावरे)",
        "name_hi": "डेयरी व्यवसाय (२ पशु)",
        "sector": BusinessSector.AGRI_ALLIED,
        "hces_category": "milk_and_milk_products",
        "decay_lambda": 0.18,
        "icon": "cow",
    },
    {
        "code": "goatery",
        "name_en": "Goat Rearing (10+1)",
        "name_mr": "शेळीपालन (१०+१)",
        "name_hi": "बकरी पालन (१०+१)",
        "sector": BusinessSector.AGRI_ALLIED,
        "hces_category": "meat_and_poultry",
        "decay_lambda": 0.18,
        "icon": "sheep",
    },
    {
        "code": "broiler",
        "name_en": "Broiler Poultry Farming (Small Batch)",
        "name_mr": "कुक्कुटपालन (ब्रॉयलर)",
        "name_hi": "मुर्गी पालन (ब्रायलर)",
        "sector": BusinessSector.AGRI_ALLIED,
        "hces_category": "meat_and_poultry",
        "decay_lambda": 0.18,
        "icon": "drumstick",
    },
    {
        "code": "kirana",
        "name_en": "Kirana / Grocery Store",
        "name_mr": "किराणा दुकान",
        "name_hi": "किराना दुकान",
        "sector": BusinessSector.TRADING,
        "hces_category": "food_and_groceries",
        "decay_lambda": 0.28,
        "icon": "shopping-cart",
    },
    {
        "code": "tailoring",
        "name_en": "Tailoring & Garment Making",
        "name_mr": "शिलाई व टेलरिंग",
        "name_hi": "सिलाई और वस्त्र निर्माण",
        "sector": BusinessSector.SERVICE,
        "hces_category": "clothing_and_bedding",
        "decay_lambda": 0.18,
        "icon": "scissors",
    },
    {
        "code": "beauty_parlour",
        "name_en": "Beauty Parlour & Grooming",
        "name_mr": "ब्युटी पार्लर",
        "name_hi": "ब्यूटी पार्लर",
        "sector": BusinessSector.SERVICE,
        "hces_category": "personal_care_and_services",
        "decay_lambda": 0.18,
        "icon": "sparkles",
    },
    {
        "code": "mobile_repair",
        "name_en": "Mobile Phone Repair & Accessories",
        "name_mr": "मोबाईल दुरुस्ती",
        "name_hi": "मोबाइल रिपेयरिंग",
        "sector": BusinessSector.SERVICE,
        "hces_category": "repair_and_maintenance",
        "decay_lambda": 0.12,
        "icon": "smartphone",
    },
    {
        "code": "flour_mill",
        "name_en": "Flour & Masala Mill",
        "name_mr": "पिठाची व मसाल्याची गिरणी",
        "name_hi": "आटा एवं मसाला चक्की",
        "sector": BusinessSector.MANUFACTURING,
        "hces_category": "food_and_groceries",
        "decay_lambda": 0.28,
        "icon": "cog",
    },
    {
        "code": "papad_pickle",
        "name_en": "Papad, Pickle & Snack Production",
        "name_mr": "पापड, लोणचे व फराळ निर्मिती",
        "name_hi": "पापड़, अचार व नाश्ता निर्माण",
        "sector": BusinessSector.MANUFACTURING,
        "hces_category": "processed_food",
        "decay_lambda": 0.28,
        "icon": "cookie",
    },
    {
        "code": "two_wheeler_repair",
        "name_en": "Two-Wheeler Servicing & Repair",
        "name_mr": "दुचाकी दुरुस्ती गॅरेज",
        "name_hi": "दोपहिया वाहन मरम्मत",
        "sector": BusinessSector.SERVICE,
        "hces_category": "repair_and_maintenance",
        "decay_lambda": 0.12,
        "icon": "wrench",
    },
]

V1_SCHEMES = [
    {
        "code": "NSFDC_MFS",
        "name_en": "NSFDC Micro Finance Scheme",
        "name_mr": "एनएसएफडीसी सूक्ष्म वित्त योजना",
        "agency": "NSFDC",
        "channel": "SCA / PSB / RRB",
        "portal_url": "https://devmosje.negd.in/?p=15629",
    },
    {
        "code": "NSFDC_TL",
        "name_en": "NSFDC Term Loan",
        "name_mr": "एनएसएफडीसी मुदत कर्ज योजना",
        "agency": "NSFDC",
        "channel": "SCA / PSB / RRB",
        "portal_url": "https://devmosje.negd.in/?p=15629",
    },
    {
        "code": "PMEGP",
        "name_en": "Prime Minister Employment Generation Programme",
        "name_mr": "पंतप्रधान रोजगार निर्मिती कार्यक्रम (PMEGP)",
        "agency": "KVIC / MSME",
        "channel": "Banks",
        "portal_url": "https://www.kviconline.gov.in/pmegpeportal/",
    },
    {
        "code": "CMEGP",
        "name_en": "Chief Minister Employment Generation Programme (Maharashtra)",
        "name_mr": "मुख्यमंत्री रोजगार निर्मिती कार्यक्रम (CMEGP)",
        "agency": "Maharashtra DIC",
        "channel": "Banks",
        "portal_url": "https://maha-cmegp.gov.in/",
    },
    {
        "code": "MUDRA_SHISHU",
        "name_en": "Pradhan Mantri Mudra Yojana - Shishu",
        "name_mr": "मुद्रा योजना - शिशु (५० हजार पर्यंत)",
        "agency": "PMMY / MUDRA",
        "channel": "Commercial Banks / RRBs / MFIs",
        "portal_url": "https://www.mudra.org.in/",
    },
    {
        "code": "MUDRA_KISHOR",
        "name_en": "Pradhan Mantri Mudra Yojana - Kishor",
        "name_mr": "मुद्रा योजना - किशोर (५० हजार ते ५ लाख)",
        "agency": "PMMY / MUDRA",
        "channel": "Commercial Banks / RRBs / MFIs",
        "portal_url": "https://www.mudra.org.in/",
    },
    {
        "code": "MUDRA_TARUN",
        "name_en": "Pradhan Mantri Mudra Yojana - Tarun",
        "name_mr": "मुद्रा योजना - तरुण (५ लाख ते १० लाख)",
        "agency": "PMMY / MUDRA",
        "channel": "Commercial Banks / RRBs / MFIs",
        "portal_url": "https://www.mudra.org.in/",
    },
    {
        "code": "MUDRA_TARUN_PLUS",
        "name_en": "Pradhan Mantri Mudra Yojana - Tarun Plus",
        "name_mr": "मुद्रा योजना - तरुण प्लस (१० लाख ते २० लाख)",
        "agency": "PMMY / MUDRA",
        "channel": "Commercial Banks / RRBs / MFIs",
        "portal_url": "https://www.mudra.org.in/",
    },
    {
        "code": "STANDUP_INDIA",
        "name_en": "Stand-Up India Scheme",
        "name_mr": "स्टँड-अप इंडिया योजना (१० लाख ते १ कोटी)",
        "agency": "SIDBI / DFS",
        "channel": "Scheduled Commercial Banks",
        "portal_url": "https://www.standupmitra.in/",
    },
    {
        "code": "MPBCDC_SEED",
        "name_en": "MPBCDC Seed Capital Scheme",
        "name_mr": "महात्मा फुले महामंडळ बीज भांडवल योजना",
        "agency": "MPBCDC (Maharashtra)",
        "channel": "District MPBCDC / Banks",
        "portal_url": "https://mahabharti.in/yojana/margin-money-scheme-for-backward-class/",
    },
    {
        "code": "DAY_NRLM_SHG",
        "name_en": "DAY-NRLM Women SHG Interest Subvention",
        "name_mr": "दीनदयाळ अंत्योदय योजना - राष्ट्रीय ग्रामीण उपजीविका अभियान (NRLM)",
        "agency": "MoRD / UMED",
        "channel": "Bank Linkage",
        "portal_url": "https://nrlm.gov.in/",
    },
    {
        "code": "NBCFDC_GL",
        "name_en": "NBCFDC General Loan Scheme",
        "name_mr": "एनबीसीएफडीसी सर्वसाधारण मुदत कर्ज",
        "agency": "NBCFDC",
        "channel": "SCAs / Banks",
        "portal_url": "https://nbcfdc.gov.in/",
    },
    {
        "code": "NSKFDC",
        "name_en": "NSKFDC Term Loan (Safai Karamcharis)",
        "name_mr": "राष्ट्रीय सफाई कर्मचारी वित्त महामंडळ योजना",
        "agency": "NSKFDC",
        "channel": "SCAs / RRBs",
        "portal_url": "https://nskfdc.nic.in/",
    },
    {
        "code": "NDFDC",
        "name_en": "NDFDC Divyangjan Loan Scheme",
        "name_mr": "राष्ट्रीय दिव्यांगजन वित्त महामंडळ योजना",
        "agency": "NDFDC",
        "channel": "SCAs / Banks",
        "portal_url": "https://www.nhfdc.nic.in/",
    },
    {
        "code": "LIDCOM",
        "name_en": "LIDCOM Leather Artisans Scheme",
        "name_mr": "संत रोहिदास चर्मोद्योग व चर्मकार विकास महामंडळ",
        "agency": "LIDCOM (Maharashtra)",
        "channel": "LIDCOM / Banks",
        "portal_url": "https://sjsa.maharashtra.gov.in/",
    },
    {
        "code": "LASDC",
        "name_en": "Lokshahir Annabhau Sathe Dev Corp Scheme",
        "name_mr": "लोकशाहीर अण्णाभाऊ साठे विकास महामंडळ",
        "agency": "LASDC (Maharashtra)",
        "channel": "LASDC / Banks",
        "portal_url": "https://sjsa.maharashtra.gov.in/",
    },
    {
        "code": "VNVJNTDC",
        "name_en": "Vasantrao Naik VJNT Dev Corp Scheme",
        "name_mr": "वसंतराव नाईक विमुक्त जाती व भटक्या जमाती विकास महामंडळ",
        "agency": "VNVJNTDC (Maharashtra)",
        "channel": "VNVJNTDC / Banks",
        "portal_url": "https://sjsa.maharashtra.gov.in/",
    },
    {
        "code": "ANNASAHEB_PATIL",
        "name_en": "Annasaheb Patil Arthik Vikas Mahamandal Scheme",
        "name_mr": "अण्णासाहेब पाटील आर्थिक मागास विकास महामंडळ",
        "agency": "APAVM (Maharashtra)",
        "channel": "Banks with Interest Subvention",
        "portal_url": "https://sjsa.maharashtra.gov.in/",
    },
]


async def seed_business_types(session: AsyncSession) -> int:
    """Seed the 10 v1 business types if not already present."""
    count = 0
    for bt_data in V1_BUSINESS_TYPES:
        res = await session.execute(select(BusinessType).where(BusinessType.code == bt_data["code"]))
        if res.scalar_one_or_none() is None:
            bt = BusinessType(**bt_data)
            session.add(bt)
            count += 1
    await session.commit()
    return count


async def seed_schemes(session: AsyncSession) -> int:
    """Seed the scheme catalog codes if not already present."""
    count = 0
    for sc_data in V1_SCHEMES:
        res = await session.execute(select(Scheme).where(Scheme.code == sc_data["code"]))
        if res.scalar_one_or_none() is None:
            sc = Scheme(**sc_data)
            session.add(sc)
            count += 1
    await session.commit()
    return count


async def seed_all(session: AsyncSession) -> dict[str, int]:
    bt_count = await seed_business_types(session)
    sc_count = await seed_schemes(session)
    return {"business_types_seeded": bt_count, "schemes_seeded": sc_count}
