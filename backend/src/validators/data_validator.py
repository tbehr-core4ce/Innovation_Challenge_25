import pandas as pd
import re
from typing import List

class DataValidator:
    """
    DataFrame validator that tracks errors and warnings
    Validates: missing values, numeric columns (>0), date columns (flexible parsing, timezone-aware, standardized output, no future dates)
    Note: unsure if the columns validated would be known by name or not
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    #  NULL CHECK 
    def check_missing_values(self):
        """Log errors for any missing values in the DataFrame"""
        for col in self.df.columns:
            missing_rows = self.df[self.df[col].isna()].index.tolist()
            if missing_rows:
                self.errors.append(f"{col}: missing values in rows {missing_rows}")

    #  DATE CHECK 
    def check_date_values(self, column: str, output_format: str = "%Y-%m-%d"):
        """
        Flexible date parsing that handles all common formats:ISO: 2025-05-12, 2025-05-12T10:30:00Z, US: 05/12/2025, 05-12-2025, European: 12/05/2025, 12.05.2025, Timestamps: Unix timestamps
        Outputs standardized ISO format (YYYY-MM-DD) by default (is this what is wanted(?))
        """
        for idx, val in self.df[column].items():
            if pd.isna(val):
                continue
            try:
                # Try to parse the date
                date_val = pd.to_datetime(val, errors='coerce')

                # If that fails, try with dayfirst for European formats
                if pd.isna(date_val):
                    date_val = pd.to_datetime(val, errors='coerce', dayfirst=True)

                # Skip null dates
                if pd.isna(date_val):
                    self.errors.append(f"{column}: invalid date '{val}' at row {idx}")
                    continue

                # Remove timezone to compare with naive now(), this was a problem when working with one of the datasets
                if date_val.tzinfo is not None:
                    date_val = date_val.tz_convert(None).tz_localize(None)

                # Check for future dates
                if date_val > pd.Timestamp.now():
                    self.errors.append(f"{column}: future date '{val}' at row {idx}")

                # Standardize to ISO format (YYYY-MM-DD)
                self.df.at[idx, column] = date_val.strftime(output_format)
            except Exception as e:
                self.errors.append(f"{column}: error '{e}' with value '{val}' at row {idx}")

    #  NUMERIC CHECK 
    def check_numeric_values(self, column: str, min_value: float = 0):
        # Validate numeric columns (must be float or int and greater than min_value which is default 0)
        # How to/should implement for lat/long?
        for idx, val in self.df[column].items():
            if pd.isna(val):
                continue
            try:
                num = float(val)
                if num < min_value:
                    self.errors.append(f"{column}: value < {min_value} '{val}' at row {idx}")
            except ValueError:
                self.errors.append(f"{column}: non-numeric value '{val}' at row {idx}")

    #  AUTO-DETECT 
    def auto_detect_and_validate(self):
        """
        Automatically detect date and numeric-like columns and validate them
        This is to not have to go into each dataset and instruct which column is date column to validate -> better way to do this?
        """
        for col in self.df.columns:
            col_lower = col.lower()

            # Date detection (matches words like "_date", "-timestamp", "date" anywhere)
            if any(re.search(rf"(?:^|[_\s-]){kw}(?:$|[_\s-])", col_lower) for kw in ["date", "time", "timestamp", "recorded"]):
                self.check_date_values(col)
                continue

            # Numeric detection
            if any(re.search(rf"(?:^|[_\s-]){kw}(?:$|[_\s-])", col_lower) 
                   for kw in ["size", "count", "number", "num", "quantity", "amount", "total", "population"]):
                self.check_numeric_values(col, min_value=0)
                continue

    #  REPORT 
    def generate_report(self) -> str:
        self.check_missing_values()
        self.auto_detect_and_validate()

        report_lines = ["DATA VALIDATION REPORT"]

        if self.errors:
            report_lines.append(f"\n{len(self.errors)} Errors:")
            for e in self.errors:
                report_lines.append(f"- {e}")
        else:
            report_lines.append("\nNo errors detected.")

        if self.warnings:
            report_lines.append(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                report_lines.append(f"• {w}")
        else:
            report_lines.append("\nNo warnings detected.")

        return "\n".join(report_lines)


#  EXAMPLE 
if __name__ == "__main__":
    # Example
    url = "https://raw.githubusercontent.com/tbehr-core4ce/Innovation_Challenge_25/refs/heads/main/datasets/raw/nwssh5sitemapnocoords.csv"
    df = pd.read_csv(url)
    
    validator = DataValidator(df)
    print(validator.generate_report())