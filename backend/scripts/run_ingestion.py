#!/usr/bin/env python3
"""
End-to-end H5N1 data ingestion pipeline.

This script orchestrates the complete data ingestion workflow:
1. Parse CSV files using dataset-specific parsers
2. Apply geocoding to add lat/long coordinates
3. Validate data against schema
4. Load into database with duplicate detection
5. Track import in DataImport table

Usage:
    python backend/scripts/run_ingestion.py --all
    python backend/scripts/run_ingestion.py --dataset commercial
    python backend/scripts/run_ingestion.py --dataset wild_bird
    python backend/scripts/run_ingestion.py --dataset mammal

backend/scripts/run_ingestion.py
"""

import sys
import os
from pathlib import Path
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.commercial import CommercialPoultryParser
from src.parsers.wild_bird import WildBirdParser
from src.parsers.mammal import MammalParser
from src.parsers.loader import H5N1DataLoader
from src.validators.geocoder import GeocodingService
from src.validators.schema import SchemaValidator
from src.core.database import SessionLocal
from src.core.models import DataSource


def get_dataset_paths():
    """Get paths to the three priority H5N1 datasets."""
    base_dir = Path(__file__).parent.parent.parent
    datasets_dir = base_dir / "datasets" / "raw"

    return {
        'commercial': datasets_dir / "commercial-backyard-flocks.csv",
        'wild_bird': datasets_dir / "HPAI Detections in Wild Birds.csv",
        'mammal': datasets_dir / "HPAI Detections in Mammals.csv"
    }


def run_commercial_ingestion(session, geocoder: GeocodingService):
    """
    Ingest commercial poultry outbreak data.

    Args:
        session: Database session
        geocoder: Geocoding service
    """
    print("\n" + "="*80)
    print("INGESTING: Commercial & Backyard Poultry Flocks")
    print("="*80)

    paths = get_dataset_paths()
    file_path = str(paths['commercial'])

    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return

    # 1. Parse CSV
    parser = CommercialPoultryParser(file_path)
    df, parse_errors = parser.parse()

    if parse_errors:
        print(f"⚠ Parsing errors: {len(parse_errors)}")

    # 2. Add geocoding
    df = geocoder.geocode_dataframe(df)

    # 3. Validate
    validator = SchemaValidator()
    df, validation_errors = validator.validate(df)

    if validation_errors:
        print(f"⚠ Validation errors: {len(validation_errors)}")

    # 4. Load into database
    parser.clean_df = df  # Update with geocoded/validated data
    loader = H5N1DataLoader(session)
    success, failed, duplicates = loader.load_from_parser(parser, validate=False)

    return {
        'dataset': 'commercial',
        'success': success,
        'failed': failed,
        'duplicates': duplicates
    }


def run_wild_bird_ingestion(session, geocoder: GeocodingService):
    """
    Ingest wild bird H5N1 detection data.

    Args:
        session: Database session
        geocoder: Geocoding service
    """
    print("\n" + "="*80)
    print("INGESTING: Wild Bird HPAI Detections")
    print("="*80)

    paths = get_dataset_paths()
    file_path = str(paths['wild_bird'])

    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return

    # 1. Parse CSV
    parser = WildBirdParser(file_path)
    df, parse_errors = parser.parse()

    if parse_errors:
        print(f"⚠ Parsing errors: {len(parse_errors)}")

    # 2. Add geocoding
    df = geocoder.geocode_dataframe(df)

    # 3. Validate
    validator = SchemaValidator()
    df, validation_errors = validator.validate(df)

    if validation_errors:
        print(f"⚠ Validation errors: {len(validation_errors)}")

    # 4. Load into database
    parser.clean_df = df
    loader = H5N1DataLoader(session)
    success, failed, duplicates = loader.load_from_parser(parser, validate=False)

    return {
        'dataset': 'wild_bird',
        'success': success,
        'failed': failed,
        'duplicates': duplicates
    }


def run_mammal_ingestion(session, geocoder: GeocodingService):
    """
    Ingest mammal H5N1 detection data.

    Args:
        session: Database session
        geocoder: Geocoding service
    """
    print("\n" + "="*80)
    print("INGESTING: Mammal HPAI Detections")
    print("="*80)

    paths = get_dataset_paths()
    file_path = str(paths['mammal'])

    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return

    # 1. Parse CSV
    parser = MammalParser(file_path)
    df, parse_errors = parser.parse()

    if parse_errors:
        print(f"⚠ Parsing errors: {len(parse_errors)}")

    # 2. Add geocoding
    df = geocoder.geocode_dataframe(df)

    # 3. Validate
    validator = SchemaValidator()
    df, validation_errors = validator.validate(df)

    if validation_errors:
        print(f"⚠ Validation errors: {len(validation_errors)}")

    # 4. Load into database
    parser.clean_df = df
    loader = H5N1DataLoader(session)
    success, failed, duplicates = loader.load_from_parser(parser, validate=False)

    return {
        'dataset': 'mammal',
        'success': success,
        'failed': failed,
        'duplicates': duplicates
    }


def main():
    """Main entry point for data ingestion."""
    parser = argparse.ArgumentParser(
        description='H5N1 Data Ingestion Pipeline'
    )
    parser.add_argument(
        '--dataset',
        choices=['commercial', 'wild_bird', 'mammal', 'all'],
        default='all',
        help='Dataset to ingest (default: all)'
    )
    parser.add_argument(
        '--no-geocode',
        action='store_true',
        help='Skip geocoding step'
    )

    args = parser.parse_args()

    # Initialize services
    print("\n" + "="*80)
    print("H5N1 DATA INGESTION PIPELINE")
    print("="*80)

    # Create database session
    session = SessionLocal()

    # Initialize geocoding service
    geocoder = GeocodingService()
    if not args.no_geocode:
        print(f"Geocoding service: {geocoder.get_stats()}")

    results = []

    try:
        # Run ingestion based on arguments
        if args.dataset == 'all' or args.dataset == 'commercial':
            result = run_commercial_ingestion(session, geocoder)
            if result:
                results.append(result)

        if args.dataset == 'all' or args.dataset == 'wild_bird':
            result = run_wild_bird_ingestion(session, geocoder)
            if result:
                results.append(result)

        if args.dataset == 'all' or args.dataset == 'mammal':
            result = run_mammal_ingestion(session, geocoder)
            if result:
                results.append(result)

        # Print summary
        print("\n" + "="*80)
        print("INGESTION SUMMARY")
        print("="*80)

        total_success = sum(r['success'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        total_duplicates = sum(r['duplicates'] for r in results)

        for result in results:
            print(f"\n{result['dataset'].upper()}:")
            print(f"  ✓ Successful: {result['success']}")
            print(f"  ✗ Failed: {result['failed']}")
            print(f"  ≈ Duplicates: {result['duplicates']}")

        print(f"\nTOTAL:")
        print(f"  ✓ Successful: {total_success}")
        print(f"  ✗ Failed: {total_failed}")
        print(f"  ≈ Duplicates: {total_duplicates}")
        print("="*80)

    finally:
        session.close()


if __name__ == '__main__':
    main()
