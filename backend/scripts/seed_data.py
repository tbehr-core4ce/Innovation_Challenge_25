#!/usr/bin/env python3
"""
1. Import parser/ingestor to find dataset files and process them
2. Use validator sparingly just for practice
3. Insert data into database (placeholder until DB is set up)
"""

import os
import sys
from pathlib import Path
import pandas as pd
# from sqlalchemy import create_engine  # uncomment when DB is ready (?)

# These two lines allowed my program to run to test it
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from backend.src.parsers.ingestors import (
    CommercialBackyardFlock_Ingestor,
    HPAIDetectionsInMammals_Ingestor,
    DusekDataReleaseList_Ingestor,
    WildBirdHPAI_Ingestor,
    ICLNREVSSClinicalLabs_Ingestor
)

# Database configuration - uncomment when ready (?)
# DATABASE_URL = os.getenv(
#     "DATABASE_URL", 
#     "sqlite:///./hpai_data.db"  # Default to SQLite if no env variable
# )
# engine = create_engine(DATABASE_URL, echo=False)

# for now, just testing ingestors - no DB needed
engine = None  # placeholder

# Path to datasets
DATASETS_PATH = os.getenv(
    "DATASETS_PATH",
    "./datasets"  # default path
)

# Map filename patterns to ingestor classes
INGESTOR_MAP = {
    "commercial-backyard-flocks": CommercialBackyardFlock_Ingestor,
    "HPAI Detections in Mammals.csv": HPAIDetectionsInMammals_Ingestor,
    "Dusek_data release list": DusekDataReleaseList_Ingestor,
    "HPAI Detections in Wild Birds": WildBirdHPAI_Ingestor,
    "ICL_NREVSS_Clinical_Labs": ICLNREVSSClinicalLabs_Ingestor,
}

def pick_ingestor(filename: str):
    # Return ingestor class based on filename
    for key, ingestor_cls in INGESTOR_MAP.items():
        if key.lower() in filename.lower():
            return ingestor_cls
    return None


def load_dataframe(df: pd.DataFrame, table_name: str):
    # Placeholder for loading dataframe into database
    # Not yet sure about database so just placeholder for now 

    print(f"Would load {len(df)} rows into '{table_name}'")
    
    # Uncomment when database is ready (?)
    # try:
    #     df.to_sql(
    #         table_name,
    #         con=engine,
    #         if_exists='replace',
    #         index=False,
    #         chunksize=1000
    #     )
    #     print(f"Loaded {len(df)} rows into '{table_name}'")
    # except Exception as e:
    #     print(f"Error loading '{table_name}': {e}")
    #     raise


def validate_datasets_path():
    # Validate that the datasets path exists and contains CSV files.
    if not os.path.exists(DATASETS_PATH):
        print(f"Error: Datasets path '{DATASETS_PATH}' does not exist.")
        return False
    
    csv_files = []
    for root, dirs, files in os.walk(DATASETS_PATH):
        csv_files.extend([f for f in files if f.endswith(".csv")])
    
    if not csv_files:
        print(f"Warning: No CSV files found in '{DATASETS_PATH}'")
        return False
    
    return True

def main():
    """
    Main execution function:
    - Validates datasets path
    - Walks through directories to find CSV files
    - Processes each file with appropriate ingestor
    - Loads data into database
    """
    print("=" * 60)
    print("HPAI Database Seeding Script")
    print("=" * 60)
    
    # Validate datasets path
    if not validate_datasets_path():
        sys.exit(1)
    
    processed_count = 0
    skipped = []          # store names of files without an ingestor
    error_count = 0
    
    # Walk through nested directories
    for root, dirs, files in os.walk(DATASETS_PATH):
        for filename in files:
            if not filename.endswith(".csv"):
                continue
            
            file_path = os.path.join(root, filename)  # Full nested path
            
            # Find appropriate ingestor
            IngClass = pick_ingestor(filename)
            if IngClass is None:
                skipped.append(filename)
                continue
            
            try:
                print(f"\n{'─' * 60}")
                print(f"Processing: {filename}")
                print(f"Using: {IngClass.__name__}")
                print(f"Path: {file_path}")
                
                # Ingest data
                ingestor = IngClass(file_path)
                df = ingestor.ingest()
                
                # Create table name from filename
                table_name = os.path.splitext(filename)[0].lower()
                table_name = table_name.replace('-', '_')  # Replace hyphens with underscores
                
                # Load into database (placeholder)
                load_dataframe(df, table_name)
                processed_count += 1
                
            except Exception as e:
                print(f"\nError processing '{filename}': {e}")
                error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60)
    print(f"\nSuccessfully processed: {processed_count} file(s)")
    
    if skipped:
        print(f"Skipped: {len(skipped)} file(s)")
        print("Files without an ingestor:")
        for f in skipped:
            print(f"  - {f}")
    
    if error_count > 0:
        print(f"Errors: {error_count} file(s)")
    
    print("=" * 60)
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())