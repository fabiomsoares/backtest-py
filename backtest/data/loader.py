"""Data loading utilities."""

import pandas as pd
from typing import Optional, Union
from pathlib import Path


class DataLoader:
    """
    Utility class for loading historical price data from various sources.
    
    Supports loading from CSV files, Yahoo Finance, and other data providers.
    
    Example:
        >>> loader = DataLoader()
        >>> data = loader.load_csv('data.csv')
        >>> data = loader.load_yahoo('AAPL', start='2020-01-01', end='2021-12-31')
    """
    
    @staticmethod
    def load_csv(
        filepath: Union[str, Path],
        date_column: str = 'date',
        parse_dates: bool = True,
    ) -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Args:
            filepath: Path to CSV file
            date_column: Name of the date column
            parse_dates: Whether to parse dates automatically
            
        Returns:
            DataFrame with historical price data
            
        Example:
            >>> data = DataLoader.load_csv('prices.csv', date_column='Date')
        """
        df = pd.read_csv(filepath, parse_dates=[date_column] if parse_dates else False)
        
        if date_column in df.columns:
            df.set_index(date_column, inplace=True)
        
        # Standardize column names to lowercase
        df.columns = [col.lower() for col in df.columns]
        
        return df
    
    @staticmethod
    def load_yahoo(
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = '1d',
    ) -> pd.DataFrame:
        """
        Load data from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            start: Start date (format: 'YYYY-MM-DD')
            end: End date (format: 'YYYY-MM-DD')
            interval: Data interval ('1d', '1wk', '1mo', etc.)
            
        Returns:
            DataFrame with historical price data
            
        Example:
            >>> data = DataLoader.load_yahoo('AAPL', start='2020-01-01')
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError(
                "yfinance is required for loading Yahoo Finance data. "
                "Install it with: pip install yfinance"
            )
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)
        
        # Standardize column names
        df.columns = [col.lower() for col in df.columns]
        
        return df
    
    @staticmethod
    def load_pandas_datareader(
        symbol: str,
        data_source: str = 'yahoo',
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load data using pandas-datareader.
        
        Args:
            symbol: Stock ticker symbol
            data_source: Data source ('yahoo', 'fred', 'iex', etc.)
            start: Start date
            end: End date
            
        Returns:
            DataFrame with historical price data
            
        Example:
            >>> data = DataLoader.load_pandas_datareader('AAPL', 'yahoo')
        """
        try:
            import pandas_datareader as pdr
        except ImportError:
            raise ImportError(
                "pandas-datareader is required. "
                "Install it with: pip install pandas-datareader"
            )
        
        df = pdr.DataReader(symbol, data_source, start=start, end=end)
        
        # Standardize column names
        df.columns = [col.lower() for col in df.columns]
        
        return df
    
    @staticmethod
    def load_from_dict(data_dict: dict) -> pd.DataFrame:
        """
        Create DataFrame from dictionary.
        
        Args:
            data_dict: Dictionary with data
            
        Returns:
            DataFrame with historical price data
        """
        return pd.DataFrame(data_dict)
