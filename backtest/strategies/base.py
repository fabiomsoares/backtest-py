"""Base strategy class for all trading strategies."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All custom strategies must inherit from this class and implement
    the generate_signals method.
    
    Attributes:
        name (str): Name of the strategy
        
    Example:
        >>> class MyStrategy(BaseStrategy):
        ...     def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        ...         signals = pd.DataFrame(index=data.index)
        ...         signals['signal'] = 0
        ...         # Custom logic here
        ...         return signals
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy (defaults to class name)
        """
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on historical data.
        
        This method must be implemented by all concrete strategy classes.
        
        Args:
            data: Historical price data with OHLCV columns
            
        Returns:
            DataFrame with 'signal' column where:
                1 = buy signal
                -1 = sell signal
                0 = hold (no action)
                
        Example:
            >>> signals = strategy.generate_signals(data)
            >>> print(signals['signal'].value_counts())
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate that the input data meets strategy requirements.
        
        Args:
            data: Historical price data to validate
            
        Raises:
            ValueError: If data is invalid or missing required columns
        """
        if data is None or len(data) == 0:
            raise ValueError("Data cannot be empty")
        
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be a DatetimeIndex")
        
        # Check for required columns
        required_columns = self._get_required_columns()
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for NaN values
        if data[required_columns].isnull().any().any():
            raise ValueError("Data contains NaN values in required columns")
    
    def _get_required_columns(self) -> list:
        """
        Get list of required data columns for this strategy.
        
        Override this method in subclasses to specify different requirements.
        
        Returns:
            List of required column names
        """
        return ['close']
    
    def __repr__(self) -> str:
        """String representation of the strategy."""
        return f"{self.__class__.__name__}(name={self.name})"
