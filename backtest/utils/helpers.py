"""Helper utility functions."""

import pandas as pd
from typing import Optional, Union


def format_currency(amount: float, symbol: str = "$") -> str:
    """
    Format a number as currency.
    
    Args:
        amount: Amount to format
        symbol: Currency symbol
        
    Returns:
        Formatted currency string
        
    Example:
        >>> format_currency(1234.56)
        '$1,234.56'
    """
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a number as percentage.
    
    Args:
        value: Value to format (as decimal, e.g., 0.15 for 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
        
    Example:
        >>> format_percentage(0.1234, 2)
        '12.34%'
    """
    return f"{value:.{decimals}f}%"


def calculate_position_size(
    capital: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float,
    position_sizing_method: str = "fixed_risk",
) -> int:
    """
    Calculate position size based on risk management rules.
    
    Args:
        capital: Available capital
        risk_per_trade: Risk per trade as percentage (e.g., 0.02 for 2%)
        entry_price: Entry price per share
        stop_loss_price: Stop loss price per share
        position_sizing_method: Method for sizing ('fixed_risk', 'fixed_percentage')
        
    Returns:
        Number of shares to buy
        
    Example:
        >>> size = calculate_position_size(100000, 0.02, 150, 145)
        >>> print(size)
    """
    if position_sizing_method == "fixed_risk":
        # Risk-based position sizing
        risk_amount = capital * risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return 0
        
        shares = int(risk_amount / risk_per_share)
        return shares
    
    elif position_sizing_method == "fixed_percentage":
        # Percentage of capital
        allocation = capital * risk_per_trade
        shares = int(allocation / entry_price)
        return shares
    
    else:
        raise ValueError(f"Unknown position sizing method: {position_sizing_method}")


def resample_data(
    data: pd.DataFrame,
    frequency: str = 'D',
    agg_methods: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Resample OHLCV data to different frequency.
    
    Args:
        data: OHLCV DataFrame
        frequency: Target frequency ('D' for daily, 'W' for weekly, 'M' for monthly)
        agg_methods: Dictionary specifying aggregation methods per column
        
    Returns:
        Resampled DataFrame
        
    Example:
        >>> weekly_data = resample_data(daily_data, 'W')
    """
    if agg_methods is None:
        agg_methods = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
        }
    
    # Only resample columns that exist in the data
    agg_methods = {k: v for k, v in agg_methods.items() if k in data.columns}
    
    return data.resample(frequency).agg(agg_methods).dropna()


def calculate_returns_from_prices(
    prices: pd.Series,
    method: str = 'simple',
) -> pd.Series:
    """
    Calculate returns from price series.
    
    Args:
        prices: Price series
        method: 'simple' or 'log'
        
    Returns:
        Returns series
    """
    if method == 'simple':
        return prices.pct_change()
    elif method == 'log':
        import numpy as np
        return np.log(prices / prices.shift(1))
    else:
        raise ValueError(f"Unknown method: {method}")


def get_date_range(data: pd.DataFrame) -> tuple:
    """
    Get date range from DataFrame.
    
    Args:
        data: DataFrame with datetime index
        
    Returns:
        Tuple of (start_date, end_date)
    """
    return (data.index.min(), data.index.max())


def split_train_test(
    data: pd.DataFrame,
    train_ratio: float = 0.8,
) -> tuple:
    """
    Split data into training and testing sets.
    
    Args:
        data: DataFrame to split
        train_ratio: Ratio of data to use for training (e.g., 0.8 for 80%)
        
    Returns:
        Tuple of (train_data, test_data)
        
    Example:
        >>> train, test = split_train_test(data, 0.8)
    """
    split_idx = int(len(data) * train_ratio)
    train = data.iloc[:split_idx]
    test = data.iloc[split_idx:]
    
    return train, test
