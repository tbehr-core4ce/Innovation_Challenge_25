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