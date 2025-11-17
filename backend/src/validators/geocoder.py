"""
Geocoding service for converting US county/state to lat/long coordinates.
Uses simple lookup table approach for US counties.
backend/src/validators/geocoder.py
"""

import pandas as pd
from typing import Optional, Tuple, Dict
import os
from pathlib import Path


class GeocodingService:
    """
    Service for geocoding US counties to latitude/longitude coordinates.

    Uses a lookup table of US county centroids for fast, offline geocoding.
    """

    def __init__(self, lookup_file: Optional[str] = None):
        """
        Initialize geocoding service.

        Args:
            lookup_file: Path to county lookup CSV file
        """
        self.lookup_file = lookup_file
        self.county_lookup: Optional[pd.DataFrame] = None
        self.cache: Dict[str, Tuple[float, float]] = {}

        # Try to load lookup table if file provided
        if lookup_file and os.path.exists(lookup_file):
            self.load_lookup_table(lookup_file)

    def load_lookup_table(self, file_path: str):
        """
        Load county centroid lookup table from CSV.

        Expected columns: county, state, latitude, longitude

        Args:
            file_path: Path to lookup CSV file
        """
        try:
            df = pd.read_csv(file_path)

            # Clean column names
            df.columns = df.columns.str.strip().str.lower()

            # Validate required columns exist
            required_cols = ['county', 'state', 'latitude', 'longitude']
            if not all(col in df.columns for col in required_cols):
                print(f"Warning: Lookup file missing required columns. Expected: {required_cols}")
                return

            # Create composite key
            df['lookup_key'] = (
                df['county'].str.strip().str.title() + '|' +
                df['state'].str.strip().str.title()
            )

            self.county_lookup = df
            print(f"Loaded geocoding lookup table: {len(df)} counties")

        except Exception as e:
            print(f"Error loading geocoding lookup table: {e}")

    def geocode_county(
        self,
        county: str,
        state: str
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Geocode a US county to lat/long coordinates.

        Args:
            county: County name (e.g., "Los Angeles")
            state: State name (e.g., "California") or abbreviation (e.g., "CA")

        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found
        """
        # Handle null/empty values
        if pd.isna(county) or pd.isna(state):
            return (None, None)

        # Normalize inputs
        county = str(county).strip().title()
        state = str(state).strip().title()

        # Create lookup key
        lookup_key = f"{county}|{state}"

        # Check cache first
        if lookup_key in self.cache:
            return self.cache[lookup_key]

        # Try lookup table
        if self.county_lookup is not None:
            match = self.county_lookup[
                self.county_lookup['lookup_key'] == lookup_key
            ]

            if not match.empty:
                lat = match.iloc[0]['latitude']
                lon = match.iloc[0]['longitude']

                # Cache result
                self.cache[lookup_key] = (lat, lon)
                return (lat, lon)

        # Fallback: Return state-level centroids for common states
        state_centroids = self._get_state_centroids()
        if state in state_centroids:
            coords = state_centroids[state]
            self.cache[lookup_key] = coords
            return coords

        # Not found
        return (None, None)

    def _get_state_centroids(self) -> Dict[str, Tuple[float, float]]:
        """
        Get approximate centroids for US states and territories.

        Returns:
            Dictionary of state/territory name -> (lat, lon)
        """
        return {
            'Alabama': (32.806671, -86.791130),
            'Alaska': (61.370716, -152.404419),
            'Arizona': (33.729759, -111.431221),
            'Arkansas': (34.969704, -92.373123),
            'California': (36.116203, -119.681564),
            'Colorado': (39.059811, -105.311104),
            'Connecticut': (41.597782, -72.755371),
            'Delaware': (39.318523, -75.507141),
            'District Of Columbia': (38.9072, -77.0369),
            'Dc': (38.9072, -77.0369),  # Handle DC abbreviation
            'Florida': (27.766279, -81.686783),
            'Georgia': (33.040619, -83.643074),
            'Hawaii': (21.094318, -157.498337),
            'Idaho': (44.240459, -114.478828),
            'Illinois': (40.349457, -88.986137),
            'Indiana': (39.849426, -86.258278),
            'Iowa': (42.011539, -93.210526),
            'Kansas': (38.526600, -96.726486),
            'Kentucky': (37.668140, -84.670067),
            'Louisiana': (31.169546, -91.867805),
            'Maine': (44.693947, -69.381927),
            'Maryland': (39.063946, -76.802101),
            'Massachusetts': (42.230171, -71.530106),
            'Michigan': (43.326618, -84.536095),
            'Minnesota': (45.694454, -93.900192),
            'Mississippi': (32.741646, -89.678696),
            'Missouri': (38.456085, -92.288368),
            'Montana': (46.921925, -110.454353),
            'Nebraska': (41.125370, -98.268082),
            'Nevada': (38.313515, -117.055374),
            'New Hampshire': (43.452492, -71.563896),
            'New Jersey': (40.298904, -74.521011),
            'New Mexico': (34.840515, -106.248482),
            'New York': (42.165726, -74.948051),
            'North Carolina': (35.630066, -79.806419),
            'North Dakota': (47.528912, -99.784012),
            'Ohio': (40.388783, -82.764915),
            'Oklahoma': (35.565342, -96.928917),
            'Oregon': (44.572021, -122.070938),
            'Pennsylvania': (40.590752, -77.209755),
            'Rhode Island': (41.680893, -71.511780),
            'South Carolina': (33.856892, -80.945007),
            'South Dakota': (44.299782, -99.438828),
            'Tennessee': (35.747845, -86.692345),
            'Texas': (31.054487, -97.563461),
            'Utah': (40.150032, -111.862434),
            'Vermont': (44.045876, -72.710686),
            'Virginia': (37.769337, -78.169968),
            'Washington': (47.400902, -121.490494),
            'West Virginia': (38.491226, -80.954453),
            'Wisconsin': (44.268543, -89.616508),
            'Wyoming': (42.755966, -107.302490),
            # US Territories
            'Puerto Rico': (18.2208, -66.5901),
            'Guam': (13.4443, 144.7937),
            'U.S. Virgin Islands': (18.3358, -64.8963),
            'American Samoa': (-14.2710, -170.1322),
            'Northern Mariana Islands': (15.0979, 145.6739)
        }

    def geocode_dataframe(
        self,
        df: pd.DataFrame,
        county_col: str = 'county',
        state_col: str = 'state_province'
    ) -> Tuple[pd.DataFrame, list]:
        """
        Add latitude and longitude columns to DataFrame based on county/state.

        Args:
            df: DataFrame with county and state columns
            county_col: Name of county column
            state_col: Name of state column

        Returns:
            Tuple of (DataFrame with 'latitude' and 'longitude' columns added, list of failed records)
        """
        df = df.copy()
        failed_records = []

        # Apply geocoding to each row and track failures
        def geocode_with_tracking(row, idx):
            county = row.get(county_col)
            state = row.get(state_col)
            coords = self.geocode_county(county, state)

            # Track failures
            if coords[0] is None or coords[1] is None:
                reason = "Missing county or state" if pd.isna(county) or pd.isna(state) else "County not found in lookup table"
                failed_records.append({
                    'index': idx,
                    'county': str(county) if not pd.isna(county) else "N/A",
                    'state': str(state) if not pd.isna(state) else "N/A",
                    'reason': reason
                })

            return coords

        coords = df.apply(
            lambda row: geocode_with_tracking(row, row.name),
            axis=1
        )

        # Split tuple into separate columns
        df['latitude'] = coords.apply(lambda x: x[0])
        df['longitude'] = coords.apply(lambda x: x[1])

        # Count successful geocodes
        success_count = df['latitude'].notna().sum()
        total_count = len(df)
        print(f"Geocoded {success_count}/{total_count} records ({success_count/total_count*100:.1f}%)")

        return df, failed_records

    def get_stats(self) -> Dict:
        """
        Get geocoding service statistics.

        Returns:
            Dictionary of stats
        """
        return {
            'lookup_table_loaded': self.county_lookup is not None,
            'lookup_table_size': len(self.county_lookup) if self.county_lookup is not None else 0,
            'cache_size': len(self.cache),
            'state_centroids': len(self._get_state_centroids())
        }
