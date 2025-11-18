"""
Dashboard Router for BETS
Provides aggregated analytics and statistics for dashboard visualization
backend/src/api/routes/dashboard.py
"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.utils.transformers import (CATEGORY_COLORS, CATEGORY_NAMES,
                                        STATUS_COLORS, STATUS_NAMES,
                                        format_category_name,
                                        format_status_name)
from src.core.database import get_db
from src.core.models import H5N1Case

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# Response Models
class AnalyticsData(BaseModel):
    totalCases: int
    confirmedCases: int
    suspectedCases: int
    underInvestigation: int
    criticalSeverity: int
    highSeverity: int
    animalsAffected: int
    animalsDeceased: int
    lastUpdated: str


class TimelineDataPoint(BaseModel):
    month: str
    total: int
    poultry: int
    dairy_cattle: int
    wild_bird: int
    wild_mammal: int


class RegionDataPoint(BaseModel):
    name: str
    value: int


class AnimalCategoryData(BaseModel):
    name: str
    value: int
    color: str


class StatusData(BaseModel):
    name: str
    value: int
    color: str


class DataSourceData(BaseModel):
    name: str
    value: int


@router.get("/overview", response_model=AnalyticsData)
def get_dashboard_overview(
    days: int = Query(90, description="Date range in days"),
    db: Session = Depends(get_db)
):
    """
    Get dashboard overview metrics.

    Provides aggregate statistics for cases including counts by status,
    severity, and total animals affected.

    Args:
        days: Date range in days (default 90)
        db: Database session

    Returns:
        AnalyticsData with overview metrics
    """
    # Build date filter
    date_filter = True
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        date_filter = H5N1Case.case_date >= cutoff_date

    # Query aggregates
    result = db.query(
        func.count(H5N1Case.id).label('total_cases'),
        func.count(H5N1Case.id).filter(H5N1Case.status == 'confirmed').label('confirmed'),
        func.count(H5N1Case.id).filter(H5N1Case.status == 'suspected').label('suspected'),
        func.count(H5N1Case.id).filter(H5N1Case.status == 'under_investigation').label('under_investigation'),
        func.count(H5N1Case.id).filter(H5N1Case.severity == 'critical').label('critical'),
        func.count(H5N1Case.id).filter(H5N1Case.severity == 'high').label('high'),
        func.coalesce(func.sum(H5N1Case.animals_affected), 0).label('affected'),
        func.coalesce(func.sum(H5N1Case.animals_dead), 0).label('deceased')
    ).filter(
        H5N1Case.is_deleted == False,
        date_filter
    ).first()

    return AnalyticsData(
        totalCases=result.total_cases or 0,
        confirmedCases=result.confirmed or 0,
        suspectedCases=result.suspected or 0,
        underInvestigation=result.under_investigation or 0,
        criticalSeverity=result.critical or 0,
        highSeverity=result.high or 0,
        animalsAffected=result.affected or 0,
        animalsDeceased=result.deceased or 0,
        lastUpdated=datetime.now().isoformat()
    )


@router.get("/timeline", response_model=List[TimelineDataPoint])
def get_dashboard_timeline(
    months: int = Query(12, description="Number of months to include"),
    db: Session = Depends(get_db)
):
    """
    Get monthly timeline data by animal category.

    Args:
        months: Number of months to include (default 12)
        db: Database session

    Returns:
        List of TimelineDataPoint with monthly breakdown
    """
    # Calculate date range
    cutoff_date = datetime.now() - timedelta(days=months * 30)

    # Query monthly data - use date_trunc for grouping only
    month_trunc = func.date_trunc('month', H5N1Case.case_date).label('month_date')

    results = db.query(
        month_trunc,
        func.count(H5N1Case.id).label('total'),
        func.count(H5N1Case.id).filter(H5N1Case.animal_category == 'poultry').label('poultry'),
        func.count(H5N1Case.id).filter(H5N1Case.animal_category == 'dairy_cattle').label('dairy_cattle'),
        func.count(H5N1Case.id).filter(H5N1Case.animal_category == 'wild_bird').label('wild_bird'),
        func.count(H5N1Case.id).filter(H5N1Case.animal_category == 'wild_mammal').label('wild_mammal')
    ).filter(
        H5N1Case.is_deleted == False,
        H5N1Case.case_date >= cutoff_date
    ).group_by(
        month_trunc
    ).order_by(
        month_trunc
    ).all()

    return [
        TimelineDataPoint(
            month=row.month_date.strftime('%b') if row.month_date else 'Unknown',
            total=row.total or 0,
            poultry=row.poultry or 0,
            dairy_cattle=row.dairy_cattle or 0,
            wild_bird=row.wild_bird or 0,
            wild_mammal=row.wild_mammal or 0
        )
        for row in results
    ]


@router.get("/regions", response_model=List[RegionDataPoint])
def get_dashboard_regions(
    days: int = Query(90, description="Date range in days"),
    limit: int = Query(10, description="Number of top regions to return"),
    db: Session = Depends(get_db)
):
    """
    Get regional breakdown of cases.

    Args:
        days: Date range in days (default 90)
        limit: Number of top regions (default 10)
        db: Database session

    Returns:
        List of RegionDataPoint with case counts by state
    """
    # Build date filter
    date_filter = True
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        date_filter = H5N1Case.case_date >= cutoff_date

    # Query by state_province
    results = db.query(
        H5N1Case.state_province.label('name'),
        func.count(H5N1Case.id).label('value')
    ).filter(
        H5N1Case.is_deleted == False,
        H5N1Case.state_province.isnot(None),
        date_filter
    ).group_by(
        H5N1Case.state_province
    ).order_by(
        func.count(H5N1Case.id).desc()
    ).limit(limit).all()

    return [
        RegionDataPoint(name=row.name, value=row.value or 0)
        for row in results
    ]


@router.get("/animal-categories", response_model=List[AnimalCategoryData])
def get_animal_categories(
    days: int = Query(90, description="Date range in days"),
    db: Session = Depends(get_db)
):
    """
    Get case distribution by animal category.

    Args:
        days: Date range in days (default 90)
        db: Database session

    Returns:
        List of AnimalCategoryData with counts and colors
    """
    # Build date filter
    date_filter = True
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        date_filter = H5N1Case.case_date >= cutoff_date

    # Query by animal_category
    results = db.query(
        H5N1Case.animal_category.label('category'),
        func.count(H5N1Case.id).label('value')
    ).filter(
        H5N1Case.is_deleted == False,
        date_filter
    ).group_by(
        H5N1Case.animal_category
    ).order_by(
        func.count(H5N1Case.id).desc()
    ).all()

    return [
        AnimalCategoryData(
            name=format_category_name(row.category.value if hasattr(row.category, 'value') else row.category),
            value=row.value or 0,
            color=CATEGORY_COLORS.get(row.category.value if hasattr(row.category, 'value') else row.category, '#6b7280')
        )
        for row in results
    ]


@router.get("/status", response_model=List[StatusData])
def get_status_breakdown(
    days: int = Query(90, description="Date range in days"),
    db: Session = Depends(get_db)
):
    """
    Get case status breakdown.

    Args:
        days: Date range in days (default 90)
        db: Database session

    Returns:
        List of StatusData with counts and colors
    """
    # Build date filter
    date_filter = True
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        date_filter = H5N1Case.case_date >= cutoff_date

    # Query by status
    results = db.query(
        H5N1Case.status.label('status'),
        func.count(H5N1Case.id).label('value')
    ).filter(
        H5N1Case.is_deleted == False,
        date_filter
    ).group_by(
        H5N1Case.status
    ).order_by(
        func.count(H5N1Case.id).desc()
    ).all()

    return [
        StatusData(
            name=format_status_name(row.status.value if hasattr(row.status, 'value') else row.status),
            value=row.value or 0,
            color=STATUS_COLORS.get(row.status.value if hasattr(row.status, 'value') else row.status, '#6b7280')
        )
        for row in results
    ]


@router.get("/sources", response_model=List[DataSourceData])
def get_data_sources(
    days: int = Query(90, description="Date range in days"),
    db: Session = Depends(get_db)
):
    """
    Get data source breakdown.

    Args:
        days: Date range in days (default 90)
        db: Database session

    Returns:
        List of DataSourceData with case counts by source
    """
    # Build date filter
    date_filter = True
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        date_filter = H5N1Case.case_date >= cutoff_date

    # Query by data_source
    results = db.query(
        H5N1Case.data_source.label('source'),
        func.count(H5N1Case.id).label('value')
    ).filter(
        H5N1Case.is_deleted == False,
        date_filter
    ).group_by(
        H5N1Case.data_source
    ).order_by(
        func.count(H5N1Case.id).desc()
    ).all()

    return [
        DataSourceData(
            name=(row.source.value if hasattr(row.source, 'value') else row.source).upper(),
            value=row.value or 0
        )
        for row in results
    ]
