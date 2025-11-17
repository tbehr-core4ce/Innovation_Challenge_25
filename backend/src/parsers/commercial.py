"""
Parser for commercial and backyard poultry flock H5N1 data.
Handles USDA commercial-backyard-flocks.csv dataset.
backend/src/parsers/commercial.py
"""

import pandas as pd
from typing import Dict, Any

from core.models import AnimalCategory, DataSource, CaseStatus
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

        return df

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