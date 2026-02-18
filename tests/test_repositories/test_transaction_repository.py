"""Tests for TransactionRepository."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from backtest.repositories.transaction_repository import TransactionRepository
from backtest.models.transaction import Transaction, TransactionType


@pytest.fixture
def repo():
    """Create a transaction repository."""
    return TransactionRepository()


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    transactions = [
        Transaction(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time,
            description="Reserve margin",
            available_balance_change=Decimal("-1000"),
            unavailable_balance_change=Decimal("1000"),
            transaction_type=TransactionType.RESERVE_MARGIN
        ),
        Transaction(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(minutes=1),
            description="Fill fee",
            available_balance_change=Decimal("-10"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.FEE_FILL
        ),
        Transaction(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(minutes=2),
            description="Close PnL",
            available_balance_change=Decimal("500"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.CLOSE_PNL
        ),
    ]
    
    return account_id, run_id, transactions


def test_repository_save_and_get(repo):
    """Test saving and retrieving transactions."""
    transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        description="Test",
        available_balance_change=Decimal("100"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.ADJUSTMENT
    )
    
    saved = repo.save(transaction)
    assert saved == transaction
    
    retrieved = repo.get(transaction.transaction_id)
    assert retrieved == transaction


def test_get_by_account(repo, sample_transactions):
    """Test getting transactions by account."""
    account_id, run_id, transactions = sample_transactions
    
    for t in transactions:
        repo.save(t)
    
    # Add transaction for different account
    other_transaction = Transaction(
        account_id=uuid4(),
        backtest_run_id=run_id,
        timestamp=datetime.now(),
        description="Other account",
        available_balance_change=Decimal("0"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.ADJUSTMENT
    )
    repo.save(other_transaction)
    
    account_transactions = repo.get_by_account(account_id)
    assert len(account_transactions) == 3
    assert all(t.account_id == account_id for t in account_transactions)


def test_get_by_order(repo):
    """Test getting transactions by order."""
    order_id = uuid4()
    account_id = uuid4()
    run_id = uuid4()
    
    t1 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=datetime.now(),
        description="Reserve for order",
        available_balance_change=Decimal("-100"),
        unavailable_balance_change=Decimal("100"),
        transaction_type=TransactionType.RESERVE_MARGIN,
        order_id=order_id
    )
    
    t2 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=datetime.now() + timedelta(seconds=1),
        description="Fill order",
        available_balance_change=Decimal("0"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.FILL_BUY,
        order_id=order_id
    )
    
    repo.save(t1)
    repo.save(t2)
    
    order_transactions = repo.get_by_order(order_id)
    assert len(order_transactions) == 2
    assert all(t.order_id == order_id for t in order_transactions)


def test_get_by_type(repo, sample_transactions):
    """Test getting transactions by type."""
    account_id, run_id, transactions = sample_transactions
    
    for t in transactions:
        repo.save(t)
    
    reserve_transactions = repo.get_by_type(TransactionType.RESERVE_MARGIN)
    assert len(reserve_transactions) == 1
    assert reserve_transactions[0].transaction_type == TransactionType.RESERVE_MARGIN


def test_get_by_time_range(repo, sample_transactions):
    """Test getting transactions by time range."""
    account_id, run_id, transactions = sample_transactions
    base_time = transactions[0].timestamp
    
    for t in transactions:
        repo.save(t)
    
    # Get transactions in middle of range
    start_time = base_time
    end_time = base_time + timedelta(minutes=1, seconds=30)
    
    range_transactions = repo.get_by_time_range(account_id, start_time, end_time)
    assert len(range_transactions) == 2


def test_get_since_timestamp(repo, sample_transactions):
    """Test getting transactions since a timestamp."""
    account_id, run_id, transactions = sample_transactions
    base_time = transactions[0].timestamp
    
    for t in transactions:
        repo.save(t)
    
    # Get transactions after first one
    since_time = base_time
    
    since_transactions = repo.get_since_timestamp(account_id, since_time)
    assert len(since_transactions) == 2  # Should not include first one


def test_clear_run(repo):
    """Test clearing transactions for a run."""
    run_id1 = uuid4()
    run_id2 = uuid4()
    account_id = uuid4()
    
    # Create transactions for two runs
    for i in range(3):
        repo.save(Transaction(
            account_id=account_id,
            backtest_run_id=run_id1,
            timestamp=datetime.now(),
            description=f"Run 1 transaction {i}",
            available_balance_change=Decimal("0"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.ADJUSTMENT
        ))
    
    for i in range(2):
        repo.save(Transaction(
            account_id=account_id,
            backtest_run_id=run_id2,
            timestamp=datetime.now(),
            description=f"Run 2 transaction {i}",
            available_balance_change=Decimal("0"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.ADJUSTMENT
        ))
    
    assert len(repo.get_all()) == 5
    
    deleted = repo.clear_run(run_id1)
    assert deleted == 3
    assert len(repo.get_all()) == 2


def test_transactions_sorted_by_time(repo, sample_transactions):
    """Test that transactions are returned sorted by timestamp."""
    account_id, run_id, transactions = sample_transactions
    
    # Save in random order
    repo.save(transactions[2])
    repo.save(transactions[0])
    repo.save(transactions[1])
    
    account_transactions = repo.get_by_account(account_id)
    
    # Should be sorted by timestamp
    for i in range(len(account_transactions) - 1):
        assert account_transactions[i].timestamp <= account_transactions[i + 1].timestamp
