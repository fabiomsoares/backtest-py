"""Tests for BaseStrategy."""

import pytest
from decimal import Decimal
from typing import List

from backtest import BaseStrategy, BacktestContext, TradingOrder, OrderDirection
from backtest.models.market_data import BarData


class TestStrategy(BaseStrategy):
    """Concrete event-driven strategy for testing."""

    def __init__(self, name="TestStrategy"):
        super().__init__(name=name)
        self.on_start_called = False
        self.on_end_called = False
        self.bars_processed = 0

    def on_start(self, context: BacktestContext) -> None:
        self.on_start_called = True
        self.bars_processed = 0

    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        self.bars_processed += 1
        return []

    def on_end(self, context: BacktestContext) -> None:
        self.on_end_called = True


def test_base_strategy_initialization():
    """Test BaseStrategy initialization."""
    strategy = TestStrategy(name="MyTestStrategy")
    assert strategy.name == "MyTestStrategy"


def test_base_strategy_default_name():
    """Test default strategy name."""
    strategy = TestStrategy()
    assert strategy.name == "TestStrategy"


def test_strategy_lifecycle_hooks(backtest_context):
    """Test that lifecycle hooks are called."""
    strategy = TestStrategy()

    # Verify initial state
    assert not strategy.on_start_called
    assert not strategy.on_end_called
    assert strategy.bars_processed == 0

    # Call lifecycle methods
    strategy.on_start(backtest_context)
    assert strategy.on_start_called
    assert strategy.bars_processed == 0

    strategy.on_end(backtest_context)
    assert strategy.on_end_called


def test_strategy_on_bar_processing(backtest_context, simple_price_data):
    """Test that on_bar processes bars correctly."""
    strategy = TestStrategy()
    strategy.on_start(backtest_context)

    # Create a sample bar
    from backtest.models.market_data import TimeFrame, TimeUnit

    bar = BarData(
        symbol="TEST",
        timeframe=TimeFrame(unit=TimeUnit.DAY, multiplier=1, offset=0),
        timestamp=simple_price_data.index[0].to_pydatetime(),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("1000000"),
    )

    orders = strategy.on_bar(bar, backtest_context)

    assert strategy.bars_processed == 1
    assert isinstance(orders, list)
    assert len(orders) == 0  # TestStrategy returns empty list


def test_on_bar_is_abstract():
    """Test that on_bar must be implemented."""
    # Cannot instantiate BaseStrategy directly
    with pytest.raises(TypeError):
        BaseStrategy(name="Test")


def test_strategy_repr():
    """Test strategy string representation."""
    strategy = TestStrategy(name="MyTest")
    repr_str = repr(strategy)
    assert "TestStrategy" in repr_str or "MyTest" in repr_str


def test_strategy_helper_methods(backtest_context):
    """Test strategy helper methods."""
    strategy = TestStrategy()

    # Test get_account_balance
    accounts = backtest_context.accounts.get_all()
    if accounts:
        account_id = str(accounts[0].id)
        balance = strategy.get_account_balance(backtest_context, account_id)
        assert balance is not None
        assert isinstance(balance, Decimal)


def test_strategy_create_market_order(backtest_context):
    """Test creating market orders."""
    strategy = TestStrategy()

    accounts = backtest_context.accounts.get_all()
    if accounts:
        account_id = str(accounts[0].id)

        order = strategy.create_market_order(
            trading_pair_code="BTCUSDT",
            direction=OrderDirection.LONG,
            volume=Decimal("1.0"),
            current_price=Decimal("50000"),
            context=backtest_context,
            account_id=account_id,
        )

        assert order is not None
        assert isinstance(order, TradingOrder)
        assert order.direction == OrderDirection.LONG
        assert order.volume == Decimal("1.0")


def test_strategy_with_stop_loss_take_profit(backtest_context):
    """Test creating orders with stop-loss and take-profit."""
    strategy = TestStrategy()

    accounts = backtest_context.accounts.get_all()
    if accounts:
        account_id = str(accounts[0].id)

        order = strategy.create_market_order(
            trading_pair_code="BTCUSDT",
            direction=OrderDirection.LONG,
            volume=Decimal("1.0"),
            current_price=Decimal("50000"),
            context=backtest_context,
            account_id=account_id,
            stop_loss=Decimal("48000"),
            take_profit=Decimal("55000"),
        )

        assert order.stop_loss == Decimal("48000")
        assert order.take_profit == Decimal("55000")
