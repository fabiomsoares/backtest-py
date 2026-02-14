"""Order execution and management module."""

from enum import Enum
from typing import Optional
from datetime import datetime


class OrderType(Enum):
    """Enumeration of order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Enumeration of order sides."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Enumeration of order statuses."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order:
    """
    Represents a trading order.
    
    Attributes:
        symbol (str): Trading symbol/ticker
        order_type (OrderType): Type of order (market, limit, etc.)
        side (OrderSide): Buy or sell
        quantity (float): Number of shares/units
        price (Optional[float]): Order price (None for market orders)
        stop_price (Optional[float]): Stop price for stop orders
        timestamp (datetime): Order creation time
        status (OrderStatus): Current order status
        filled_quantity (float): Quantity filled so far
        filled_price (Optional[float]): Average fill price
        order_id (Optional[str]): Unique order identifier
    
    Example:
        >>> order = Order(
        ...     symbol="AAPL",
        ...     order_type=OrderType.MARKET,
        ...     side=OrderSide.BUY,
        ...     quantity=100
        ... )
    """
    
    def __init__(
        self,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        timestamp: Optional[datetime] = None,
        order_id: Optional[str] = None,
    ):
        """
        Initialize a new order.
        
        Args:
            symbol: Trading symbol/ticker
            order_type: Type of order
            side: Buy or sell
            quantity: Number of shares/units
            price: Order price (None for market orders)
            stop_price: Stop price for stop orders
            timestamp: Order creation time (defaults to now)
            order_id: Unique order identifier
        """
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.timestamp = timestamp or datetime.now()
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0.0
        self.filled_price = None
        self.order_id = order_id
    
    def fill(self, quantity: float, price: float) -> None:
        """
        Fill the order (fully or partially).
        
        Args:
            quantity: Quantity to fill
            price: Fill price
        """
        if quantity > self.quantity - self.filled_quantity:
            raise ValueError("Fill quantity exceeds remaining order quantity")
        
        # Update filled quantity and average price
        if self.filled_price is None:
            self.filled_price = price
        else:
            total_value = self.filled_price * self.filled_quantity + price * quantity
            self.filled_quantity += quantity
            self.filled_price = total_value / self.filled_quantity
            quantity = 0  # Reset since we already added above
        
        self.filled_quantity += quantity
        
        # Update status
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self) -> None:
        """Cancel the order."""
        if self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel order with status {self.status}")
        self.status = OrderStatus.CANCELLED
    
    def reject(self) -> None:
        """Reject the order."""
        self.status = OrderStatus.REJECTED
    
    @property
    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_active(self) -> bool:
        """Check if order is active (pending or partially filled)."""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
    
    @property
    def remaining_quantity(self) -> float:
        """Get remaining quantity to be filled."""
        return self.quantity - self.filled_quantity
    
    def __repr__(self) -> str:
        """String representation of the order."""
        return (
            f"Order(symbol={self.symbol}, type={self.order_type.value}, "
            f"side={self.side.value}, quantity={self.quantity}, "
            f"price={self.price}, status={self.status.value})"
        )
