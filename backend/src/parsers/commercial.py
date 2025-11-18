"""
Parser for commercial and backyard poultry flock H5N1 data.
Handles USDA commercial-backyard-flocks.csv dataset.
backend/src/parsers/commercial.py
"""

from typing import Any, Dict

import pandas as pd

from src.core.models import AnimalCategory, CaseStatus, DataSource

from .base import BaseParser


class CommercialPoultryParser(BaseParser):
    """
    Parser for commercial and backyard poultry outbreak data.

    Dataset: datasets/raw/commercial-backyard-flocks.csv
    Columns: County, State, Outbreak Date, Flock Type, Flock Size
    """

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
        "country": "USA",
        "status": CaseStatus.CONFIRMED
    }

    def parse_specific(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply commercial poultry-specific parsing logic.

        Transformations:
        - Parse Outbreak Date to datetime (format: MM-DD-YYYY)
        - Convert Flock Size to integer
        - Title case for County and State
        - Trim whitespace from Flock Type

        Args:
            df: Raw DataFrame

        Returns:
            Parsed DataFrame
        """
        df = df.copy()

        # Parse date (format: MM-DD-YYYY, e.g., "12-31-2024")
        if 'Outbreak Date' in df.columns:
            df['Outbreak Date'] = pd.to_datetime(
                df['Outbreak Date'],
                format='%m-%d-%Y',
                errors='coerce'
            )

        # Clean location fields
        if 'County' in df.columns:
            df['County'] = df['County'].str.strip().str.title()

        if 'State' in df.columns:
            df['State'] = df['State'].str.strip().str.title()

        # Clean flock type
        if 'Flock Type' in df.columns:
            df['Flock Type'] = df['Flock Type'].str.strip()

        # Convert flock size to integer
        if 'Flock Size' in df.columns:
            df['Flock Size'] = pd.to_numeric(
                df['Flock Size'],
                errors='coerce'
            ).astype('Int64')

        # Aggregate duplicate detections BEFORE column standardization
        # (Need original column names for grouping)
        df = self.aggregate_duplicates(df)

        return df

    def aggregate_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate duplicate detections into single records.

        Multiple reports of same flock size in same county on same day
        are combined into one record with total birds affected.

        Args:
            df: DataFrame with ORIGINAL column names (before standardization)

        Returns:
            DataFrame with duplicates aggregated
        """
        # Group by key fields that define a unique "outbreak event"
        group_cols = ['County', 'State', 'Outbreak Date', 'Flock Type', 'Flock Size']

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

        # Multiply flock size by detection count to get total birds affected
        # e.g., 3 reports of 20 birds each = 60 birds total
        df_agg['Total Flock Size'] = df_agg['Flock Size'] * df_agg['detection_count']

        # Update Flock Size with total (this will be mapped to animals_affected)
        df_agg['Flock Size'] = df_agg['Total Flock Size']

        # Add description for multi-detection records
        def create_description(row):
            count = row.get('detection_count', 1)
            flock_size = row.get('Flock Size', 0) // count if count > 0 else 0  # Original flock size
            if count > 1:
                return f"Aggregated from {count} detections of {flock_size} birds each ({row.get('Flock Size', 0)} total)"
            return None

        df_agg['description'] = df_agg.apply(create_description, axis=1)

        # Drop temporary columns
        df_agg = df_agg.drop(columns=['detection_count', 'Total Flock Size'])

        original_count = len(df)
        aggregated_count = len(df_agg)
        if original_count > aggregated_count:
            print(f"  📊 Aggregated {original_count} outbreak reports into {aggregated_count} unique records")

        return df_agg

    def generate_external_id(self, row: pd.Series, source_prefix: str) -> str:
        """
        Generate unique external_id for commercial poultry.

        Includes flock size to differentiate multiple outbreaks in same county on same day.

        Args:
            row: DataFrame row
            source_prefix: Prefix for external_id (e.g., 'COMM')

        Returns:
            Unique external_id string
        """
        import hashlib

        # Combine key fields for uniqueness - include flock size to distinguish different farms
        key_parts = [
            str(row.get('county', '')),
            str(row.get('state_province', '')),
            str(row.get('case_date', ''))[:10],  # Date only (YYYY-MM-DD)
            str(row.get('animal_species', '')),
            str(row.get('animals_affected', ''))  # Different flock size = different farm
        ]

        key_string = '|'.join(key_parts)
        hash_obj = hashlib.md5(key_string.encode())
        hash_hex = hash_obj.hexdigest()[:12]

        return f"{source_prefix}_{hash_hex}"

    def add_defaults(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add default values and generate external IDs.

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
                lambda row: self.generate_external_id(row, 'COMM'),
                axis=1
            )

        return df