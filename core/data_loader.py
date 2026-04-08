"""
Data loading and preprocessing utilities
"""

import pandas as pd
from typing import Tuple
from datetime import datetime, timedelta


class DataLoader:
    """Handle data loading and preprocessing"""
    
    def __init__(self, file_path: str, text_columns: list, metric_columns: list):
        """
        Initialize data loader
        
        Args:
            file_path: Path to Excel file
            text_columns: List of text column names
            metric_columns: List of metric column names
        """
        self.file_path = file_path
        self.text_columns = text_columns
        self.metric_columns = metric_columns
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel file"""
        self.df = pd.read_excel(self.file_path)
        return self.df
    
    def clean_text_columns(self):
        """Clean text columns by filling NaN and converting to string"""
        for col in self.text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("").astype(str)
    
    def normalize_dates(self):
        """Normalize date columns (keep full datetime, not just date)"""
        self.df["PublishedDate"] = pd.to_datetime(
            self.df["PublishedDate"], 
            errors="coerce"
        )
        self.df = self.df[self.df["PublishedDate"].notna()].copy()
        # Keep PublishedDay for backward compatibility
        self.df["PublishedDay"] = self.df["PublishedDate"].dt.date
    
    def ensure_numeric_columns(self):
        """Ensure metric columns are numeric"""
        for col in self.metric_columns:
            if col in self.df.columns:
                # Convert to numeric, non-numeric values become NaN
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                # Fill NaN with 0
                self.df[col] = self.df[col].fillna(0)
    
    def preprocess(self) -> pd.DataFrame:
        """Run all preprocessing steps"""
        print("      → Loading Excel file...")
        self.load_data()
        print(f"      → Loaded {len(self.df)} rows")
        
        print("      → Cleaning text columns...")
        self.clean_text_columns()
        
        print("      → Normalizing dates...")
        self.normalize_dates()
        print(f"      → Valid dates: {len(self.df)} rows")
        
        print("      → Converting numeric columns...")
        self.ensure_numeric_columns()
        
        return self.df
    
    def filter_by_datetime_range(self, end_datetime: str, days: int = 1) -> pd.DataFrame:
        """
        Filter dataframe by datetime range (end_datetime - N days to end_datetime)
        
        Args:
            end_datetime: End datetime string in format "YYYY-MM-DD HH:MM:SS"
            days: Number of days to look back (default: 1 for daily reports, use 7 for weekly)
                  Note: This creates an INCLUSIVE range of N days
                  Example: days=7 means 7 full days including start and end
            
        Returns:
            Filtered dataframe for the specified time window
        """
        end_dt = pd.to_datetime(end_datetime)
        # Fix: For N days inclusive, subtract (N-1) days and reset to start of day
        # Example: If end_dt = 2026-04-06 23:59 and days=7
        #          start_dt = 2026-03-31 00:00 (7 days total: 31 Mar to 6 Apr)
        start_dt = end_dt - timedelta(days=days-1, hours=end_dt.hour, minutes=end_dt.minute, seconds=end_dt.second)
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return self.df[
            (self.df["PublishedDate"] >= start_dt) &
            (self.df["PublishedDate"] <= end_dt)
        ].copy()
    
    def filter_by_date(self, date: str) -> pd.DataFrame:
        """
        Filter dataframe by specific date (backward compatibility)
        
        Args:
            date: Date string in format YYYY-MM-DD
            
        Returns:
            Filtered dataframe
        """
        target_date = pd.to_datetime(date).date()
        return self.df[self.df["PublishedDay"] == target_date].copy()
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter dataframe by date range
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Filtered dataframe
        """
        start = pd.to_datetime(start_date).date()
        end = pd.to_datetime(end_date).date()
        return self.df[
            (self.df["PublishedDay"] >= start) & 
            (self.df["PublishedDay"] <= end)
        ].copy()
    
    def get_date_range_for_lookback(self, report_date: str, 
                                      lookback_days: int) -> Tuple[str, str]:
        """
        Calculate date range for lookback period
        
        Args:
            report_date: Report date string
            lookback_days: Number of days to look back
            
        Returns:
            Tuple of (start_date, end_date) as strings
        """
        end = pd.to_datetime(report_date).date()
        start = end - timedelta(days=lookback_days - 1)
        return str(start), str(end)


def calculate_percentage_change(today: float, yesterday: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        today: Current value
        yesterday: Previous value
        
    Returns:
        Percentage change rounded to 2 decimals
    """
    if yesterday == 0:
        return 0.0 if today == 0 else 100.0
    return round((today - yesterday) / yesterday * 100, 2)


def calculate_engagement(df: pd.DataFrame) -> pd.Series:
    """
    Calculate engagement score for each row
    
    Always calculates from: Reactions + Shares + Comments
    (Ignores Interactions column if it exists)
    
    Args:
        df: Dataframe with Reactions, Shares, Comments columns
        
    Returns:
        Series with engagement scores
    """
    # Handle empty DataFrame
    if len(df) == 0:
        return pd.Series(dtype='float64')
    
    # Calculate from individual metrics
    # Get columns or create Series of zeros with same index as df
    if "Reactions" in df.columns:
        reactions = pd.to_numeric(df["Reactions"], errors="coerce").fillna(0)
    else:
        reactions = pd.Series(0, index=df.index)
    
    if "Shares" in df.columns:
        shares = pd.to_numeric(df["Shares"], errors="coerce").fillna(0)
    else:
        shares = pd.Series(0, index=df.index)
    
    if "Comments" in df.columns:
        comments = pd.to_numeric(df["Comments"], errors="coerce").fillna(0)
    else:
        comments = pd.Series(0, index=df.index)
    
    return reactions + shares + comments
