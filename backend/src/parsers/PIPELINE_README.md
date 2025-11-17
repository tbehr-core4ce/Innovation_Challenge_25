# H5N1 Data Ingestion Pipeline

## Overview

This is the complete end-to-end data ingestion pipeline for the BETS (Bio-Event Tracking System) H5N1 tracking application.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA INGESTION PIPELINE                   │
└─────────────────────────────────────────────────────────────┘

1. CSV Files (datasets/raw/)
   ├── commercial-backyard-flocks.csv
   ├── HPAI Detections in Wild Birds.csv
   └── HPAI Detections in Mammals.csv
          ↓
2. Dataset-Specific Parsers (src/parsers/)
   ├── CommercialPoultryParser (commercial.py)
   ├── WildBirdParser (wild_bird.py)
   └── MammalParser (mammal.py)
   │
   │  • Inherits from BaseParser (base.py)
   │  • Reads CSV
   │  • Cleans data
   │  • Standardizes columns
   │  • Applies dataset-specific transformations
   │  • Calculates severity
   │  • Generates external_id
          ↓
3. Standardized DataFrame
   Columns: case_date, animal_category, animal_species,
            county, state_province, country, etc.
          ↓
4. Geocoding Service (validators/geocoder.py)
   • Converts county + state → lat/long
   • Uses state centroids as fallback
   • Caches results for performance
          ↓
5. Schema Validator (validators/schema.py)
   • Validates required fields
   • Checks enum values
   • Validates date formats
   • Checks coordinate ranges
   • Applies business rules
          ↓
6. Clean DataFrame with (clean_df, errors_list)
          ↓
7. Database Loader (parsers/loader.py)
   • Bulk insert into H5N1Case table
   • Duplicate detection via external_id
   • Creates DataImport tracking record
   • Error logging
          ↓
8. PostgreSQL Database
   ├── h5n1_cases (main data table)
   └── data_imports (tracking/audit table)
```

## File Structure

```
backend/
├── src/
│   ├── parsers/
│   │   ├── base.py              # BaseParser abstract class
│   │   ├── commercial.py        # Commercial poultry parser
│   │   ├── wild_bird.py         # Wild bird parser
│   │   ├── mammal.py            # Mammal parser
│   │   ├── loader.py            # Database loader
│   │   ├── ingestors.py         # DEPRECATED (old code)
│   │   └── PIPELINE_README.md   # This file
│   │
│   ├── validators/
│   │   ├── geocoder.py          # Geocoding service
│   │   └── schema.py            # Schema validator
│   │
│   └── core/
│       ├── models.py            # SQLAlchemy models
│       └── database.py          # Database connection
│
└── scripts/
    └── run_ingestion.py         # End-to-end pipeline script
```

## Usage

### Run Complete Pipeline (All 3 Datasets)

```bash
cd /home/user/Innovation_Challenge_25
python backend/scripts/run_ingestion.py --all
```

### Run Individual Datasets

```bash
# Commercial poultry only
python backend/scripts/run_ingestion.py --dataset commercial

# Wild birds only
python backend/scripts/run_ingestion.py --dataset wild_bird

# Mammals only
python backend/scripts/run_ingestion.py --dataset mammal
```

### Skip Geocoding (Faster Testing)

```bash
python backend/scripts/run_ingestion.py --all --no-geocode
```

## Parser Details

### BaseParser (base.py)

Abstract base class providing common parsing logic:

- **read_csv()**: Read CSV with column name cleaning
- **clean_data()**: Strip whitespace from strings
- **standardize_columns()**: Rename columns via COLUMN_MAPPING
- **add_defaults()**: Add default values for required fields
- **calculate_severity()**: Calculate severity based on animals_affected
- **generate_external_id()**: Create deterministic unique ID
- **parse()**: Main orchestration method
- **to_dict_list()**: Convert DataFrame to database records

Subclasses must define:
- `COLUMN_MAPPING`: Dict mapping CSV columns to H5N1Case fields
- `DEFAULTS`: Dict of default values
- `parse_specific()`: Dataset-specific transformations

### CommercialPoultryParser (commercial.py)

Parses: `commercial-backyard-flocks.csv`

**Column Mapping:**
- County → county
- State → state_province
- Outbreak Date → case_date
- Flock Type → animal_species
- Flock Size → animals_affected

**Defaults:**
- animal_category: POULTRY
- data_source: USDA
- country: USA
- status: CONFIRMED

**Transformations:**
- Parse date (MM-DD-YYYY format)
- Title case for county/state
- Numeric conversion for flock size

### WildBirdParser (wild_bird.py)

Parses: `HPAI Detections in Wild Birds.csv`

**Column Mapping:**
- State → state_province
- County → county
- Collection Date → case_date
- Date Detected → report_date
- Bird Species → animal_species

**Defaults:**
- animal_category: WILD_BIRD
- data_source: USDA
- country: USA
- status: CONFIRMED
- animals_affected: 1 (individual bird)

**Extra Fields Stored in extra_metadata JSON:**
- HPAI Strain
- WOAH Classification
- Sampling Method
- Submitting Agency

### MammalParser (mammal.py)

Parses: `HPAI Detections in Mammals.csv`

**Column Mapping:**
- State → state_province
- County → county
- Date Collected → case_date
- Date Detected → report_date
- Species → animal_species

**Defaults:**
- data_source: USDA
- country: USA
- status: CONFIRMED
- animals_affected: 1 (individual mammal)

**Smart Animal Category Detection:**
- Checks species name against DOMESTIC_MAMMALS list
- Sets DOMESTIC_MAMMAL or WILD_MAMMAL accordingly
- Domestic examples: "Domestic cat", "Dairy cattle"
- Wild examples: "Polar bear", "Black bear"

**Severity Calculation:**
- HIGH for domestic mammals (human contact risk)
- MEDIUM for wild mammals

## Validation

### SchemaValidator (validators/schema.py)

Performs comprehensive validation:

**Required Fields Check:**
- case_date, animal_category, country, data_source, status

**Enum Validation:**
- animal_category: poultry, wild_bird, wild_mammal, domestic_mammal, etc.
- data_source: usda, cdc, woah, state_agency, etc.
- status: suspected, confirmed, resolved, under_investigation
- severity: low, medium, high, critical

**Date Validation:**
- case_date not null
- No future dates (H5N1 cases can't be in the future)

**Coordinate Validation:**
- latitude: -90 to 90
- longitude: -180 to 180

**Business Rules:**
- animals_dead ≤ animals_affected

Returns: `(clean_df, errors_list)`

## Geocoding

### GeocodingService (validators/geocoder.py)

Converts county + state → latitude/longitude:

**Features:**
- In-memory caching for performance
- State-level centroid fallback (50 US states)
- Graceful degradation (returns None if not found)
- Batch geocoding via `geocode_dataframe()`

**Usage:**

```python
geocoder = GeocodingService()
df = geocoder.geocode_dataframe(df, county_col='county', state_col='state_province')
```

**Future Enhancement:**
- Load county centroid lookup table from CSV
- Use datasets/raw/National_Incorporated_Places_and_Counties.csv

## Database Loading

### H5N1DataLoader (parsers/loader.py)

Handles bulk database insertion:

**Features:**
- Bulk insert (1000 records/batch) for performance
- Duplicate detection via file_hash (SHA-256)
- Prevents re-importing same file
- Duplicate external_id handling (IntegrityError catch)
- DataImport tracking for auditing
- Error logging (first 100 errors stored)

**DataImport Table Fields:**
- source, filename, file_hash
- total_rows, successful_rows, failed_rows, duplicate_rows
- status, started_at, completed_at, duration_seconds
- error_log

**Usage:**

```python
from src.core.database import SessionLocal
from src.parsers.loader import H5N1DataLoader

session = SessionLocal()
loader = H5N1DataLoader(session)

# Option 1: Load from parser
success, failed, dupes = loader.load_from_parser(parser)

# Option 2: Load from DataFrame
success, failed, dupes = loader.bulk_insert(df, DataSource.USDA, file_path)

session.close()
```

## Expected Output

When running the full pipeline, you should see:

```
================================================================================
H5N1 DATA INGESTION PIPELINE
================================================================================
Geocoding service: {'lookup_table_loaded': False, 'cache_size': 0, ...}

================================================================================
INGESTING: Commercial & Backyard Poultry Flocks
================================================================================
Reading: datasets/raw/commercial-backyard-flocks.csv
Read 200 rows, 5 columns
✓ Parsing complete: 200 records
Geocoded 180/200 records (90.0%)

Validating schema for 200 records...
✓ Validation complete: 200 valid, 0 errors

Loading 200 records into database...
  ✓ Inserted batch 1: 200 records

================================================================================
Import Summary:
  ✓ Successful: 200
  ✗ Failed: 0
  ≈ Duplicates: 0
  ⏱ Duration: 2.34s
================================================================================

[... Wild Bird ingestion ...]
[... Mammal ingestion ...]

================================================================================
INGESTION SUMMARY
================================================================================

COMMERCIAL:
  ✓ Successful: 200
  ✗ Failed: 0
  ≈ Duplicates: 0

WILD_BIRD:
  ✓ Successful: 40000
  ✗ Failed: 0
  ≈ Duplicates: 0

MAMMAL:
  ✓ Successful: 150
  ✗ Failed: 0
  ≈ Duplicates: 0

TOTAL:
  ✓ Successful: 40350
  ✗ Failed: 0
  ≈ Duplicates: 0
================================================================================
```

## Database Schema

### h5n1_cases Table

Main table storing H5N1 case data:

```sql
CREATE TABLE h5n1_cases (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,

    -- Dates
    case_date TIMESTAMP NOT NULL,
    report_date TIMESTAMP,

    -- Classification
    status VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,

    -- Animal Info
    animal_category VARCHAR(50) NOT NULL,
    animal_species VARCHAR(255),
    animals_affected INTEGER,
    animals_dead INTEGER,

    -- Location
    country VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    county VARCHAR(100),
    city VARCHAR(100),
    location_name VARCHAR(255),

    -- Geospatial
    latitude FLOAT,
    longitude FLOAT,
    location GEOMETRY(POINT, 4326),

    -- Source
    data_source VARCHAR(50) NOT NULL,
    source_url TEXT,

    -- Additional
    description TEXT,
    control_measures TEXT,
    extra_metadata JSON,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),

    -- Soft Delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP
);
```

**Indexes:**
- external_id (unique)
- case_date
- status
- animal_category
- severity
- country, state_province, county
- Composite: (case_date, status), (country, animal_category), (severity, case_date)
- Spatial: location (GiST index)

## Testing

### Quick Test (Dry Run)

Test parsing without database insertion:

```python
from src.parsers.commercial import CommercialPoultryParser

parser = CommercialPoultryParser('datasets/raw/commercial-backyard-flocks.csv')
df, errors = parser.parse()

print(parser.get_stats())
print(df.head())
```

### Validation Test

```python
from src.validators.schema import SchemaValidator

validator = SchemaValidator()
clean_df, errors = validator.validate(df)

print(validator.get_validation_summary())
```

### Geocoding Test

```python
from src.validators.geocoder import GeocodingService

geocoder = GeocodingService()
df = geocoder.geocode_dataframe(df)

print(f"Geocoded: {df['latitude'].notna().sum()}/{len(df)}")
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`, ensure you're running from the project root:

```bash
cd /home/user/Innovation_Challenge_25
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python backend/scripts/run_ingestion.py --all
```

### Database Connection Errors

Check that PostgreSQL is running and credentials are correct in `backend/src/utils/settings.py`:

```bash
# Check database status
docker-compose ps

# View logs
docker-compose logs db
```

### Duplicate Import Errors

If you need to re-import data, you can:

1. Delete the DataImport record with that file_hash
2. Or drop and recreate the h5n1_cases table

```sql
-- Delete import record
DELETE FROM data_imports WHERE file_hash = 'abc123...';

-- Or truncate table (WARNING: deletes all data)
TRUNCATE TABLE h5n1_cases CASCADE;
TRUNCATE TABLE data_imports CASCADE;
```

## Future Enhancements

### Phase 2: Additional Datasets

- FluView clinical lab surveillance
- Dusek Iceland wild bird data
- DOI North American wild bird data

### Phase 3: Advanced Features

- County centroid lookup table integration
- Incremental updates (only import new rows)
- Data quality scoring
- Automated alert generation based on thresholds
- Cluster detection (multiple cases in same county/week)

### Phase 4: Production

- Async processing with Celery
- Scheduled imports (cron jobs)
- API endpoints for triggering imports
- Real-time websocket updates
- Dashboard for monitoring imports

## License

Part of the BETS (Bio-Event Tracking System) prototype for H5N1 surveillance.
