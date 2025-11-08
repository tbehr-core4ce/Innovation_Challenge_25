"""
BETS Backend API - H5N1 Case Data Service
FastAPI backend for serving map visualization data
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime, timedelta
import pandas as pd
from enum import Enum

app = FastAPI(title="BETS API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class CaseType(str, Enum):
    human = "human"
    avian = "avian"
    dairy = "dairy"
    environmental = "environmental"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Status(str, Enum):
    active = "active"
    contained = "contained"
    monitoring = "monitoring"

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class H5N1Case(BaseModel):
    id: str
    lat: float
    lng: float
    location: str
    caseType: CaseType
    count: int
    severity: Severity
    reportedDate: str
    status: Status
    description: Optional[str] = None

class HotspotZone(BaseModel):
    id: str
    lat: float
    lng: float
    radius: int  # in meters
    caseCount: int
    riskLevel: RiskLevel

class MapDataResponse(BaseModel):
    cases: List[H5N1Case]
    hotspots: List[HotspotZone]
    lastUpdated: str

class StatsResponse(BaseModel):
    totalCases: int
    humanCases: int
    avianCases: int
    dairyCases: int
    environmentalCases: int
    criticalCases: int
    activeCases: int
    lastUpdated: str

# ==================== MOCK DATA STORE ====================
# In production, this would be a database

mock_cases = [
    {
        "id": "1",
        "lat": 36.7783,
        "lng": -119.4179,
        "location": "Tulare County, CA",
        "caseType": "dairy",
        "count": 15,
        "severity": "high",
        "reportedDate": "2025-11-05",
        "status": "monitoring",
        "description": "Dairy cattle herd showing symptoms. Quarantine measures in place."
    },
    {
        "id": "2",
        "lat": 37.6391,
        "lng": -120.9970,
        "location": "Merced County, CA",
        "caseType": "dairy",
        "count": 8,
        "severity": "medium",
        "reportedDate": "2025-11-04",
        "status": "contained"
    },
    {
        "id": "3",
        "lat": 36.7477,
        "lng": -119.7871,
        "location": "Fresno, CA",
        "caseType": "human",
        "count": 2,
        "severity": "critical",
        "reportedDate": "2025-11-06",
        "status": "active",
        "description": "Two dairy workers tested positive. Hospitalized and receiving treatment."
    },
    {
        "id": "4",
        "lat": 39.7392,
        "lng": -104.9903,
        "location": "Denver, CO",
        "caseType": "human",
        "count": 1,
        "severity": "high",
        "reportedDate": "2025-11-03",
        "status": "monitoring",
        "description": "Poultry worker exposed. Currently isolated."
    },
    {
        "id": "5",
        "lat": 40.7128,
        "lng": -74.0060,
        "location": "New York, NY",
        "caseType": "avian",
        "count": 45,
        "severity": "medium",
        "reportedDate": "2025-11-01",
        "status": "contained",
        "description": "Wild bird population affected in Central Park area."
    },
    {
        "id": "6",
        "lat": 41.8781,
        "lng": -87.6298,
        "location": "Chicago, IL",
        "caseType": "avian",
        "count": 32,
        "severity": "high",
        "reportedDate": "2025-10-30",
        "status": "monitoring"
    },
    {
        "id": "7",
        "lat": 47.6062,
        "lng": -122.3321,
        "location": "Seattle, WA",
        "caseType": "avian",
        "count": 67,
        "severity": "critical",
        "reportedDate": "2025-11-05",
        "status": "active",
        "description": "Major outbreak in commercial poultry facilities."
    },
    {
        "id": "8",
        "lat": 29.7604,
        "lng": -95.3698,
        "location": "Houston, TX",
        "caseType": "environmental",
        "count": 3,
        "severity": "low",
        "reportedDate": "2025-10-28",
        "status": "monitoring",
        "description": "Virus detected in wastewater sampling."
    }
]

mock_hotspots = [
    {
        "id": "h1",
        "lat": 36.8,
        "lng": -119.5,
        "radius": 50000,
        "caseCount": 42,
        "riskLevel": "critical"
    },
    {
        "id": "h2",
        "lat": 47.6062,
        "lng": -122.3321,
        "radius": 30000,
        "caseCount": 67,
        "riskLevel": "critical"
    },
    {
        "id": "h3",
        "lat": 41.8781,
        "lng": -87.6298,
        "radius": 40000,
        "caseCount": 32,
        "riskLevel": "high"
    }
]

# ==================== HOTSPOT DETECTION ====================

def detect_hotspots(cases: List[dict], radius_km: float = 50) -> List[dict]:
    """
    Simple hotspot detection algorithm using spatial clustering
    In production, use DBSCAN or similar clustering algorithms
    """
    if not cases:
        return []
    
    df = pd.DataFrame(cases)
    hotspots = []
    
    # Group nearby cases (simple distance-based approach)
    # In production, use geopandas and proper geospatial clustering
    
    # For demo, return predefined hotspots
    return mock_hotspots

# ==================== API ENDPOINTS ====================

@app.get("/")
def read_root():
    return {
        "service": "BETS API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/map-data", response_model=MapDataResponse)
def get_map_data(
    case_type: Optional[CaseType] = Query(None, description="Filter by case type"),
    severity: Optional[Severity] = Query(None, description="Filter by severity"),
    days: Optional[int] = Query(7, description="Cases from last N days")
):
    """
    Get all map visualization data (cases + hotspots)
    """
    cases = mock_cases.copy()
    
    # Apply filters
    if case_type:
        cases = [c for c in cases if c["caseType"] == case_type]
    
    if severity:
        cases = [c for c in cases if c["severity"] == severity]
    
    if days:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        cases = [c for c in cases if c["reportedDate"] >= cutoff_date]
    
    # Detect hotspots from filtered cases
    hotspots = detect_hotspots(cases)
    
    return MapDataResponse(
        cases=cases,
        hotspots=hotspots,
        lastUpdated=datetime.now().isoformat()
    )

@app.get("/api/cases", response_model=List[H5N1Case])
def get_cases(
    case_type: Optional[CaseType] = None,
    severity: Optional[Severity] = None,
    status: Optional[Status] = None
):
    """
    Get filtered H5N1 cases
    """
    cases = mock_cases.copy()
    
    if case_type:
        cases = [c for c in cases if c["caseType"] == case_type]
    
    if severity:
        cases = [c for c in cases if c["severity"] == severity]
    
    if status:
        cases = [c for c in cases if c["status"] == status]
    
    return cases

@app.get("/api/hotspots", response_model=List[HotspotZone])
def get_hotspots(
    min_risk_level: Optional[RiskLevel] = Query(None, description="Minimum risk level")
):
    """
    Get detected hotspot zones
    """
    hotspots = mock_hotspots.copy()
    
    if min_risk_level:
        risk_order = ["low", "medium", "high", "critical"]
        min_index = risk_order.index(min_risk_level)
        hotspots = [
            h for h in hotspots 
            if risk_order.index(h["riskLevel"]) >= min_index
        ]
    
    return hotspots

@app.get("/api/stats", response_model=StatsResponse)
def get_statistics():
    """
    Get aggregate statistics
    """
    cases = mock_cases
    
    stats = {
        "totalCases": sum(c["count"] for c in cases),
        "humanCases": sum(c["count"] for c in cases if c["caseType"] == "human"),
        "avianCases": sum(c["count"] for c in cases if c["caseType"] == "avian"),
        "dairyCases": sum(c["count"] for c in cases if c["caseType"] == "dairy"),
        "environmentalCases": sum(c["count"] for c in cases if c["caseType"] == "environmental"),
        "criticalCases": sum(c["count"] for c in cases if c["severity"] == "critical"),
        "activeCases": sum(c["count"] for c in cases if c["status"] == "active"),
        "lastUpdated": datetime.now().isoformat()
    }
    
    return stats

@app.post("/api/cases")
def create_case(case: H5N1Case):
    """
    Report a new H5N1 case
    """
    # In production, this would save to database
    mock_cases.append(case.dict())
    return {"message": "Case reported successfully", "id": case.id}

@app.get("/api/alerts")
def get_alerts():
    """
    Get active alerts based on thresholds
    """
    alerts = []
    
    # Check for critical cases
    critical_cases = [c for c in mock_cases if c["severity"] == "critical"]
    if critical_cases:
        alerts.append({
            "level": "critical",
            "message": f"{len(critical_cases)} critical cases detected",
            "timestamp": datetime.now().isoformat()
        })
    
    # Check for human cases
    human_cases = [c for c in mock_cases if c["caseType"] == "human"]
    if len(human_cases) > 2:
        alerts.append({
            "level": "warning",
            "message": f"Multiple human cases reported: {len(human_cases)}",
            "timestamp": datetime.now().isoformat()
        })
    
    return alerts

# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
