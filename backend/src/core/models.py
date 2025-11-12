"""
BETS Models for API use
"""
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Literal


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