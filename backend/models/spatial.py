from typing import Any, Optional
from sqlalchemy.types import String, TypeDecorator
from geoalchemy2.types import Geometry


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
        if dialect is not None and dialect.name == "postgresql":
            return dialect.type_descriptor(Geometry(self.geometry_type, srid=self.srid, spatial_index=False))
        return dialect.type_descriptor(String())
