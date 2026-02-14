"""Validation utility functions."""

import pandas as pd
from typing import List, Optional


def validate_data(
    data: pd.DataFrame,
    required_columns: Optional[List[str]] = None,
    check_nulls: bool = True,
) -> bool:
    """
    Validate that data meets basic requirements.
    
    Args:
        data: DataFrame to validate
        required_columns: List of required column names
        check_nulls: Whether to check for null values
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
        
    Example:
        >>> validate_data(data, required_columns=['open', 'high', 'low', 'close'])
    """
    if data is None or len(data) == 0:
        raise ValueError("Data is empty")
    
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have a DatetimeIndex")
    
    if required_columns:
        missing = [col for col in required_columns if col not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    if check_nulls:
        if data.isnull().any().any():
            null_cols = data.columns[data.isnull().any()].tolist()
            raise ValueError(f"Data contains null values in columns: {null_cols}")
    
    return True


def validate_strategy(strategy) -> bool:
    """
    Validate that a strategy implements required methods.
    
    Args:
        strategy: Strategy object to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    from backtest.strategies.base import BaseStrategy
    
    if not isinstance(strategy, BaseStrategy):
        raise ValueError("Strategy must inherit from BaseStrategy")
    
    if not hasattr(strategy, 'generate_signals'):
        raise ValueError("Strategy must implement generate_signals method")
    
    return True


def validate_ohlcv(data: pd.DataFrame) -> bool:
    """
    Validate OHLCV data structure.
    
    Args:
        data: OHLCV DataFrame
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    required = ['open', 'high', 'low', 'close', 'volume']
    
    # Check if all required columns exist
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")
    
    # Validate price relationships
    if (data['high'] < data['low']).any():
        raise ValueError("High prices cannot be lower than low prices")
    
    if (data['high'] < data['close']).any():
        raise ValueError("High prices cannot be lower than close prices")
    
    if (data['low'] > data['close']).any():
        raise ValueError("Low prices cannot be higher than close prices")
    
    if (data['high'] < data['open']).any():
        raise ValueError("High prices cannot be lower than open prices")
    
    if (data['low'] > data['open']).any():
        raise ValueError("Low prices cannot be higher than open prices")
    
    # Check for negative values
    if (data[required] < 0).any().any():
        raise ValueError("OHLCV data cannot contain negative values")
    
    return True


def validate_portfolio_config(
    initial_capital: float,
    commission: float = 0.0,
) -> bool:
    """
    Validate portfolio configuration.
    
    Args:
        initial_capital: Initial capital amount
        commission: Commission rate or fixed amount
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    if initial_capital <= 0:
        raise ValueError("Initial capital must be positive")
    
    if commission < 0:
        raise ValueError("Commission cannot be negative")
    
    if commission >= 1 and commission > initial_capital:
        raise ValueError("Fixed commission cannot exceed initial capital")
    
    return True
