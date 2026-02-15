"""
Position model representing an open trading position.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Position:
    """
    Represents an open trading position.
    
    Attributes:
        symbol: Trading symbol
        quantity: Number of shares/contracts (positive for long, negative for short)
        entry_price: Average entry price
        entry_time: When the position was opened
        current_price: Current market price
        unrealized_pnl: Unrealized profit/loss
    """
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    current_price: Optional[float] = None
    
    @property
    def market_value(self) -> float:
        """Calculate current market value of the position."""
        if self.current_price is None:
            return self.quantity * self.entry_price
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """Calculate the cost basis of the position."""
        return abs(self.quantity) * self.entry_price
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss."""
        if self.current_price is None:
            return 0.0
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """Calculate unrealized profit/loss as a percentage."""
        if self.entry_price == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100
    
    def is_long(self) -> bool:
        """Check if this is a long position."""
        return self.quantity > 0
    
    def is_short(self) -> bool:
        """Check if this is a short position."""
        return self.quantity < 0
    
    def update_price(self, price: float):
        """Update the current price of the position."""
        self.current_price = price
