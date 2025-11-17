# ingestors.py - Legacy ingestor classes (DEPRECATED)
#
# NOTE: These old ingestor classes have been REPLACED by the new parser architecture:
# - base.py: BaseParser abstract class
# - commercial.py: CommercialPoultryParser
# - wild_bird.py: WildBirdParser
# - mammal.py: MammalParser
# - loader.py: H5N1DataLoader for database insertion
#
# See backend/scripts/run_ingestion.py for the new end-to-end pipeline.
#
# This file is kept for reference only and should not be used in production.

import os
from datetime import datetime
from typing import List

import pandas as pd


class CommercialBackyardFlock_Ingestor:
    # Ingestor for commercial-backyard-flocks.csv dataset
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
    # check if commercial / not 
    # change whats being returned, for db setup! 
    def ingest(self) -> pd.DataFrame: 
        # Ingest dataset from CSV
        print(f"\nParsing: {self.file_path}")
        
        # Read CSV
        df = pd.read_csv(self.file_path)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Clean the data
        df['County'] = df['County'].str.strip().str.title()
        df['State'] = df['State'].str.strip().str.title()
        df['Flock Type'] = df['Flock Type'].str.strip()

        # Standardize date to datetime object
        df['Outbreak Date'] = pd.to_datetime(df['Outbreak Date'], format='%m-%d-%Y', errors='coerce')        

        # Convert Flock Size to integer
        df['Flock Size'] = pd.to_numeric(df['Flock Size'], errors='coerce').astype('Int64')

        # Add metadata (if needed (?) commented out for now)
        # df['ingested_at'] = datetime.now()
        # df['data_source'] = 'commercial_backyard_flocks.csv'

        # blah: H5N1Detection    blah.detection_data = df["confirmed_date"]

        self.df = df
        print(f"Parsed {len(df)} records")
        return df

    # DEPRECATED: Use CommercialPoultryParser from commercial.py instead
    # def convert() -> H5N1Case:
    #     This method is no longer needed with the new parser architecture




class HPAIDetectionsInMammals_Ingestor:
    # Ingestor for HPAIDetectionsInMammals.csv
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def ingest(self) -> pd.DataFrame:
        # Ingest dataset from CSV
        print(f"\nParsing: {self.file_path}")

         # Read CSV
        df = pd.read_csv(self.file_path)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Transform data
        df['State'] = df['State'].str.strip().str.title()
        df['County'] = df['County'].str.strip().str.title()
        df['HPAI Strain'] = df['HPAI Strain'].str.strip()  
        df['Species'] = df['Species'].str.strip().str.title()  

        # Standardize date to datetime object; do we need date collected?
        df['Date Collected'] = pd.to_datetime(df['Date Collected'], errors='coerce')
        df['Date Detected'] = pd.to_datetime(df['Date Detected'], errors='coerce')
        
        # Add metadata (if needed (?) commented out for now)
        # df['ingested_at'] = datetime.now()
        # df['data_source'] = 'HPAIDetectionsinMammals.csv'

        self.df = df
        print(f"Parsed {len(df)} records")
        return df
    



class DusekDataReleaseList_Ingestor:
    # Ingestor for DusekDataReleaseList.csv
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
    
    def ingest(self) -> pd.DataFrame:
        # Ingest dataset from CSV
        print(f"\nParsing: {self.file_path}")

        # Read CSV
        df = pd.read_csv(self.file_path)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Clean string columns that might have extra spaces - take out columns we don't need, 
        string_columns = [
                'Case-Acc #', 'Species', 'Scientific Name', 'Order', 'Family', 
                'Capture Status', 'Age', 'Sex', 'Location', 'Region',
                'Season', 'Sample 1', 'Result', 'Final HA Result', 'MA PCR of Egg Fluid'
        ]      

        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            
        # Standardize location columns (title case)
        if 'Location' in df.columns:
            df['Location'] = df['Location'].str.title()
        if 'Region' in df.columns:
            df['Region'] = df['Region'].str.title()
        
        # Convert dates to MM-DD-YYYY format
        if 'Date Collected' in df.columns:
            df['Date Collected'] = pd.to_datetime(df['Date Collected'], errors='coerce')
        if 'PCR Date' in df.columns:
            df['PCR Date'] = pd.to_datetime(df['PCR Date'], errors='coerce')        
        
        # Convert numeric columns
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        if 'Band No.' in df.columns:
            df['Band No.'] = pd.to_numeric(df['Band No.'], errors='coerce').astype('Int64')
        if 'Ct' in df.columns:
            # Ct column has "No Ct" values, convert to numeric (will become NaN)
            df['Ct'] = pd.to_numeric(df['Ct'], errors='coerce')

        # Add metadata (if needed (?) commented out for now)
        # df['ingested_at'] = datetime.now()
        # df['data_source'] = 'HusketDataReleaseList.csv'
        
        self.df = df
        print(f"Parsed {len(df)} records")
        return df
    



class WildBirdHPAI_Ingestor:
    # Ingestor for HPAIDetectionInWildBirds.csv
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
    
    def ingest(self) -> pd.DataFrame:
        # Ingest dataset from CSV
        print(f"\nParsing: {self.file_path}")

        # Read CSV
        df = pd.read_csv(self.file_path)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Clean the data
        df['State'] = df['State'].str.strip().str.title()
        df['County'] = df['County'].str.strip().str.title()
        df['HPAI Strain'] = df['HPAI Strain'].str.strip()
        df['Bird Species'] = df['Bird Species'].str.strip().str.title()
        df['WOAH Classification'] = df['WOAH Classification'].str.strip()
        df['Sampling Method'] = df['Sampling Method'].str.strip()
        df['Submitting Agency'] = df['Submitting Agency'].str.strip()

        # Standardize date to datetime object
        df['Collection Date'] = pd.to_datetime(df['Collection Date'], errors='coerce')
        df['Date Detected'] = pd.to_datetime(df['Date Detected'], errors='coerce')

        # Add metadata (if needed (?) commented out for now)
        # df['ingested_at'] = datetime.now()
        # df['data_source'] = 'HPAIDetectionsInWildBirds.csv'

        self.df = df
        print(f"Parsed {len(df)} records")
        return df




class ICLNREVSSClinicalLabs_Ingestor:
    # Ingestor for ICLNREVSSClinicalLabs.csv dataset
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
    
    def ingest(self) -> pd.DataFrame:
        # Ingest dataset from CSV
        print(f"\nParsing: {self.file_path}")
        
        # Read CSV, but skip first description text row
        df = pd.read_csv(self.file_path, skiprows=1)
        # Clean column names
        df.columns = df.columns.str.strip()

        # Clean the data
        df['REGION TYPE'] = df['REGION TYPE'].str.strip()
        df['REGION'] = df['REGION'].str.strip()

        # Convert yr and wk to integers
        df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce').astype('Int64')
        df['WEEK'] = pd.to_numeric(df['WEEK'], errors='coerce').astype('Int64')

        # Convert numeric columns
        df['TOTAL SPECIMENS'] = pd.to_numeric(df['TOTAL SPECIMENS'], errors='coerce').astype('Int64')
        df['TOTAL A'] = pd.to_numeric(df['TOTAL A'], errors='coerce').astype('Int64')
        df['TOTAL B'] = pd.to_numeric(df['TOTAL B'], errors='coerce').astype('Int64')
        df['PERCENT POSITIVE'] = pd.to_numeric(df['PERCENT POSITIVE'], errors='coerce')
        df['PERCENT A'] = pd.to_numeric(df['PERCENT A'], errors='coerce')
        df['PERCENT B'] = pd.to_numeric(df['PERCENT B'], errors='coerce')

        # Add metadata (if needed (?) commented out for now)
        # df['ingested_at'] = datetime.now()
        # df['data_source'] = 'FluViewPhase2Data.csv'

        self.df = df
        print(f"Parsed {len(df)} records")
        return df
    

if __name__ == "__main__":

    datasets_path = "/home/gmwright/core4ce_innovation/Innovation_Challenge_25/datasets/"

    for filename in os.listdir(datasets_path):
        data_path = os.path.join(datasets_path, filename)
        df = pd.read_csv(data_path)

