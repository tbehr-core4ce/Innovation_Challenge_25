"""
Database models for BETS H5N1 tracking system.
Includes support for WOAH categorization and geospatial data.
backend/src/core/models.py
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text,
    ForeignKey, Index, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from datetime import datetime
from enum import Enum
from typing import Optional

from .database import Base


# ============================================================================
# Enums for H5N1 Classification
# ============================================================================

class AnimalCategory(str, Enum):
    """WOAH animal categorization for H5N1 reporting."""
    POULTRY = "poultry"
    DAIRY_CATTLE = "dairy_cattle"
    WILD_BIRD = "wild_bird"
    WILD_MAMMAL = "wild_mammal"
    DOMESTIC_MAMMAL = "domestic_mammal"
    OTHER = "other"


class CaseStatus(str, Enum):
    """Status of H5N1 case reporting."""
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"
    UNDER_INVESTIGATION = "under_investigation"


class Severity(str, Enum):
    """Severity level of outbreak."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataSource(str, Enum):
    """Source of case data."""
    WOAH = "woah"  # World Organisation for Animal Health
    CDC = "cdc"
    USDA = "usda"
    STATE_AGENCY = "state_agency"
    MANUAL_ENTRY = "manual_entry"
    OTHER = "other"


# ============================================================================
# Main Case Model
# ============================================================================

class H5N1Case(Base):
    """
    Core model for H5N1 bird flu cases.
    Stores case information with geospatial data and WOAH categorization.
    """
    __tablename__ = "h5n1_cases"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # External Reference IDs
    external_id = Column(String(255), unique=True, nullable=True, index=True,
                        comment="ID from external data source (WOAH, CDC, etc.)")
    
    # Basic Information
    case_date = Column(DateTime, nullable=False, index=True,
                      comment="Date when case was reported/detected")
    report_date = Column(DateTime, nullable=True,
                        comment="Date when case was officially reported")
    
    # Status and Classification
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.SUSPECTED,
                   nullable=False, index=True)
    severity = Column(SQLEnum(Severity), default=Severity.LOW,
                     nullable=False, index=True)
    
    # Animal Information (WOAH Categories)
    animal_category = Column(SQLEnum(AnimalCategory), nullable=False, index=True,
                            comment="WOAH animal category")
    animal_species = Column(String(255), nullable=True,
                           comment="Specific species affected (e.g., 'Chicken', 'Holstein cow')")
    animals_affected = Column(Integer, nullable=True,
                             comment="Number of animals affected")
    animals_dead = Column(Integer, nullable=True,
                         comment="Number of animals deceased")
    
    # Location Information
    country = Column(String(100), nullable=False, index=True)
    state_province = Column(String(100), nullable=True, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True)
    location_name = Column(String(255), nullable=True,
                          comment="Farm name, facility name, etc.")
    
    # Geospatial Data (PostGIS)
    # SRID 4326 is WGS84 (standard for GPS coordinates)
    location = Column(Geometry('POINT', srid=4326), nullable=True,
                     comment="Geographic coordinates (longitude, latitude)")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Data Source
    data_source = Column(SQLEnum(DataSource), nullable=False, index=True)
    source_url = Column(Text, nullable=True,
                       comment="URL to original report/data")
    
    # Additional Details
    description = Column(Text, nullable=True,
                        comment="Additional case details and notes")
    control_measures = Column(Text, nullable=True,
                             comment="Control measures taken")
    extra_metadata = Column(JSON, nullable=True,
                     comment="Additional structured metadata")
    
    # Audit Fields
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                       onupdate=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    alerts = relationship("Alert", back_populates="case", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_case_date_status', 'case_date', 'status'),
        Index('idx_location_category', 'country', 'animal_category'),
        Index('idx_severity_date', 'severity', 'case_date'),
        Index('idx_spatial', 'location', postgresql_using='gist'),
    )
    
    def __repr__(self):
        return f"<H5N1Case(id={self.id}, date={self.case_date}, category={self.animal_category})>"


# ============================================================================
# Alert System
# ============================================================================

class AlertType(str, Enum):
    """Types of alerts for H5N1 surveillance."""
    NEW_OUTBREAK = "new_outbreak"
    CLUSTER_DETECTED = "cluster_detected"
    SEVERITY_INCREASE = "severity_increase"
    CROSS_SPECIES = "cross_species"
    GEOGRAPHIC_SPREAD = "geographic_spread"
    THRESHOLD_EXCEEDED = "threshold_exceeded"


class Alert(Base):
    """
    Alert notifications for significant H5N1 events.
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert Details
    alert_type = Column(SQLEnum(AlertType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(Severity), nullable=False)
    
    # Related Case
    case_id = Column(Integer, ForeignKey("h5n1_cases.id"), nullable=True)
    case = relationship("H5N1Case", back_populates="alerts")
    
    # Geographic Context
    country = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(255), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                       onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_active_alerts', 'is_active', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, active={self.is_active})>"


# ============================================================================
# Data Import Tracking
# ============================================================================

class DataImport(Base):
    """
    Track data import batches from various sources.
    Useful for auditing and debugging CSV imports.
    """
    __tablename__ = "data_imports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Import Details
    source = Column(SQLEnum(DataSource), nullable=False)
    filename = Column(String(255), nullable=True)
    file_hash = Column(String(64), nullable=True,
                      comment="SHA-256 hash to detect duplicate imports")
    
    # Results
    total_rows = Column(Integer, nullable=False, default=0)
    successful_rows = Column(Integer, nullable=False, default=0)
    failed_rows = Column(Integer, nullable=False, default=0)
    duplicate_rows = Column(Integer, nullable=False, default=0)
    
    # Status
    status = Column(String(50), nullable=False, default="pending")
    error_log = Column(Text, nullable=True,
                      comment="Error messages from failed imports")
    
    # Timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Audit
    imported_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_import_status', 'status', 'created_at'),
    )
    
    def __repr__(self):
        return f"<DataImport(id={self.id}, source={self.source}, status={self.status})>"


# ============================================================================
# Geographic Boundaries (Optional - for hotspot analysis)
# ============================================================================

class GeographicBoundary(Base):
    """
    Store geographic boundaries for counties, states, etc.
    Useful for hotspot zone analysis and geographic queries.
    """
    __tablename__ = "geographic_boundaries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    name = Column(String(255), nullable=False)
    boundary_type = Column(String(50), nullable=False, index=True,
                          comment="Type: country, state, county, custom")
    code = Column(String(50), nullable=True, index=True,
                 comment="FIPS code, ISO code, etc.")
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey("geographic_boundaries.id"), nullable=True)
    country = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    
    # Geospatial Data
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=False)
    centroid = Column(Geometry('POINT', srid=4326), nullable=True)
    area_sq_km = Column(Float, nullable=True)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Audit
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                       onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_boundary_spatial', 'boundary', postgresql_using='gist'),
    )
    
    def __repr__(self):
        return f"<GeographicBoundary(id={self.id}, name={self.name}, type={self.boundary_type})>"


# ============================================================================
# User Model (Optional - for authentication)
# ============================================================================

class User(Base):
    """
    User accounts for BETS system access.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="viewer")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Security
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Audit
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                       onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"