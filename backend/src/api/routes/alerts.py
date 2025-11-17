"""
Alerts Router for BETS
Generates and serves alerts based on case data patterns
backend/src/api/routes/alerts.py
"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.models import H5N1Case

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# Response Models
class RecentAlert(BaseModel):
    date: str
    type: str
    location: str
    severity: str
    message: str


@router.get("/recent", response_model=List[RecentAlert])
def get_recent_alerts(
    days: int = Query(30, description="Look back period in days"),
    limit: int = Query(10, description="Maximum number of alerts to return"),
    db: Session = Depends(get_db)
):
    """
    Get recent alerts based on case patterns.

    Automatically generates alerts for:
    - Critical severity cases
    - Geographic clusters (multiple cases in same county)
    - Large outbreaks (>10,000 animals affected)

    Args:
        days: Look back period in days (default 30)
        limit: Maximum number of alerts (default 10)
        db: Database session

    Returns:
        List of RecentAlert objects
    """
    alerts = []
    cutoff_date = datetime.now() - timedelta(days=days)

    # Alert Type 1: Critical severity cases
    critical_cases = db.query(H5N1Case).filter(
        H5N1Case.severity == 'critical',
        H5N1Case.case_date >= cutoff_date,
        H5N1Case.is_deleted == False
    ).order_by(H5N1Case.case_date.desc()).limit(5).all()

    for case in critical_cases:
        location = case.state_province or case.country
        animal_category = case.animal_category.value if hasattr(case.animal_category, 'value') else str(case.animal_category)

        # Format message based on animals affected
        if case.animals_affected and case.animals_affected > 1000:
            message = f"Large-scale {animal_category} outbreak - {case.animals_affected:,} animals affected"
        else:
            message = f"Critical severity {animal_category} case detected"

        alerts.append(RecentAlert(
            date=case.case_date.strftime("%Y-%m-%d") if case.case_date else datetime.now().strftime("%Y-%m-%d"),
            type="Critical Severity",
            location=location,
            severity="high",
            message=message
        ))

    # Alert Type 2: Geographic clusters (3+ cases in same county within 7 days)
    cluster_window = datetime.now() - timedelta(days=7)

    clusters = db.query(
        H5N1Case.county,
        H5N1Case.state_province,
        func.count(H5N1Case.id).label('count'),
        func.max(H5N1Case.case_date).label('latest_date')
    ).filter(
        H5N1Case.case_date >= cluster_window,
        H5N1Case.is_deleted == False,
        H5N1Case.county.isnot(None)
    ).group_by(
        H5N1Case.county,
        H5N1Case.state_province
    ).having(
        func.count(H5N1Case.id) >= 3
    ).order_by(
        func.count(H5N1Case.id).desc()
    ).limit(5).all()

    for cluster in clusters:
        location = f"{cluster.county}, {cluster.state_province}" if cluster.county else cluster.state_province

        alerts.append(RecentAlert(
            date=cluster.latest_date.strftime("%Y-%m-%d") if cluster.latest_date else datetime.now().strftime("%Y-%m-%d"),
            type="Cluster Detected",
            location=location,
            severity="medium",
            message=f"Multiple cases detected in area ({cluster.count} cases within 7 days)"
        ))

    # Alert Type 3: Large outbreaks (>10,000 animals affected)
    large_outbreaks = db.query(H5N1Case).filter(
        H5N1Case.animals_affected >= 10000,
        H5N1Case.case_date >= cutoff_date,
        H5N1Case.is_deleted == False
    ).order_by(H5N1Case.case_date.desc()).limit(5).all()

    for outbreak in large_outbreaks:
        location = outbreak.state_province or outbreak.country
        animal_category = outbreak.animal_category.value if hasattr(outbreak.animal_category, 'value') else str(outbreak.animal_category)

        alerts.append(RecentAlert(
            date=outbreak.case_date.strftime("%Y-%m-%d") if outbreak.case_date else datetime.now().strftime("%Y-%m-%d"),
            type="Large Outbreak",
            location=location,
            severity="high",
            message=f"Large-scale outbreak - {outbreak.animals_affected:,} {animal_category} affected"
        ))

    # Alert Type 4: High severity spike (5+ high/critical cases in last 3 days)
    spike_window = datetime.now() - timedelta(days=3)

    high_severity_count = db.query(func.count(H5N1Case.id)).filter(
        H5N1Case.severity.in_(['high', 'critical']),
        H5N1Case.case_date >= spike_window,
        H5N1Case.is_deleted == False
    ).scalar()

    if high_severity_count and high_severity_count >= 5:
        alerts.append(RecentAlert(
            date=datetime.now().strftime("%Y-%m-%d"),
            type="Severity Spike",
            location="Multiple Regions",
            severity="high",
            message=f"Elevated threat level: {high_severity_count} high/critical cases in past 3 days"
        ))

    # Sort all alerts by date (most recent first)
    alerts.sort(key=lambda x: x.date, reverse=True)

    # Return limited number of alerts
    return alerts[:limit]
