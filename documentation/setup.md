FastAPI - Modern, fast, auto-generated API docs
# Simpler than Rails for a prototype
```

### React Frontend - Perfect for:
- Interactive dashboards
- Real-time map visualizations
- Chart libraries (Recharts, Plotly.js)
- Responsive UI for decision-makers

## Proposed Stack:
```
Frontend: React + TypeScript + Tailwind
  └─ Libraries: Leaflet/Mapbox for maps, Recharts for charts
  
Backend: FastAPI (Python)
  └─ pandas/geopandas for data processing
  └─ SQLite or PostgreSQL for storage
  
Deployment: Docker Compose (you already know this)
```

## Quick Start Architecture:
```
/bets-prototype
├── frontend/          (React + TypeScript)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── MapView.tsx
│   │   │   └── AlertPanel.tsx
│   │   └── services/
│   │       └── api.ts
│   └── package.json
│
├── backend/           (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── data_ingestion.py
│   │   │   ├── analytics.py
│   │   │   └── alerts.py
│   │   ├── services/
│   │   │   ├── data_processor.py
│   │   │   └── anomaly_detector.py
│   │   └── models/
│   └── requirements.txt
│
└── docker-compose.yml