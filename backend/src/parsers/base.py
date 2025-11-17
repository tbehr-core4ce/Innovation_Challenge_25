"""
Base parser class for H5N1 data ingestion.
Provides common parsing logic and abstract methods for specific parsers.
backend/src/parsers/base.py
"""

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.core.models import (AnimalCategory, CaseStatus, DataSource, H5N1Case,
                             Severity)


class BaseParser(ABC):
    """
    Abstract base class for all H5N1 data parsers.

    Subclasses must define:
    - COLUMN_MAPPING: Dict mapping CSV columns to H5N1Case fields
    - DEFAULTS: Dict of default values for required fields
    - parse_specific(): Any dataset-specific parsing logic
    """

    # Subclasses must define these
    COLUMN_MAPPING: Dict[str, str] = {}
    DEFAULTS: Dict[str, Any] = {}

    def __init__(self, file_path: str):
        """
        Initialize parser with file path.

        Args:
            file_path: Path to CSV file to parse
        """
        self.file_path = file_path
        self.raw_df: Optional[pd.DataFrame] = None
        self.clean_df: Optional[pd.DataFrame] = None
        self.errors: List[Dict] = []

    def read_csv(self, **kwargs) -> pd.DataFrame:
        """
        Read CSV file into DataFrame.

        Args:
            **kwargs: Additional arguments to pass to pd.read_csv()

        Returns:
            Raw DataFrame from CSV
        """
        print(f"Reading: {self.file_path}")
        df = pd.read_csv(self.file_path, **kwargs)

        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()

        self.raw_df = df
        print(f"Read {len(df)} rows, {len(df.columns)} columns")
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply common data cleaning operations.

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid modifying original
        df = df.copy()

        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

        return df

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns according to COLUMN_MAPPING.

        Args:
            df: DataFrame with original column names

        Returns:
            DataFrame with standardized column names
        """
        # Only rename columns that exist in the DataFrame
        rename_dict = {
            old_col: new_col
            for old_col, new_col in self.COLUMN_MAPPING.items()
            if old_col in df.columns
        }

        df = df.rename(columns=rename_dict)
        return df

    def add_defaults(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add default values for required fields.

        Args:
            df: DataFrame

        Returns:
            DataFrame with default columns added
        """
        for col, value in self.DEFAULTS.items():
            if col not in df.columns:
                df[col] = value

        return df

    def calculate_severity(self, row: pd.Series) -> Severity:
        """
        Calculate severity based on outbreak characteristics.

        Rules:
        - CRITICAL: > 50,000 animals affected
        - HIGH: > 10,000 animals affected
        - MEDIUM: > 100 animals affected
        - LOW: <= 100 animals affected or unknown

        Args:
            row: DataFrame row

        Returns:
            Severity enum value
        """
        affected = row.get('animals_affected', 0)

        if pd.isna(affected) or affected == 0:
            return Severity.LOW

        if affected > 50000:
            return Severity.CRITICAL
        elif affected > 10000:
            return Severity.HIGH
        elif affected > 100:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def generate_external_id(self, row: pd.Series, source_prefix: str) -> str:
        """
        Generate a unique external_id for a case.

        Uses hash of key fields to create deterministic ID.

        Args:
            row: DataFrame row
            source_prefix: Prefix for ID (e.g., 'COMM', 'WILD', 'MAMM')

        Returns:
            External ID string
        """
        # Combine key fields for hashing
        key_parts = [
            str(row.get('case_date', '')),
            str(row.get('county', '')),
            str(row.get('state_province', '')),
            str(row.get('animal_species', '')),
            str(row.get('animals_affected', ''))
        ]
        key_string = '|'.join(key_parts)

        # Generate hash
        hash_obj = hashlib.md5(key_string.encode())
        hash_hex = hash_obj.hexdigest()[:12]  # Use first 12 chars

        return f"{source_prefix}_{hash_hex}"

    @abstractmethod
    def parse_specific(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply dataset-specific parsing logic.

        Subclasses must implement this to handle their specific data format.

        Args:
            df: Raw DataFrame

        Returns:
            Parsed DataFrame with dataset-specific transformations
        """
        pass

    def parse(self, **read_kwargs) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Main parsing method. Orchestrates the entire parsing pipeline.

        Pipeline:
        1. Read CSV
        2. Apply dataset-specific parsing
        3. Clean data
        4. Standardize columns
        5. Add defaults
        6. Calculate derived fields

        Args:
            **read_kwargs: Additional arguments for read_csv()

        Returns:
            Tuple of (clean_df, errors_list)
        """
        print(f"\n{'='*60}")
        print(f"Parsing: {self.file_path}")
        print(f"{'='*60}")

        try:
            # Step 1: Read CSV
            df = self.read_csv(**read_kwargs)

            # Step 2: Dataset-specific parsing
            df = self.parse_specific(df)

            # Step 3: Clean data
            df = self.clean_data(df)

            # Step 4: Standardize columns
            df = self.standardize_columns(df)

            # Step 5: Add defaults
            df = self.add_defaults(df)

            # Step 6: Calculate severity if not already set
            if 'severity' not in df.columns or df['severity'].isna().all():
                df['severity'] = df.apply(self.calculate_severity, axis=1)

            # Store cleaned DataFrame
            self.clean_df = df

            print(f" Parsing complete: {len(df)} records")
            print(f"  Columns: {', '.join(df.columns.tolist()[:10])}...")

            return df, self.errors

        except Exception as e:
            error = {
                'file': self.file_path,
                'error_type': type(e).__name__,
                'message': str(e),
                'timestamp': datetime.now()
            }
            self.errors.append(error)
            print(f" Parsing failed: {e}")
            raise

    def to_dict_list(self, df: Optional[pd.DataFrame] = None) -> List[Dict]:
        """
        Convert DataFrame to list of dictionaries for database insertion.

        Args:
            df: DataFrame to convert (uses self.clean_df if not provided)

        Returns:
            List of dictionaries, one per row
        """
        if df is None:
            df = self.clean_df

        if df is None:
            raise ValueError("No DataFrame available. Call parse() first.")

        # Replace NaN with None for database insertion
        df = df.where(pd.notna(df), None)

        # Convert to list of dicts
        records = df.to_dict('records')

        return records

    def get_stats(self) -> Dict[str, Any]:
        """
        Get parsing statistics.

        Returns:
            Dictionary of parsing stats
        """
        if self.clean_df is None:
            return {'status': 'not_parsed'}

        return {
            'file': self.file_path,
            'total_rows': len(self.clean_df),
            'errors': len(self.errors),
            'columns': list(self.clean_df.columns),
            'date_range': {
                'min': self.clean_df['case_date'].min() if 'case_date' in self.clean_df.columns else None,
                'max': self.clean_df['case_date'].max() if 'case_date' in self.clean_df.columns else None
            },
            'animal_categories': self.clean_df['animal_category'].value_counts().to_dict() if 'animal_category' in self.clean_df.columns else {}
        }
