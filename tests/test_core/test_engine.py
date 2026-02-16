"""Tests for BacktestEngine."""

import pytest
import pandas as pd
from decimal import Decimal

from backtest import BacktestEngine, BacktestContext, setup_example_configuration
from backtest.strategies import MovingAverageStrategy


def test_engine_initialization(backtest_context):
    """Test BacktestEngine initialization."""
    strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("100000")
    )

    assert engine.initial_capital == Decimal("100000")
    assert engine.strategy == strategy
    assert engine.context == backtest_context


def test_engine_initialization_without_context():
    """Test BacktestEngine creates default context if none provided."""
    strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
    engine = BacktestEngine(strategy=strategy, initial_capital=Decimal("50000"))

    assert engine.context is not None
    assert engine.initial_capital == Decimal("50000")


def test_engine_run_with_sample_data(sample_price_data, backtest_context):
    """Test running backtest with sample data."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("100000")
    )

    results = engine.run(sample_price_data, symbol="TEST")

    # Verify results structure
    assert 'total_return' in results
    assert 'final_balance' in results
    assert 'initial_capital' in results
    assert results['initial_capital'] == 100000.0
    assert 'num_trades' in results


def test_engine_with_invalid_data(backtest_context):
    """Test engine with invalid data."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(strategy=strategy, context=backtest_context)

    # Empty DataFrame should raise ValueError
    with pytest.raises(ValueError):
        engine.run(pd.DataFrame())


def test_engine_get_orders(sample_price_data, backtest_context):
    """Test getting order history."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("50000")
    )

    engine.run(sample_price_data, symbol="TEST")
    orders = engine.get_orders()

    assert isinstance(orders, list)
    # Should have at least one order if strategy generated signals
    # (exact number depends on strategy logic and data)


def test_engine_balance_history(sample_price_data, backtest_context):
    """Test balance history tracking."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("100000")
    )

    engine.run(sample_price_data, symbol="TEST")
    balance_history = engine.get_balance_history()

    assert isinstance(balance_history, pd.DataFrame)
    assert len(balance_history) > 0
    assert 'balance' in balance_history.columns


def test_engine_metrics_calculation(sample_price_data, backtest_context):
    """Test performance metrics calculation."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("100000")
    )

    results = engine.run(sample_price_data, symbol="TEST")

    # Check basic metrics
    assert 'total_return' in results
    assert 'total_pnl' in results
    assert 'num_trades' in results
    assert isinstance(results['total_return'], float)
    assert isinstance(results['final_balance'], float)
    assert results['final_balance'] > 0


def test_engine_date_filtering(sample_price_data, backtest_context):
    """Test running backtest with date filters."""
    strategy = MovingAverageStrategy(fast_window=5, slow_window=10)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("100000")
    )

    # Run with date range
    results = engine.run(
        sample_price_data,
        symbol="TEST",
        start_date='2020-06-01',
        end_date='2020-09-30'
    )

    assert 'total_return' in results
    assert 'num_trades' in results


def test_engine_with_simple_data(simple_price_data, backtest_context):
    """Test engine with simple price data (close only)."""
    strategy = MovingAverageStrategy(fast_window=2, slow_window=3)
    engine = BacktestEngine(
        strategy=strategy,
        context=backtest_context,
        initial_capital=Decimal("10000")
    )

    results = engine.run(simple_price_data, symbol="SIMPLE")

    assert 'final_balance' in results
    assert results['initial_capital'] == 10000.0
