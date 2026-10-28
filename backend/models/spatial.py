from typing import Any

from geoalchemy2.types import Geometry
from sqlalchemy.types import String, TypeDecorator


# Set at startup: True only after `CREATE EXTENSION postgis` succeeded.
POSTGIS_ENABLED = False


class SafeGeometry(TypeDecorator):
    """
    PostGIS Geometry type on PostgreSQL, falling back to String on SQLite and other dialects
    that do not have native spatial extensions loaded.
    Prevents missing 'RecoverGeometryColumn' errors during SQLite-based unit testing.
    """

    impl = String
    cache_ok = True

    def __init__(self, geometry_type: str = "POINT", srid: int = 4326, **kwargs: Any) -> None:
        self.geometry_type = geometry_type
        self.srid = srid
        super().__init__(**kwargs)

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect is None:
            return self.impl_instance
        if dialect.name == "postgresql" and POSTGIS_ENABLED:
            return dialect.type_descriptor(Geometry(self.geometry_type, srid=self.srid, spatial_index=False))
        return dialect.type_descriptor(String())
