"""Repositories for orders and order history."""

from typing import List, Optional
from uuid import UUID

from backtest.models import TradingOrder, TradingOrderHistory, OrderStatus
from backtest.repositories.base import InMemoryRepository


class OrderRepository(InMemoryRepository[TradingOrder]):
    """Repository for TradingOrder entities with various lookups."""
    
    def get_by_run_id(self, run_id: UUID) -> List[TradingOrder]:
        """
        Get all orders for a backtest run.
        
        Args:
            run_id: UUID of the backtest run
            
        Returns:
            List of orders for the run
        """
        return [order for order in self.get_all() if order.backtest_run_id == run_id]
    
    def get_active_orders(self, agent_id: UUID) -> List[TradingOrder]:
        """
        Get all active orders (pending or filled) for an agent.
        
        Args:
            agent_id: UUID of the trading agent
            
        Returns:
            List of active orders
        """
        return [
            order for order in self.get_all()
            if order.agent_id == agent_id and order.is_active
        ]
    
    def get_by_agent(self, agent_id: UUID) -> List[TradingOrder]:
        """
        Get all orders for an agent.
        
        Args:
            agent_id: UUID of the trading agent
            
        Returns:
            List of orders for the agent
        """
        return [order for order in self.get_all() if order.agent_id == agent_id]
    
    def get_by_account(self, account_id: UUID) -> List[TradingOrder]:
        """
        Get all orders for an account.
        
        Args:
            account_id: UUID of the account
            
        Returns:
            List of orders for the account
        """
        return [order for order in self.get_all() if order.account_id == account_id]
    
    def get_by_status(
        self, 
        status: OrderStatus, 
        agent_id: Optional[UUID] = None
    ) -> List[TradingOrder]:
        """
        Get orders by status, optionally filtered by agent.
        
        Args:
            status: Order status to filter by
            agent_id: Optional agent ID to filter by
            
        Returns:
            List of orders matching the criteria
        """
        orders = [order for order in self.get_all() if order.status == status]
        if agent_id:
            orders = [order for order in orders if order.agent_id == agent_id]
        return orders
    
    def get_pending_orders(self, agent_id: Optional[UUID] = None) -> List[TradingOrder]:
        """Get all pending orders, optionally for a specific agent."""
        return self.get_by_status(OrderStatus.PENDING, agent_id)
    
    def get_filled_orders(self, agent_id: Optional[UUID] = None) -> List[TradingOrder]:
        """Get all filled orders, optionally for a specific agent."""
        return self.get_by_status(OrderStatus.FILLED, agent_id)
    
    def get_closed_orders(self, agent_id: Optional[UUID] = None) -> List[TradingOrder]:
        """Get all closed orders, optionally for a specific agent."""
        return self.get_by_status(OrderStatus.CLOSED, agent_id)


class OrderHistoryRepository(InMemoryRepository[TradingOrderHistory]):
    """Repository for TradingOrderHistory snapshots."""
    
    def save_snapshot(self, snapshot: TradingOrderHistory) -> TradingOrderHistory:
        """
        Save a snapshot of order history.
        
        Args:
            snapshot: Order history snapshot
            
        Returns:
            Saved snapshot
        """
        return self.save(snapshot)
    
    def get_history_for_order(self, order_id: UUID) -> List[TradingOrderHistory]:
        """
        Get all history snapshots for an order.
        
        Args:
            order_id: UUID of the order
            
        Returns:
            List of history snapshots, sorted by timestamp
        """
        snapshots = [
            snapshot for snapshot in self.get_all()
            if snapshot.order_id == order_id
        ]
        return sorted(snapshots, key=lambda s: s.timestamp)
    
    def get_latest_snapshot(self, order_id: UUID) -> Optional[TradingOrderHistory]:
        """
        Get the latest history snapshot for an order.
        
        Args:
            order_id: UUID of the order
            
        Returns:
            Latest snapshot if found, None otherwise
        """
        snapshots = self.get_history_for_order(order_id)
        return snapshots[-1] if snapshots else None
