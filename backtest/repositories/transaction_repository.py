"""Repository for Transaction entities."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from backtest.repositories.base import InMemoryRepository
from backtest.models.transaction import Transaction, TransactionType


class TransactionRepository(InMemoryRepository[Transaction]):
    """
    Repository for Transaction entities with specialized queries.
    
    Provides methods to query transactions by account, backtest run,
    type, and time range for balance reconciliation.
    """
    
    def save(self, entity: Transaction) -> Transaction:
        """Save a transaction using transaction_id as key."""
        self._storage[entity.transaction_id] = entity
        return entity
    
    def get(self, entity_id: UUID) -> Optional[Transaction]:
        """Get a transaction by transaction_id."""
        return self._storage.get(entity_id)
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete a transaction by transaction_id."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False
    
    def get_by_account(
        self,
        account_id: UUID,
        backtest_run_id: Optional[UUID] = None
    ) -> List[Transaction]:
        """
        Get all transactions for an account.
        
        Args:
            account_id: Account ID
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of transactions for the account
        """
        transactions = [
            t for t in self.get_all()
            if t.account_id == account_id
        ]
        
        if backtest_run_id is not None:
            transactions = [
                t for t in transactions
                if t.backtest_run_id == backtest_run_id
            ]
        
        return sorted(transactions, key=lambda t: t.timestamp)
    
    def get_by_order(self, order_id: UUID) -> List[Transaction]:
        """
        Get all transactions related to a specific order.
        
        Args:
            order_id: Order ID
            
        Returns:
            List of transactions for the order
        """
        return sorted(
            [t for t in self.get_all() if t.order_id == order_id],
            key=lambda t: t.timestamp
        )
    
    def get_by_type(
        self,
        transaction_type: TransactionType,
        backtest_run_id: Optional[UUID] = None
    ) -> List[Transaction]:
        """
        Get all transactions of a specific type.
        
        Args:
            transaction_type: Type of transaction
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of transactions of the specified type
        """
        transactions = [
            t for t in self.get_all()
            if t.transaction_type == transaction_type
        ]
        
        if backtest_run_id is not None:
            transactions = [
                t for t in transactions
                if t.backtest_run_id == backtest_run_id
            ]
        
        return sorted(transactions, key=lambda t: t.timestamp)
    
    def get_by_time_range(
        self,
        account_id: UUID,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Transaction]:
        """
        Get transactions within a time range for an account.
        
        Args:
            account_id: Account ID
            start_time: Start of time range (inclusive)
            end_time: End of time range (inclusive), None for all after start
            
        Returns:
            List of transactions in the time range
        """
        transactions = [
            t for t in self.get_all()
            if t.account_id == account_id and t.timestamp >= start_time
        ]
        
        if end_time is not None:
            transactions = [
                t for t in transactions
                if t.timestamp <= end_time
            ]
        
        return sorted(transactions, key=lambda t: t.timestamp)
    
    def get_since_timestamp(
        self,
        account_id: UUID,
        since_timestamp: datetime
    ) -> List[Transaction]:
        """
        Get all transactions after a specific timestamp.
        
        Useful for balance reconciliation.
        
        Args:
            account_id: Account ID
            since_timestamp: Timestamp (exclusive)
            
        Returns:
            List of transactions after the timestamp
        """
        return sorted(
            [
                t for t in self.get_all()
                if t.account_id == account_id and t.timestamp > since_timestamp
            ],
            key=lambda t: t.timestamp
        )
    
    def clear_run(self, backtest_run_id: UUID) -> int:
        """
        Clear all transactions for a specific backtest run.
        
        Args:
            backtest_run_id: Backtest run ID
            
        Returns:
            Number of transactions deleted
        """
        to_delete = [
            t.transaction_id
            for t in self.get_all()
            if t.backtest_run_id == backtest_run_id
        ]
        
        for transaction_id in to_delete:
            self.delete(transaction_id)
        
        return len(to_delete)
