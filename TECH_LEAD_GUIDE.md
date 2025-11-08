# BETS Map Visualization - Tech Lead Guide

## ✅ What's Built

I've created a complete map visualization system with:

### Frontend (React + TypeScript)
- **BETSMapVisualization.tsx** - Core map component with Leaflet
- **BETSDashboard.tsx** - Main dashboard with auto-refresh
- **betsApiService.ts** - API client for backend communication
- **ExampleApp.tsx** - Simple usage example

### Backend (Python + FastAPI)
- **backend_api.py** - Complete REST API with:
  - `/api/map-data` - Cases + hotspots
  - `/api/cases` - Filtered case queries
  - `/api/hotspots` - Risk zones
  - `/api/stats` - Aggregate statistics
  - `/api/alerts` - Threshold-based alerts

### DevOps
- **docker-compose.yml** - One-command deployment
- **Dockerfiles** - Containerization for both services
- **requirements.txt** - Python dependencies
- **package.json** - Node dependencies

---

## 🎯 Why This Stack Works for BETS

### Python Backend ✅
**Wins:**
- Pandas for data ingestion/cleaning
- Simple geospatial calculations
- Fast prototyping with FastAPI
- Auto-generated API docs (Swagger)
- Easy to extend with ML/anomaly detection

### React Frontend ✅
**You already know this:**
- TypeScript for type safety
- Same patterns as snappi_dashboard
- Leaflet for maps (simpler than Mapbox)
- No new learning curve for you

---

## Quick Start (3 Commands)

```bash
# 1. Start backend
cd backend && python backend_api.py

# 2. Start frontend (new terminal)
cd frontend && npm install && npm start

# 3. Open browser
http://localhost:3000
```

Or with Docker:
```bash
docker compose up --build
```

---

## 📊 Map Features Implemented

### Core Requirements ✅
- [x] Interactive map with pan/zoom
- [x] Case markers (color-coded by severity)
- [x] Clustering for performance
- [x] Hotspot zones (circular risk areas)
- [x] Case type filtering
- [x] Real-time stats panel
- [x] Click markers for details
- [x] Auto-refresh capability

### Stretch Goals (Easy Adds)
- [ ] Animated playback (timeline slider)
- [ ] Heatmap layer
- [ ] 3D terrain view
- [ ] Predictive risk scoring (ML)
- [ ] Export reports (PDF)

---

## 🔧 What Your Team Should Do

### Non-Tech Team Tasks:
1. **Data Collection** - Find real H5N1 datasets:
   - CDC FluView data
   - USDA APHIS reports
   - State health department CSVs
   
2. **Requirements Refinement**:
   - Define alert thresholds (e.g., ">3 human cases = red alert")
   - Specify what visualizations matter most
   - Determine dashboard layout preferences

3. **Testing**:
   - Manual test all map controls
   - Verify case data displays correctly
   - Test on different browsers
   - Check mobile responsiveness

4. **Documentation**:
   - User guide for demo
   - Data source citations
   - Assumptions document

### Your Tech Lead Tasks:
1. **Data Pipeline** - Ingest real H5N1 data:
   ```python
   # In backend_api.py
   import pandas as pd
   df = pd.read_csv('h5n1_cases.csv')
   cases = df.to_dict('records')
   ```

2. **Hotspot Algorithm** - Implement DBSCAN clustering:
   ```python
   from sklearn.cluster import DBSCAN
   # Cluster cases by lat/lng proximity
   ```

3. **Alert System** - Define business rules:
   ```python
   def check_alerts(cases):
       if len([c for c in cases if c['severity'] == 'critical']) > 5:
           return {"level": "critical", "message": "..."}
   ```

4. **Deployment** - Deploy to AWS/Azure/GCP
   - Use Docker Compose on EC2
   - Or deploy separately (Vercel frontend + Lambda backend)

---

## 📈 Architecture Decision Record

### Why Python Backend?
**Decision:** Use FastAPI (Python) instead of Rails

**Reasoning:**
- BETS is data-heavy, not CRUD-heavy
- Python's data science ecosystem (pandas, geopandas, scipy)
- Team doesn't know Rails
- Faster to prototype for government demo

**Trade-offs:**
- ✅ Better for data processing
- ✅ Simpler for non-tech team
- ✅ Auto-generated API docs
- ❌ You have more Rails experience
- ❌ Not reusing snappi_dashboard patterns

**Verdict:** Worth it for this specific use case

### Why Leaflet over Mapbox?
**Decision:** Use Leaflet for maps

**Reasoning:**
- Free, no API keys needed
- Simpler API than Mapbox
- Open-source, government-friendly
- Good enough for prototype

**Trade-offs:**
- ✅ No costs, no quotas
- ✅ Easier to learn
- ❌ Less fancy visuals than Mapbox
- ❌ Fewer built-in features

**Verdict:** Perfect for prototype

---

## File Organization

```
bets-prototype/
├── backend/
│   ├── backend_api.py          # ← START HERE
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BETSMapVisualization.tsx  # ← Core map
│   │   │   └── BETSDashboard.tsx         # ← Main app
│   │   └── services/
│   │       └── betsApiService.ts         # ← API client
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## UI/UX Notes

### Color Scheme
- **Low**: Green (#22c55e)
- **Medium**: Yellow (#eab308)
- **High**: Orange (#f97316)
- **Critical**: Red (#ef4444)

### Case Type Symbols
- **Human**: ● (circle)
- **Avian**: ▲ (triangle)
- **Dairy**: ■ (square)
- **Environmental**: ◆ (diamond)

### Layout
- Map takes full screen
- Controls in top-right
- Stats panel in bottom-left
- Header bar with refresh button

---

## API Integration Pattern

**Frontend calls backend like this:**

```typescript
// In BETSDashboard.tsx
const fetchData = async () => {
  const data = await betsApi.getMapData();
  setCases(data.cases);
  setHotspots(data.hotspots);
};
```

**Backend serves data like this:**

```python
# In backend_api.py
@app.get("/api/map-data")
def get_map_data():
    return {
        "cases": mock_cases,
        "hotspots": detect_hotspots(mock_cases)
    }
```

**You change mock_cases to real data:**

```python
# Replace mock_cases with database query
cases = db.query(Case).filter(Case.date > cutoff).all()
```

---

## Next Steps (Priority Order)

1. **Week 1 - Data**
   - [ ] Get real H5N1 datasets
   - [ ] Parse CSVs into case format
   - [ ] Replace mock_cases in backend

2. **Week 2 - Features**
   - [ ] Implement hotspot detection algorithm
   - [ ] Add alert threshold system
   - [ ] Create export functionality

3. **Week 3 - Polish**
   - [ ] Add animated timeline
   - [ ] Improve UI/UX based on feedback
   - [ ] Write user documentation

4. **Week 4 - Demo Prep**
   - [ ] Deploy to cloud
   - [ ] Prepare demo script
   - [ ] Test on presentation setup

---

## 🐛 Common Issues (From Your Docker Experience)

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### CORS Errors
Already configured in `backend_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"]
)
```

### Map Not Rendering
- Check browser console for Leaflet CSS errors
- Ensure lat/lng are valid numbers
- Verify cases array isn't empty

---

## Tips for Your Team

1. **Use the Swagger docs** - Auto-generated at `http://localhost:8000/docs`
2. **Test API directly** - Use Swagger UI to test endpoints before frontend work
3. **Start simple** - Get basic map working, then add features
4. **Version control** - Commit early, commit often
5. **Document assumptions** - Write down what data fields mean

---

## Success Criteria

The demo should show:
- ✅ Map loads with H5N1 case markers
- ✅ Cases are color-coded by severity
- ✅ Hotspots show high-risk areas
- ✅ Filters work (human cases only, etc.)
- ✅ Stats update in real-time
- ✅ Clicking markers shows details
- ✅ Data refreshes automatically

**Good enough for government demo? YES.**

---

## Need Help?

1. Check the README.md
2. Look at ExampleApp.tsx for usage
3. Use Swagger docs for API testing
4. Console.log is your friend

