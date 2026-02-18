"""
Example demonstrating the new transaction and balance system.

This example shows how:
1. Transactions track all balance changes
2. Balances are reconciled from transactions
3. Available vs unavailable balance tracking works
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from backtest.models.transaction import Transaction, TransactionType
from backtest.models.balance import Balance
from backtest.repositories.transaction_repository import TransactionRepository
from backtest.repositories.balance_repository import BalanceRepository


def main():
    """Demonstrate transaction and balance system."""
    
    # Setup
    account_id = uuid4()
    run_id = uuid4()
    transaction_repo = TransactionRepository()
    balance_repo = BalanceRepository()
    
    print("=" * 70)
    print("Transaction and Balance System Example")
    print("=" * 70)
    
    # Initial balance
    start_time = datetime.now()
    initial_balance = Balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time,
        available_balance=Decimal("100000"),
        unavailable_balance=Decimal("0")
    )
    balance_repo.save(initial_balance)
    
    print(f"\nInitial Balance: {initial_balance}")
    print(f"  Available: ${initial_balance.available_balance:,.2f}")
    print(f"  Unavailable: ${initial_balance.unavailable_balance:,.2f}")
    print(f"  Total: ${initial_balance.total_balance:,.2f}")
    
    # Simulate creating an order (reserve margin)
    print("\n" + "-" * 70)
    print("Action: Create order - reserve $10,000 margin")
    print("-" * 70)
    
    t1 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=1),
        description="Reserve margin for new order",
        available_balance_change=Decimal("-10000"),
        unavailable_balance_change=Decimal("10000"),
        transaction_type=TransactionType.RESERVE_MARGIN
    )
    transaction_repo.save(t1)
    print(f"Transaction: {t1.description}")
    print(f"  Available change: ${t1.available_balance_change:,.2f}")
    print(f"  Unavailable change: ${t1.unavailable_balance_change:,.2f}")
    
    # Reconcile balance
    transactions = transaction_repo.get_since_timestamp(account_id, start_time)
    balance1 = balance_repo.reconcile_balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=1),
        transactions=transactions,
        initial_balance=initial_balance
    )
    print(f"\nNew Balance: {balance1}")
    print(f"  Available: ${balance1.available_balance:,.2f}")
    print(f"  Unavailable: ${balance1.unavailable_balance:,.2f}")
    print(f"  Utilization: {balance1.utilization_rate:.1f}%")
    
    # Simulate order fill (pay fee)
    print("\n" + "-" * 70)
    print("Action: Order filled - pay $50 fee")
    print("-" * 70)
    
    t2 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=2),
        description="Order fill fee",
        available_balance_change=Decimal("-50"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.FEE_FILL
    )
    transaction_repo.save(t2)
    print(f"Transaction: {t2.description}")
    print(f"  Fee: ${abs(t2.available_balance_change):,.2f}")
    
    # Reconcile balance
    transactions = transaction_repo.get_since_timestamp(
        account_id, 
        balance1.timestamp
    )
    balance2 = balance_repo.reconcile_balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=2),
        transactions=transactions,
        initial_balance=balance1
    )
    print(f"\nNew Balance: {balance2}")
    print(f"  Available: ${balance2.available_balance:,.2f}")
    print(f"  Unavailable: ${balance2.unavailable_balance:,.2f}")
    print(f"  Total: ${balance2.total_balance:,.2f}")
    
    # Simulate closing position with profit
    print("\n" + "-" * 70)
    print("Action: Close position - realize $1,500 profit")
    print("-" * 70)
    
    t3 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=3),
        description="Return margin from closed position",
        available_balance_change=Decimal("10000"),
        unavailable_balance_change=Decimal("-10000"),
        transaction_type=TransactionType.RETURN_MARGIN
    )
    transaction_repo.save(t3)
    
    t4 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=3),
        description="Realized profit from closed position",
        available_balance_change=Decimal("1500"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.CLOSE_PNL
    )
    transaction_repo.save(t4)
    
    t5 = Transaction(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=3),
        description="Close fee",
        available_balance_change=Decimal("-50"),
        unavailable_balance_change=Decimal("0"),
        transaction_type=TransactionType.FEE_CLOSE
    )
    transaction_repo.save(t5)
    
    print(f"Transactions:")
    print(f"  1. Return margin: +${abs(t3.available_balance_change):,.2f} to available")
    print(f"  2. Profit: ${t4.available_balance_change:,.2f}")
    print(f"  3. Close fee: ${t5.available_balance_change:,.2f}")
    
    # Reconcile final balance
    transactions = transaction_repo.get_since_timestamp(
        account_id, 
        balance2.timestamp
    )
    balance3 = balance_repo.reconcile_balance(
        account_id=account_id,
        backtest_run_id=run_id,
        timestamp=start_time + timedelta(seconds=3),
        transactions=transactions,
        initial_balance=balance2
    )
    print(f"\nFinal Balance: {balance3}")
    print(f"  Available: ${balance3.available_balance:,.2f}")
    print(f"  Unavailable: ${balance3.unavailable_balance:,.2f}")
    print(f"  Total: ${balance3.total_balance:,.2f}")
    print(f"  Net P&L: ${balance3.total_balance - initial_balance.total_balance:,.2f}")
    
    # Show all transactions
    print("\n" + "=" * 70)
    print("All Transactions Summary")
    print("=" * 70)
    
    all_transactions = transaction_repo.get_by_account(account_id, run_id)
    for i, t in enumerate(all_transactions, 1):
        print(f"\n{i}. {t.transaction_type.name}")
        print(f"   {t.description}")
        print(f"   Available: {t.available_balance_change:+,.2f}, "
              f"Unavailable: {t.unavailable_balance_change:+,.2f}")
    
    # Show balance history
    print("\n" + "=" * 70)
    print("Balance History")
    print("=" * 70)
    
    all_balances = balance_repo.get_by_account(account_id, run_id)
    for i, b in enumerate(all_balances):
        print(f"\n{i}. Time: {b.timestamp.strftime('%H:%M:%S')}")
        print(f"   Available: ${b.available_balance:,.2f}, "
              f"Unavailable: ${b.unavailable_balance:,.2f}, "
              f"Total: ${b.total_balance:,.2f}")
    
    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
