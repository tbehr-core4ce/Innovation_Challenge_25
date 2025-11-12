# TODO make sure to intergrate this into actual main :) along with backend-api

"""
Example integration of the logging system into your FastAPI application.
Add this code to your main.py or app initialization file.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import structlog
import os
import time
from typing import Callable

from app.core.logging import (
    get_logger,
    setup_logging,
    configure_json_logging,
    configure_console_logging,
)
from app.core.errors import BETSError

# Initialize the FastAPI app
app = FastAPI(title="BETS - Bird flu Early Tracking System")

# Get logger
logger = get_logger(__name__)


# ============================================================================
# Logging Configuration
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


# ============================================================================
# Logging Middleware
# ============================================================================

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


# ============================================================================
# Error Handlers
# ============================================================================

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


# ============================================================================
# Example Endpoints with Logging
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "BETS API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy"}


@app.get("/cases")
async def get_cases(
    limit: int = 100,
    offset: int = 0,
):
    """Example endpoint with structured logging."""
    logger.info("Fetching cases", limit=limit, offset=offset)
    
    try:
        # Your logic here
        cases = []  # fetch from database
        
        logger.info(
            "Cases fetched successfully",
            count=len(cases),
            limit=limit,
            offset=offset,
        )
        
        return {"cases": cases}
        
    except Exception as e:
        logger.error(
            "Failed to fetch cases",
            error=str(e),
            limit=limit,
            offset=offset,
        )
        raise


# ============================================================================
# Application Shutdown
# ============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down")


# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    # The logging middleware will automatically log all requests
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development only
        log_level="info",
    )