"""Tests for BaseStrategy."""

import pytest
import pandas as pd
from backtest.strategies.base import BaseStrategy


class TestStrategy(BaseStrategy):
    """Concrete strategy for testing."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        return signals


def test_base_strategy_initialization():
    """Test BaseStrategy initialization."""
    strategy = TestStrategy(name="TestStrategy")
    assert strategy.name == "TestStrategy"


def test_base_strategy_default_name():
    """Test default strategy name."""
    strategy = TestStrategy()
    assert strategy.name == "TestStrategy"


def test_validate_data_valid(sample_price_data):
    """Test data validation with valid data."""
    strategy = TestStrategy()
    # Should not raise
    strategy.validate_data(sample_price_data)


def test_validate_data_empty():
    """Test data validation with empty data."""
    strategy = TestStrategy()
    with pytest.raises(ValueError, match="empty"):
        strategy.validate_data(pd.DataFrame())


def test_validate_data_missing_columns():
    """Test data validation with missing required columns."""
    strategy = TestStrategy()
    data = pd.DataFrame({'open': [1, 2, 3]}, 
                       index=pd.date_range('2020-01-01', periods=3))
    
    with pytest.raises(ValueError, match="Missing required columns"):
        strategy.validate_data(data)


def test_generate_signals_abstract():
    """Test that generate_signals is abstract."""
    # Cannot instantiate BaseStrategy directly
    with pytest.raises(TypeError):
        BaseStrategy()


def test_strategy_repr():
    """Test strategy string representation."""
    strategy = TestStrategy(name="MyTest")
    repr_str = repr(strategy)
    assert "TestStrategy" in repr_str
