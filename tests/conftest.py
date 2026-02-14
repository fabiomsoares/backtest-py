"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_price_data():
    """Generate sample OHLCV price data for testing."""
    dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
    n = len(dates)
    
    # Generate synthetic price data
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(n) * 2)
    
    data = pd.DataFrame({
        'open': prices + np.random.randn(n) * 0.5,
        'high': prices + abs(np.random.randn(n) * 1.5),
        'low': prices - abs(np.random.randn(n) * 1.5),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n),
    }, index=dates)
    
    # Ensure OHLC relationships are valid
    data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
    data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
    
    return data


@pytest.fixture
def simple_price_data():
    """Generate simple price data for basic tests."""
    dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
    
    data = pd.DataFrame({
        'close': [100, 102, 101, 105, 103, 107, 106, 110, 108, 112],
    }, index=dates)
    
    return data


@pytest.fixture
def sample_returns():
    """Generate sample returns series for testing."""
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    np.random.seed(42)
    returns = pd.Series(np.random.randn(100) * 0.01, index=dates)
    return returns


@pytest.fixture
def mock_strategy():
    """Create a mock strategy for testing."""
    from backtest.strategies.base import BaseStrategy
    import pandas as pd
    
    class MockStrategy(BaseStrategy):
        def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
            signals = pd.DataFrame(index=data.index)
            signals['signal'] = 0
            # Simple rule: buy on day 1, sell on day 5
            if len(data) >= 5:
                signals.iloc[1, signals.columns.get_loc('signal')] = 1
                signals.iloc[5, signals.columns.get_loc('signal')] = -1
            return signals
    
    return MockStrategy()


@pytest.fixture
def initial_capital():
    """Default initial capital for tests."""
    return 100000.0


@pytest.fixture
def commission():
    """Default commission for tests."""
    return 0.001
