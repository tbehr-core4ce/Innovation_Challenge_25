"""
Schema validation for H5N1 case data.
Validates DataFrame columns match expected schema and enum values.
backend/src/validators/schema.py
"""

import pandas as pd
from typing import List, Dict, Tuple, Any
from datetime import datetime

from src.core.models import (
    AnimalCategory, CaseStatus, Severity, DataSource
)


class SchemaValidator:
    """
    Validates DataFrames against the H5N1Case schema.

    Checks:
    - Required fields present
    - Enum values valid
    - Date formats valid
    - Coordinate ranges valid
    - Business rules (e.g., animals_dead <= animals_affected)
    """

    REQUIRED_FIELDS = [
        'case_date',
        'animal_category',
        'country',
        'data_source',
        'status'
    ]

    OPTIONAL_FIELDS = [
        'external_id',
        'report_date',
        'severity',
        'animal_species',
        'animals_affected',
        'animals_dead',
        'state_province',
        'county',
        'city',
        'location_name',
        'latitude',
        'longitude',
        'source_url',
        'description',
        'control_measures',
        'extra_metadata'
    ]

    def __init__(self):
        """Initialize schema validator."""
        self.errors: List[Dict] = []

    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Validate DataFrame against schema.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (validated_df, errors_list)
        """
        print(f"\nValidating schema for {len(df)} records...")
        self.errors = []

        # Make a copy to avoid modifying original
        df = df.copy()

        # Validate required fields
        self._validate_required_fields(df)

        # Validate enum fields
        self._validate_enums(df)

        # Validate dates
        self._validate_dates(df)

        # Validate coordinates
        self._validate_coordinates(df)

        # Validate business rules
        self._validate_business_rules(df)

        # Remove invalid rows if any critical errors
        df_clean = self._remove_invalid_rows(df)

        print(f"✓ Validation complete: {len(df_clean)} valid, {len(self.errors)} errors")

        return df_clean, self.errors

    def _validate_required_fields(self, df: pd.DataFrame):
        """Check that all required fields are present."""
        missing = [field for field in self.REQUIRED_FIELDS if field not in df.columns]

        if missing:
            error = {
                'type': 'missing_required_fields',
                'message': f"Missing required fields: {missing}",
                'severity': 'critical',
                'timestamp': datetime.now()
            }
            self.errors.append(error)
            print(f"✗ Missing required fields: {missing}")

    def _validate_enums(self, df: pd.DataFrame):
        """Validate enum field values."""

        # AnimalCategory
        if 'animal_category' in df.columns:
            valid_categories = [e.value for e in AnimalCategory]
            invalid_mask = ~df['animal_category'].isin(valid_categories) & df['animal_category'].notna()

            if invalid_mask.any():
                invalid_values = df[invalid_mask]['animal_category'].unique()
                error = {
                    'type': 'invalid_enum',
                    'field': 'animal_category',
                    'message': f"Invalid animal_category values: {invalid_values}",
                    'count': invalid_mask.sum(),
                    'severity': 'error'
                }
                self.errors.append(error)

        # DataSource
        if 'data_source' in df.columns:
            valid_sources = [e.value for e in DataSource]
            invalid_mask = ~df['data_source'].isin(valid_sources) & df['data_source'].notna()

            if invalid_mask.any():
                invalid_values = df[invalid_mask]['data_source'].unique()
                error = {
                    'type': 'invalid_enum',
                    'field': 'data_source',
                    'message': f"Invalid data_source values: {invalid_values}",
                    'count': invalid_mask.sum(),
                    'severity': 'error'
                }
                self.errors.append(error)

        # CaseStatus
        if 'status' in df.columns:
            valid_statuses = [e.value for e in CaseStatus]
            invalid_mask = ~df['status'].isin(valid_statuses) & df['status'].notna()

            if invalid_mask.any():
                invalid_values = df[invalid_mask]['status'].unique()
                error = {
                    'type': 'invalid_enum',
                    'field': 'status',
                    'message': f"Invalid status values: {invalid_values}",
                    'count': invalid_mask.sum(),
                    'severity': 'error'
                }
                self.errors.append(error)

        # Severity
        if 'severity' in df.columns:
            valid_severities = [e.value for e in Severity]
            invalid_mask = ~df['severity'].isin(valid_severities) & df['severity'].notna()

            if invalid_mask.any():
                invalid_values = df[invalid_mask]['severity'].unique()
                error = {
                    'type': 'invalid_enum',
                    'field': 'severity',
                    'message': f"Invalid severity values: {invalid_values}",
                    'count': invalid_mask.sum(),
                    'severity': 'warning'
                }
                self.errors.append(error)

    def _validate_dates(self, df: pd.DataFrame):
        """Validate date fields."""

        # Check case_date is valid datetime
        if 'case_date' in df.columns:
            null_dates = df['case_date'].isna()

            if null_dates.any():
                error = {
                    'type': 'null_date',
                    'field': 'case_date',
                    'message': f"Found {null_dates.sum()} null case_date values",
                    'count': null_dates.sum(),
                    'severity': 'error'
                }
                self.errors.append(error)

            # Check for future dates (shouldn't have H5N1 cases in the future)
            if not null_dates.all():
                future_dates = df['case_date'] > pd.Timestamp.now()

                if future_dates.any():
                    error = {
                        'type': 'future_date',
                        'field': 'case_date',
                        'message': f"Found {future_dates.sum()} future case_date values",
                        'count': future_dates.sum(),
                        'severity': 'warning'
                    }
                    self.errors.append(error)

    def _validate_coordinates(self, df: pd.DataFrame):
        """Validate latitude and longitude ranges."""

        if 'latitude' in df.columns:
            # Valid latitude: -90 to 90
            invalid_lat = (df['latitude'] < -90) | (df['latitude'] > 90)
            invalid_lat = invalid_lat & df['latitude'].notna()

            if invalid_lat.any():
                error = {
                    'type': 'invalid_coordinate',
                    'field': 'latitude',
                    'message': f"Found {invalid_lat.sum()} invalid latitude values (must be -90 to 90)",
                    'count': invalid_lat.sum(),
                    'severity': 'error'
                }
                self.errors.append(error)

        if 'longitude' in df.columns:
            # Valid longitude: -180 to 180
            invalid_lon = (df['longitude'] < -180) | (df['longitude'] > 180)
            invalid_lon = invalid_lon & df['longitude'].notna()

            if invalid_lon.any():
                error = {
                    'type': 'invalid_coordinate',
                    'field': 'longitude',
                    'message': f"Found {invalid_lon.sum()} invalid longitude values (must be -180 to 180)",
                    'count': invalid_lon.sum(),
                    'severity': 'error'
                }
                self.errors.append(error)

    def _validate_business_rules(self, df: pd.DataFrame):
        """Validate business logic rules."""

        # Rule: animals_dead should not exceed animals_affected
        if 'animals_dead' in df.columns and 'animals_affected' in df.columns:
            # Only check where both values are not null
            both_present = df['animals_dead'].notna() & df['animals_affected'].notna()
            violation = both_present & (df['animals_dead'] > df['animals_affected'])

            if violation.any():
                error = {
                    'type': 'business_rule_violation',
                    'rule': 'animals_dead <= animals_affected',
                    'message': f"Found {violation.sum()} cases where animals_dead > animals_affected",
                    'count': violation.sum(),
                    'severity': 'warning'
                }
                self.errors.append(error)

    def _remove_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows with critical errors.

        Args:
            df: DataFrame

        Returns:
            DataFrame with invalid rows removed
        """
        # For now, only remove rows with null required fields
        if 'case_date' in df.columns:
            df = df[df['case_date'].notna()]

        return df

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation results.

        Returns:
            Dictionary of validation stats
        """
        error_types = {}
        for error in self.errors:
            error_type = error.get('type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            'total_errors': len(self.errors),
            'error_types': error_types,
            'errors': self.errors
        }
