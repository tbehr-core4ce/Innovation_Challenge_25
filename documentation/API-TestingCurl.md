# 1. Health Check
curl http://localhost:8000/health

# 2. Root Endpoint
curl http://localhost:8000/

# 3. Map Data (with pretty JSON)
curl -s http://localhost:8000/api/map-data?days=7 | jq '.'

# 4. Dashboard Overview
curl -s http://localhost:8000/api/dashboard/overview | jq '.'

# 5. Dashboard Timeline
curl -s http://localhost:8000/api/dashboard/timeline | jq '.'

# 6. Dashboard Regions
curl -s http://localhost:8000/api/dashboard/regions | jq '.'

# 7. Animal Categories
curl -s http://localhost:8000/api/dashboard/animal-categories | jq '.'

# 8. Status Breakdown
curl -s http://localhost:8000/api/dashboard/status | jq '.'

# 9. Data Sources
curl -s http://localhost:8000/api/dashboard/sources | jq '.'

# 10. Recent Alerts
curl -s http://localhost:8000/api/alerts/recent | jq '.'

# Map data - last 30 days
curl -s "http://localhost:8000/api/map-data?days=30" | jq '.'

# Map data - all time (0 = no date filter)
curl -s "http://localhost:8000/api/map-data?days=0" | jq '.'

# Map data - filter by poultry only
curl -s "http://localhost:8000/api/map-data?case_type=poultry" | jq '.'

# Map data - filter by critical severity
curl -s "http://localhost:8000/api/map-data?severity=critical" | jq '.'

# Dashboard overview - last 30 days
curl -s "http://localhost:8000/api/dashboard/overview?days=30" | jq '.'

# Alerts - last 7 days
curl -s "http://localhost:8000/api/alerts/recent?days=7&limit=5" | jq '.'

# Count map cases
curl -s "http://localhost:8000/api/map-data?days=30" | jq '.cases | length'

# Count hotspots
curl -s "http://localhost:8000/api/map-data?days=30" | jq '.hotspots | length'

# Count alerts
curl -s "http://localhost:8000/api/alerts/recent" | jq 'length'