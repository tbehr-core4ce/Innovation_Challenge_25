"""
Database loader for H5N1 case data.
Handles bulk insertion into database with DataImport tracking.
backend/src/parsers/loader.py
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import hashlib
import time

from src.core.models import H5N1Case, DataImport, DataSource
from src.core.database import get_db


class H5N1DataLoader:
    """
    Loads parsed and validated H5N1 data into the database.

    Features:
    - Bulk insert for performance
    - Duplicate detection via external_id
    - DataImport tracking for auditing
    - Error logging
    """

    def __init__(self, session: Session):
        """
        Initialize data loader.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.import_record: Optional[DataImport] = None

    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file for duplicate detection.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal hash string
        """
        hash_obj = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def check_duplicate_import(self, file_hash: str) -> bool:
        """
        Check if file has already been imported.

        Args:
            file_hash: SHA-256 hash of file

        Returns:
            True if file was previously imported successfully
        """
        existing = self.session.query(DataImport).filter(
            DataImport.file_hash == file_hash,
            DataImport.status == 'completed'
        ).first()

        return existing is not None

    def create_import_record(
        self,
        source: DataSource,
        filename: str,
        file_hash: str,
        total_rows: int
    ) -> DataImport:
        """
        Create DataImport tracking record.

        Args:
            source: Data source enum
            filename: Name of source file
            file_hash: SHA-256 hash of file
            total_rows: Total rows to import

        Returns:
            DataImport record
        """
        import_record = DataImport(
            source=source,
            filename=filename,
            file_hash=file_hash,
            total_rows=total_rows,
            successful_rows=0,
            failed_rows=0,
            duplicate_rows=0,
            status='in_progress',
            started_at=datetime.now()
        )

        self.session.add(import_record)
        self.session.commit()

        self.import_record = import_record
        return import_record

    def bulk_insert(
        self,
        df: pd.DataFrame,
        source: DataSource,
        file_path: str
    ) -> Tuple[int, int, int]:
        """
        Bulk insert DataFrame into H5N1Case table.

        Args:
            df: Validated DataFrame with H5N1 case data
            source: Data source enum
            file_path: Path to source file

        Returns:
            Tuple of (successful_count, failed_count, duplicate_count)
        """
        print(f"\nLoading {len(df)} records into database...")

        start_time = time.time()

        # Calculate file hash
        file_hash = self.calculate_file_hash(file_path)
        filename = file_path.split('/')[-1]

        # Check for duplicate import
        if self.check_duplicate_import(file_hash):
            print(f"⚠ File already imported (hash: {file_hash[:12]}...)")
            return (0, 0, len(df))

        # Create import tracking record
        self.create_import_record(source, filename, file_hash, len(df))

        successful = 0
        failed = 0
        duplicates = 0
        errors = []

        # Convert DataFrame to records
        records = df.to_dict('records')

        # Batch insert for better performance
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            try:
                # Deduplicate within batch by external_id (keep first occurrence)
                seen_ids = set()
                unique_batch = []
                batch_duplicates = 0

                for record in batch:
                    external_id = record.get('external_id')
                    if external_id and external_id in seen_ids:
                        batch_duplicates += 1
                        duplicates += 1
                    else:
                        if external_id:
                            seen_ids.add(external_id)
                        unique_batch.append(record)

                if batch_duplicates > 0:
                    print(f"  ⚠ Batch {i//batch_size + 1}: Removed {batch_duplicates} within-batch duplicates")

                # Create H5N1Case objects from unique records only
                cases = []
                for record in unique_batch:
                    try:
                        # Convert enum string values to enum objects if needed
                        # (Parsers typically provide enum objects, but pandas may convert to strings)
                        from src.core.models import AnimalCategory, CaseStatus, Severity

                        if 'animal_category' in record and isinstance(record['animal_category'], str):
                            record['animal_category'] = AnimalCategory(record['animal_category'])

                        if 'status' in record and isinstance(record['status'], str):
                            record['status'] = CaseStatus(record['status'])

                        if 'severity' in record and isinstance(record['severity'], str):
                            record['severity'] = Severity(record['severity'])

                        if 'data_source' in record and isinstance(record['data_source'], str):
                            record['data_source'] = DataSource(record['data_source'])

                        # Create case object
                        case = H5N1Case(**record)
                        cases.append(case)

                    except Exception as e:
                        failed += 1
                        errors.append({
                            'record': record,
                            'error': str(e)
                        })

                # Bulk insert batch
                if cases:
                    try:
                        self.session.bulk_save_objects(cases)
                        self.session.commit()
                        successful += len(cases)

                        print(f"  ✓ Inserted batch {i//batch_size + 1}: {len(cases)} records")

                    except IntegrityError as e:
                        # Handle duplicate external_id
                        self.session.rollback()

                        # Try inserting one by one to identify duplicates
                        for case in cases:
                            try:
                                self.session.add(case)
                                self.session.commit()
                                successful += 1
                            except IntegrityError:
                                self.session.rollback()
                                duplicates += 1

            except Exception as e:
                self.session.rollback()
                failed += len(batch)
                print(f"  ✗ Batch {i//batch_size + 1} failed: {e}")

        # Update import record
        duration = time.time() - start_time

        if self.import_record:
            self.import_record.successful_rows = successful
            self.import_record.failed_rows = failed
            self.import_record.duplicate_rows = duplicates
            self.import_record.status = 'completed' if failed == 0 else 'completed_with_errors'
            self.import_record.completed_at = datetime.now()
            self.import_record.duration_seconds = duration

            if errors:
                error_log = '\n'.join([f"{e['error']}: {e['record'].get('external_id', 'unknown')}" for e in errors[:100]])
                self.import_record.error_log = error_log

            self.session.commit()

        print(f"\n{'='*60}")
        print(f"Import Summary:")
        print(f"  ✓ Successful: {successful}")
        print(f"  ✗ Failed: {failed}")
        print(f"  ≈ Duplicates: {duplicates}")
        print(f"  ⏱ Duration: {duration:.2f}s")

        # Print sample errors for debugging
        if errors:
            print(f"\n⚠ Sample errors (showing first 5):")
            for i, error in enumerate(errors[:5], 1):
                print(f"  {i}. {error['error']}")
                if 'record' in error:
                    print(f"     Record: external_id={error['record'].get('external_id', 'N/A')}, "
                          f"species={error['record'].get('animal_species', 'N/A')}, "
                          f"date={error['record'].get('case_date', 'N/A')}")

        print(f"{'='*60}\n")

        return (successful, failed, duplicates)

    def load_from_parser(
        self,
        parser,
        validate: bool = True
    ) -> Tuple[int, int, int]:
        """
        Load data from a parser object (convenience method).

        Args:
            parser: BaseParser subclass instance (must have run parse())
            validate: Whether to run validation before loading

        Returns:
            Tuple of (successful_count, failed_count, duplicate_count)
        """
        if parser.clean_df is None:
            raise ValueError("Parser has no cleaned data. Call parse() first.")

        df = parser.clean_df

        # Optional validation
        if validate:
            from src.validators.schema import SchemaValidator
            validator = SchemaValidator()
            df, errors = validator.validate(df)

            if errors:
                print(f"⚠ Validation found {len(errors)} issues")

        # Get data source from parser defaults
        source = parser.DEFAULTS.get('data_source', DataSource.OTHER)

        # Load into database
        return self.bulk_insert(df, source, parser.file_path)
