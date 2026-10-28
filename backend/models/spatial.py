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

    # geoalchemy2's PostgreSQL create/drop hooks read these attributes from any column that
    # resolves to Geometry. Without them, attribute lookup falls through to the String impl
    # and create_all() crashes with "'String' object has no attribute 'spatial_index'".
    # use_typmod=None => column is created inline (not via AddGeometryColumn);
    # spatial_index=False => no automatic GiST index (the column is not queried yet).
    spatial_index = False
    use_N_D_index = False
    use_typmod = None
    dimension = 2

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
