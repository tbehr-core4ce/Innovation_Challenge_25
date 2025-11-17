"""
Data Ingestion Router for BETS (Bird flu Early Tracking System)
Handles CSV file uploads and parsing for H5N1 surveillance data
"""
import csv
import io
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data-ingestion", tags=["data-ingestion"])


# WOAH Category Enum (World Organisation for Animal Health)
class AnimalCategory(str, Enum):
    POULTRY = "poultry"
    DAIRY_CATTLE = "dairy_cattle"
    WILD_BIRDS = "wild_birds"
    WILD_MAMMALS = "wild_mammals"
    OTHER = "other"


# Pydantic models for data validation
class H5N1CaseRecord(BaseModel):
    """Model for individual H5N1 case record"""
    case_id: Optional[str] = None
    date: str
    country: str
    region: Optional[str] = None
    latitude: float
    longitude: float
    animal_category: AnimalCategory
    species: str
    num_cases: int = Field(gt=0, description="Number of cases must be positive")
    num_deaths: Optional[int] = Field(ge=0, default=0)
    source: Optional[str] = None
    notes: Optional[str] = None

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

    @validator('date')
    def validate_date(cls, v):
        try:
            # Try parsing various date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    datetime.strptime(v, fmt)
                    return v
                except ValueError:
                    continue
            raise ValueError('Invalid date format')
        except Exception:
            raise ValueError('Date must be in format YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY')


class IngestionResponse(BaseModel):
    """Response model for ingestion operations"""
    success: bool
    message: str
    records_processed: int
    records_valid: int
    records_invalid: int
    errors: List[Dict[str, Any]] = []
    data: Optional[List[Dict[str, Any]]] = None


# Helper functions
def normalize_animal_category(category_str: str) -> str:
    """Normalize animal category strings to enum values"""
    category_map = {
        'poultry': AnimalCategory.POULTRY,
        'chicken': AnimalCategory.POULTRY,
        'chickens': AnimalCategory.POULTRY,
        'turkey': AnimalCategory.POULTRY,
        'turkeys': AnimalCategory.POULTRY,
        'duck': AnimalCategory.POULTRY,
        'ducks': AnimalCategory.POULTRY,
        'cattle': AnimalCategory.DAIRY_CATTLE,
        'dairy': AnimalCategory.DAIRY_CATTLE,
        'dairy cattle': AnimalCategory.DAIRY_CATTLE,
        'cow': AnimalCategory.DAIRY_CATTLE,
        'cows': AnimalCategory.DAIRY_CATTLE,
        'wild bird': AnimalCategory.WILD_BIRDS,
        'wild birds': AnimalCategory.WILD_BIRDS,
        'bird': AnimalCategory.WILD_BIRDS,
        'wild mammal': AnimalCategory.WILD_MAMMALS,
        'wild mammals': AnimalCategory.WILD_MAMMALS,
        'mammal': AnimalCategory.WILD_MAMMALS,
    }
    
    normalized = category_str.lower().strip()
    return category_map.get(normalized, AnimalCategory.OTHER).value


def parse_csv_content(content: str, delimiter: str = ',') -> List[Dict[str, Any]]:
    """Parse CSV content into list of dictionaries"""
    csv_file = io.StringIO(content)
    reader = csv.DictReader(csv_file, delimiter=delimiter)
    return list(reader)


def validate_and_transform_record(record: Dict[str, Any], row_number: int) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate and transform a single CSV record
    Returns: (transformed_record, error_message)
    """
    try:
        # Map common CSV header variations to expected fields
        field_mappings = {
            'date': ['date', 'report_date', 'detection_date', 'Date', 'DATE'],
            'country': ['country', 'Country', 'COUNTRY', 'nation'],
            'region': ['region', 'state', 'province', 'Region', 'STATE'],
            'latitude': ['latitude', 'lat', 'Latitude', 'LAT'],
            'longitude': ['longitude', 'lon', 'lng', 'long', 'Longitude', 'LON'],
            'animal_category': ['animal_category', 'category', 'animal_type', 'type'],
            'species': ['species', 'Species', 'animal_species'],
            'num_cases': ['num_cases', 'cases', 'count', 'number_cases'],
            'num_deaths': ['num_deaths', 'deaths', 'fatalities'],
            'source': ['source', 'data_source', 'Source'],
            'notes': ['notes', 'comments', 'remarks', 'Notes'],
        }

        # Transform record using field mappings
        transformed = {}
        for field, variations in field_mappings.items():
            for variation in variations:
                if variation in record:
                    transformed[field] = record[variation]
                    break

        # Normalize animal category if present
        if 'animal_category' in transformed:
            transformed['animal_category'] = normalize_animal_category(transformed['animal_category'])

        # Convert numeric fields
        if 'num_cases' in transformed:
            transformed['num_cases'] = int(transformed['num_cases'])
        if 'num_deaths' in transformed:
            transformed['num_deaths'] = int(transformed['num_deaths']) if transformed['num_deaths'] else 0
        if 'latitude' in transformed:
            transformed['latitude'] = float(transformed['latitude'])
        if 'longitude' in transformed:
            transformed['longitude'] = float(transformed['longitude'])

        # Validate using Pydantic model
        validated = H5N1CaseRecord(**transformed)
        return validated.dict(), None

    except Exception as e:
        error_msg = f"Row {row_number}: {str(e)}"
        logger.warning(error_msg)
        return None, error_msg


# API Endpoints
@router.post("/upload-csv", response_model=IngestionResponse)
async def upload_csv(
    file: UploadFile = File(...),
    delimiter: str = Query(',', description="CSV delimiter character"),
    validate_only: bool = Query(False, description="Only validate without storing data")
):
    """
    Upload and parse CSV file containing H5N1 case data
    
    Expected CSV columns (flexible header names):
    - date: Date of detection/report
    - country: Country name
    - region: State/province (optional)
    - latitude: Latitude coordinate
    - longitude: Longitude coordinate
    - animal_category: Type of animal (poultry, dairy_cattle, wild_birds, wild_mammals, other)
    - species: Specific species name
    - num_cases: Number of cases
    - num_deaths: Number of deaths (optional)
    - source: Data source (optional)
    - notes: Additional notes (optional)
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.CSV')):
            raise HTTPException(status_code=400, detail="File must be a CSV file")

        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8-sig')  # Handle BOM if present

        # Parse CSV
        records = parse_csv_content(content_str, delimiter=delimiter)
        
        if not records:
            raise HTTPException(status_code=400, detail="CSV file is empty or invalid")

        # Validate and transform records
        valid_records = []
        errors = []
        
        for idx, record in enumerate(records, start=2):  # Start at 2 (row 1 is header)
            validated_record, error = validate_and_transform_record(record, idx)
            if validated_record:
                valid_records.append(validated_record)
            else:
                errors.append({
                    "row": idx,
                    "error": error,
                    "data": record
                })

        # If not validate_only, here you would insert into database
        # For now, we'll just return the validated data
        if not validate_only:
            # TODO: Insert valid_records into database
            logger.info(f"Would insert {len(valid_records)} records into database")
            pass

        return IngestionResponse(
            success=True,
            message=f"Processed {len(records)} records: {len(valid_records)} valid, {len(errors)} invalid",
            records_processed=len(records),
            records_valid=len(valid_records),
            records_invalid=len(errors),
            errors=errors[:50],  # Limit errors in response
            data=valid_records if validate_only else None
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please use UTF-8 encoded CSV")
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/supported-categories")
async def get_supported_categories():
    """Get list of supported WOAH animal categories"""
    return {
        "categories": [
            {
                "value": cat.value,
                "name": cat.name,
                "description": {
                    "poultry": "Domestic birds including chickens, turkeys, ducks",
                    "dairy_cattle": "Dairy cattle and cows",
                    "wild_birds": "Wild bird species",
                    "wild_mammals": "Wild mammal species",
                    "other": "Other animal types"
                }[cat.value]
            }
            for cat in AnimalCategory
        ]
    }


@router.get("/validation-template")
async def get_validation_template():
    """
    Get CSV template with required columns and example data
    """
    template = {
        "headers": [
            "date", "country", "region", "latitude", "longitude",
            "animal_category", "species", "num_cases", "num_deaths",
            "source", "notes"
        ],
        "example_row": {
            "date": "2024-01-15",
            "country": "United States",
            "region": "California",
            "latitude": 36.7783,
            "longitude": -119.4179,
            "animal_category": "dairy_cattle",
            "species": "Holstein dairy cow",
            "num_cases": 25,
            "num_deaths": 3,
            "source": "USDA",
            "notes": "Outbreak at dairy facility"
        },
        "field_descriptions": {
            "date": "Date in YYYY-MM-DD format (required)",
            "country": "Country name (required)",
            "region": "State/province/region (optional)",
            "latitude": "Latitude between -90 and 90 (required)",
            "longitude": "Longitude between -180 and 180 (required)",
            "animal_category": "One of: poultry, dairy_cattle, wild_birds, wild_mammals, other (required)",
            "species": "Specific species name (required)",
            "num_cases": "Number of cases, must be positive integer (required)",
            "num_deaths": "Number of deaths, non-negative integer (optional)",
            "source": "Data source reference (optional)",
            "notes": "Additional notes or context (optional)"
        }
    }
    return template

# TODO add in 
@router.post("/validate-data", response_model=IngestionResponse)
async def validate_data(records: List[Dict[str, Any]]):
    """
    Validate JSON data without uploading
    Useful for frontend validation before submission
    """
    try:
        valid_records = []
        errors = []
        
        for idx, record in enumerate(records):
            validated_record, error = validate_and_transform_record(record, idx + 1)
            if validated_record:
                valid_records.append(validated_record)
            else:
                errors.append({
                    "index": idx,
                    "error": error,
                    "data": record
                })

        return IngestionResponse(
            success=True,
            message=f"Validated {len(records)} records: {len(valid_records)} valid, {len(errors)} invalid",
            records_processed=len(records),
            records_valid=len(valid_records),
            records_invalid=len(errors),
            errors=errors,
            data=valid_records
        )

    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for data ingestion service"""
    return {
        "status": "healthy",
        "service": "data-ingestion",
        "timestamp": datetime.utcnow().isoformat()
    }