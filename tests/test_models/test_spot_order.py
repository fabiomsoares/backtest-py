"""Tests for SpotOrder model."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from backtest.models.spot_order import SpotOrder
from backtest.models.orders import OrderDirection, OrderStatus


def test_spot_order_creation():
    """Test creating a basic spot order."""
    broker_id = uuid4()
    agent_id = uuid4()
    account_id = uuid4()
    run_id = uuid4()
    
    order = SpotOrder(
        broker_id=broker_id,
        trading_pair_code="BTCUSD",
        agent_id=agent_id,
        account_id=account_id,
        backtest_run_id=run_id,
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1.5")
    )
    
    assert order.broker_id == broker_id
    assert order.trading_pair_code == "BTCUSD"
    assert order.direction == OrderDirection.LONG
    assert order.status == OrderStatus.PENDING
    assert order.volume == Decimal("1.5")
    assert order.is_market_order
    assert not order.is_limit_order


def test_spot_order_limit_order():
    """Test creating a limit order."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="ETHUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=2,
        direction=OrderDirection.SHORT,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("10"),
        limit_price=Decimal("2000")
    )
    
    assert order.limit_price == Decimal("2000")
    assert order.is_limit_order
    assert not order.is_market_order


def test_spot_order_root_id_auto_set():
    """Test that root_id is automatically set to id for original orders."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1")
    )
    
    assert order.root_id == order.id
    assert order.parent_id is None


def test_spot_order_invalid_empty_pair():
    """Test that empty trading pair raises error."""
    with pytest.raises(ValueError, match="trading_pair_code cannot be empty"):
        SpotOrder(
            broker_id=uuid4(),
            trading_pair_code="",
            agent_id=uuid4(),
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            order_number=1,
            direction=OrderDirection.LONG,
            status=OrderStatus.PENDING,
            create_timestamp=datetime.now(),
            volume=Decimal("1")
        )


def test_spot_order_invalid_volume():
    """Test that invalid volume raises error."""
    with pytest.raises(ValueError, match="volume must be positive"):
        SpotOrder(
            broker_id=uuid4(),
            trading_pair_code="BTCUSD",
            agent_id=uuid4(),
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            order_number=1,
            direction=OrderDirection.LONG,
            status=OrderStatus.PENDING,
            create_timestamp=datetime.now(),
            volume=Decimal("0")
        )


def test_spot_order_invalid_limit_price():
    """Test that invalid limit price raises error."""
    with pytest.raises(ValueError, match="limit_price must be positive"):
        SpotOrder(
            broker_id=uuid4(),
            trading_pair_code="BTCUSD",
            agent_id=uuid4(),
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            order_number=1,
            direction=OrderDirection.LONG,
            status=OrderStatus.PENDING,
            create_timestamp=datetime.now(),
            volume=Decimal("1"),
            limit_price=Decimal("0")
        )


def test_spot_order_properties():
    """Test order status properties."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1")
    )
    
    assert order.is_pending
    assert not order.is_filled
    assert not order.is_cancelled
    assert order.is_active


def test_spot_order_filled_copy():
    """Test creating a filled copy of an order."""
    original = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("2")
    )
    
    fill_time = datetime.now()
    filled = original.create_filled_copy(
        fill_timestamp=fill_time,
        fill_price=Decimal("50000"),
        fill_volume=Decimal("2"),
        fee_fill=Decimal("10")
    )
    
    assert filled.id == original.id
    assert filled.status == OrderStatus.FILLED
    assert filled.fill_timestamp == fill_time
    assert filled.fill_price == Decimal("50000")
    assert filled.fill_volume == Decimal("2")
    assert filled.fee_fill == Decimal("10")


def test_spot_order_partial_fill():
    """Test partial fill."""
    original = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("10")
    )
    
    filled = original.create_filled_copy(
        fill_timestamp=datetime.now(),
        fill_price=Decimal("50000"),
        fill_volume=Decimal("5")
    )
    
    assert filled.fill_volume == Decimal("5")
    assert filled.remaining_volume == Decimal("5")


def test_spot_order_cancelled_copy():
    """Test creating a cancelled copy of an order."""
    original = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("2")
    )
    
    cancel_time = datetime.now()
    cancelled = original.create_cancelled_copy(
        cancel_timestamp=cancel_time,
        cancel_volume=Decimal("2"),
        fee_cancel=Decimal("1")
    )
    
    assert cancelled.id == original.id
    assert cancelled.status == OrderStatus.CANCELLED
    assert cancelled.cancel_timestamp == cancel_time
    assert cancelled.cancel_volume == Decimal("2")
    assert cancelled.fee_cancel == Decimal("1")


def test_spot_order_total_fees():
    """Test total fees calculation."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1"),
        fee_create=Decimal("5"),
        fee_fill=Decimal("10"),
        fee_cancel=Decimal("2")
    )
    
    assert order.total_fees == Decimal("17")


def test_spot_order_remaining_volume():
    """Test remaining volume calculation."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("10"),
        fill_volume=Decimal("6"),
        cancel_volume=Decimal("2")
    )
    
    assert order.remaining_volume == Decimal("2")


def test_spot_order_immutability():
    """Test that SpotOrder is immutable (frozen)."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1")
    )
    
    # Should not be able to modify fields
    with pytest.raises(Exception):
        order.volume = Decimal("2")


def test_spot_order_repr():
    """Test string representation."""
    order = SpotOrder(
        broker_id=uuid4(),
        trading_pair_code="BTCUSD",
        agent_id=uuid4(),
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        order_number=42,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1.5"),
        limit_price=Decimal("50000")
    )
    
    repr_str = repr(order)
    assert "SpotOrder" in repr_str
    assert "#42" in repr_str
    assert "LONG" in repr_str
