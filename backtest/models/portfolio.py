"""
Portfolio model representing the overall trading portfolio state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from backtest.models.position import Position


@dataclass
class Portfolio:
    """
    Represents a trading portfolio with cash and positions.
    
    Attributes:
        initial_capital: Starting capital
        cash: Current available cash
        positions: Dictionary of symbol -> Position
        created_at: When the portfolio was created
        transaction_history: List of all transactions
    """
    initial_capital: float
    cash: float
    positions: Dict[str, Position] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    transaction_history: List[Dict] = field(default_factory=list)
    
    @property
    def equity(self) -> float:
        """Calculate total equity (cash + market value of positions)."""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_pnl(self) -> float:
        """Calculate total profit/loss."""
        return self.equity - self.initial_capital
    
    @property
    def total_pnl_percent(self) -> float:
        """Calculate total profit/loss as a percentage."""
        if self.initial_capital == 0:
            return 0.0
        return (self.total_pnl / self.initial_capital) * 100
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol."""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """Check if a position exists for a symbol."""
        return symbol in self.positions
    
    def add_position(self, position: Position):
        """Add or update a position."""
        self.positions[position.symbol] = position
    
    def remove_position(self, symbol: str):
        """Remove a position."""
        if symbol in self.positions:
            del self.positions[symbol]
    
    def update_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions."""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)
    
    def record_transaction(self, transaction: Dict):
        """Record a transaction in history."""
        self.transaction_history.append(transaction)
