"""Return calculation functions."""

import pandas as pd
import numpy as np
from typing import Union


def calculate_returns(
    prices: Union[pd.Series, pd.DataFrame],
    method: str = 'simple',
) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate returns from price series.
    
    Args:
        prices: Price series or DataFrame
        method: 'simple' for percentage returns or 'log' for log returns
        
    Returns:
        Returns series or DataFrame
        
    Example:
        >>> returns = calculate_returns(data['close'])
    """
    if method == 'simple':
        return prices.pct_change()
    elif method == 'log':
        return np.log(prices / prices.shift(1))
    else:
        raise ValueError(f"Unknown method: {method}. Use 'simple' or 'log'")


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Calculate cumulative returns from a returns series.
    
    Args:
        returns: Returns series
        
    Returns:
        Cumulative returns series
        
    Example:
        >>> cum_returns = calculate_cumulative_returns(returns)
    """
    return (1 + returns).cumprod() - 1


def calculate_annualized_return(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized return.
    
    Args:
        returns: Returns series
        periods_per_year: Number of periods in a year (252 for daily, 52 for weekly)
        
    Returns:
        Annualized return as a percentage
    """
    total_return = (1 + returns).prod() - 1
    n_periods = len(returns)
    years = n_periods / periods_per_year
    
    if years > 0:
        return (pow(1 + total_return, 1 / years) - 1) * 100
    return 0.0


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: float,
) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).
    
    Args:
        start_value: Starting portfolio value
        end_value: Ending portfolio value
        years: Number of years
        
    Returns:
        CAGR as a percentage
    """
    if years <= 0 or start_value <= 0:
        return 0.0
    
    return (pow(end_value / start_value, 1 / years) - 1) * 100
