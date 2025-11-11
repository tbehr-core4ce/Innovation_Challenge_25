# scripts/process_all_csvs.py
"""
Run this to process all CSVs in /datasets/raw/
"""
from src.parsers import (
    CommercialParser, 
    WildBirdParser, 
    MammalParser,
    SurveillanceParser,
    TimeseriesParser
)

PARSER_MAPPING = {
    'commercial-backyard-flocks.csv': CommercialParser,
    'HPAI Detections in Wild Birds.csv': WildBirdParser,
    'HPAI Detections in Mammals.csv': MammalParser,
    'Dusek_data release list.csv': SurveillanceParser,
    'data-table.csv': TimeseriesParser,
}

def process_dataset(csv_path: Path):
    parser_class = PARSER_MAPPING.get(csv_path.name)
    parser = parser_class()
    
    # Parse
    records = parser.parse(csv_path)
    
    # Validate
    valid_records = validate_records(records)
    
    # Geocode (add lat/lon)
    geocoded = geocode_records(valid_records)
    
    # Load to DB
    load_to_db(geocoded)