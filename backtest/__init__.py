"""
backtest-py: A simple but sophisticated backtesting framework in Python.

This package provides a comprehensive framework for backtesting trading strategies
on historical data. It includes tools for portfolio management, strategy development,
performance analysis, and visualization.

Main Components:
    - BacktestEngine: Core engine for running backtests
    - BaseStrategy: Abstract base class for creating trading strategies
    - Portfolio: Portfolio management and tracking
    - Order: Order execution and management
    - Position: Position tracking and P&L calculation

Example:
    >>> from backtest import BacktestEngine, BaseStrategy
    >>> # Create a strategy
    >>> strategy = MyStrategy()
    >>> # Initialize engine
    >>> engine = BacktestEngine(strategy=strategy, initial_capital=100000)
    >>> # Run backtest
    >>> results = engine.run(data)
    >>> # Analyze results
    >>> metrics = engine.get_metrics()
"""

__version__ = "0.1.0"
__author__ = "Fabio Soares"

# Import main classes for easy access
from backtest.core.engine import BacktestEngine
from backtest.core.portfolio import Portfolio
from backtest.core.order import Order
from backtest.core.position import Position
from backtest.strategies.base import BaseStrategy

__all__ = [
    "BacktestEngine",
    "Portfolio",
    "Order",
    "Position",
    "BaseStrategy",
    "__version__",
]
