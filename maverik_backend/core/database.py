import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker


def connect_tcp_socket(
    username: str,
    hostname: str,
    database: str,
    password: str | None = None,
    port: int | None = 5432,
) -> sqlalchemy.engine.base.Engine:
    connect_args = {}

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=username,
            password=password,
            host=hostname,
            port=port,
            database=database,
        ),
        connect_args=connect_args,
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
    )

    return pool


def create_engine_and_session_factory(
    username: str,
    hostname: str,
    database: str,
    password: str | None = None,
    port: int = 5432,
) -> tuple[sqlalchemy.engine.Engine, sessionmaker[Session]]:
    engine = connect_tcp_socket(
        username=username,
        password=password,
        hostname=hostname,
        database=database,
        port=port,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


def get_sessionmaker(app_config) -> sessionmaker[Session]:
    _, SessionLocal = create_engine_and_session_factory(
        username=app_config.db_username,
        password=app_config.db_password,
        hostname=app_config.db_host,
        database=app_config.db_name,
        port=app_config.db_port,
    )

    return SessionLocal
