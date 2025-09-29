from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# ✔ Importá tu Base (ajusta el path real de tu proyecto)
# Ejemplos comunes (dejé varias alternativas):
# from maverik_backend.db.base import Base
# from maverik_backend.models import Base
from maverik_backend.core.database import create_engine_and_session_factory
from maverik_backend.settings import load_config

# Alembic config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === SETTINGS / URL desde tu config de app ===
app_cfg = load_config()

# Si usás pg8000 como driver (según tu requirements), arma la URL así:
DB_USER = app_cfg.db_username
DB_PASS = app_cfg.db_password
DB_HOST = app_cfg.db_host
DB_PORT = getattr(app_cfg, "db_port", 5432)
DB_NAME = app_cfg.db_name
DB_SCHEMA = getattr(app_cfg, "db_schema", "public")

SQLALCHEMY_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Inyectá la URL en la config de Alembic (sirve para offline y online)
config.set_main_option("sqlalchemy.url", SQLALCHEMY_URL)

# === METADATA para autogenerate ===
# IMPORTANTE: asegurate de que el import de Base traiga registradas TODAS las tablas.
try:
    from maverik_backend.db.base import Base  # <- AJUSTA AQUÍ si tu Base vive en otro módulo
except Exception:
    Base = None

target_metadata = Base.metadata if Base is not None else None

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,                 # útil si usas schema distinto a public
        version_table_schema=DB_SCHEMA if DB_SCHEMA else None,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        if DB_SCHEMA and DB_SCHEMA != "public":
            context.execute(f"SET search_path TO {DB_SCHEMA}")
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Si preferís reutilizar tu factory:
    engine, _ = create_engine_and_session_factory(
        username=DB_USER, password=DB_PASS, hostname=DB_HOST, database=DB_NAME, port=DB_PORT
    )
    with engine.connect() as connection:
        if DB_SCHEMA and DB_SCHEMA != "public":
            connection.execute(f"SET search_path TO {DB_SCHEMA}")
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=DB_SCHEMA if DB_SCHEMA else None,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()