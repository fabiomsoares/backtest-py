"""Position tracking and P&L calculation module."""

from typing import Optional
from datetime import datetime


class Position:
    """
    Represents a trading position in a security.
    
    This class tracks an open position in a security, including entry details,
    current value, and profit/loss calculations.
    
    Attributes:
        symbol (str): Trading symbol/ticker
        quantity (float): Current position size (positive for long, negative for short)
        entry_price (float): Average entry price
        entry_time (datetime): Time when position was opened
        current_price (Optional[float]): Current market price
        
    Example:
        >>> position = Position(
        ...     symbol="AAPL",
        ...     quantity=100,
        ...     entry_price=150.0
        ... )
        >>> position.update_price(155.0)
        >>> print(position.unrealized_pnl)
        500.0
    """
    
    def __init__(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        entry_time: Optional[datetime] = None,
    ):
        """
        Initialize a new position.
        
        Args:
            symbol: Trading symbol/ticker
            quantity: Position size (positive for long, negative for short)
            entry_price: Average entry price
            entry_time: Time when position was opened (defaults to now)
        """
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_time = entry_time or datetime.now()
        self.current_price: Optional[float] = None
        self.realized_pnl = 0.0
    
    def update_price(self, price: float) -> None:
        """
        Update the current market price.
        
        Args:
            price: Current market price
        """
        self.current_price = price
    
    def add_shares(self, quantity: float, price: float) -> None:
        """
        Add shares to the position (average up).
        
        Args:
            quantity: Number of shares to add
            price: Price at which shares are added
        """
        if (self.quantity > 0 and quantity < 0) or (self.quantity < 0 and quantity > 0):
            raise ValueError("Cannot add shares in opposite direction. Use close_shares instead.")
        
        total_cost = self.entry_price * abs(self.quantity) + price * abs(quantity)
        self.quantity += quantity
        if self.quantity != 0:
            self.entry_price = total_cost / abs(self.quantity)
    
    def close_shares(self, quantity: float, price: float) -> float:
        """
        Close part or all of the position.
        
        Args:
            quantity: Number of shares to close (positive value)
            price: Price at which shares are closed
            
        Returns:
            Realized P&L from this closing transaction
        """
        if abs(quantity) > abs(self.quantity):
            raise ValueError("Cannot close more shares than current position")
        
        # Calculate realized P&L
        if self.quantity > 0:
            pnl = (price - self.entry_price) * quantity
            self.quantity -= quantity
        else:
            pnl = (self.entry_price - price) * quantity
            self.quantity += quantity
        
        self.realized_pnl += pnl
        return pnl
    
    @property
    def market_value(self) -> float:
        """
        Calculate current market value of the position.
        
        Returns:
            Current market value (position size * current price)
        """
        if self.current_price is None:
            return self.quantity * self.entry_price
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """
        Calculate cost basis of the position.
        
        Returns:
            Cost basis (position size * entry price)
        """
        return self.quantity * self.entry_price
    
    @property
    def unrealized_pnl(self) -> float:
        """
        Calculate unrealized profit/loss.
        
        Returns:
            Unrealized P&L based on current price
        """
        if self.current_price is None:
            return 0.0
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def total_pnl(self) -> float:
        """
        Calculate total profit/loss (realized + unrealized).
        
        Returns:
            Total P&L
        """
        return self.realized_pnl + self.unrealized_pnl
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """
        Calculate unrealized P&L as a percentage.
        
        Returns:
            Unrealized P&L percentage
        """
        if self.entry_price == 0:
            return 0.0
        return (self.unrealized_pnl / abs(self.cost_basis)) * 100
    
    @property
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.quantity > 0
    
    @property
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.quantity < 0
    
    @property
    def is_closed(self) -> bool:
        """Check if position is closed."""
        return self.quantity == 0
    
    def __repr__(self) -> str:
        """String representation of the position."""
        direction = "LONG" if self.is_long else "SHORT" if self.is_short else "CLOSED"
        return (
            f"Position(symbol={self.symbol}, {direction}, "
            f"quantity={abs(self.quantity)}, entry={self.entry_price:.2f}, "
            f"current={self.current_price:.2f if self.current_price else 'N/A'}, "
            f"unrealized_pnl={self.unrealized_pnl:.2f})"
        )
