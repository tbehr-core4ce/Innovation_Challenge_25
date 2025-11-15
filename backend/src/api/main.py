"""
src/api/main.py
BETS Backend API - H5N1 Case Data Service
FastAPI backend for serving map visualization data
"""
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional
import uuid
import time
import os
import structlog
from utils.settings import settings
from routes import data_ingestion
from core.models import H5N1Case, HotspotZone, MapDataResponse, CaseType, Severity, RiskLevel, Status, StatsResponse
from parsers.csv_parser import parse_h5n1_csv
from core.logging import (
    get_logger,
    setup_logging,
    configure_json_logging,
    configure_console_logging,
)
from core.errors import BETSError

app = FastAPI(title="BETS API", version="1.0.0")

app.include_router(data_ingestion.router)

logger = get_logger(__name__)

# ==================== API ENDPOINTS ====================
# Connect parser to the FastAPI backend
@app.post("/api/ingest-csv")
async def ingest_csv_data(file: UploadFile):
    """
    Upload and ingest CSV file of H5N1 cases
    """
    # Save uploaded file
    contents = await file.read()
    with open(f"/tmp/{file.filename}", "wb") as f:
        f.write(contents)
    
    # Parse CSV
    cases = parse_h5n1_csv(f"/tmp/{file.filename}")
    
    # Validate
    validator = DataValidator()
    valid_cases = [c for c in cases if validator.validate_case(c)]
    
    # Store in database (or update mock_cases for now)
    mock_cases.extend(valid_cases)
    
    return {
        "message": f"Ingested {len(valid_cases)} cases",
        "validation_report": validator.get_report()
    }


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
    # in example code params are limit and offset
    # logger.info("Fetching cases", limit=limit, offset=offset)
    try:
        cases = mock_cases.copy() # TODO change to database operations :)
        
        logger.info(
            "Cases fetched successfully",
            count=len(cases),
            # limit=limit,
            # offset=offset,
        )
        
        if case_type:
            cases = [c for c in cases if c["caseType"] == case_type]
        
        if severity:
            cases = [c for c in cases if c["severity"] == severity]
        
        if status:
            cases = [c for c in cases if c["status"] == status]
        
        return cases
    
    except Exception as e:
        logger.error(
            "Failed to fetch cases",
            error=str(e),
            # limit=limit,
            # offset=offset,
        )
        #raise 

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

# ============================================================================
# Base Endpoints | Configurations
# ============================================================================

@app.on_event("startup")
async def configure_logging_on_startup():
    """Configure logging based on environment."""
    environment = os.getenv("ENVIRONMENT", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Initialize base logging
    setup_logging(log_level)
    
    # Configure output format based on environment
    if environment == "production":
        configure_json_logging()
        logger.info("Logging configured for production (JSON output)")
    else:
        configure_console_logging()
        logger.info("Logging configured for development (console output)")
    
    logger.info(
        "Application starting",
        environment=environment,
        log_level=log_level,
    )

@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable):
    """
    Log all HTTP requests with timing and status information.
    Adds request context to all logs within the request lifecycle.
    """
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    
    # Bind request context for all logs in this request
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )
    
    # Log request
    logger.info(
        "Request started",
        user_agent=request.headers.get("user-agent"),
    )
    
    # Process request and measure time
    start_time = time.time()
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log response
        logger.info(
            "Request completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            "Request failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=duration_ms,
            exc_info=True,
        )
        raise
        
    finally:
        # Clear request context
        structlog.contextvars.clear_contextvars()

@app.exception_handler(BETSError)
async def bets_error_handler(request: Request, exc: BETSError):
    """
    Handle BETS custom errors.
    Logging is already done in the error constructor.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all error handler for unexpected exceptions.
    """
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down")

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "BETS API", "status": "running"}

@app.get("/health")
def health_check():
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

        # reload=True,  # Development only
