"""Tests for BacktestEngine."""

import pytest
import pandas as pd
from backtest.core.engine import BacktestEngine
from backtest.strategies.moving_average import MovingAverageStrategy


def test_engine_initialization():
    """Test BacktestEngine initialization."""
    strategy = MovingAverageStrategy()
    engine = BacktestEngine(strategy=strategy, initial_capital=100000)
    
    assert engine.initial_capital == 100000
    assert engine.strategy == strategy
    assert engine.commission == 0.0


def test_engine_run_with_sample_data(sample_price_data):
    """Test running backtest with sample data."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(strategy=strategy, initial_capital=100000)
    
    results = engine.run(sample_price_data)
    
    assert 'total_return' in results
    assert 'final_value' in results
    assert 'initial_capital' in results
    assert results['initial_capital'] == 100000


def test_engine_with_invalid_data():
    """Test engine with invalid data."""
    strategy = MovingAverageStrategy()
    engine = BacktestEngine(strategy=strategy)
    
    # Empty DataFrame
    with pytest.raises(ValueError):
        engine.run(pd.DataFrame())


def test_engine_get_metrics(sample_price_data):
    """Test getting performance metrics."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(strategy=strategy, initial_capital=50000)
    
    engine.run(sample_price_data)
    metrics = engine.get_metrics()
    
    assert 'total_return' in metrics
    assert 'sharpe_ratio' in metrics or 'volatility' in metrics
    assert isinstance(metrics, dict)


def test_engine_portfolio_history(sample_price_data):
    """Test portfolio history tracking."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(strategy=strategy)
    
    engine.run(sample_price_data)
    history = engine.get_portfolio_history()
    
    assert isinstance(history, pd.DataFrame)
    assert len(history) > 0
