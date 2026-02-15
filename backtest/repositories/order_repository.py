"""
In-memory repository for storing and managing orders.
"""

from typing import List, Optional, Dict
from backtest.models.order import Order, OrderStatus


class OrderRepository:
    """
    In-memory repository for orders.
    
    Stores and manages trading orders in memory.
    """
    
    def __init__(self):
        """Initialize the order repository."""
        self._orders: Dict[str, Order] = {}
    
    def add(self, order: Order):
        """
        Add an order to the repository.
        
        Args:
            order: Order to add
        """
        self._orders[order.order_id] = order
    
    def get(self, order_id: str) -> Optional[Order]:
        """
        Get an order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order or None if not found
        """
        return self._orders.get(order_id)
    
    def get_all(self) -> List[Order]:
        """
        Get all orders.
        
        Returns:
            List of all orders
        """
        return list(self._orders.values())
    
    def get_by_status(self, status: OrderStatus) -> List[Order]:
        """
        Get all orders with a specific status.
        
        Args:
            status: Order status to filter by
            
        Returns:
            List of orders with the specified status
        """
        return [order for order in self._orders.values() if order.status == status]
    
    def get_by_symbol(self, symbol: str) -> List[Order]:
        """
        Get all orders for a specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            List of orders for the symbol
        """
        return [order for order in self._orders.values() if order.symbol == symbol]
    
    def update(self, order: Order):
        """
        Update an existing order.
        
        Args:
            order: Order to update
        """
        if order.order_id in self._orders:
            self._orders[order.order_id] = order
    
    def delete(self, order_id: str):
        """
        Delete an order.
        
        Args:
            order_id: ID of order to delete
        """
        if order_id in self._orders:
            del self._orders[order_id]
    
    def clear(self):
        """Clear all orders from the repository."""
        self._orders.clear()
    
    def count(self) -> int:
        """
        Count the number of orders.
        
        Returns:
            Number of orders
        """
        return len(self._orders)
