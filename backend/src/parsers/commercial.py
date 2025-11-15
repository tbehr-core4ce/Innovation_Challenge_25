# src/parsers/commercial.py
from core.models import AnimalCategory, DataSource
class CommercialPoultryParser(BaseParser):
    COLUMN_MAPPING = {
        "County": "county",
        "State": "state_province",
        "Outbreak Date": "case_date",
        "Flock Type": "animal_species",
        "Flock Size": "animals_affected"
    }
    
    DEFAULTS = {
        "animal_category": AnimalCategory.POULTRY,
        "data_source": DataSource.USDA,
        "country": "USA"
    }