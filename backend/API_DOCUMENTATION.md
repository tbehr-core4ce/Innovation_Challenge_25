# BETS API Documentation

Bio-Event Tracking System (BETS) - H5N1 Surveillance API

**Base URL**: `http://localhost:8000`

**Version**: 1.0.0

---

## Table of Contents

1. [Health & Status Endpoints](#health--status-endpoints)
2. [Dashboard Endpoints](#dashboard-endpoints)
3. [Map Data Endpoints](#map-data-endpoints)
4. [Alert Endpoints](#alert-endpoints)

---

## Health & Status Endpoints

### GET /health

Health check endpoint to verify API is running.

**Parameters**: None

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T00:35:43.123456"
}
```

**Example**:
```bash
curl 'http://localhost:8000/health'
```

---

### GET /debug/config

Debug endpoint to verify configuration (development only).

**Parameters**: None

**Response**:
```json
{
  "DATABASE_URL": "postgresql+psycopg://bets_user:***@postgres:5432/bets_db",
  "ENVIRONMENT": "dev",
  "ENV_DATABASE_URL": "postgresql+psycopg://bets_user:bets_password@postg..."
}
```

**Example**:
```bash
curl 'http://localhost:8000/debug/config'
```

---

## Dashboard Endpoints

### GET /api/dashboard/overview

Get aggregate overview metrics for the dashboard.

**Query Parameters**:
- `days` (integer, optional): Number of days to look back. Default: 90. Use 0 for all time.

**Response**:
```json
{
  "totalCases": 1234,
  "confirmedCases": 890,
  "suspectedCases": 234,
  "underInvestigation": 110,
  "criticalCases": 45,
  "highSeverityCases": 123,
  "totalAnimalsAffected": 45678,
  "totalAnimalsDeceased": 12345
}
```

**Example**:
```bash
# Last 90 days (default)
curl 'http://localhost:8000/api/dashboard/overview'

# Last 30 days
curl 'http://localhost:8000/api/dashboard/overview?days=30'

# All time
curl 'http://localhost:8000/api/dashboard/overview?days=0'
```

---

### GET /api/dashboard/timeline

Get monthly timeline data broken down by animal category.

**Query Parameters**:
- `months` (integer, optional): Number of months to include. Default: 12.

**Response**:
```json
[
  {
    "month": "Jan",
    "total": 156,
    "poultry": 89,
    "dairy_cattle": 23,
    "wild_bird": 34,
    "wild_mammal": 10
  },
  {
    "month": "Feb",
    "total": 178,
    "poultry": 95,
    "dairy_cattle": 28,
    "wild_bird": 42,
    "wild_mammal": 13
  }
]
```

**Example**:
```bash
# Last 12 months (default)
curl 'http://localhost:8000/api/dashboard/timeline'

# Last 6 months
curl 'http://localhost:8000/api/dashboard/timeline?months=6'
```

---

### GET /api/dashboard/regions

Get top regions (states/provinces) by case count.

**Query Parameters**:
- `days` (integer, optional): Number of days to look back. Default: 90.
- `limit` (integer, optional): Maximum number of regions to return. Default: 10.

**Response**:
```json
[
  {
    "region": "California",
    "caseCount": 456
  },
  {
    "region": "Texas",
    "caseCount": 389
  },
  {
    "region": "Iowa",
    "caseCount": 234
  }
]
```

**Example**:
```bash
# Top 10 regions, last 90 days (default)
curl 'http://localhost:8000/api/dashboard/regions'

# Top 5 regions, last 30 days
curl 'http://localhost:8000/api/dashboard/regions?days=30&limit=5'
```

---

### GET /api/dashboard/animal-categories

Get distribution of cases by animal category with color coding.

**Query Parameters**:
- `days` (integer, optional): Number of days to look back. Default: 90.

**Response**:
```json
[
  {
    "category": "Poultry",
    "count": 567,
    "color": "#f97316"
  },
  {
    "category": "Dairy Cattle",
    "count": 234,
    "color": "#eab308"
  },
  {
    "category": "Wild Bird",
    "count": 189,
    "color": "#3b82f6"
  },
  {
    "category": "Wild Mammal",
    "count": 45,
    "color": "#8b5cf6"
  },
  {
    "category": "Domestic Mammal",
    "count": 23,
    "color": "#ec4899"
  },
  {
    "category": "Other",
    "count": 12,
    "color": "#6b7280"
  }
]
```

**Example**:
```bash
# Last 90 days (default)
curl 'http://localhost:8000/api/dashboard/animal-categories'

# Last 30 days
curl 'http://localhost:8000/api/dashboard/animal-categories?days=30'
```

---

### GET /api/dashboard/status

Get distribution of cases by status (confirmed, suspected, under investigation).

**Query Parameters**:
- `days` (integer, optional): Number of days to look back. Default: 90.

**Response**:
```json
[
  {
    "status": "confirmed",
    "count": 890
  },
  {
    "status": "suspected",
    "count": 234
  },
  {
    "status": "under_investigation",
    "count": 110
  }
]
```

**Example**:
```bash
# Last 90 days (default)
curl 'http://localhost:8000/api/dashboard/status'

# Last 7 days
curl 'http://localhost:8000/api/dashboard/status?days=7'
```

---

### GET /api/dashboard/sources

Get distribution of cases by data source.

**Query Parameters**:
- `days` (integer, optional): Number of days to look back. Default: 90.

**Response**:
```json
[
  {
    "source": "USDA",
    "count": 567
  },
  {
    "source": "CDC",
    "count": 345
  },
  {
    "source": "STATE_HEALTH",
    "count": 234
  }
]
```

**Example**:
```bash
# Last 90 days (default)
curl 'http://localhost:8000/api/dashboard/sources'

# All time
curl 'http://localhost:8000/api/dashboard/sources?days=0'
```

---

## Map Data Endpoints

### GET /api/map-data

Get H5N1 case locations and detected hotspot zones for map visualization.

**Query Parameters**:
- `days` (integer, optional): Number of days to look back for cases. Default: 30.
- `lat_min` (float, optional): Minimum latitude for bounding box filter.
- `lat_max` (float, optional): Maximum latitude for bounding box filter.
- `lng_min` (float, optional): Minimum longitude for bounding box filter.
- `lng_max` (float, optional): Maximum longitude for bounding box filter.
- `category` (string, optional): Filter by animal category (e.g., "poultry", "dairy_cattle").
- `severity` (string, optional): Filter by severity level ("low", "medium", "high", "critical").

**Response**:
```json
{
  "cases": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "lat": 37.7749,
      "lng": -122.4194,
      "location": "San Francisco, California",
      "caseType": "poultry",
      "count": 1500,
      "severity": "high",
      "reportedDate": "2025-01-15",
      "status": "confirmed",
      "description": "Commercial poultry farm outbreak - 1,500 birds affected"
    }
  ],
  "hotspots": [
    {
      "id": "h0",
      "lat": 37.7749,
      "lng": -122.4194,
      "radius": 75000,
      "caseCount": 15,
      "riskLevel": "high"
    },
    {
      "id": "h1",
      "lat": 34.0522,
      "lng": -118.2437,
      "radius": 95000,
      "caseCount": 23,
      "riskLevel": "critical"
    }
  ]
}
```

**Hotspot Detection**:
- Uses PostGIS ST_ClusterKMeans algorithm to identify 5 geographic clusters
- Risk level calculated based on:
  - Case density (number of cases in cluster)
  - Average severity score
- Radius scales from 50km (base) up to 100km for large clusters

**Risk Levels**:
- **Critical**: 10+ cases with high average severity (score ≥ 3)
- **High**: 5+ cases OR high average severity
- **Medium**: 3+ cases OR medium average severity
- **Low**: Fewer than 3 cases with low severity

**Example**:
```bash
# Last 30 days, all cases (default)
curl 'http://localhost:8000/api/map-data'

# Last 7 days
curl 'http://localhost:8000/api/map-data?days=7'

# Filter by bounding box (California area)
curl 'http://localhost:8000/api/map-data?lat_min=32&lat_max=42&lng_min=-125&lng_max=-114'

# Filter by category
curl 'http://localhost:8000/api/map-data?category=poultry'

# Filter by severity
curl 'http://localhost:8000/api/map-data?severity=critical'

# Combined filters
curl 'http://localhost:8000/api/map-data?days=7&category=dairy_cattle&severity=high'
```

---

## Alert Endpoints

### GET /api/alerts/recent

Get recent alerts generated from case patterns and anomalies.

**Query Parameters**:
- `days` (integer, optional): Look back period in days. Default: 30.
- `limit` (integer, optional): Maximum number of alerts to return. Default: 10.

**Response**:
```json
[
  {
    "id": "alert_critical_123",
    "type": "outbreak",
    "severity": "critical",
    "title": "Critical Severity Case",
    "message": "Critical case reported: San Francisco, California - Commercial poultry farm outbreak",
    "location": "San Francisco, California",
    "date": "2025-01-15T14:30:00",
    "caseCount": 1
  },
  {
    "id": "alert_cluster_456",
    "type": "cluster",
    "severity": "high",
    "title": "Geographic Cluster Detected",
    "message": "5 cases detected in Los Angeles County, California within 7 days",
    "location": "Los Angeles County, California",
    "date": "2025-01-14T09:15:00",
    "caseCount": 5
  },
  {
    "id": "alert_large_789",
    "type": "outbreak",
    "severity": "high",
    "title": "Large Outbreak",
    "message": "Large outbreak reported: 12,500 animals affected in Iowa",
    "location": "Iowa",
    "date": "2025-01-13T16:45:00",
    "caseCount": 1
  }
]
```

**Alert Types**:

1. **Critical Severity Cases**
   - Triggered by: Cases marked as critical severity
   - Type: "outbreak"
   - Severity: "critical"

2. **Geographic Clusters**
   - Triggered by: 3+ cases in same county within 7 days
   - Type: "cluster"
   - Severity: "high"

3. **Large Outbreaks**
   - Triggered by: Single event affecting 10,000+ animals
   - Type: "outbreak"
   - Severity: "high"

4. **Severity Spikes**
   - Triggered by: 5+ high/critical severity cases within 3 days
   - Type: "spike"
   - Severity: "high"

**Example**:
```bash
# Last 30 days, up to 10 alerts (default)
curl 'http://localhost:8000/api/alerts/recent'

# Last 7 days, up to 5 alerts
curl 'http://localhost:8000/api/alerts/recent?days=7&limit=5'

# Last 60 days, up to 20 alerts
curl 'http://localhost:8000/api/alerts/recent?days=60&limit=20'
```

---

## Data Models

### Animal Categories
- `poultry` - Chickens, turkeys, ducks, geese
- `dairy_cattle` - Dairy cows
- `wild_bird` - Wild bird species
- `wild_mammal` - Wild mammals (foxes, skunks, etc.)
- `domestic_mammal` - Domestic mammals (cats, dogs, etc.)
- `other` - Other or unspecified

### Case Status
- `confirmed` - Laboratory confirmed H5N1
- `suspected` - Suspected case pending confirmation
- `under_investigation` - Currently being investigated
- `negative` - Tested negative
- `inconclusive` - Inconclusive test results

### Severity Levels
- `low` - Minor impact, few animals affected
- `medium` - Moderate impact
- `high` - Significant impact, many animals affected
- `critical` - Severe outbreak, critical intervention needed

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request**:
```json
{
  "error": "Invalid query parameter",
  "status_code": 400
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "status_code": 500
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. This may be added in future versions.

---

## CORS

The API allows cross-origin requests from:
- `http://localhost:3000` (frontend development server)

Additional origins can be configured in the backend configuration.

---

## Database

- **Engine**: PostgreSQL 18 with PostGIS 3.6
- **Connection**: Docker network (`postgres:5432`)
- **Spatial Features**: PostGIS for geographic clustering and spatial queries

---

## Notes

- All timestamps are in ISO 8601 format
- All coordinates use WGS 84 (EPSG:4326) spatial reference system
- Case counts exclude soft-deleted records (`is_deleted = false`)
- Geographic clustering uses ST_ClusterKMeans for performance
- Default query parameters provide sensible defaults for most use cases
