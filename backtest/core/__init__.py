"""
Core module for backtest-py.

This module contains the core backtesting engine and related functionality
for executing trading strategies and calculating performance metrics.
"""

from backtest.core.engine import BacktestEngine
from backtest.core.event_handler import EventHandler
from backtest.core.performance import PerformanceMetrics

__all__ = [
    "BacktestEngine",
    "EventHandler",
    "PerformanceMetrics",
]
