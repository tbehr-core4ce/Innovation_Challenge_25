# BETS Frontend API Integration Plan

## Executive Summary

This document outlines the **exact API endpoints** that need to be implemented in the backend to make the frontend fully functional. The database is already populated with data from commercial-backyard-flocks.csv, HPAI Detections in Mammals.csv, and HPAI Detections in Wild Birds.csv.

**Current State:**
- ✅ Database: PostgreSQL with PostGIS running with data
- ✅ Models: Complete database schema in `backend/src/core/models.py`
- ✅ Frontend: Complete UI in `frontend_work` branch expecting API data
- ❌ API Endpoints: Route files exist but are empty (except data_ingestion.py)

---

## Database to Frontend Field Mapping

### Database Schema (h5n1_cases table)
```
id, external_id, case_date, report_date, status, severity,
animal_category, animal_species, animals_affected, animals_dead,
country, state_province, county, city, location_name,
location (PostGIS), latitude, longitude, data_source, source_url,
description, control_measures, extra_metadata,
created_at, updated_at, is_deleted
```

### Frontend Expected Format (from betsApi.ts)

#### For Map (H5N1Case)
```typescript
{
  id: string,                    // → h5n1_cases.id
  lat: number,                   // → h5n1_cases.latitude
  lng: number,                   // → h5n1_cases.longitude
  location: string,              // → "{city/county}, {state_province}"
  caseType: string,              // → h5n1_cases.animal_category
  count: number,                 // → h5n1_cases.animals_affected
  severity: string,              // → h5n1_cases.severity (lowercase)
  reportedDate: string,          // → h5n1_cases.case_date (ISO format)
  status: string,                // → h5n1_cases.status (lowercase, no underscores)
  description?: string           // → h5n1_cases.description
}
```

#### For Map (HotspotZone)
```typescript
{
  id: string,                    // → Generated from cluster
  lat: number,                   // → Centroid of cluster
  lng: number,                   // → Centroid of cluster
  radius: number,                // → Calculated cluster radius (meters)
  caseCount: number,             // → COUNT of cases in cluster
  riskLevel: string              // → 'low' | 'medium' | 'high' | 'critical'
}
```

---

## Required API Endpoints

### Priority 1: Map Visualization (CRITICAL)

#### 1. GET `/api/map-data`
**Frontend calls:** `betsApi.getMapData()`
**Location:** `backend/src/api/routes/map_data.py`

**Query Parameters:**
- `case_type` (optional): Filter by animal_category
- `severity` (optional): Filter by severity level
- `days` (optional, default=7): Show cases from last N days

**Response:**
```json
{
  "cases": [
    {
      "id": "1",
      "lat": 37.769337,
      "lng": -78.169968,
      "location": "Accomack, Virginia",
      "caseType": "poultry",
      "count": 441000,
      "severity": "critical",
      "reportedDate": "2025-01-21T00:00:00",
      "status": "confirmed",
      "description": "Commercial Broiler Production"
    }
  ],
  "hotspots": [
    {
      "id": "h1",
      "lat": 44.240459,
      "lng": -114.478828,
      "radius": 50000,
      "caseCount": 8,
      "riskLevel": "medium"
    }
  ],
  "lastUpdated": "2025-11-17T20:36:38.432181"
}
```

**Implementation Notes:**
- Query `h5n1_cases` with filters
- Transform database fields to frontend format
- Calculate hotspots using ST_ClusterKMeans
- Risk level based on case density and severity

**SQL Query Pattern:**
```sql
SELECT
  id, latitude, longitude,
  COALESCE(city, county, state_province) || ', ' || COALESCE(state_province, country) as location,
  animal_category, animals_affected, severity,
  case_date, status, description
FROM h5n1_cases
WHERE
  is_deleted = false
  AND case_date >= NOW() - INTERVAL '7 days'
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL
ORDER BY case_date DESC;
```

**Hotspot Detection (PostGIS):**
```sql
-- Use ST_ClusterKMeans to create circular clusters
WITH clustered AS (
  SELECT
    latitude, longitude,
    ST_ClusterKMeans(
      ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),
      5  -- number of clusters
    ) OVER () as cluster_id
  FROM h5n1_cases
  WHERE case_date >= NOW() - INTERVAL '30 days'
    AND latitude IS NOT NULL
    AND longitude IS NOT NULL
    AND is_deleted = false
)
SELECT
  cluster_id,
  AVG(latitude) as lat,
  AVG(longitude) as lng,
  COUNT(*) as case_count
FROM clustered
GROUP BY cluster_id;
```

---

### Priority 2: Dashboard Overview (CRITICAL)

#### 2. GET `/api/dashboard/overview`
**Frontend calls:** `betsApi.getDashboardOverview()`
**Location:** `backend/src/api/routes/dashboard.py`

**Response:**
```json
{
  "totalCases": 247,
  "confirmedCases": 189,
  "suspectedCases": 34,
  "underInvestigation": 24,
  "criticalSeverity": 8,
  "highSeverity": 34,
  "animalsAffected": 12450,
  "animalsDeceased": 3890,
  "lastUpdated": "2025-11-17T20:36:38.432181"
}
```

**SQL Query:**
```sql
SELECT
  COUNT(*) as total_cases,
  COUNT(*) FILTER (WHERE status = 'confirmed') as confirmed_cases,
  COUNT(*) FILTER (WHERE status = 'suspected') as suspected_cases,
  COUNT(*) FILTER (WHERE status = 'under_investigation') as under_investigation,
  COUNT(*) FILTER (WHERE severity = 'critical') as critical_severity,
  COUNT(*) FILTER (WHERE severity = 'high') as high_severity,
  COALESCE(SUM(animals_affected), 0) as animals_affected,
  COALESCE(SUM(animals_dead), 0) as animals_deceased
FROM h5n1_cases
WHERE is_deleted = false
  AND case_date >= NOW() - INTERVAL '90 days';
```

---

#### 3. GET `/api/dashboard/timeline`
**Frontend calls:** `betsApi.getDashboardTimeline()`
**Location:** `backend/src/api/routes/dashboard.py`

**Response:**
```json
[
  {
    "month": "Jan",
    "total": 45,
    "poultry": 38,
    "dairy_cattle": 5,
    "wild_bird": 2,
    "wild_mammal": 0
  },
  {
    "month": "Feb",
    "total": 62,
    "poultry": 52,
    "dairy_cattle": 7,
    "wild_bird": 3,
    "wild_mammal": 0
  }
]
```

**SQL Query:**
```sql
SELECT
  TO_CHAR(case_date, 'Mon') as month,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE animal_category = 'poultry') as poultry,
  COUNT(*) FILTER (WHERE animal_category = 'dairy_cattle') as dairy_cattle,
  COUNT(*) FILTER (WHERE animal_category = 'wild_bird') as wild_bird,
  COUNT(*) FILTER (WHERE animal_category = 'wild_mammal') as wild_mammal
FROM h5n1_cases
WHERE is_deleted = false
  AND case_date >= NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', case_date), TO_CHAR(case_date, 'Mon')
ORDER BY DATE_TRUNC('month', case_date);
```

---

#### 4. GET `/api/dashboard/regions`
**Frontend calls:** `betsApi.getDashboardRegions()`
**Location:** `backend/src/api/routes/dashboard.py`

**Response:**
```json
[
  { "name": "California", "value": 45 },
  { "name": "Texas", "value": 38 },
  { "name": "Virginia", "value": 32 }
]
```

**SQL Query:**
```sql
SELECT
  state_province as name,
  COUNT(*) as value
FROM h5n1_cases
WHERE is_deleted = false
  AND state_province IS NOT NULL
  AND case_date >= NOW() - INTERVAL '90 days'
GROUP BY state_province
ORDER BY value DESC
LIMIT 10;
```

---

#### 5. GET `/api/dashboard/animal-categories`
**Frontend calls:** `betsApi.getAnimalCategories()`
**Location:** `backend/src/api/routes/dashboard.py`

**Response:**
```json
[
  { "name": "Poultry", "value": 189, "color": "#f97316" },
  { "name": "Dairy Cattle", "value": 46, "color": "#eab308" },
  { "name": "Wild Bird", "value": 10, "color": "#3b82f6" },
  { "name": "Wild Mammal", "value": 2, "color": "#8b5cf6" }
]
```

**Implementation:**
```python
# Color mapping
CATEGORY_COLORS = {
    'poultry': '#f97316',
    'dairy_cattle': '#eab308',
    'wild_bird': '#3b82f6',
    'wild_mammal': '#8b5cf6',
    'other': '#6b7280'
}

# Name mapping (database → frontend)
CATEGORY_NAMES = {
    'poultry': 'Poultry',
    'dairy_cattle': 'Dairy Cattle',
    'wild_bird': 'Wild Bird',
    'wild_mammal': 'Wild Mammal',
    'other': 'Other'
}
```

**SQL Query:**
```sql
SELECT
  animal_category,
  COUNT(*) as value
FROM h5n1_cases
WHERE is_deleted = false
  AND case_date >= NOW() - INTERVAL '90 days'
GROUP BY animal_category
ORDER BY value DESC;
```

---

#### 6. GET `/api/dashboard/status`
**Frontend calls:** `betsApi.getStatusBreakdown()`
**Location:** `backend/src/api/routes/dashboard.py`

**Response:**
```json
[
  { "name": "Confirmed", "value": 189, "color": "#10b981" },
  { "name": "Suspected", "value": 34, "color": "#f59e0b" },
  { "name": "Under Investigation", "value": 24, "color": "#3b82f6" }
]
```

**Implementation:**
```python
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
```

---

#### 7. GET `/api/dashboard/sources`
**Frontend calls:** `betsApi.getDataSources()`
**Location:** `backend/src/api/routes/dashboard.py`

**Response:**
```json
[
  { "name": "USDA", "value": 120 },
  { "name": "CDC", "value": 45 },
  { "name": "WOAH", "value": 67 }
]
```

**SQL Query:**
```sql
SELECT
  data_source as name,
  COUNT(*) as value
FROM h5n1_cases
WHERE is_deleted = false
  AND case_date >= NOW() - INTERVAL '90 days'
GROUP BY data_source
ORDER BY value DESC;
```

---

### Priority 3: Alerts (HIGH)

#### 8. GET `/api/alerts/recent`
**Frontend calls:** `betsApi.getDashboardAlerts()`
**Location:** `backend/src/api/routes/alerts.py`

**Response:**
```json
[
  {
    "date": "2025-01-21",
    "type": "New Outbreak",
    "location": "Virginia",
    "severity": "high",
    "message": "Large commercial poultry operation affected - 441,000 birds"
  },
  {
    "date": "2025-01-15",
    "type": "Cluster Detected",
    "location": "Idaho",
    "severity": "medium",
    "message": "Multiple cases in Ada County"
  }
]
```

**Alert Generation Logic:**
```python
def generate_alerts(db: Session):
    alerts = []

    # Alert Type 1: Critical severity cases
    critical = db.query(H5N1Case).filter(
        H5N1Case.severity == 'critical',
        H5N1Case.case_date >= datetime.now() - timedelta(days=7),
        H5N1Case.is_deleted == False
    ).all()

    for case in critical:
        alerts.append({
            "date": case.case_date.strftime("%Y-%m-%d"),
            "type": "Critical Severity",
            "location": case.state_province or case.country,
            "severity": "high",
            "message": f"{case.animal_category} outbreak - {case.animals_affected:,} animals affected"
        })

    # Alert Type 2: Geographic clusters
    # Query for multiple cases in same county within 7 days
    clusters = db.query(
        H5N1Case.county,
        H5N1Case.state_province,
        func.count(H5N1Case.id).label('count')
    ).filter(
        H5N1Case.case_date >= datetime.now() - timedelta(days=7),
        H5N1Case.is_deleted == False,
        H5N1Case.county.isnot(None)
    ).group_by(
        H5N1Case.county,
        H5N1Case.state_province
    ).having(
        func.count(H5N1Case.id) >= 3
    ).all()

    for cluster in clusters:
        alerts.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Cluster Detected",
            "location": f"{cluster.county}, {cluster.state_province}",
            "severity": "medium",
            "message": f"Multiple cases detected ({cluster.count} cases)"
        })

    # Alert Type 3: Large outbreaks (>10,000 animals)
    large = db.query(H5N1Case).filter(
        H5N1Case.animals_affected >= 10000,
        H5N1Case.case_date >= datetime.now() - timedelta(days=30),
        H5N1Case.is_deleted == False
    ).all()

    for case in large:
        alerts.append({
            "date": case.case_date.strftime("%Y-%m-%d"),
            "type": "Large Outbreak",
            "location": case.state_province or case.country,
            "severity": "high",
            "message": f"Large-scale outbreak - {case.animals_affected:,} {case.animal_category} affected"
        })

    # Sort by date, most recent first
    alerts.sort(key=lambda x: x['date'], reverse=True)

    return alerts[:10]  # Return top 10 most recent
```

---

## Data Transformation Functions

### Helper Functions Needed

Create file: `backend/src/api/utils/transformers.py`

```python
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.models import H5N1Case

def transform_case_for_map(case: H5N1Case) -> Dict[str, Any]:
    """Transform database case to frontend map format"""

    # Build location string
    location_parts = [
        case.city,
        case.county,
        case.state_province
    ]
    location = ", ".join([p for p in location_parts if p])
    if not location:
        location = case.country

    # Transform status (remove underscores, lowercase)
    status = case.status.value.replace('_', '').lower() if case.status else 'unknown'

    return {
        "id": str(case.id),
        "lat": case.latitude,
        "lng": case.longitude,
        "location": location,
        "caseType": case.animal_category.value if case.animal_category else 'other',
        "count": case.animals_affected or 1,
        "severity": case.severity.value.lower() if case.severity else 'low',
        "reportedDate": case.case_date.isoformat() if case.case_date else datetime.now().isoformat(),
        "status": status,
        "description": case.description or f"{case.animal_species or case.animal_category.value}"
    }

def calculate_risk_level(case_count: int, avg_severity: str) -> str:
    """Calculate risk level for hotspot based on case count and severity"""

    severity_weights = {
        'critical': 4,
        'high': 3,
        'medium': 2,
        'low': 1
    }

    severity_score = severity_weights.get(avg_severity, 1)

    # Combined score
    if case_count >= 10 and severity_score >= 3:
        return 'critical'
    elif case_count >= 5 or severity_score >= 3:
        return 'high'
    elif case_count >= 3 or severity_score >= 2:
        return 'medium'
    else:
        return 'low'
```

---

## Implementation Checklist

### Phase 1: Map Endpoints (CRITICAL - Frontend can't function without this)
- [ ] Create `backend/src/api/routes/map_data.py`
- [ ] Implement `GET /api/map-data` endpoint
  - [ ] Query h5n1_cases with filters
  - [ ] Transform to frontend format using `transform_case_for_map()`
  - [ ] Implement hotspot detection with ST_ClusterKMeans
  - [ ] Calculate risk levels for hotspots
  - [ ] Return MapDataResponse
- [ ] Add router to main.py: `app.include_router(map_data.router)`
- [ ] Test with: `curl http://localhost:8000/api/map-data`

### Phase 2: Dashboard Endpoints (CRITICAL)
- [ ] Create `backend/src/api/routes/dashboard.py`
- [ ] Implement all 6 dashboard endpoints:
  - [ ] `GET /api/dashboard/overview`
  - [ ] `GET /api/dashboard/timeline`
  - [ ] `GET /api/dashboard/regions`
  - [ ] `GET /api/dashboard/animal-categories`
  - [ ] `GET /api/dashboard/status`
  - [ ] `GET /api/dashboard/sources`
- [ ] Add color/name mappings for categories and statuses
- [ ] Add router to main.py: `app.include_router(dashboard.router)`
- [ ] Test each endpoint individually

### Phase 3: Alert System (HIGH)
- [ ] Create `backend/src/api/routes/alerts.py`
- [ ] Implement alert generation logic
- [ ] Implement `GET /api/alerts/recent`
- [ ] Add router to main.py: `app.include_router(alerts.router)`

### Phase 4: Update Main.py
- [ ] Remove mock data references
- [ ] Import and include all routers
- [ ] Add database session dependency
- [ ] Verify CORS settings for frontend

### Phase 5: Frontend Integration
- [ ] Update `frontend/services/betsApi.ts`
- [ ] Change API_BASE_URL to backend URL
- [ ] Remove mock data, uncomment real API calls
- [ ] Test dashboard page
- [ ] Test map page

---

## Date Range Support

All endpoints should support these date ranges:

### Standard Ranges
- **7 days** (real-time): `WHERE case_date >= NOW() - INTERVAL '7 days'`
- **30 days**: `WHERE case_date >= NOW() - INTERVAL '30 days'`
- **60 days**: `WHERE case_date >= NOW() - INTERVAL '60 days'`
- **90 days** (default): `WHERE case_date >= NOW() - INTERVAL '90 days'`
- **All time**: No date filter

### Query Parameter
Add to all endpoints:
```python
@router.get("/endpoint")
def endpoint(
    days: Optional[int] = Query(90, description="Date range in days, 0 for all time")
):
    # Build date filter
    if days > 0:
        date_filter = H5N1Case.case_date >= datetime.now() - timedelta(days=days)
    else:
        date_filter = True  # No filter
```

---

## Missing Data Types

Based on database analysis, the following data types are **NOT** currently in the database:

### Human Cases
- **Status**: No human cases detected in current data
- **Impact**: Map will only show animal cases
- **Action Needed**: Ingest human H5N1 dataset when available
- **Frontend**: Already supports `caseType: 'human'` but won't display until data exists

### Environmental Cases
- **Status**: No environmental monitoring data
- **Impact**: Limited environmental tracking
- **Action Needed**: Ingest wastewater/environmental surveillance data if available

---

## Hotspot Detection Details

### ST_ClusterKMeans Implementation

```python
from geoalchemy2.functions import ST_ClusterKMeans, ST_Centroid, ST_MakePoint, ST_SetSRID
from sqlalchemy import func

def detect_hotspots(db: Session, days: int = 30, num_clusters: int = 5):
    """
    Detect geographic hotspots using KMeans clustering

    Args:
        db: Database session
        days: Date range for analysis
        num_clusters: Number of clusters to create

    Returns:
        List of hotspot zones with centroid, radius, and risk level
    """

    # Step 1: Create clusters using PostGIS
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
        # Calculate average severity
        severity_weights = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        avg_severity_score = sum(severity_weights.get(s, 1) for s in cluster.severities) / len(cluster.severities)

        if avg_severity_score >= 3:
            avg_severity = 'critical'
        elif avg_severity_score >= 2.5:
            avg_severity = 'high'
        elif avg_severity_score >= 1.5:
            avg_severity = 'medium'
        else:
            avg_severity = 'low'

        # Calculate radius (50km base, scale by case count)
        radius = min(50000 + (cluster.case_count * 5000), 100000)  # Cap at 100km

        hotspots.append({
            "id": f"h{cluster.cluster_id}",
            "lat": float(cluster.lat),
            "lng": float(cluster.lng),
            "radius": radius,
            "caseCount": cluster.case_count,
            "riskLevel": calculate_risk_level(cluster.case_count, avg_severity)
        })

    return hotspots
```

### Alternative: Density-Based Hotspots

For areas with varying case density, you could also use:

```sql
-- Find areas with high case density (within 50km radius)
WITH nearby_counts AS (
  SELECT
    a.id,
    a.latitude,
    a.longitude,
    COUNT(b.id) as nearby_cases
  FROM h5n1_cases a
  LEFT JOIN h5n1_cases b
    ON ST_DWithin(
      ST_SetSRID(ST_MakePoint(a.longitude, a.latitude), 4326)::geography,
      ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography,
      50000  -- 50km radius
    )
    AND b.case_date >= NOW() - INTERVAL '30 days'
  WHERE a.case_date >= NOW() - INTERVAL '30 days'
  GROUP BY a.id, a.latitude, a.longitude
)
SELECT * FROM nearby_counts WHERE nearby_cases >= 5;
```

---

## API Response Time Targets

- Map endpoints: < 500ms
- Dashboard aggregations: < 300ms
- Alerts: < 200ms

### Optimization Strategies
1. **Indexes**: Already defined in models.py
2. **Caching**: Use Redis for dashboard aggregations (5-minute TTL)
3. **Query Limits**: Default LIMIT 1000 for case queries
4. **Pagination**: Add offset/limit for large datasets

---

## Environment Variables

Ensure these are set:

```bash
# Backend
DATABASE_URL=postgresql://bets_user:bets_password@localhost:5432/bets_db
ENVIRONMENT=development
LOG_LEVEL=INFO

# Frontend (in .env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Router Setup in main.py

Update `backend/src/api/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from src.api.routes import data_ingestion, dashboard, map_data, alerts

app = FastAPI(title="BETS API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data_ingestion.router)
app.include_router(dashboard.router)
app.include_router(map_data.router)
app.include_router(alerts.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

---

## Quick Start Commands

```bash
# Terminal 1: Start Backend
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend (in frontend_work branch)
cd frontend
npm install
npm run dev

# Terminal 3: Test API
curl http://localhost:8000/api/map-data
curl http://localhost:8000/api/dashboard/overview
curl http://localhost:8000/api/alerts/recent
```

---

## Next Steps

1. **Implement map_data.py** - This unblocks the map visualization
2. **Implement dashboard.py** - This unblocks the dashboard
3. **Implement alerts.py** - This adds the alert system
4. **Update betsApi.ts** - Switch from mock to real data
5. **Test end-to-end** - Verify frontend displays real data

---

## Notes

- Database already has good data distribution across states (Virginia, Idaho, etc.)
- PostGIS extension is enabled (location column exists)
- All necessary indexes are in place
- No schema changes needed - just implement the endpoints
- Frontend TypeScript interfaces already match the response format
