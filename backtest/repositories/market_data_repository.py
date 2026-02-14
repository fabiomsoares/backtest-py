"""
In-memory repository for storing and retrieving market data.
"""

from datetime import datetime
from typing import List, Optional, Dict
from backtest.models.market_data import MarketBar


class MarketDataRepository:
    """
    In-memory repository for market data.
    
    Stores market bars in memory for fast access during backtesting.
    """
    
    def __init__(self):
        """Initialize the market data repository."""
        self._data: Dict[str, List[MarketBar]] = {}
    
    def add_bar(self, bar: MarketBar):
        """
        Add a market bar to the repository.
        
        Args:
            bar: MarketBar to add
        """
        if bar.symbol not in self._data:
            self._data[bar.symbol] = []
        self._data[bar.symbol].append(bar)
    
    def add_bars(self, bars: List[MarketBar]):
        """
        Add multiple market bars to the repository.
        
        Args:
            bars: List of MarketBar objects to add
        """
        for bar in bars:
            self.add_bar(bar)
    
    def get_bars(self, symbol: str, start_date: Optional[datetime] = None, 
                 end_date: Optional[datetime] = None) -> List[MarketBar]:
        """
        Get market bars for a symbol within a date range.
        
        Args:
            symbol: Trading symbol
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of market bars
        """
        if symbol not in self._data:
            return []
        
        bars = self._data[symbol]
        
        if start_date:
            bars = [b for b in bars if b.timestamp >= start_date]
        if end_date:
            bars = [b for b in bars if b.timestamp <= end_date]
        
        return sorted(bars, key=lambda b: b.timestamp)
    
    def get_latest_bar(self, symbol: str) -> Optional[MarketBar]:
        """
        Get the most recent market bar for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest MarketBar or None if no data exists
        """
        if symbol not in self._data or not self._data[symbol]:
            return None
        return max(self._data[symbol], key=lambda b: b.timestamp)
    
    def get_symbols(self) -> List[str]:
        """
        Get all symbols in the repository.
        
        Returns:
            List of symbol strings
        """
        return list(self._data.keys())
    
    def clear(self):
        """Clear all data from the repository."""
        self._data.clear()
    
    def count(self, symbol: Optional[str] = None) -> int:
        """
        Count the number of bars.
        
        Args:
            symbol: If provided, count bars for this symbol only
            
        Returns:
            Number of bars
        """
        if symbol:
            return len(self._data.get(symbol, []))
        return sum(len(bars) for bars in self._data.values())
