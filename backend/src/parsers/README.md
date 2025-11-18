datasets/
  ├── commercial_poultry.csv
  ├── wild_birds.csv  
  ├── mammals.csv
  └── surveillance.csv

          ↓

src/parsers/
  ├── base.py              # BaseParser class with common logic # 
  ├── commercial.py        # Handles commercial poultry format # datasets/raw/commercial-backyard-flocks.csv
  ├── wild_bird.py         # Handles wild bird format # datasets/raw/HPAI Detections in Wild Birds.csv
  ├── mammal.py            # Handles mammal format # datasets/raw/HPAI Detections in Mammals.csv
  └── surveillance.py      # Handles surveillance format # maybe use this and add fake table ??/ datasets/raw/data-table.csv

          ↓ (each parser outputs)

Pandas DataFrame with standardized columns matching your schema:
  - case_date
  - animal_category
  - animal_species
  - county, state_province, country
  - animals_affected, animals_dead
  - data_source
  - etc.

          ↓

src/validators/
  # Validates the standardized DataFrame
  - Required fields present?
  - Valid date formats?
  - Enum values valid?
  - Coordinate ranges valid?
  - Business rules (dead ≤ affected)?

          ↓ (outputs)

(clean_df, errors_list)

          ↓

src/loaders/ingestors.py  # Your file with 5 errors
  # Bulk insert clean_df into H5N1Case table
  # Track in DataImport table
  # Log errors









  ### Old code

  ```
  # data_parser.py

#Goal: Parse real H5N1 datasets into the format the map needs

import pandas as pd
from datetime import datetime
from typing import List, Dict

def parse_h5n1_csv(filepath: str) -> List[Dict]:
    """
    Parse H5N1 case data from CSV into API format
    
    Expected CSV columns:
    - location, lat, lng, case_type, count, 
      severity, reported_date, status, description
    
    Returns list of case dictionaries
    """
    df = pd.read_csv(filepath)
    
    # Data validation
    required_columns = ['location', 'lat', 'lng', 'case_type']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Clean and transform
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    df = df.dropna(subset=['lat', 'lng'])
    
    # Convert to API format
    cases = []
    for idx, row in df.iterrows():
        cases.append({
            "id": str(idx),
            "lat": float(row['lat']),
            "lng": float(row['lng']),
            "location": row['location'],
            "caseType": row['case_type'],
            "count": int(row.get('count', 1)),
            "severity": row.get('severity', 'medium'),
            "reportedDate": row.get('reported_date', datetime.now().isoformat()),
            "status": row.get('status', 'monitoring'),
            "description": row.get('description', '')
        })
    
    return cases

if __name__ == "__main__":
    # Test with sample data
    cases = parse_h5n1_csv('sample_h5n1_data.csv')
    print(f"Parsed {len(cases)} cases")
    print(cases[0])  # Show first case
```