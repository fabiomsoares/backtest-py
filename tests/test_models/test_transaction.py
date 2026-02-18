"""Tests for Transaction model."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from backtest.models.transaction import Transaction, TransactionType


def test_transaction_creation():
    """Test creating a basic transaction."""
    account_id = uuid4()
    run_id = uuid4()
    order_id = uuid4()
    
    transaction = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=datetime.now(),
        description="Test transaction",
        available_balance_change=Decimal("100"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.CLOSE_PNL,
        order_id=order_id
    )
    
    assert transaction.account_id == account_id
    assert transaction.backtest_run_id == run_id
    assert transaction.order_id == order_id
    assert transaction.available_balance_change == Decimal("100")
    assert transaction.unavailable_balance_change == Decimal("0")
    assert transaction.transaction_type == TransactionType.CLOSE_PNL


def test_transaction_reserve_margin():
    """Test reserve margin transaction."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Reserve margin for order",
        available_balance_change=Decimal("-1000"),
        unavailable_balance_change=Decimal("1000"),
        transaction_type=TransactionType.RESERVE_MARGIN
    )
    
    assert transaction.available_balance_change == Decimal("-1000")
    assert transaction.unavailable_balance_change == Decimal("1000")
    assert transaction.total_balance_change == Decimal("0")


def test_transaction_return_margin():
    """Test return margin transaction."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Return margin from cancelled order",
        available_balance_change=Decimal("1000"),
        unavailable_balance_change=Decimal("-1000"),
        transaction_type=TransactionType.RETURN_MARGIN
    )
    
    assert transaction.available_balance_change == Decimal("1000")
    assert transaction.unavailable_balance_change == Decimal("-1000")
    assert transaction.total_balance_change == Decimal("0")


def test_transaction_fee():
    """Test fee transaction."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Fill fee",
        available_balance_change=Decimal("-10"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.FEE_FILL
    )
    
    assert transaction.available_balance_change == Decimal("-10")
    assert transaction.total_balance_change == Decimal("-10")


def test_transaction_pnl():
    """Test PnL transaction."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Realized profit",
        available_balance_change=Decimal("500"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.CLOSE_PNL
    )
    
    assert transaction.available_balance_change == Decimal("500")
    assert transaction.total_balance_change == Decimal("500")


def test_transaction_empty_description():
    """Test that empty description raises error."""
    with pytest.raises(ValueError, match="description cannot be empty"):
        Transaction(
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            timestamp=datetime.now(),
            description="",
            available_balance_change=Decimal("0"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.ADJUSTMENT
        )


def test_transaction_total_balance_change():
    """Test total balance change calculation."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Test",
        available_balance_change=Decimal("50"),
        unavailable_balance_change=Decimal("30"),
        transaction_type=TransactionType.ADJUSTMENT
    )
    
    assert transaction.total_balance_change == Decimal("80")


def test_transaction_negative_changes():
    """Test transaction with negative changes."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Negative test",
        available_balance_change=Decimal("-100"),
        unavailable_balance_change=Decimal("-50"),
        transaction_type=TransactionType.FEE_OVERNIGHT
    )
    
    assert transaction.total_balance_change == Decimal("-150")


def test_transaction_immutability():
    """Test that Transaction is immutable (frozen)."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Test immutability",
        available_balance_change=Decimal("100"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.ADJUSTMENT
    )
    
    # Should not be able to modify fields
    with pytest.raises(Exception):  # dataclass frozen raises FrozenInstanceError or AttributeError
        transaction.available_balance_change = Decimal("200")


def test_transaction_repr():
    """Test transaction string representation."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Test repr with a very long description that should be truncated",
        available_balance_change=Decimal("100"),
        unavailable_balance_change=Decimal("50"),
        transaction_type=TransactionType.RESERVE_MARGIN
    )
    
    repr_str = repr(transaction)
    assert "Transaction" in repr_str
    assert "RESERVE_MARGIN" in repr_str
    assert "100" in repr_str


def test_all_transaction_types():
    """Test that all transaction types can be created."""
    for trans_type in TransactionType:
        transaction = Transaction(
            account_id=uuid4(),
            backtest_run_id=uuid4(),
            timestamp=datetime.now(),
            description=f"Test {trans_type.name}",
            available_balance_change=Decimal("0"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=trans_type
        )
        assert transaction.transaction_type == trans_type
