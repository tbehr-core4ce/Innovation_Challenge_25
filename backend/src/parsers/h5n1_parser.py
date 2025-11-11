import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re

""" 
~~~~~~~~~~~~~ LOAD LOOKUP DICTIONARY ~~~~~~~~~~~~~
The map format requires latitude and longitude.
"""

print("Loading location lookup database...")
places_df = pd.read_csv('National_Incorporated_Places_and_Counties.csv')

county_lookup = {}
city_lookup = {}

for _, row in places_df.iterrows():
    name = str(row['Name']).strip().lower()
    state = str(row['State Name']).strip().lower()
    lat = float(row['Primary Lat Dec'])
    lng = float(row['Primary Long Dec'])
    class_code = str(row['Class Code']).strip().upper()

    key = f"{name}, {state}"
    coords = (lat, lng)

    if class_code.startswith('H'):
        county_lookup[key] = coords
    elif class_code.startswith('C'):
        city_lookup[key] = coords

print(f"Loaded {len(county_lookup)} counties and {len(city_lookup)} cities/towns")


# ~~~~~~~~~~~~~ LOCAL GEOCODING ~~~~~~~~~~~~~
def geocode_location(location: str, state: Optional[str] = None, county: Optional[str] = None) -> Tuple[Optional[float], Optional[float], str]:
    if not state:
        return None, None, 'failed'
    
    state_lower = state.strip().lower()
    
    if county:
        county_clean = county.strip().lower()
        county_clean = re.sub(r'\s*city\s*$', '', county_clean, flags=re.IGNORECASE).strip()
        county_clean = re.sub(r'\s*(county|parish|borough|census area|\(ca\))\s*$', '', county_clean, flags=re.IGNORECASE).strip()
        
        variations = [
            county_clean,
            county_clean + ' county',
            county_clean.replace('st.', 'saint'),
            county_clean.replace('st ', 'saint '),
            county_clean.replace('saint', 'st.'),
            county_clean.replace(' ', '-'),
            county_clean.replace('-', ' '),
            county_clean + 'ugh',
            county_clean.replace('ugh', '')
        ]
        
        for variant in variations:
            key = f"{variant}, {state_lower}"
            if key in county_lookup:
                return (*county_lookup[key], 'county')
        
        for variant in variations:
            key = f"{variant}, {state_lower}"
            if key in city_lookup:
                return (*city_lookup[key], 'independent-city')
    
    if location:
        loc_clean = location.strip().lower()
        loc_clean = re.sub(r'^(city of|town of|village of|borough of)\s+', '', loc_clean, flags=re.IGNORECASE).strip()
        key = f"{loc_clean}, {state_lower}"
        if key in city_lookup:
            return (*city_lookup[key], 'city')
        if key in county_lookup:
            return (*county_lookup[key], 'county')

        loc_clean = re.sub(r'\s*(county|parish|borough|census area)\s*$', '', loc_clean, flags=re.IGNORECASE).strip()
        key = f"{loc_clean}, {state_lower}"
        if key in county_lookup:
            return (*county_lookup[key], 'county-fallback')
    
    return None, None, 'failed'


# ~~~~~~~~~~~~~ COLUMN HELPERS ~~~~~~~~~~~~~
COLUMN_MAPPINGS = {
    'location': ['location', 'county', 'city', 'place', 'area', 'region'],
    'latitude': ['lat', 'latitude', 'lat_dd', 'y', 'coord_y'],
    'longitude': ['lng', 'lon', 'long', 'longitude', 'lng_dd', 'x', 'coord_x'],
    'date': ['date', 'outbreak date', 'reported date', 'detection date', 'sample date'],
    'count': ['count', 'cases', 'flock size', 'birds', 'animals', 'number', 'total'],
    'type': ['type', 'case type', 'flock type', 'species', 'host', 'animal type'],
    'severity': ['severity', 'risk', 'level', 'priority'],
    'status': ['status', 'current_status', 'case_status', 'condition', 'outbreak_status'],
    'description': ['description', 'notes', 'comments', 'details', 'remarks'],
    'state': ['state', 'province', 'region', 'admin1'],
    'county': ['county', 'district', 'admin2']
}

def find_column(df: pd.DataFrame, field_type: str) -> Optional[str]:
    if field_type not in COLUMN_MAPPINGS:
        return None
    possible_names = COLUMN_MAPPINGS[field_type]
    df_columns_lower = {col.lower().strip(): col for col in df.columns}
    for name in possible_names:
        if name.lower() in df_columns_lower:
            return df_columns_lower[name.lower()]
    return None

def infer_case_type(type_text: str) -> str:
    if pd.isna(type_text):
        return 'avian'
    text = str(type_text).lower()
    if any(word in text for word in ['human', 'person', 'patient', 'people']):
        return 'human'
    if any(word in text for word in ['dairy', 'cow', 'cattle', 'milk']):
        return 'dairy'
    if any(word in text for word in ['bird', 'avian', 'poultry', 'chicken', 'turkey']):
        return 'avian'
    if any(word in text for word in ['environment', 'water', 'soil', 'wild']):
        return 'environmental'
    return 'avian'

def infer_severity(count: int, case_type: str) -> str:
    if case_type == 'human':
        return 'critical' if count >= 5 else 'high'
    if count >= 1000:
        return 'high'
    if count >= 100:
        return 'medium'
    return 'low'

def infer_status(severity: str) -> str:
    if severity in ['critical', 'high']:
        return 'active'
    if severity == 'medium':
        return 'monitoring'
    return 'contained'


# ~~~~~~~~~~~~~ MAIN PARSER ~~~~~~~~~~~~~
def parse_dataset(filepath: str, encoding: str = 'utf-8') -> List[Dict]:
    try:
        df = pd.read_csv(filepath, encoding=encoding)
    except Exception:
        df = pd.read_csv(filepath, encoding='latin-1')
    
    print(f"Loaded CSV with {len(df)} rows")
    
    column_map = {field: find_column(df, field) for field in COLUMN_MAPPINGS.keys()}
    print(f"Detected columns: {column_map}")

    cases = []
    skipped = 0

    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Processing row {idx}/{len(df)}...")

        lat_col = column_map.get('latitude')
        lng_col = column_map.get('longitude')

        if lat_col and lng_col and pd.notna(row.get(lat_col)) and pd.notna(row.get(lng_col)):
            lat, lng = float(row[lat_col]), float(row[lng_col])
            accuracy = 'exact'
        else:
            loc_col = column_map.get('location')
            state_col = column_map.get('state')
            county_col = column_map.get('county')

            location_text = str(row.get(loc_col, '')) if loc_col else ''
            state_text = str(row.get(state_col, '')) if state_col else None
            county_text = str(row.get(county_col, '')) if county_col else None

            lat, lng, accuracy = geocode_location(location_text, state_text, county_text)
            if lat is None or lng is None:
                skipped += 1
                continue

        parts = []
        if county_col and pd.notna(row.get(county_col)):
            parts.append(str(row[county_col]))
        if state_col and pd.notna(row.get(state_col)):
            parts.append(str(row[state_col]))
        location_str = ', '.join(parts) if parts else 'Unknown Location'

        type_col = column_map.get('type')
        case_type = infer_case_type(row.get(type_col)) if type_col else 'avian'

        count_col = column_map.get('count')
        count = int(float(row[count_col])) if count_col and pd.notna(row.get(count_col)) else 1

        severity_col = column_map.get('severity')
        severity = str(row[severity_col]).lower() if severity_col and pd.notna(row.get(severity_col)) else infer_severity(count, case_type)

        status_col = column_map.get('status')
        status = str(row[status_col]).lower() if status_col and pd.notna(row.get(status_col)) else infer_status(severity)

        date_col = column_map.get('date')
        if date_col and pd.notna(row.get(date_col)):
            try:
                reported_date = pd.to_datetime(row[date_col]).isoformat()
            except:
                reported_date = datetime.now().isoformat()
        else:
            reported_date = datetime.now().isoformat()

        desc_col = column_map.get('description')
        desc_parts = [str(row[desc_col])] if desc_col and pd.notna(row.get(desc_col)) else []
        desc_parts.append(f"Type: {case_type}, Count: {count}, Accuracy: {accuracy}")
        description = ' | '.join(desc_parts)

        case = {
            "id": f"case_{idx}",
            "lat": lat,
            "lng": lng,
            "location": location_str,
            "caseType": case_type,
            "count": count,
            "severity": severity,
            "reportedDate": reported_date,
            "status": status,
            "description": description
        }

        cases.append(case)

    print(f"\nParsing complete! Successfully parsed: {len(cases)} cases, Skipped: {skipped} rows")
    return cases, df  # return df for skipped rows debugging


# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    URL = 'https://raw.githubusercontent.com/tbehr-core4ce/Innovation_Challenge_25/main/datasets/raw/commercial-backyard-flocks.csv'

    cases, df = parse_dataset(URL)

    print("\nFirst 3 parsed cases:")
    for case in cases[:3]:
        print(case)

    print("\n=== DEBUGGING SKIPPED ROWS ===")
    skipped_rows = []

    for idx, row in df.iterrows():
        state = str(row.get('State', '')) if pd.notna(row.get('State')) else None
        county = str(row.get('County', '')) if pd.notna(row.get('County')) else None
        lat, lng, accuracy = geocode_location(None, state, county)
        if lat is None:
            skipped_rows.append({
                'row': idx,
                'county': county,
                'state': state,
                'reason': 'No match found'
            })

    print(f"\nFound {len(skipped_rows)} problematic rows")
    print("\nFirst 10 skipped rows:")
    for item in skipped_rows[:10]:
        print(f"Row {item['row']}: {item['county']}, {item['state']} - {item['reason']}")
