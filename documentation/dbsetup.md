# BETS Database Setup Guide

## Overview

The BETS database uses **PostgreSQL 15** with the **PostGIS** extension for geospatial H5N1 tracking. This guide covers setup, migrations, and common operations.

## 🚀 Quick Start (Docker)

### 1. Start the Database

```bash
# Start PostgreSQL + PostGIS
docker-compose up -d postgres

# Verify it's running
docker-compose ps

# Check logs
docker-compose logs -f postgres
```

The database will be available at `localhost:5432` with:
- **Database**: `bets_db`
- **User**: `bets_user`
- **Password**: `bets_password`

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy template and edit
cp .env.template .env

# Edit .env with your settings
# DATABASE_URL is already configured for Docker
```

### 4. Run Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 5. Seed Sample Data

```bash
# Run the database manager utility
python scripts/db_manager.py seed
```

✅ Your database is now ready!

## 📊 Database Schema

### Core Tables

#### `h5n1_cases`
Main table for H5N1 bird flu cases with geospatial data.

**Key Fields:**
- `id` - Primary key
- `external_id` - ID from external sources (WOAH, CDC, etc.)
- `case_date`, `report_date` - Temporal tracking
- `status` - Case status (suspected, confirmed, etc.)
- `severity` - Severity level (low, medium, high, critical)
- `animal_category` - WOAH categorization (poultry, dairy_cattle, wild_bird, etc.)
- `animal_species` - Specific species affected
- `animals_affected`, `animals_dead` - Impact metrics
- `location` - PostGIS POINT geometry (lon, lat)
- `latitude`, `longitude` - Decimal coordinates
- `country`, `state_province`, `county`, `city` - Geographic hierarchy
- `data_source` - Source of the data

**Indexes:**
- Spatial index on `location` (GiST)
- Composite indexes on frequently queried combinations

#### `alerts`
Alert notifications for significant H5N1 events.

#### `data_imports`
Track CSV/data import batches for auditing.

#### `geographic_boundaries`
Optional: Store geographic boundaries for hotspot analysis.

#### `users`
User accounts for system access.

### WOAH Animal Categories

The system uses WOAH (World Organisation for Animal Health) categorization:

- `poultry` - Chickens, turkeys, ducks, geese
- `dairy_cattle` - Dairy cows
- `wild_bird` - Wild bird species
- `wild_mammal` - Wild mammals (raccoons, foxes, etc.)
- `domestic_mammal` - Domestic mammals (cats, dogs, pigs)
- `other` - Other animal types

## 🛠️ Database Management

### Using the DB Manager Utility

```bash
# Check database connection
python scripts/db_manager.py check

# Initialize database (creates all tables)
python scripts/db_manager.py init

# Run migrations
python scripts/db_manager.py migrate

# Seed with sample data (100 cases, 15 alerts, 1 admin user)
python scripts/db_manager.py seed

# Reset database (WARNING: destroys all data)
python scripts/db_manager.py reset
```

### Manual Operations

```python
# In Python shell or script
from app.core.database import SessionLocal, check_db_connection
from app.models import H5N1Case

# Check connection
check_db_connection()

# Get a session
db = SessionLocal()

# Query cases
cases = db.query(H5N1Case).filter(
    H5N1Case.status == "confirmed"
).all()

# Close session
db.close()
```

## 🔄 Migrations with Alembic

### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to cases"

# Create empty migration (for manual changes)
alembic revision -m "Add custom index"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade by specific number of versions
alembic upgrade +1

# Downgrade by one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123
```

### Check Migration Status

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

### Example: Manual Migration

Edit the generated migration file in `alembic/versions/`:

```python
def upgrade():
    # Add a column
    op.add_column('h5n1_cases', 
        sa.Column('new_field', sa.String(100), nullable=True)
    )
    
    # Create an index
    op.create_index(
        'idx_new_field',
        'h5n1_cases',
        ['new_field']
    )

def downgrade():
    op.drop_index('idx_new_field', 'h5n1_cases')
    op.drop_column('h5n1_cases', 'new_field')
```

## 🗺️ Working with Geospatial Data

### Inserting Location Data

```python
from app.models import H5N1Case
from sqlalchemy import text

case = H5N1Case(
    # ... other fields ...
    latitude=37.7749,
    longitude=-122.4194,
)

# Set PostGIS geometry from lat/lng
case.location = text(
    f"ST_GeomFromText('POINT({case.longitude} {case.latitude})', 4326)"
)

db.add(case)
db.commit()
```

### Spatial Queries

```python
from sqlalchemy import text

# Find cases within 50km radius of a point
point_lng, point_lat = -122.4194, 37.7749
radius_meters = 50000

cases = db.query(H5N1Case).filter(
    text(
        f"ST_DWithin(location::geography, "
        f"ST_GeomFromText('POINT({point_lng} {point_lat})', 4326)::geography, "
        f"{radius_meters})"
    )
).all()

# Find cases within a bounding box
min_lng, min_lat = -123.0, 37.0
max_lng, max_lat = -122.0, 38.0

cases = db.query(H5N1Case).filter(
    text(
        f"ST_Within(location, "
        f"ST_MakeEnvelope({min_lng}, {min_lat}, {max_lng}, {max_lat}, 4326))"
    )
).all()
```

## 📁 CSV Data Import

Your student can use this pattern for importing CSV data:

```python
from app.core.logging import get_logger
from app.core.errors import ValidationError
from app.models import H5N1Case, DataImport, DataSource
import pandas as pd
from datetime import datetime

logger = get_logger(__name__)

def import_woah_csv(file_path: str, db):
    """Import WOAH H5N1 data from CSV."""
    
    # Create import record
    import_record = DataImport(
        source=DataSource.WOAH,
        filename=file_path,
        started_at=datetime.now(),
        status="in_progress"
    )
    db.add(import_record)
    db.commit()
    
    try:
        # Read CSV
        df = pd.read_csv(file_path)
        import_record.total_rows = len(df)
        
        successful = 0
        failed = 0
        
        for idx, row in df.iterrows():
            try:
                case = H5N1Case(
                    external_id=row.get('id'),
                    case_date=pd.to_datetime(row['date']),
                    animal_category=row['category'],
                    # ... map other fields ...
                )
                db.add(case)
                successful += 1
                
            except Exception as e:
                logger.error(f"Failed to import row {idx}", error=str(e))
                failed += 1
        
        # Update import record
        db.commit()
        import_record.successful_rows = successful
        import_record.failed_rows = failed
        import_record.status = "completed"
        import_record.completed_at = datetime.now()
        db.commit()
        
        logger.info("Import completed", 
                   successful=successful, 
                   failed=failed)
        
    except Exception as e:
        import_record.status = "failed"
        import_record.error_log = str(e)
        db.commit()
        logger.error("Import failed", error=str(e))
        raise
```

## 🔍 pgAdmin Access (Optional)

If you started pgAdmin with Docker Compose:

1. Open http://localhost:5050
2. Login with:
   - Email: `admin@bets.local`
   - Password: `admin`
3. Add server:
   - Host: `postgres` (or `localhost` if not using Docker)
   - Port: `5432`
   - Database: `bets_db`
   - Username: `bets_user`
   - Password: `bets_password`

## 🧪 Testing

### Run Tests with Test Database

```python
# tests/conftest.py
import pytest
from app.core.database import Base, get_test_db_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db():
    """Provide a test database session."""
    engine = get_test_db_engine()
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

# tests/test_cases.py
def test_create_case(db):
    from app.models import H5N1Case
    
    case = H5N1Case(
        case_date=datetime.now(),
        status="confirmed",
        # ...
    )
    db.add(case)
    db.commit()
    
    assert case.id is not None
```

## 🔧 Troubleshooting

### Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Test connection from command line
psql postgresql://bets_user:bets_password@localhost:5432/bets_db
```

### PostGIS Not Enabled

```sql
-- Connect to database and run:
CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_version();
```

### Migration Conflicts

```bash
# Show current state
alembic current

# Check for multiple heads
alembic heads

# Merge multiple heads
alembic merge heads -m "Merge migrations"
```

### Reset Everything (Development Only)

```bash
# Stop containers
docker-compose down

# Remove volumes (destroys all data)
docker-compose down -v

# Restart fresh
docker-compose up -d postgres
python scripts/db_manager.py init
python scripts/db_manager.py seed
```

## 📈 Performance Tips

1. **Use Indexes**: Add indexes for frequently queried fields
2. **Batch Inserts**: Use `bulk_save_objects()` for large imports
3. **Connection Pooling**: Already configured in database.py
4. **Query Optimization**: Use `explain()` to analyze slow queries
5. **Spatial Indexes**: PostGIS automatically creates spatial indexes

## 🔐 Security Checklist

- [ ] Change default passwords in production
- [ ] Use environment variables for sensitive data
- [ ] Enable SSL for database connections in production
- [ ] Restrict database access by IP
- [ ] Regular backups configured
- [ ] Audit logging enabled
- [ ] Read-only users for reporting

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)