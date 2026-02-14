"""
In-memory repository for storing and managing positions.
"""

from typing import List, Optional, Dict
from backtest.models.position import Position


class PositionRepository:
    """
    In-memory repository for positions.
    
    Stores and manages trading positions in memory.
    """
    
    def __init__(self):
        """Initialize the position repository."""
        self._positions: Dict[str, Position] = {}
    
    def add(self, position: Position):
        """
        Add or update a position in the repository.
        
        Args:
            position: Position to add or update
        """
        self._positions[position.symbol] = position
    
    def get(self, symbol: str) -> Optional[Position]:
        """
        Get a position by symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position or None if not found
        """
        return self._positions.get(symbol)
    
    def get_all(self) -> List[Position]:
        """
        Get all positions.
        
        Returns:
            List of all positions
        """
        return list(self._positions.values())
    
    def get_long_positions(self) -> List[Position]:
        """
        Get all long positions.
        
        Returns:
            List of long positions (quantity > 0)
        """
        return [pos for pos in self._positions.values() if pos.is_long()]
    
    def get_short_positions(self) -> List[Position]:
        """
        Get all short positions.
        
        Returns:
            List of short positions (quantity < 0)
        """
        return [pos for pos in self._positions.values() if pos.is_short()]
    
    def update(self, position: Position):
        """
        Update an existing position.
        
        Args:
            position: Position to update
        """
        self._positions[position.symbol] = position
    
    def delete(self, symbol: str):
        """
        Delete a position.
        
        Args:
            symbol: Symbol of position to delete
        """
        if symbol in self._positions:
            del self._positions[symbol]
    
    def exists(self, symbol: str) -> bool:
        """
        Check if a position exists for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if position exists, False otherwise
        """
        return symbol in self._positions
    
    def clear(self):
        """Clear all positions from the repository."""
        self._positions.clear()
    
    def count(self) -> int:
        """
        Count the number of positions.
        
        Returns:
            Number of positions
        """
        return len(self._positions)
