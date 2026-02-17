"""Repository for Balance entities."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from backtest.repositories.base import InMemoryRepository
from backtest.models.balance import Balance
from backtest.models.transaction import Transaction


class BalanceRepository(InMemoryRepository[Balance]):
    """
    Repository for Balance entities with balance reconciliation support.
    
    Provides methods to track balance over time and reconcile from transactions.
    """
    
    def save(self, entity: Balance) -> Balance:
        """Save a balance using balance_id as key."""
        self._storage[entity.balance_id] = entity
        return entity
    
    def get(self, entity_id: UUID) -> Optional[Balance]:
        """Get a balance by balance_id."""
        return self._storage.get(entity_id)
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete a balance by balance_id."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False
    
    def get_by_account(
        self,
        account_id: UUID,
        backtest_run_id: Optional[UUID] = None
    ) -> List[Balance]:
        """
        Get all balance snapshots for an account.
        
        Args:
            account_id: Account ID
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of balance snapshots, sorted by timestamp
        """
        balances = [
            b for b in self.get_all()
            if b.account_id == account_id
        ]
        
        if backtest_run_id is not None:
            balances = [
                b for b in balances
                if b.backtest_run_id == backtest_run_id
            ]
        
        return sorted(balances, key=lambda b: b.timestamp)
    
    def get_latest_balance(
        self,
        account_id: UUID,
        backtest_run_id: UUID
    ) -> Optional[Balance]:
        """
        Get the most recent balance for an account.
        
        Args:
            account_id: Account ID
            backtest_run_id: Backtest run ID
            
        Returns:
            Latest balance or None if no balances exist
        """
        balances = self.get_by_account(account_id, backtest_run_id)
        return balances[-1] if balances else None
    
    def get_balance_at_time(
        self,
        account_id: UUID,
        timestamp: datetime,
        backtest_run_id: UUID
    ) -> Optional[Balance]:
        """
        Get the balance at or before a specific time.
        
        Args:
            account_id: Account ID
            timestamp: Timestamp to query
            backtest_run_id: Backtest run ID
            
        Returns:
            Balance at or before the timestamp, or None if none exists
        """
        balances = [
            b for b in self.get_by_account(account_id, backtest_run_id)
            if b.timestamp <= timestamp
        ]
        
        return balances[-1] if balances else None
    
    def reconcile_balance(
        self,
        account_id: UUID,
        backtest_run_id: UUID,
        timestamp: datetime,
        transactions: List[Transaction],
        initial_balance: Optional[Balance] = None
    ) -> Balance:
        """
        Reconcile a new balance from transactions.
        
        This is the core method for balance reconciliation. It takes the last
        balance and applies all transactions to compute the new balance.
        
        Args:
            account_id: Account ID
            backtest_run_id: Backtest run ID
            timestamp: Timestamp for the new balance
            transactions: List of transactions to apply
            initial_balance: Starting balance (if None, starts from 0)
            
        Returns:
            New reconciled balance
        """
        if initial_balance is None:
            available = Decimal("0")
            unavailable = Decimal("0")
        else:
            available = initial_balance.available_balance
            unavailable = initial_balance.unavailable_balance
        
        # Apply each transaction
        for transaction in transactions:
            available += transaction.available_balance_change
            unavailable += transaction.unavailable_balance_change
        
        # Create and save new balance
        new_balance = Balance(
            account_id=account_id,
            backtest_run_id=backtest_run_id,
            timestamp=timestamp,
            available_balance=available,
            unavailable_balance=unavailable
        )
        
        return self.save(new_balance)
    
    def get_balance_history_df(
        self,
        account_id: UUID,
        backtest_run_id: UUID
    ):
        """
        Get balance history as a pandas DataFrame.
        
        Args:
            account_id: Account ID
            backtest_run_id: Backtest run ID
            
        Returns:
            DataFrame with columns: timestamp, available, unavailable, total
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for balance history DataFrame")
        
        balances = self.get_by_account(account_id, backtest_run_id)
        
        if not balances:
            return pd.DataFrame(columns=['timestamp', 'available', 'unavailable', 'total'])
        
        data = [
            {
                'timestamp': b.timestamp,
                'available': float(b.available_balance),
                'unavailable': float(b.unavailable_balance),
                'total': float(b.total_balance),
            }
            for b in balances
        ]
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def clear_run(self, backtest_run_id: UUID) -> int:
        """
        Clear all balances for a specific backtest run.
        
        Args:
            backtest_run_id: Backtest run ID
            
        Returns:
            Number of balances deleted
        """
        to_delete = [
            b.balance_id
            for b in self.get_all()
            if b.backtest_run_id == backtest_run_id
        ]
        
        for balance_id in to_delete:
            self.delete(balance_id)
        
        return len(to_delete)
