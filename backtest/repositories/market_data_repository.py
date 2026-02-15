"""Repository for market data optimized for millions of bars."""

from typing import Dict, List, Optional
from datetime import datetime

from backtest.models import BarData


class MarketDataRepository:
    """
    Repository for market data optimized for large datasets.
    
    Uses composite keys (symbol_timeframe) for efficient lookups.
    Stores bars in chronological order for each symbol/timeframe combination.
    """
    
    def __init__(self):
        """Initialize empty market data storage."""
        # Key: f"{symbol}_{timeframe_code}", Value: List of BarData sorted by timestamp
        self._data: Dict[str, List[BarData]] = {}
    
    def save_bar(self, bar: BarData) -> None:
        """
        Save a single bar.
        
        Args:
            bar: Bar data to save
        """
        key = self._make_key(bar.symbol, bar.timeframe.code)
        
        if key not in self._data:
            self._data[key] = []
        
        # Insert in chronological order
        bars = self._data[key]
        insert_idx = len(bars)
        
        # Find insertion point (binary search could be used for large datasets)
        for i, existing_bar in enumerate(bars):
            if existing_bar.timestamp == bar.timestamp:
                # Replace existing bar with same timestamp
                bars[i] = bar
                return
            elif existing_bar.timestamp > bar.timestamp:
                insert_idx = i
                break
        
        bars.insert(insert_idx, bar)
    
    def save_bars(self, bars: List[BarData]) -> None:
        """
        Save multiple bars efficiently.
        
        Args:
            bars: List of bars to save
        """
        for bar in bars:
            self.save_bar(bar)
    
    def get_bars(
        self,
        symbol: str,
        timeframe_code: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[BarData]:
        """
        Get bars for a symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe_code: Timeframe code (e.g., "1h", "1d")
            start: Optional start timestamp (inclusive)
            end: Optional end timestamp (inclusive)
            limit: Optional maximum number of bars to return
            
        Returns:
            List of bars matching the criteria
        """
        key = self._make_key(symbol, timeframe_code)
        bars = self._data.get(key, [])
        
        # Filter by date range
        if start:
            bars = [bar for bar in bars if bar.timestamp >= start]
        if end:
            bars = [bar for bar in bars if bar.timestamp <= end]
        
        # Apply limit
        if limit and limit > 0:
            bars = bars[:limit]
        
        return bars
    
    def get_latest_bar(
        self,
        symbol: str,
        timeframe_code: str,
        before: Optional[datetime] = None
    ) -> Optional[BarData]:
        """
        Get the latest bar for a symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe_code: Timeframe code
            before: Optional timestamp to get bar before this time
            
        Returns:
            Latest bar if found, None otherwise
        """
        key = self._make_key(symbol, timeframe_code)
        bars = self._data.get(key, [])
        
        if not bars:
            return None
        
        if before:
            # Find last bar before the specified time
            for bar in reversed(bars):
                if bar.timestamp < before:
                    return bar
            return None
        
        return bars[-1]
    
    def get_historical_bars(
        self,
        symbol: str,
        timeframe_code: str,
        n: int,
        end: Optional[datetime] = None
    ) -> List[BarData]:
        """
        Get the last N bars for a symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe_code: Timeframe code
            n: Number of bars to return
            end: Optional end timestamp (returns N bars up to this time)
            
        Returns:
            List of up to N bars
        """
        key = self._make_key(symbol, timeframe_code)
        bars = self._data.get(key, [])
        
        if end:
            # Filter bars up to end time
            bars = [bar for bar in bars if bar.timestamp <= end]
        
        # Return last N bars
        return bars[-n:] if n > 0 else []
    
    def count_bars(self, symbol: str, timeframe_code: str) -> int:
        """
        Count bars for a symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe_code: Timeframe code
            
        Returns:
            Number of bars
        """
        key = self._make_key(symbol, timeframe_code)
        return len(self._data.get(key, []))
    
    def get_symbols(self) -> List[str]:
        """
        Get all unique symbols in the repository.
        
        Returns:
            List of symbol strings
        """
        symbols = set()
        for key in self._data.keys():
            symbol = key.split('_')[0]
            symbols.add(symbol)
        return sorted(list(symbols))
    
    def clear(self) -> None:
        """Clear all market data."""
        self._data.clear()
    
    def _make_key(self, symbol: str, timeframe_code: str) -> str:
        """Create composite key for storage."""
        return f"{symbol}_{timeframe_code}"
