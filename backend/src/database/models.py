from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .connection import Base

class H5N1Detection(Base):
    __tablename__ = "h5n1_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_date = Column(Date, nullable=False, index=True)
    report_date = Column(Date)
    
    # Location
    state = Column(String(100))
    county = Column(String(100))
    country = Column(String(100))
    lat = Column(String)  # Store as string initially, convert later
    lon = Column(String)
    geom = Column(Geometry('POINT', srid=4326))  # PostGIS geometry
    
    # WOAH Classification
    category = Column(String(50), nullable=False, index=True)
    
    # Detection details
    species = Column(String(200))
    strain = Column(String(50))
    flock_size = Column(Integer)
    
    # Metadata
    source_dataset = Column(String(100))
    source_row_id = Column(String(100))
    
    created_at = Column(DateTime, server_default=func.now())

class CommercialOutbreak(Base):
    __tablename__ = "commercial_outbreaks"
    
    id = Column(Integer, primary_key=True)
    detection_id = Column(Integer, ForeignKey('h5n1_detections.id'))
    flock_type = Column(String(200))
    # Add other commercial-specific fields