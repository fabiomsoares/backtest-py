"""
backtest-py: A production-grade backtesting framework in Python.

This package provides a comprehensive framework for backtesting trading strategies
on historical data with realistic broker modeling, Decimal precision, and comprehensive
order lifecycle tracking.

Main Components:
    - BacktestEngine: Core engine for running backtests with event-driven strategies
    - BaseStrategy: Abstract base class for creating trading strategies
    - BacktestContext: Central repository context for managing state
    - TradingOrder: Production-grade order model with fees, leverage, and P&L tracking
    - BarData: Market data representation with OHLC and volume

Example:
    >>> from backtest import BacktestEngine, BaseStrategy, BacktestContext
    >>> from backtest import setup_example_configuration
    >>> from decimal import Decimal
    >>>
    >>> # Setup context
    >>> context = BacktestContext()
    >>> setup_example_configuration(context)
    >>>
    >>> # Create strategy
    >>> class MyStrategy(BaseStrategy):
    ...     def on_bar(self, bar, context):
    ...         # Your strategy logic
    ...         return []
    >>>
    >>> # Run backtest
    >>> engine = BacktestEngine(
    ...     strategy=MyStrategy(),
    ...     context=context,
    ...     initial_capital=Decimal("100000")
    ... )
    >>> results = engine.run(data, symbol="BTCUSDT")
"""

__version__ = "0.2.0"
__author__ = "Fabio Soares"

# Core engine
from backtest.core.engine import BacktestEngine

# Strategy base
from backtest.strategies.base import BaseStrategy

# Production models
from backtest.models.orders import TradingOrder, OrderDirection, OrderStatus
from backtest.models.financial_entities import (
    Asset,
    TradingPair,
    Broker,
    Account,
    TraderAgent,
)
from backtest.models.market_data import BarData, TimeFrame
from backtest.models.trading_rules import TradingRules, FeeType, Fee
from backtest.models.backtest_run import BacktestRun, AccountBalance, AccountTransaction

# Repository layer
from backtest.repositories.context import BacktestContext
from backtest.repositories.setup_helpers import (
    setup_example_configuration,
)

__all__ = [
    # Core
    "BacktestEngine",
    "BaseStrategy",
    # Models
    "TradingOrder",
    "OrderDirection",
    "OrderStatus",
    "Asset",
    "TradingPair",
    "Broker",
    "Account",
    "TraderAgent",
    "BarData",
    "TimeFrame",
    "TradingRules",
    "FeeType",
    "Fee",
    "BacktestRun",
    "AccountBalance",
    "AccountTransaction",
    # Repository & Configuration
    "BacktestContext",
    "setup_example_configuration",
    # Version
    "__version__",
]
