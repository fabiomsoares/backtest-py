"""Tests for returns calculations."""

import pytest
import pandas as pd
import numpy as np
from backtest.metrics.returns import (
    calculate_returns,
    calculate_cumulative_returns,
    calculate_annualized_return,
    calculate_cagr,
)


def test_calculate_simple_returns():
    """Test simple returns calculation."""
    prices = pd.Series([100, 110, 105, 115])
    returns = calculate_returns(prices, method='simple')
    
    assert len(returns) == 4
    assert pd.isna(returns.iloc[0])  # First value should be NaN
    assert abs(returns.iloc[1] - 0.10) < 0.0001  # 10% increase


def test_calculate_log_returns():
    """Test log returns calculation."""
    prices = pd.Series([100, 110, 105, 115])
    returns = calculate_returns(prices, method='log')
    
    assert len(returns) == 4
    assert pd.isna(returns.iloc[0])


def test_calculate_cumulative_returns():
    """Test cumulative returns calculation."""
    returns = pd.Series([0.01, 0.02, -0.01, 0.015])
    cum_returns = calculate_cumulative_returns(returns)
    
    assert len(cum_returns) == 4
    assert cum_returns.iloc[-1] > 0  # Should have positive cumulative return


def test_calculate_annualized_return():
    """Test annualized return calculation."""
    # Create returns for approximately 252 trading days
    returns = pd.Series([0.001] * 252)  # Small daily gains
    ann_return = calculate_annualized_return(returns, periods_per_year=252)
    
    assert ann_return > 0


def test_calculate_cagr():
    """Test CAGR calculation."""
    start_value = 100000
    end_value = 150000
    years = 3
    
    cagr = calculate_cagr(start_value, end_value, years)
    
    assert cagr > 0
    assert cagr < 20  # Should be reasonable growth rate
