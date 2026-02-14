"""
Order models for representing trading orders in the backtesting system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderType(Enum):
    """Type of order."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Side of the order (buy or sell)."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Status of an order."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """
    Represents a trading order.
    
    Attributes:
        order_id: Unique identifier for the order
        symbol: Trading symbol
        side: Buy or sell
        order_type: Type of order (market, limit, etc.)
        quantity: Number of shares/contracts
        price: Price for limit orders (None for market orders)
        timestamp: When the order was created
        status: Current status of the order
        filled_quantity: Quantity that has been filled
        filled_price: Average price at which the order was filled
    """
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    timestamp: datetime
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    filled_price: Optional[float] = None
    
    def is_filled(self) -> bool:
        """Check if the order is completely filled."""
        return self.status == OrderStatus.FILLED
    
    def fill(self, quantity: float, price: float):
        """
        Fill the order partially or completely.
        
        Args:
            quantity: Quantity to fill
            price: Price at which to fill
        """
        if quantity > (self.quantity - self.filled_quantity):
            raise ValueError("Fill quantity exceeds remaining quantity")
        
        # Update filled quantity and average price
        total_value = (self.filled_quantity * (self.filled_price or 0)) + (quantity * price)
        self.filled_quantity += quantity
        self.filled_price = total_value / self.filled_quantity
        
        # Update status
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
