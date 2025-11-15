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





def seed():
    from src.parsers.ingestors import CommercialBackyardFlock_Ingestor

    ingest = CommercialBackyardFlock_Ingestor(file_path=)

    df = ingest.ingest()

    



if __name__ = main
    seed()