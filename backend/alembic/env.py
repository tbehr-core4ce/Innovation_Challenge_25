import sys
from logging.config import fileConfig
from pathlib import Path

import geoalchemy2
from sqlalchemy import engine_from_config, pool

from alembic import context
from src.utils.settings import settings

backend_path = Path(__file__).parent.parent

sys.path.insert(0, str(backend_path))
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from src.core.logging import get_logger, setup_logging

setup_logging("INFO")

logger = get_logger("alembic.env")

# Import all models for 'autogenerate' support

from src.core.database import Base
from src.core.models import *  # Import all models

target_metadata = Base.metadata # This line is key!

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
        logger.info("Offline migrations completed")

def include_object(object, name, type_, reflected, compare_to):
    """
    Filter out PostGIS extension tables from Alembic's consideration.
    
    PostGIS creates system tables that should never be managed by Alembic:
    - spatial_ref_sys: Spatial reference system definitions
    - geometry_columns: Geometry column registry (if not using typmod)
    - geography_columns: Geography column registry
    - topology: Topology extension tables
    - layer: Topology layer definitions
    - Tiger geocoder tables: geocode_*, zip_*, tiger_*, loader_*, etc.
    """
    if type_ == "table":
        # Get schema
        schema = getattr(object, "schema", None)
        
        # Exclude tiger and tiger_data schemas entirely
        if schema in ("tiger", "tiger_data", "topology"):
            return False
        
        # PostGIS core system tables (always in public schema)
        postgis_system_tables = {
            'spatial_ref_sys',
            'geometry_columns',
            'geography_columns',
            'raster_columns',
            'raster_overviews'
        }
        
        # PostGIS topology extension tables
        topology_tables = {
            'topology',
            'layer'
        }
        
        # Tiger geocoder tables (partial list - match by prefix)
        tiger_prefixes = (
            'geocode_', 'zip_', 'tiger_', 'loader_',
            'pagc_', 'addrfeat', 'bg', 'tabblock',
            'county', 'cousub', 'edges', 'faces',
            'featnames', 'place', 'state', 'tract'
        )
        
        # Check exact matches
        if name in postgis_system_tables or name in topology_tables:
            return False
        
        # Check prefix matches
        if name.startswith(tiger_prefixes):
            return False
    
    return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    logger.info("Running migrations in online mode")
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=False, # Don't track other schemas AI-Generated
            compare_type=True, # AI-Generated
        )

        with context.begin_transaction():
            context.run_migrations()
            logger.info("Online migrations completed")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
