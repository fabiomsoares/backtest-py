"""Risk metrics calculations."""

import pandas as pd
import numpy as np
from typing import Optional, Union


def calculate_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
    annualize: bool = True,
) -> float:
    """
    Calculate volatility (standard deviation of returns).
    
    Args:
        returns: Returns series
        periods_per_year: Number of periods per year for annualization
        annualize: Whether to annualize the volatility
        
    Returns:
        Volatility as a percentage
    """
    vol = returns.std()
    
    if annualize:
        vol = vol * np.sqrt(periods_per_year)
    
    return vol * 100


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: Returns series
        risk_free_rate: Risk-free rate (annualized percentage)
        periods_per_year: Number of periods per year
        
    Returns:
        Sharpe ratio
        
    Example:
        >>> sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)
    """
    excess_returns = returns - (risk_free_rate / 100 / periods_per_year)
    
    if excess_returns.std() == 0:
        return 0.0
    
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Sortino ratio (uses downside deviation instead of total volatility).
    
    Args:
        returns: Returns series
        risk_free_rate: Risk-free rate (annualized percentage)
        periods_per_year: Number of periods per year
        
    Returns:
        Sortino ratio
    """
    excess_returns = returns - (risk_free_rate / 100 / periods_per_year)
    
    # Calculate downside deviation (only negative returns)
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    downside_std = downside_returns.std()
    
    return (excess_returns.mean() / downside_std) * np.sqrt(periods_per_year)


def calculate_max_drawdown(
    returns: pd.Series,
    return_series: bool = False,
) -> Union[float, pd.Series]:
    """
    Calculate maximum drawdown.
    
    Args:
        returns: Returns series
        return_series: If True, return full drawdown series
        
    Returns:
        Maximum drawdown as a percentage (negative value)
        
    Example:
        >>> max_dd = calculate_max_drawdown(returns)
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    if return_series:
        return drawdown * 100
    
    return drawdown.min() * 100


def calculate_calmar_ratio(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Calmar ratio (annualized return / maximum drawdown).
    
    Args:
        returns: Returns series
        periods_per_year: Number of periods per year
        
    Returns:
        Calmar ratio
    """
    from backtest.metrics.returns import calculate_annualized_return
    
    ann_return = calculate_annualized_return(returns, periods_per_year)
    max_dd = abs(calculate_max_drawdown(returns))
    
    if max_dd == 0:
        return 0.0
    
    return ann_return / max_dd


def calculate_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns: Returns series
        confidence_level: Confidence level (e.g., 0.95 for 95%)
        
    Returns:
        VaR as a percentage (negative value represents loss)
    """
    return np.percentile(returns, (1 - confidence_level) * 100) * 100


def calculate_cvar(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.
    
    Args:
        returns: Returns series
        confidence_level: Confidence level
        
    Returns:
        CVaR as a percentage
    """
    var_threshold = np.percentile(returns, (1 - confidence_level) * 100)
    return returns[returns <= var_threshold].mean() * 100


def calculate_beta(
    returns: pd.Series,
    market_returns: pd.Series,
) -> float:
    """
    Calculate beta relative to market returns.
    
    Args:
        returns: Strategy returns
        market_returns: Market benchmark returns
        
    Returns:
        Beta coefficient
    """
    covariance = returns.cov(market_returns)
    market_variance = market_returns.var()
    
    if market_variance == 0:
        return 0.0
    
    return covariance / market_variance
