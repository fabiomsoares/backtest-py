"""
backtest-py: A simple but sophisticated backtesting framework in Python.

This package provides a modular framework for backtesting trading strategies
using historical market data with an in-memory database for fast operations.
"""

__version__ = "0.1.0"
__author__ = "Fabio Soares"

from backtest.core.engine import BacktestEngine
from backtest.models.strategy import Strategy

__all__ = ["BacktestEngine", "Strategy"]
