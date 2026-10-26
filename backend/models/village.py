from __future__ import annotations

from typing import Any
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base
from .enums import CoordSource, SectorType
from .spatial import SafeGeometry


class Village(Base):
    __tablename__ = "villages"

    lgd_code = Column(Integer, primary_key=True)
    name_en = Column(String(255), nullable=False, index=True)
    name_mr = Column(String(255), nullable=False, index=True)
    subdistrict_lgd = Column(Integer, nullable=False, index=True)
    subdistrict_name = Column(String(255), nullable=False)
    district_lgd = Column(Integer, nullable=False, index=True)
    district_name = Column(String(255), nullable=False)

    census2011_code = Column(String(50), nullable=True, index=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    coord_source = Column(Enum(CoordSource), nullable=True)

    pop_2011 = Column(Integer, nullable=True)
    households_2011 = Column(Integer, nullable=True)
    sc_pop_2011 = Column(Integer, nullable=True)
    st_pop_2011 = Column(Integer, nullable=True)
    literacy_rate = Column(Float, nullable=True)

    # Mission Antyodaya amenities
    ma_has_market = Column(Boolean, nullable=True)
    ma_has_haat = Column(Boolean, nullable=True)
    ma_haat_day = Column(String(50), nullable=True)
    ma_bank_branch = Column(Boolean, nullable=True)
    ma_bc_point = Column(Boolean, nullable=True)
    ma_power_hours = Column(Float, nullable=True)
    ma_all_weather_road = Column(Boolean, nullable=True)
    ma_milk_centre = Column(Boolean, nullable=True)
    ma_year = Column(Integer, nullable=True)

    geom = Column(SafeGeometry("POINT", srid=4326), nullable=True)

    cases = relationship("Case", back_populates="village")

    __table_args__: Any = (
        Index("ix_villages_subdistrict_district", "district_lgd", "subdistrict_lgd"),
    )


class VillageNeighbour(Base):
    __tablename__ = "village_neighbours"

    lgd_code = Column(Integer, ForeignKey("villages.lgd_code", ondelete="CASCADE"), primary_key=True)
    neighbour_lgd = Column(Integer, ForeignKey("villages.lgd_code", ondelete="CASCADE"), primary_key=True)
    dist_km = Column(Float, nullable=False)


class StateParam(Base):
    __tablename__ = "state_params"

    state = Column(String(50), primary_key=True)
    key = Column(String(100), primary_key=True)
    value = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)
    source = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)


class HcesShare(Base):
    __tablename__ = "hces_shares"

    state = Column(String(50), primary_key=True)
    sector = Column(Enum(SectorType), primary_key=True)
    category = Column(String(100), primary_key=True)
    share = Column(Float, nullable=False)
    source = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
