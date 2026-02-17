"""Tests for Balance model."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from backtest.models.balance import Balance


def test_balance_creation():
    """Test creating a basic balance."""
    account_id = uuid4()
    run_id = uuid4()
    
    balance = Balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=datetime.now(),
        available_balance=Decimal("95000"),
        unavailable_balance=Decimal("5000")
    )
    
    assert balance.account_id == account_id
    assert balance.backtest_run_id == run_id
    assert balance.available_balance == Decimal("95000")
    assert balance.unavailable_balance == Decimal("5000")


def test_balance_total_balance():
    """Test total balance calculation."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("80000"),
        unavailable_balance=Decimal("20000")
    )
    
    assert balance.total_balance == Decimal("100000")


def test_balance_utilization_rate():
    """Test utilization rate calculation."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("70000"),
        unavailable_balance=Decimal("30000")
    )
    
    assert balance.utilization_rate == Decimal("30")


def test_balance_zero_utilization():
    """Test utilization rate with no unavailable balance."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("100000"),
        unavailable_balance=Decimal("0")
    )
    
    assert balance.utilization_rate == Decimal("0")


def test_balance_full_utilization():
    """Test utilization rate with all balance unavailable."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("0"),
        unavailable_balance=Decimal("100000")
    )
    
    assert balance.utilization_rate == Decimal("100")


def test_balance_zero_total():
    """Test utilization rate with zero total balance."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("0"),
        unavailable_balance=Decimal("0")
    )
    
    assert balance.total_balance == Decimal("0")
    assert balance.utilization_rate == Decimal("0")


def test_balance_negative_available():
    """Test that negative available balance raises error."""
    with pytest.raises(ValueError, match="available_balance cannot be negative"):
        Balance(
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            timestamp=datetime.now(),
            available_balance=Decimal("-100"),
            unavailable_balance=Decimal("0")
        )


def test_balance_negative_unavailable():
    """Test that negative unavailable balance raises error."""
    with pytest.raises(ValueError, match="unavailable_balance cannot be negative"):
        Balance(
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            timestamp=datetime.now(),
            available_balance=Decimal("100"),
            unavailable_balance=Decimal("-50")
        )


def test_balance_immutability():
    """Test that Balance is immutable (frozen)."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("100000"),
        unavailable_balance=Decimal("0")
    )
    
    # Should not be able to modify fields
    with pytest.raises(Exception):
        balance.available_balance = Decimal("200000")


def test_balance_repr():
    """Test string representation."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("95000"),
        unavailable_balance=Decimal("5000")
    )
    
    repr_str = repr(balance)
    assert "Balance" in repr_str
    assert "100000" in repr_str  # total
    assert "95000" in repr_str   # available
    assert "5000" in repr_str    # unavailable


def test_balance_with_decimal_precision():
    """Test balance with high decimal precision."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("99999.99"),
        unavailable_balance=Decimal("0.01")
    )
    
    assert balance.total_balance == Decimal("100000.00")
    assert balance.utilization_rate == Decimal("0.00001")
