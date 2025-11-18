"""
Parser for wild bird H5N1 detection data.
Handles USDA HPAI Detections in Wild Birds.csv dataset.
backend/src/parsers/wild_bird.py
"""

import json
from typing import Any, Dict

import pandas as pd

from src.core.models import AnimalCategory, CaseStatus, DataSource

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
        "Bird Species": "animal_species",
        "Flock Size": "animals_affected"  # Added by aggregation
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

        # Aggregate duplicate detections BEFORE column standardization
        # (Need original column names for grouping)
        df = self.aggregate_duplicates(df)

        return df

    def aggregate_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate duplicate detections into single records.

        Multiple detections of same species in same county on same day
        are combined into one record with detection count.

        Args:
            df: DataFrame with ORIGINAL column names (before standardization)

        Returns:
            DataFrame with duplicates aggregated
        """
        # Group by key fields that define a unique "event" - using ORIGINAL column names
        group_cols = ['County', 'State', 'Collection Date', 'Date Detected',
                      'Bird Species', 'HPAI Strain']

        # Only use columns that exist
        group_cols = [col for col in group_cols if col in df.columns]

        if not group_cols:
            return df

        # Count detections per group
        detection_counts = df.groupby(group_cols, dropna=False).size().reset_index(name='detection_count')

        # Keep first row of each group (has all the metadata)
        df_agg = df.groupby(group_cols, dropna=False).first().reset_index()

        # Add detection counts
        df_agg = df_agg.merge(detection_counts, on=group_cols, how='left')

        # Add Flock Size column with detection count (will be mapped to animals_affected)
        df_agg['Flock Size'] = df_agg['detection_count']

        # Add description for multi-detection records (lowercase for model compatibility)
        def create_description(row):
            count = row.get('detection_count', 1)
            if count > 1:
                return f"Aggregated from {count} individual bird detections"
            return None

        df_agg['description'] = df_agg.apply(create_description, axis=1)

        # Drop the temporary count column
        df_agg = df_agg.drop(columns=['detection_count'])

        original_count = len(df)
        aggregated_count = len(df_agg)
        if original_count > aggregated_count:
            print(f"  📊 Aggregated {original_count} detections into {aggregated_count} unique records")

        return df_agg

    def generate_external_id(self, row: pd.Series, source_prefix: str) -> str:
        """
        Generate unique external_id for wild bird detections.

        After aggregation, each unique detection event gets one external_id.

        Args:
            row: DataFrame row
            source_prefix: Prefix for external_id (e.g., 'WILD')

        Returns:
            Unique external_id string
        """
        import hashlib

        # Combine key fields for uniqueness - these match the aggregation grouping
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
