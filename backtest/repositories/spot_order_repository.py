"""Repository for SpotOrder entities."""

from typing import List, Optional
from uuid import UUID

from backtest.repositories.base import InMemoryRepository
from backtest.models.spot_order import SpotOrder
from backtest.models.orders import OrderStatus


class SpotOrderRepository(InMemoryRepository[SpotOrder]):
    """
    Repository for SpotOrder entities with specialized queries.
    
    Provides methods to query orders by status, agent, account, and trading pair.
    """
    
    def get_by_status(
        self,
        status: OrderStatus,
        backtest_run_id: Optional[UUID] = None
    ) -> List[SpotOrder]:
        """
        Get all orders with a specific status.
        
        Args:
            status: Order status to filter by
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of orders with the specified status
        """
        orders = [
            o for o in self.get_all()
            if o.status == status
        ]
        
        if backtest_run_id is not None:
            orders = [
                o for o in orders
                if o.backtest_run_id == backtest_run_id
            ]
        
        return sorted(orders, key=lambda o: o.create_timestamp)
    
    def get_by_agent(
        self,
        agent_id: UUID,
        backtest_run_id: Optional[UUID] = None
    ) -> List[SpotOrder]:
        """
        Get all orders for a specific agent.
        
        Args:
            agent_id: Agent ID
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of orders for the agent
        """
        orders = [
            o for o in self.get_all()
            if o.agent_id == agent_id
        ]
        
        if backtest_run_id is not None:
            orders = [
                o for o in orders
                if o.backtest_run_id == backtest_run_id
            ]
        
        return sorted(orders, key=lambda o: o.create_timestamp)
    
    def get_by_account(
        self,
        account_id: UUID,
        backtest_run_id: Optional[UUID] = None
    ) -> List[SpotOrder]:
        """
        Get all orders for a specific account.
        
        Args:
            account_id: Account ID
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of orders for the account
        """
        orders = [
            o for o in self.get_all()
            if o.account_id == account_id
        ]
        
        if backtest_run_id is not None:
            orders = [
                o for o in orders
                if o.backtest_run_id == backtest_run_id
            ]
        
        return sorted(orders, key=lambda o: o.create_timestamp)
    
    def get_pending_orders(
        self,
        agent_id: Optional[UUID] = None,
        backtest_run_id: Optional[UUID] = None
    ) -> List[SpotOrder]:
        """
        Get all pending orders, optionally filtered by agent.
        
        Args:
            agent_id: Optional agent ID filter
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of pending orders
        """
        orders = [
            o for o in self.get_all()
            if o.status == OrderStatus.PENDING
        ]
        
        if agent_id is not None:
            orders = [
                o for o in orders
                if o.agent_id == agent_id
            ]
        
        if backtest_run_id is not None:
            orders = [
                o for o in orders
                if o.backtest_run_id == backtest_run_id
            ]
        
        return sorted(orders, key=lambda o: o.create_timestamp)
    
    def get_by_trading_pair(
        self,
        trading_pair_code: str,
        backtest_run_id: Optional[UUID] = None
    ) -> List[SpotOrder]:
        """
        Get all orders for a specific trading pair.
        
        Args:
            trading_pair_code: Trading pair code
            backtest_run_id: Optional backtest run filter
            
        Returns:
            List of orders for the trading pair
        """
        orders = [
            o for o in self.get_all()
            if o.trading_pair_code == trading_pair_code
        ]
        
        if backtest_run_id is not None:
            orders = [
                o for o in orders
                if o.backtest_run_id == backtest_run_id
            ]
        
        return sorted(orders, key=lambda o: o.create_timestamp)
    
    def get_by_root_id(self, root_id: UUID) -> List[SpotOrder]:
        """
        Get all orders in an order chain (original + splits/modifications).
        
        Args:
            root_id: Root order ID
            
        Returns:
            List of orders in the chain
        """
        return sorted(
            [o for o in self.get_all() if o.root_id == root_id],
            key=lambda o: o.create_timestamp
        )
    
    def clear_run(self, backtest_run_id: UUID) -> int:
        """
        Clear all orders for a specific backtest run.
        
        Args:
            backtest_run_id: Backtest run ID
            
        Returns:
            Number of orders deleted
        """
        to_delete = [
            o.id
            for o in self.get_all()
            if o.backtest_run_id == backtest_run_id
        ]
        
        for order_id in to_delete:
            self.delete(order_id)
        
        return len(to_delete)
