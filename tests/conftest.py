"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

from backtest import BacktestContext, BaseStrategy, TradingOrder, OrderDirection
from backtest import setup_example_configuration
from backtest.models.market_data import BarData
from typing import List


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
def backtest_context():
    """Create a BacktestContext with example configuration."""
    context = BacktestContext()
    setup_example_configuration(context)
    return context


@pytest.fixture
def mock_strategy():
    """Create a mock event-driven strategy for testing."""

    class MockStrategy(BaseStrategy):
        """Simple test strategy that buys on bar 1 and sells on bar 5."""

        def __init__(self):
            super().__init__(name="MockStrategy")
            self.bar_count = 0
            self.position_open = False

        def on_start(self, context: BacktestContext) -> None:
            self.bar_count = 0
            self.position_open = False

        def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
            self.bar_count += 1
            orders = []

            # Buy on bar 1
            if self.bar_count == 1 and not self.position_open:
                accounts = context.accounts.get_all()
                if accounts:
                    account_id = str(accounts[0].id)
                    balance = self.get_account_balance(context, account_id)
                    volume = (balance * Decimal("0.5")) / bar.close

                    order = self.create_market_order(
                        trading_pair_code=bar.symbol,
                        direction=OrderDirection.LONG,
                        volume=volume,
                        current_price=bar.close,
                        context=context,
                        account_id=account_id,
                    )
                    orders.append(order)
                    self.position_open = True

            # Sell on bar 5
            elif self.bar_count == 5 and self.position_open:
                accounts = context.accounts.get_all()
                if accounts:
                    agent_id = accounts[0].agent.id
                    active_orders = context.orders.get_active_orders(agent_id)
                    long_orders = [o for o in active_orders if o.direction == OrderDirection.LONG]

                    if long_orders:
                        total_volume = sum(o.volume for o in long_orders)
                        account_id = str(accounts[0].id)

                        order = self.create_market_order(
                            trading_pair_code=bar.symbol,
                            direction=OrderDirection.SHORT,
                            volume=total_volume,
                            current_price=bar.close,
                            context=context,
                            account_id=account_id,
                        )
                        orders.append(order)
                        self.position_open = False

            return orders

        def on_end(self, context: BacktestContext) -> None:
            pass

    return MockStrategy()


@pytest.fixture
def initial_capital():
    """Default initial capital for tests."""
    return Decimal("100000.0")


@pytest.fixture
def commission():
    """Default commission for tests."""
    return Decimal("0.001")
