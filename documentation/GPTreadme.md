# BETS - Bio-Event Tracking System
## H5N1 Map Visualization Prototype

A real-time interactive map visualization system for tracking H5N1 bird flu cases across multiple categories (human, avian, dairy, environmental).

---

## Features

- **Interactive Map Visualization**
  - Clustered markers for better performance
  - Color-coded severity indicators (Low/Medium/High/Critical)
  - Different shapes for case types (●Human ▲Avian ■Dairy ◆Environmental)
  - Click markers for detailed case information

- **Hotspot Detection**
  - Circular zones showing high-density outbreak areas
  - Risk-level color coding
  - Dynamic radius based on case concentration

- **Real-Time Updates**
  - Auto-refresh capabilities (configurable intervals)
  - Live statistics panel
  - Last-updated timestamps

- **Filtering & Controls**
  - Filter by case type
  - Toggle marker clustering
  - Show/hide hotspot zones
  - Heatmap view (stretch goal)

- **Dashboard Statistics**
  - Total case counts by type
  - Severity breakdown
  - Active vs contained cases

---

## Architecture

```
┌─────────────────────────────────────┐
│       React Frontend (TypeScript)   │
│  ┌─────────────────────────────┐   │
│  │  BETSDashboard.tsx          │   │
│  │  (Main orchestrator)        │   │
│  └─────────┬───────────────────┘   │
│            │                        │
│  ┌─────────▼───────────────────┐   │
│  │  BETSMapVisualization.tsx   │   │
│  │  (Leaflet map component)    │   │
│  └─────────────────────────────┘   │
│            │                        │
│  ┌─────────▼───────────────────┐   │
│  │  betsApiService.ts          │   │
│  │  (API client)               │   │
│  └─────────┬───────────────────┘   │
└────────────┼───────────────────────┘
             │ HTTP/REST
             │
┌────────────▼───────────────────────┐
│       Python Backend (FastAPI)     │
│  ┌─────────────────────────────┐  │
│  │  backend_api.py             │  │
│  │  (/api/map-data)            │  │
│  │  (/api/cases)               │  │
│  │  (/api/hotspots)            │  │
│  │  (/api/stats)               │  │
│  │  (/api/alerts)              │  │
│  └─────────┬───────────────────┘  │
└────────────┼───────────────────────┘
             │
┌────────────▼───────────────────────┐
│    Data Sources (Future)           │
│  - CSV uploads                     │
│  - Database (PostgreSQL)           │
│  - External APIs (CDC, USDA)       │
└────────────────────────────────────┘
```

---

## Installation

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.9+
- **pip** package manager

### Backend Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server**:
   ```bash
   python backend_api.py
   ```
   
   Backend will be available at: `http://localhost:8000`
   
   API docs (Swagger): `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Create `.env` file** (optional):
   ```bash
   REACT_APP_API_URL=http://localhost:8000
   ```

3. **Run the development server**:
   ```bash
   npm start
   ```
   
   Frontend will open at: `http://localhost:3000`

---

## Quick Start

1. **Start the backend**:
   ```bash
   python backend_api.py
   ```

2. **In a new terminal, start the frontend**:
   ```bash
   npm start
   ```

3. **Open your browser** to `http://localhost:3000`

You should see the map with sample H5N1 case data!

---

## Project Structure

```
bets-prototype/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BETSMapVisualization.tsx    # Main map component
│   │   │   └── BETSDashboard.tsx           # Dashboard wrapper
│   │   ├── services/
│   │   │   └── betsApiService.ts           # API client
│   │   └── App.tsx                         # Root component
│   └── package.json
│
├── backend/
│   ├── backend_api.py                      # FastAPI server
│   └── requirements.txt
│
└── README.md
```

---

## 🔌 API Endpoints

### Get Map Data
```bash
GET /api/map-data
Query params:
  - case_type: human|avian|dairy|environmental
  - severity: low|medium|high|critical
  - days: integer (default: 7)

Response:
{
  "cases": [...],
  "hotspots": [...],
  "lastUpdated": "2025-11-07T..."
}
```

### Get Cases
```bash
GET /api/cases
Query params:
  - case_type, severity, status

Response: Array of H5N1Case objects
```

### Get Hotspots
```bash
GET /api/hotspots
Query params:
  - min_risk_level: low|medium|high|critical

Response: Array of HotspotZone objects
```

### Get Statistics
```bash
GET /api/stats

Response:
{
  "totalCases": 150,
  "humanCases": 5,
  "avianCases": 100,
  ...
}
```

### Get Alerts
```bash
GET /api/alerts

Response: Array of active alerts
```

---

## 🎨 Customization

### Adding New Case Types

**Backend** (`backend_api.py`):
```python
class CaseType(str, Enum):
    human = "human"
    avian = "avian"
    dairy = "dairy"
    environmental = "environmental"
    swine = "swine"  # Add new type
```

**Frontend** (`BETSMapVisualization.tsx`):
```typescript
const shapes: Record<H5N1Case['caseType'], string> = {
  human: '●',
  avian: '▲',
  dairy: '■',
  environmental: '◆',
  swine: '★',  // Add new shape
};
```

### Changing Map Center/Zoom

```typescript
<BETSMapVisualization
  cases={cases}
  hotspots={hotspots}
  center={[39.8283, -98.5795]}  // Change coordinates
  zoom={6}                       // Change zoom level
/>
```

### Adjusting Refresh Interval

Edit the default in `BETSDashboard.tsx`:
```typescript
const [refreshInterval, setRefreshInterval] = useState<number>(30000); // 30 seconds
```

---

## 🧪 Testing with Sample Data

The system includes mock data for testing. To add more cases:

**Backend** (`backend_api.py`):
```python
mock_cases.append({
    "id": "new-1",
    "lat": 40.7128,
    "lng": -74.0060,
    "location": "New York, NY",
    "caseType": "human",
    "count": 3,
    "severity": "high",
    "reportedDate": "2025-11-07",
    "status": "active"
})
```

---

## 📊 Data Integration (Next Steps)

For production, replace mock data with:

1. **Database Integration** (PostgreSQL + PostGIS):
   ```python
   from sqlalchemy import create_engine
   engine = create_engine('postgresql://user:pass@localhost/bets')
   ```

2. **CSV Data Import**:
   ```python
   import pandas as pd
   df = pd.read_csv('h5n1_cases.csv')
   ```

3. **External API Integration** (CDC, USDA):
   ```python
   import requests
   response = requests.get('https://api.cdc.gov/h5n1/cases')
   ```

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't connect to backend
- Check if backend is running: `curl http://localhost:8000/health`
- Verify CORS is configured in `backend_api.py`
- Check `.env` file has correct API URL

### Map not showing
- Open browser console (F12) and check for errors
- Ensure Leaflet CSS is imported
- Verify case data has valid lat/lng values

### Markers not clustering
- Install `react-leaflet-cluster`: `npm install react-leaflet-cluster`
- Check console for clustering errors
- Try disabling clustering temporarily

---

## 🔐 Security Notes (For Production)

- Add authentication to API endpoints
- Use environment variables for sensitive configs
- Implement rate limiting
- Add input validation on all endpoints
- Use HTTPS in production
- Sanitize user inputs
- Add API key authentication

---

## 📝 License

This is a prototype/proof-of-concept for the BETS challenge.

---

## 👥 Team Roles

- **Tech Lead**: Architecture, backend, frontend integration
- **Junior Dev**: 
- **Non-tech team**: Data collection, testing, documentation, requirements

---

## Support

For issues or questions, open a GitHub issue or contact the tech lead.