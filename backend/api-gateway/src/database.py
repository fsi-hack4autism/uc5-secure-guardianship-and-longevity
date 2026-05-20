"""
Database configuration and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import logging

from config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = create_engine(
    settings.db_url,
    poolclass=NullPool if settings.app_env == "testing" else None,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


# Connection pool monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections"""
    logger.debug("Database connection established")


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections"""
    logger.debug("Database connection closed")
