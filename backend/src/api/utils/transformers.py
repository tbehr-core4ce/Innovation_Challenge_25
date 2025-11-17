"""
Data transformation utilities for API responses.
Converts database models to frontend-compatible formats.
backend/src/api/utils/transformers.py
"""

from typing import Dict, Any, Optional
from datetime import datetime
from src.core.models import H5N1Case


# Color and name mappings for frontend
CATEGORY_COLORS = {
    'poultry': '#f97316',
    'dairy_cattle': '#eab308',
    'wild_bird': '#3b82f6',
    'wild_mammal': '#8b5cf6',
    'domestic_mammal': '#ec4899',
    'other': '#6b7280'
}

CATEGORY_NAMES = {
    'poultry': 'Poultry',
    'dairy_cattle': 'Dairy Cattle',
    'wild_bird': 'Wild Bird',
    'wild_mammal': 'Wild Mammal',
    'domestic_mammal': 'Domestic Mammal',
    'other': 'Other'
}

STATUS_COLORS = {
    'confirmed': '#10b981',
    'suspected': '#f59e0b',
    'under_investigation': '#3b82f6',
    'resolved': '#6b7280'
}

STATUS_NAMES = {
    'confirmed': 'Confirmed',
    'suspected': 'Suspected',
    'under_investigation': 'Under Investigation',
    'resolved': 'Resolved'
}


def transform_case_for_map(case: H5N1Case) -> Dict[str, Any]:
    """
    Transform database H5N1Case to frontend map format.

    Args:
        case: H5N1Case database model instance

    Returns:
        Dictionary in frontend H5N1Case format
    """
    # Build location string (city/county, state)
    location_parts = [
        case.city if case.city else case.county,
        case.state_province
    ]
    location = ", ".join([p for p in location_parts if p])

    if not location:
        location = case.country

    # Transform status (remove underscores, lowercase)
    status = case.status.value.replace('_', '').lower() if case.status else 'unknown'

    # Get animal category value
    case_type = case.animal_category.value if case.animal_category else 'other'

    # Get severity value
    severity = case.severity.value.lower() if case.severity else 'low'

    # Build description
    description = case.description
    if not description and case.animal_species:
        description = f"{case.animal_species}"
        if case.animals_affected and case.animals_affected > 1:
            description += f" ({case.animals_affected:,} animals affected)"

    return {
        "id": str(case.id),
        "lat": case.latitude,
        "lng": case.longitude,
        "location": location,
        "caseType": case_type,
        "count": case.animals_affected or 1,
        "severity": severity,
        "reportedDate": case.case_date.isoformat() if case.case_date else datetime.now().isoformat(),
        "status": status,
        "description": description
    }


def calculate_risk_level(case_count: int, severity_scores: list) -> str:
    """
    Calculate risk level for hotspot based on case count and average severity.

    Args:
        case_count: Number of cases in hotspot
        severity_scores: List of severity values from cases

    Returns:
        Risk level: 'low', 'medium', 'high', or 'critical'
    """
    severity_weights = {
        'critical': 4,
        'high': 3,
        'medium': 2,
        'low': 1
    }

    # Calculate average severity score
    if not severity_scores:
        avg_severity_score = 1
    else:
        scores = [severity_weights.get(s, 1) for s in severity_scores]
        avg_severity_score = sum(scores) / len(scores)

    # Combined risk calculation
    if case_count >= 10 and avg_severity_score >= 3:
        return 'critical'
    elif case_count >= 5 or avg_severity_score >= 3:
        return 'high'
    elif case_count >= 3 or avg_severity_score >= 2:
        return 'medium'
    else:
        return 'low'


def format_category_name(category_value: str) -> str:
    """Convert database category value to display name."""
    return CATEGORY_NAMES.get(category_value, category_value.replace('_', ' ').title())


def format_status_name(status_value: str) -> str:
    """Convert database status value to display name."""
    return STATUS_NAMES.get(status_value, status_value.replace('_', ' ').title())
