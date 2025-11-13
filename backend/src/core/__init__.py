"""
Models package for BETS application.
Import all models here so Alembic can detect them for migrations.
"""

from core import (
    H5N1Case,
    Alert,
    DataImport,
    GeographicBoundary,
    User,
    # Enums
    AnimalCategory,
    CaseStatus,
    Severity,
    DataSource,
    AlertType,
)

__all__ = [
    "H5N1Case",
    "Alert",
    "DataImport",
    "GeographicBoundary",
    "User",
    "AnimalCategory",
    "CaseStatus",
    "Severity",
    "DataSource",
    "AlertType",
]