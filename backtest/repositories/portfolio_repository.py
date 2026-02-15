"""
In-memory repository for storing and managing portfolio state.
"""

from typing import Optional
from backtest.models.portfolio import Portfolio


class PortfolioRepository:
    """
    In-memory repository for portfolio.
    
    Stores and manages the portfolio state in memory.
    """
    
    def __init__(self):
        """Initialize the portfolio repository."""
        self._portfolio: Optional[Portfolio] = None
    
    def save(self, portfolio: Portfolio):
        """
        Save the portfolio state.
        
        Args:
            portfolio: Portfolio to save
        """
        self._portfolio = portfolio
    
    def get(self) -> Optional[Portfolio]:
        """
        Get the current portfolio.
        
        Returns:
            Current Portfolio or None if not set
        """
        return self._portfolio
    
    def update_cash(self, amount: float):
        """
        Update the cash balance.
        
        Args:
            amount: Amount to add (positive) or subtract (negative)
        """
        if self._portfolio:
            self._portfolio.cash += amount
    
    def get_equity(self) -> float:
        """
        Get the current portfolio equity.
        
        Returns:
            Total equity value
        """
        if self._portfolio:
            return self._portfolio.equity
        return 0.0
    
    def get_cash(self) -> float:
        """
        Get the current cash balance.
        
        Returns:
            Cash balance
        """
        if self._portfolio:
            return self._portfolio.cash
        return 0.0
    
    def clear(self):
        """Clear the portfolio."""
        self._portfolio = None
