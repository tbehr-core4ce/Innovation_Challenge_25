"""
src/api/main.py
BETS Backend API - H5N1 Case Data Service
FastAPI backend for serving map visualization data
"""
import os
import time
from datetime import datetime
from typing import Callable

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.errors import BETSError
from core.logging import (configure_console_logging, configure_json_logging,
                          get_logger, setup_logging)
from routes import data_ingestion, dashboard, map_data, alerts

app = FastAPI(title="BETS API", version="1.0.0")

# Include all routers
app.include_router(data_ingestion.router)
app.include_router(dashboard.router)
app.include_router(map_data.router)
app.include_router(alerts.router)

logger = get_logger(__name__)

# ============================================================================
# Base Endpoints | Configurations
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "BETS API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

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

# Enable CORS for React/Next.js frontend
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
