"""
Parser for mammal H5N1 detection data.
Handles USDA HPAI Detections in Mammals.csv dataset.
backend/src/parsers/mammal.py
"""

import pandas as pd
from typing import Dict, Any
import json

from core.models import AnimalCategory, DataSource, CaseStatus
from .base import BaseParser


class MammalParser(BaseParser):
    """
    Parser for mammal H5N1 detection data.

    Dataset: datasets/raw/HPAI Detections in Mammals.csv
    Columns: State, County, Date Collected, Date Detected, HPAI Strain, Species
    """

    COLUMN_MAPPING = {
        "State": "state_province",
        "County": "county",
        "Date Collected": "case_date",
        "Date Detected": "report_date",
        "Species": "animal_species"
    }

    DEFAULTS = {
        "data_source": DataSource.USDA,
        "country": "USA",
        "status": CaseStatus.CONFIRMED,
        "animals_affected": 1  # Individual mammal detections
    }

    # List of domestic mammal species
    DOMESTIC_MAMMALS = [
        'domestic cat',
        'domestic dog',
        'domestic cattle',
        'domestic pig',
        'dairy cattle',
        'beef cattle',
        'alpaca',
        'llama',
        'goat',
        'sheep',
        'horse'
    ]

    def parse_specific(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply mammal-specific parsing logic.

        Transformations:
        - Parse Date Collected and Date Detected
        - Title case for County, State, Species
        - Determine if mammal is domestic or wild based on species name
        - Store HPAI Strain in metadata

        Args:
            df: Raw DataFrame

        Returns:
            Parsed DataFrame
        """
        df = df.copy()

        # Parse dates
        if 'Date Collected' in df.columns:
            df['Date Collected'] = pd.to_datetime(
                df['Date Collected'],
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

        # Clean species name
        if 'Species' in df.columns:
            df['Species'] = df['Species'].str.strip().str.title()

        # Clean HPAI Strain
        if 'HPAI Strain' in df.columns:
            df['HPAI Strain'] = df['HPAI Strain'].str.strip()

        return df

    def determine_animal_category(self, species: str) -> AnimalCategory:
        """
        Determine if mammal is domestic or wild based on species name.

        Args:
            species: Species name

        Returns:
            AnimalCategory.DOMESTIC_MAMMAL or AnimalCategory.WILD_MAMMAL
        """
        if pd.isna(species):
            return AnimalCategory.WILD_MAMMAL

        species_lower = species.lower()

        # Check if species contains any domestic mammal keyword
        for domestic in self.DOMESTIC_MAMMALS:
            if domestic in species_lower:
                return AnimalCategory.DOMESTIC_MAMMAL

        return AnimalCategory.WILD_MAMMAL

    def add_defaults(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add default values, determine animal category, and create metadata.

        Args:
            df: DataFrame with standardized columns

        Returns:
            DataFrame with defaults added
        """
        # Call parent to add basic defaults (but not animal_category yet)
        df = super().add_defaults(df)

        # Determine animal_category based on species
        if 'animal_species' in df.columns:
            df['animal_category'] = df['animal_species'].apply(
                self.determine_animal_category
            )
        else:
            df['animal_category'] = AnimalCategory.WILD_MAMMAL

        # Generate external IDs if not present
        if 'external_id' not in df.columns or df['external_id'].isna().all():
            df['external_id'] = df.apply(
                lambda row: self.generate_external_id(row, 'MAMM'),
                axis=1
            )

        # Create extra_metadata JSON for HPAI Strain
        def create_metadata(row):
            metadata = {}
            if 'HPAI Strain' in row.index and pd.notna(row['HPAI Strain']):
                metadata['hpai_strain'] = row['HPAI Strain']
            return json.dumps(metadata) if metadata else None

        if 'extra_metadata' not in df.columns and 'HPAI Strain' in df.columns:
            df['extra_metadata'] = df.apply(create_metadata, axis=1)

        return df

    def calculate_severity(self, row: pd.Series):
        """
        Override severity calculation for mammals.

        Mammal detections are concerning due to cross-species transmission.
        Set severity based on:
        - MEDIUM for wild mammals
        - HIGH for domestic mammals (potential human contact)

        Args:
            row: DataFrame row

        Returns:
            Severity enum value
        """
        from core.models import Severity

        category = row.get('animal_category', AnimalCategory.WILD_MAMMAL)

        if category == AnimalCategory.DOMESTIC_MAMMAL:
            return Severity.HIGH  # Higher risk due to human contact
        else:
            return Severity.MEDIUM  # Still concerning for wild mammals
