"""Tests for BalanceRepository."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from backtest.repositories.balance_repository import BalanceRepository
from backtest.models.balance import Balance
from backtest.models.transaction import Transaction, TransactionType


@pytest.fixture
def repo():
    """Create a balance repository."""
    return BalanceRepository()


def test_repository_save_and_get(repo):
    """Test saving and retrieving balances."""
    balance = Balance(
        account_id=uuid4(),
        backtest_run_id=uuid4(),
        timestamp=datetime.now(),
        available_balance=Decimal("95000"),
        unavailable_balance=Decimal("5000")
    )
    
    saved = repo.save(balance)
    assert saved == balance
    
    retrieved = repo.get(balance.balance_id)
    assert retrieved == balance


def test_get_by_account(repo):
    """Test getting balances by account."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    balances = []
    for i in range(3):
        balance = Balance(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(minutes=i),
            available_balance=Decimal(str(100000 - i * 1000)),
            unavailable_balance=Decimal(str(i * 1000))
        )
        repo.save(balance)
        balances.append(balance)
    
    # Add balance for different account
    other_balance = Balance(
        account_id=uuid4(),
        backtest_run_id=run_id,
        timestamp=base_time,
        available_balance=Decimal("50000"),
        unavailable_balance=Decimal("0")
    )
    repo.save(other_balance)
    
    account_balances = repo.get_by_account(account_id)
    assert len(account_balances) == 3
    assert all(b.account_id == account_id for b in account_balances)


def test_get_latest_balance(repo):
    """Test getting the latest balance."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    for i in range(3):
        balance = Balance(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(minutes=i),
            available_balance=Decimal(str(100000 + i * 1000)),
            unavailable_balance=Decimal("0")
        )
        repo.save(balance)
    
    latest = repo.get_latest_balance(account_id, run_id)
    assert latest is not None
    assert latest.available_balance == Decimal("102000")


def test_get_balance_at_time(repo):
    """Test getting balance at a specific time."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    for i in range(5):
        balance = Balance(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(minutes=i),
            available_balance=Decimal(str(100000 + i * 1000)),
            unavailable_balance=Decimal("0")
        )
        repo.save(balance)
    
    # Query at minute 2.5 should return balance from minute 2
    query_time = base_time + timedelta(minutes=2, seconds=30)
    balance = repo.get_balance_at_time(account_id, query_time, run_id)
    
    assert balance is not None
    assert balance.available_balance == Decimal("102000")


def test_reconcile_balance(repo):
    """Test balance reconciliation from transactions."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    # Initial balance
    initial = Balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=base_time,
        available_balance=Decimal("100000"),
        unavailable_balance=Decimal("0")
    )
    repo.save(initial)
    
    # Create transactions
    transactions = [
        Transaction(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(seconds=1),
            description="Reserve margin",
            available_balance_change=Decimal("-1000"),
            unavailable_balance_change=Decimal("1000"),
            transaction_type=TransactionType.RESERVE_MARGIN
        ),
        Transaction(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time + timedelta(seconds=2),
            description="Fee",
            available_balance_change=Decimal("-10"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.FEE_FILL
        ),
    ]
    
    # Reconcile new balance
    new_balance = repo.reconcile_balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=base_time + timedelta(minutes=1),
        transactions=transactions,
        initial_balance=initial
    )
    
    assert new_balance.available_balance == Decimal("98990")
    assert new_balance.unavailable_balance == Decimal("1000")
    assert new_balance.total_balance == Decimal("99990")


def test_reconcile_balance_from_zero(repo):
    """Test reconciling balance starting from zero."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    transactions = [
        Transaction(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=base_time,
            description="Initial deposit",
            available_balance_change=Decimal("100000"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.ADJUSTMENT
        ),
    ]
    
    balance = repo.reconcile_balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=base_time,
        transactions=transactions,
        initial_balance=None
    )
    
    assert balance.available_balance == Decimal("100000")
    assert balance.unavailable_balance == Decimal("0")


def test_clear_run(repo):
    """Test clearing balances for a run."""
    run_id1 = uuid4()
    run_id2 = uuid4()
    account_id = uuid4()
    base_time = datetime.now()
    
    # Create balances for two runs
    for i in range(3):
        repo.save(Balance(
            account_id=account_id,
            backtest_run_id=run_id1,
            timestamp=base_time + timedelta(minutes=i),
            available_balance=Decimal("100000"),
            unavailable_balance=Decimal("0")
        ))
    
    for i in range(2):
        repo.save(Balance(
            account_id=account_id,
            backtest_run_id=run_id2,
            timestamp=base_time + timedelta(minutes=i),
            available_balance=Decimal("100000"),
            unavailable_balance=Decimal("0")
        ))
    
    assert len(repo.get_all()) == 5
    
    deleted = repo.clear_run(run_id1)
    assert deleted == 3
    assert len(repo.get_all()) == 2


def test_balances_sorted_by_time(repo):
    """Test that balances are returned sorted by timestamp."""
    account_id = uuid4()
    run_id = uuid4()
    base_time = datetime.now()
    
    # Save in random order
    timestamps = [
        base_time + timedelta(minutes=2),
        base_time,
        base_time + timedelta(minutes=1),
    ]
    
    for ts in timestamps:
        repo.save(Balance(
            account_id=account_id,
            backtest_run_id=run_id,
            timestamp=ts,
            available_balance=Decimal("100000"),
            unavailable_balance=Decimal("0")
        ))
    
    account_balances = repo.get_by_account(account_id)
    
    # Should be sorted by timestamp
    for i in range(len(account_balances) - 1):
        assert account_balances[i].timestamp <= account_balances[i + 1].timestamp
