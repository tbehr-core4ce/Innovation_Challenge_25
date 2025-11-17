"""
Parser for wild bird H5N1 detection data.
Handles USDA HPAI Detections in Wild Birds.csv dataset.
backend/src/parsers/wild_bird.py
"""

import pandas as pd
from typing import Dict, Any
import json

from src.core.models import AnimalCategory, DataSource, CaseStatus
from .base import BaseParser


class WildBirdParser(BaseParser):
    """
    Parser for wild bird H5N1 detection data.

    Dataset: datasets/raw/HPAI Detections in Wild Birds.csv
    Columns: State, County, Collection Date, Date Detected, HPAI Strain,
             Bird Species, WOAH Classification, Sampling Method, Submitting Agency
    """

    COLUMN_MAPPING = {
        "State": "state_province",
        "County": "county",
        "Collection Date": "case_date",
        "Date Detected": "report_date",
        "Bird Species": "animal_species"
    }

    DEFAULTS = {
        "animal_category": AnimalCategory.WILD_BIRD,
        "data_source": DataSource.USDA,
        "country": "USA",
        "status": CaseStatus.CONFIRMED,
        "animals_affected": 1  # Individual bird detections
    }

    def parse_specific(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply wild bird-specific parsing logic.

        Transformations:
        - Parse Collection Date and Date Detected
        - Title case for County, State, Bird Species
        - Store extra fields (HPAI Strain, WOAH Classification, etc.) in metadata

        Args:
            df: Raw DataFrame

        Returns:
            Parsed DataFrame
        """
        df = df.copy()

        # Parse dates (format varies, use flexible parsing)
        if 'Collection Date' in df.columns:
            df['Collection Date'] = pd.to_datetime(
                df['Collection Date'],
                errors='coerce'
            )

        if 'Date Detected' in df.columns:
            df['Date Detected'] = pd.to_datetime(
                df['Date Detected'],
                errors='coerce'
            )

        # Clean location fields
        if 'State' in df.columns:
            df['State'] = df['State'].str.strip().str.title()

        if 'County' in df.columns:
            df['County'] = df['County'].str.strip().str.title()

        # Clean bird species
        if 'Bird Species' in df.columns:
            df['Bird Species'] = df['Bird Species'].str.strip().str.title()

        # Clean other string fields
        string_cols = ['HPAI Strain', 'WOAH Classification', 'Sampling Method', 'Submitting Agency']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].str.strip()

        return df

    def generate_external_id(self, row: pd.Series, source_prefix: str) -> str:
        """
        Generate unique external_id for wild bird detections.

        Includes report_date and HPAI strain to differentiate multiple detections
        in same county on same day.

        Args:
            row: DataFrame row
            source_prefix: Prefix for external_id (e.g., 'WILD')

        Returns:
            Unique external_id string
        """
        import hashlib

        # Combine key fields for uniqueness - include report_date and strain for unique detections
        key_parts = [
            str(row.get('county', '')),
            str(row.get('state_province', '')),
            str(row.get('case_date', ''))[:10],  # Collection date
            str(row.get('report_date', ''))[:10] if pd.notna(row.get('report_date')) else '',  # Report date
            str(row.get('animal_species', '')),
            str(row.get('HPAI Strain', '')) if pd.notna(row.get('HPAI Strain')) else ''  # Different strain = different record
        ]

        key_string = '|'.join(key_parts)
        hash_obj = hashlib.md5(key_string.encode())
        hash_hex = hash_obj.hexdigest()[:12]

        return f"{source_prefix}_{hash_hex}"

    def add_defaults(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add default values, generate external IDs, and create metadata.

        Args:
            df: DataFrame with standardized columns

        Returns:
            DataFrame with defaults added
        """
        # Call parent to add basic defaults
        df = super().add_defaults(df)

        # Generate external IDs if not present
        if 'external_id' not in df.columns or df['external_id'].isna().all():
            df['external_id'] = df.apply(
                lambda row: self.generate_external_id(row, 'WILD'),
                axis=1
            )

        # Create extra_metadata JSON from additional fields
        metadata_fields = ['HPAI Strain', 'WOAH Classification', 'Sampling Method', 'Submitting Agency']

        def create_metadata(row):
            metadata = {}
            for field in metadata_fields:
                if field in row.index and pd.notna(row[field]):
                    # Convert field name to snake_case for JSON
                    key = field.lower().replace(' ', '_')
                    metadata[key] = row[field]
            return json.dumps(metadata) if metadata else None

        if 'extra_metadata' not in df.columns:
            df['extra_metadata'] = df.apply(create_metadata, axis=1)

        # Drop metadata source columns (they're now in extra_metadata JSON)
        # These columns don't exist in H5N1Case model
        df = df.drop(columns=[col for col in metadata_fields if col in df.columns], errors='ignore')

        return df

    def calculate_severity(self, row: pd.Series):
        """
        Override severity calculation for wild birds.

        Wild bird detections are typically individual cases, so severity is LOW
        unless there's a cluster of detections (handled at aggregation level).

        Args:
            row: DataFrame row

        Returns:
            Severity.LOW (individual bird detections)
        """
        from src.core.models import Severity
        return Severity.LOW
