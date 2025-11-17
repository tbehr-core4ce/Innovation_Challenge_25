"""
Database configuration and connection management for BETS.
backend/src/core/database.py
"""

import os
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.utils.settings import settings

from .logging import get_logger

DATABASE_URL = settings.DATABASE_URL

logger = get_logger(__name__)

# Database URL from environment variable



# Create SQLAlchemy engine
# For production, adjust pool settings as needed
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,          # Number of connections to maintain
    max_overflow=10,      # Max connections beyond pool_size
    echo=False,           # Set to True for SQL query logging (development only)
)

# SessionLocal class for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# ============================================================================
# PostGIS Extension Setup
# ============================================================================

@event.listens_for(engine, "connect")
def setup_postgis(dbapi_conn, connection_record):
    """Enable PostGIS extension on first connection."""
    try:
        cursor = dbapi_conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        cursor.close()
        dbapi_conn.commit()
    except Exception as e:
        logger.warning("Could not enable PostGIS extension", error=str(e))


# ============================================================================
# Database Session Dependency
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to get database session.
    
    Usage:
        @app.get("/cases")
        def get_cases(db: Session = Depends(get_db)):
            cases = db.query(Case).all()
            return cases
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """
    Initialize the database by creating all tables.
    This should typically be done via Alembic migrations instead.
    """
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_all_tables():
    """
    Drop all tables. USE WITH CAUTION!
    Only for development/testing purposes.
    """
    logger.warning("Dropping all database tables")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


# ============================================================================
# Database Health Check
# ============================================================================

def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False


# ============================================================================
# Test Database Setup (for testing)
# ============================================================================

def get_test_db_engine():
    """
    Create an in-memory SQLite database for testing.
    
    Returns:
        SQLAlchemy Engine for testing
    """
    from sqlalchemy import create_engine
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    return engine


def get_test_db() -> Generator[Session, None, None]:
    """
    Get a test database session.
    
    Usage in tests:
        def test_something():
            db = next(get_test_db())
            # ... test code
    """
    engine = get_test_db_engine()
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)