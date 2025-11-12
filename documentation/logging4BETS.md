# BETS Logging System Usage Guide

## Overview

The BETS project uses a unified logging approach across both backend (Python/FastAPI) and frontend (TypeScript/React) with structured logging, automatic error logging, and consistent formatting.

## Backend (Python) Usage

### Basic Logging

```python
from app.core.logging import get_logger

# Create a logger for your module
logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debug information", user_id=123)
logger.info("General information", operation="fetch_cases")
logger.warning("Warning message", issue="slow_query")
logger.error("Error occurred", error=str(e), stack_trace=True)
logger.critical("Critical issue", system="database")
```

### Structured Logging with Context

```python
from app.core.logging import get_logger
import structlog

logger = get_logger(__name__)

# Add context that persists across multiple log calls
structlog.contextvars.bind_contextvars(
    request_id="abc-123",
    user_id=456
)

logger.info("Processing request")  # Will include request_id and user_id
logger.debug("Validating data")     # Will include request_id and user_id

# Clear context when done
structlog.contextvars.clear_contextvars()
```

### Error Handling with Logging

```python
from app.core.errors import (
    BETSError, 
    NotFoundError, 
    ValidationError,
    failed,
    require_value
)

# Errors automatically log with appropriate severity
def get_case(case_id: str):
    require_value(case_id, "case_id")  # Logs warning if missing
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise NotFoundError("Case", case_id)  # Logs error with context
    
    return case

# Custom errors with automatic logging
try:
    process_data()
except Exception as e:
    failed("process data", error=e, status_code=500)  # Logs error
```

### FastAPI Integration

```python
from fastapi import FastAPI
from app.core.logging import setup_logging, configure_console_logging, get_logger
import os

# Initialize logging on startup
app = FastAPI()
logger = get_logger(__name__)

@app.on_event("startup")
async def startup_event():
    # Use JSON logging in production
    if os.getenv("ENVIRONMENT") == "production":
        from app.core.logging import configure_json_logging
        configure_json_logging()
    else:
        # Use colorful console logging in development
        configure_console_logging()
    
    logger.info("Application started", environment=os.getenv("ENVIRONMENT"))

@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    logger.info("Fetching case", case_id=case_id)
    # ... your logic
```

### Alembic Migration Logging

The updated `alembic/env.py` automatically uses the centralized logging:

```bash
# Run migrations - logging is automatically configured
alembic upgrade head
```

## Frontend (TypeScript) Usage

### Basic Logging

```typescript
import { trace, debug, info, warn, error, fatal } from '@/core/logging';

// Simple logging
info('Map component mounted');
debug('Fetching H5N1 cases', { count: 100 });
warn('Slow API response', { duration: 3000 });
error('Failed to load data', { error: e.message });
```

### Logging with Context

```typescript
import { setLogContext, clearLogContext, info, debug } from '@/core/logging';

function MapVisualization() {
  // Set context for all subsequent logs
  setLogContext('MapVisualization');
  
  info('Component initializing');
  debug('Loading markers');
  
  // Clear context when done
  clearLogContext();
}
```

### Scoped Logger (Recommended for Components)

```typescript
import { createScopedLogger } from '@/core/logging';

function BETSMapComponent() {
  const logger = createScopedLogger('BETSMap');
  
  useEffect(() => {
    logger.info('Map initialized');
    logger.debug('Marker count', { count: markers.length });
  }, []);
  
  const handleError = (e: Error) => {
    logger.error('Map error', { error: e.message });
  };
}
```

### API Logging

```typescript
import { logApiRequest, logApiResponse } from '@/core/logging';
import { handleApiError, ApiError } from '@/core/errors';

async function fetchCases() {
  const url = '/api/cases';
  const method = 'GET';
  
  logApiRequest(method, url);
  
  try {
    const response = await fetch(url);
    logApiResponse(method, url, response.status);
    
    if (!response.ok) {
      handleApiError(response, url, method);
    }
    
    return await response.json();
  } catch (error) {
    handleApiError(error, url, method);
  }
}
```

### Error Handling

```typescript
import {
  failed,
  noValue,
  requireValue,
  notAuthorized,
  invalidParameters,
  notFound,
  CustomError,
  ValidationError,
  ApiError
} from '@/core/errors';

// Throw errors with automatic logging
function processCase(caseId: string | null) {
  // Throws MissingValueError and logs
  requireValue(caseId, 'Case ID');
  
  // Or use noValue() for a throwing version
  if (!data) {
    noValue('data');
  }
  
  // Custom error with logging
  if (invalidData) {
    invalidParameters('Case data is invalid');
  }
}

// Handle errors consistently
try {
  await fetchData();
} catch (error) {
  if (error instanceof ApiError) {
    // Handle API errors
    console.log(`API Error: ${error.status}`);
  } else if (error instanceof ValidationError) {
    // Handle validation errors
    console.log(`Validation failed: ${error.field}`);
  } else {
    // Generic error handling
    failed('process request', error);
  }
}
```

## Configuration

### Backend Environment Variables

Create a `.env` file:

```env
# Logging configuration
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=development # development, production

# In production, use JSON logging for log aggregation
# In development, use console logging with colors
```

### Frontend Log Levels

The frontend logs to the browser console. Control visibility in browser DevTools:
- **Verbose**: Shows TRACE and DEBUG
- **Info**: Shows INFO and above
- **Warnings**: Shows WARN and above
- **Errors**: Shows ERROR and FATAL only

## Best Practices

### When to Use Each Log Level

- **TRACE**: Very detailed, use sparingly for deep debugging
- **DEBUG**: Detailed diagnostic information for development
- **INFO**: General information about normal operations
- **WARN**: Something unexpected but recoverable happened
- **ERROR**: An error occurred that affects functionality
- **FATAL/CRITICAL**: Application-breaking errors

### Structured Logging Tips

1. **Use key-value pairs** for context instead of string interpolation:
   ```python
   # Good
   logger.info("User logged in", user_id=user.id, ip=request.ip)
   
   # Avoid
   logger.info(f"User {user.id} logged in from {request.ip}")
   ```

2. **Add context at boundaries**: Set context at request/component boundaries
   ```python
   structlog.contextvars.bind_contextvars(request_id=req.id)
   ```

3. **Log errors with context**: Include relevant data when logging errors
   ```typescript
   logger.error('Failed to load cases', { 
     endpoint: '/api/cases',
     status: 500,
     error: e.message 
   });
   ```

### Error Handling Best Practices

1. **Let errors bubble with context**: Don't catch and re-throw generic errors
2. **Use specific error types**: Makes error handling more precise
3. **Include recovery information**: Help users/developers understand what to do next
4. **Don't log twice**: Errors log automatically when thrown

## Testing

### Testing with Logging

```python
# Backend: Capture logs in tests
import structlog
from structlog.testing import CapturingLogger

def test_something(caplog):
    logger = get_logger(__name__)
    logger.info("test message", key="value")
    
    # Assert log output
    assert "test message" in caplog.text
```

```typescript
// Frontend: Mock console in tests
beforeEach(() => {
  jest.spyOn(console, 'info').mockImplementation();
  jest.spyOn(console, 'error').mockImplementation();
});

test('logs info message', () => {
  info('test message');
  expect(console.info).toHaveBeenCalledWith(expect.stringContaining('INFO'));
});
```

## Troubleshooting

**Problem**: Logs not appearing
- Backend: Check LOG_LEVEL environment variable
- Frontend: Check browser console filter settings

**Problem**: Too many logs
- Backend: Increase LOG_LEVEL (INFO or WARNING)
- Frontend: Filter by log level in DevTools

**Problem**: Missing context in logs
- Ensure you're using scoped loggers or setting context
- Check that context is being cleared properly

## Migration from Old Logging

If you have existing logging code:

```python
# Old
import logging
logging.info("message")

# New
from app.core.logging import get_logger
logger = get_logger(__name__)
logger.info("message")
```

```typescript
// Old
console.log("message");

// New
import { info } from '@/core/logging';
info("message");
```


# TODO

## Logging Dependencies
## Add these to your requirements.txt or pyproject.toml

structlog>=24.1.0 (dont follow the version please 0-0)
python-json-logger>=2.0.7  # Optional: for advanced JSON formatting
colorama>=0.4.6  # Optional: for colored console output on Windows

# BETS Backend Requirements
# Python 3.10+

# ============================================================================
# Web Framework
# ============================================================================
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6

# ============================================================================
# Database & ORM
# ============================================================================
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.9  # PostgreSQL adapter
geoalchemy2>=0.14.0     # PostGIS support for SQLAlchemy

# ============================================================================
# Logging
# ============================================================================
structlog>=24.1.0
python-json-logger>=2.0.7
colorama>=0.4.6  # For colored console output

# ============================================================================
# Security & Authentication
# ============================================================================
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
bcrypt>=4.1.0

# ============================================================================
# Data Processing
# ============================================================================
pandas>=2.1.0
numpy>=1.24.0
python-dateutil>=2.8.2

# ============================================================================
# Geospatial Processing
# ============================================================================
shapely>=2.0.0    # Geometric objects
pyproj>=3.6.0     # Coordinate transformations
geopy>=2.4.0      # Geocoding

# ============================================================================
# Data Validation
# ============================================================================
pydantic>=2.4.0
pydantic-settings>=2.0.0
email-validator>=2.1.0

# ============================================================================
# File Processing
# ============================================================================
openpyxl>=3.1.0   # Excel files
python-magic>=0.4.27  # File type detection

# ============================================================================
# HTTP Client
# ============================================================================
httpx>=0.25.0
requests>=2.31.0

# ============================================================================
# Configuration
# ============================================================================
python-dotenv>=1.0.0

# ============================================================================
# Testing (Development)
# ============================================================================
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.25.0  # For FastAPI test client

# ============================================================================
# Code Quality (Development)
# ============================================================================
black>=23.10.0
flake8>=6.1.0
mypy>=1.6.0
isort>=5.12.0

# ============================================================================
# Documentation (Development)
# ============================================================================
mkdocs>=1.5.0
mkdocs-material>=9.4.0

# ============================================================================
# Optional: Monitoring & Performance
# ============================================================================
# sentry-sdk[fastapi]>=1.35.0
# prometheus-client>=0.18.0
# opentelemetry-api>=1.20.0