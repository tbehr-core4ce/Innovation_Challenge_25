I'll set up a comprehensive logging system for your BETS project that uses structlog for the backend and consistent TypeScript utilities for the frontend. Let me create the necessary files:Perfect! I've set up a comprehensive, system-wide logging solution for your BETS project. Here's what I've created:

## 📦 **What Was Created**

### **Backend (Python/FastAPI)**
1. **`backend/app/core/logging.py`** - Centralized logging with structlog
   - `setup_logging()` - Initialize logging
   - `get_logger()` - Get a configured logger
   - `configure_json_logging()` - Production mode (JSON output)
   - `configure_console_logging()` - Development mode (colorful console)

2. **`backend/app/core/errors.py`** - Custom exceptions with auto-logging
   - `BETSError` - Base error class
   - Specific errors: `NotFoundError`, `ValidationError`, `UnauthorizedError`, etc.
   - Convenience functions: `failed()`, `require_value()`, `not_found()`, etc.

3. **`backend/alembic/env.py`** - Updated to use your centralized logger

4. **`backend/app/main_example.py`** - Complete FastAPI integration example showing:
   - Logging middleware for automatic request/response logging
   - Error handlers
   - Request ID tracking
   - Context binding

### **Frontend (TypeScript/React)**
1. **`frontend/src/core/logging.ts`** - Comprehensive logging utilities
   - Standard log levels: `trace()`, `debug()`, `info()`, `warn()`, `error()`, `fatal()`
   - Context support with `setLogContext()`
   - Scoped loggers with `createScopedLogger()`
   - API logging helpers

2. **`frontend/src/core/errors.ts`** - Error handling with auto-logging
   - Error classes: `CustomError`, `ApiError`, `ValidationError`, etc.
   - Convenience functions: `failed()`, `requireValue()`, `notFound()`, etc.
   - Error type checking and message extraction

### **Documentation**
1. **`LOGGING_GUIDE.md`** - Complete usage guide with examples
2. **`backend/logging_requirements.txt`** - Python dependencies

## 🚀 **Quick Start**

### **Install Backend Dependencies**
```bash
cd backend
pip install structlog>=24.1.0
```

### **Backend Usage**
```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing H5N1 cases", count=150, source="WOAH")
```

### **Frontend Usage**
```typescript
import { createScopedLogger } from '@/core/logging';

const logger = createScopedLogger('BETSMap');
logger.info('Map initialized', { markers: 42 });
```

## 🌟 **Key Features**

1. **Structured Logging** - All logs include structured data (key-value pairs)
2. **Automatic Context** - Request IDs, user info, etc. automatically included
3. **Error Auto-logging** - Errors log themselves based on severity
4. **Environment-aware** - JSON in production, colorful console in dev
5. **Consistent Interface** - Same patterns for backend and frontend

## 💡 **Integration Tips**

1. **In your FastAPI main.py**, add the startup configuration:
```python
from app.core.logging import setup_logging, configure_console_logging

@app.on_event("startup")
async def startup():
    setup_logging("INFO")
    configure_console_logging()  # or configure_json_logging() for prod
```

2. **For your student's CSV parsing work**:
```python
from app.core.logging import get_logger
from app.core.errors import ValidationError, require_value

logger = get_logger(__name__)

def parse_woah_csv(file_path: str):
    require_value(file_path, "file_path")
    logger.info("Parsing WOAH data", file=file_path)
    
    try:
        # parsing logic
        logger.info("WOAH data parsed", records=len(records))
    except Exception as e:
        logger.error("Failed to parse WOAH data", error=str(e))
        raise
```

3. **For your React map component**:
```typescript
import { createScopedLogger } from '@/core/logging';
import { handleApiError } from '@/core/errors';

const logger = createScopedLogger('BETSMapVisualization');

export function BETSMapVisualization() {
  useEffect(() => {
    logger.info('Loading H5N1 case data');
    
    fetchCases()
      .catch(e => handleApiError(e, '/api/cases', 'GET'));
  }, []);
}
```

The system is production-ready and follows best practices for both Python and TypeScript. Check the **LOGGING_GUIDE.md** for comprehensive examples and patterns! 🎯