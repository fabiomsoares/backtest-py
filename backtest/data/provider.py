"""Data provider interfaces."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional


class DataProvider(ABC):
    """
    Abstract base class for data providers.
    
    Custom data providers should inherit from this class and implement
    the get_data method.
    
    Example:
        >>> class MyDataProvider(DataProvider):
        ...     def get_data(self, symbol, start, end):
        ...         # Custom implementation
        ...         return data
    """
    
    @abstractmethod
    def get_data(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Retrieve historical data for a symbol.
        
        Args:
            symbol: Trading symbol/ticker
            start: Start date
            end: End date
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with historical price data
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that data meets minimum requirements.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        if data is None or len(data) == 0:
            return False
        
        required_columns = ['close']
        return all(col in data.columns for col in required_columns)


class YahooFinanceProvider(DataProvider):
    """
    Data provider for Yahoo Finance.
    
    Example:
        >>> provider = YahooFinanceProvider()
        >>> data = provider.get_data('AAPL', start='2020-01-01')
    """
    
    def get_data(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get data from Yahoo Finance."""
        from backtest.data.loader import DataLoader
        return DataLoader.load_yahoo(symbol, start=start, end=end, **kwargs)


class CSVDataProvider(DataProvider):
    """
    Data provider for CSV files.
    
    Example:
        >>> provider = CSVDataProvider()
        >>> data = provider.get_data('data/prices.csv')
    """
    
    def get_data(
        self,
        symbol: str,  # In this case, symbol is the file path
        start: Optional[str] = None,
        end: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Load data from CSV file."""
        from backtest.data.loader import DataLoader
        data = DataLoader.load_csv(symbol, **kwargs)
        
        # Filter by date if provided
        if start:
            data = data[data.index >= pd.to_datetime(start)]
        if end:
            data = data[data.index <= pd.to_datetime(end)]
        
        return data
