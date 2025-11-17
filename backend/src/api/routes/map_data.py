"""
Map Data Router for BETS
Provides geospatial case data and hotspot detection for map visualization
backend/src/api/routes/map_data.py
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.models import H5N1Case
from src.api.utils.transformers import (
    transform_case_for_map,
    calculate_risk_level
)

router = APIRouter(prefix="/api", tags=["map"])


# Response Models
class H5N1CaseResponse(BaseModel):
    id: str
    lat: float
    lng: float
    location: str
    caseType: str
    count: int
    severity: str
    reportedDate: str
    status: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class HotspotZoneResponse(BaseModel):
    id: str
    lat: float
    lng: float
    radius: int  # in meters
    caseCount: int
    riskLevel: str


class MapDataResponse(BaseModel):
    cases: List[H5N1CaseResponse]
    hotspots: List[HotspotZoneResponse]
    lastUpdated: str


@router.get("/map-data", response_model=MapDataResponse)
def get_map_data(
    case_type: Optional[str] = Query(None, description="Filter by animal category"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    days: Optional[int] = Query(7, description="Cases from last N days (0 for all time)"),
    db: Session = Depends(get_db)
):
    """
    Get all map visualization data (cases + hotspots).

    Args:
        case_type: Filter by animal_category (e.g., 'poultry', 'wild_bird')
        severity: Filter by severity level (e.g., 'high', 'critical')
        days: Date range in days (0 for all time, default 7)
        db: Database session

    Returns:
        MapDataResponse with cases and hotspots
    """
    # Build base query
    query = db.query(H5N1Case).filter(
        H5N1Case.is_deleted == False,
        H5N1Case.latitude.isnot(None),
        H5N1Case.longitude.isnot(None)
    )

    # Apply filters
    if case_type:
        query = query.filter(H5N1Case.animal_category == case_type)

    if severity:
        query = query.filter(H5N1Case.severity == severity)

    if days and days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(H5N1Case.case_date >= cutoff_date)

    # Execute query
    cases = query.order_by(H5N1Case.case_date.desc()).limit(1000).all()

    # Transform cases to frontend format
    case_responses = [transform_case_for_map(case) for case in cases]

    # Detect hotspots
    hotspots = detect_hotspots(db, days=days or 30)

    return MapDataResponse(
        cases=case_responses,
        hotspots=hotspots,
        lastUpdated=datetime.now().isoformat()
    )


def detect_hotspots(
    db: Session,
    days: int = 30,
    num_clusters: int = 5
) -> List[HotspotZoneResponse]:
    """
    Detect geographic hotspots using KMeans clustering.

    Uses PostGIS ST_ClusterKMeans to group cases into geographic clusters,
    then calculates risk levels based on case count and severity.

    Args:
        db: Database session
        days: Date range for analysis
        num_clusters: Number of clusters to create

    Returns:
        List of hotspot zones
    """
    # Step 1: Get cases with coordinates for clustering
    subquery = db.query(
        H5N1Case.id,
        H5N1Case.latitude,
        H5N1Case.longitude,
        H5N1Case.severity,
        func.ST_ClusterKMeans(
            func.ST_SetSRID(
                func.ST_MakePoint(H5N1Case.longitude, H5N1Case.latitude),
                4326
            ),
            num_clusters
        ).over().label('cluster_id')
    ).filter(
        H5N1Case.case_date >= datetime.now() - timedelta(days=days),
        H5N1Case.latitude.isnot(None),
        H5N1Case.longitude.isnot(None),
        H5N1Case.is_deleted == False
    ).subquery()

    # Step 2: Aggregate clusters
    clusters = db.query(
        subquery.c.cluster_id,
        func.avg(subquery.c.latitude).label('lat'),
        func.avg(subquery.c.longitude).label('lng'),
        func.count(subquery.c.id).label('case_count'),
        func.array_agg(subquery.c.severity).label('severities')
    ).group_by(
        subquery.c.cluster_id
    ).all()

    hotspots = []
    for cluster in clusters:
        # Skip if no cases
        if cluster.case_count == 0:
            continue

        # Convert severity enums to strings
        severity_values = [
            s.value if hasattr(s, 'value') else str(s).lower()
            for s in cluster.severities if s is not None
        ]

        # Calculate risk level
        risk_level = calculate_risk_level(cluster.case_count, severity_values)

        # Calculate radius (base 50km, scale by case count, cap at 100km)
        radius = min(50000 + (cluster.case_count * 5000), 100000)

        hotspots.append(HotspotZoneResponse(
            id=f"h{cluster.cluster_id}",
            lat=float(cluster.lat),
            lng=float(cluster.lng),
            radius=radius,
            caseCount=cluster.case_count,
            riskLevel=risk_level
        ))

    return hotspots
