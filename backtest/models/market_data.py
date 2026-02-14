"""
Market data model representing a single bar (candlestick) of market data.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MarketBar:
    """
    Represents a single bar of market data (OHLCV).
    
    Attributes:
        timestamp: The datetime of the bar
        symbol: The trading symbol (e.g., 'AAPL', 'BTCUSD')
        open: Opening price
        high: Highest price during the period
        low: Lowest price during the period
        close: Closing price
        volume: Trading volume
    """
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def __post_init__(self):
        """Validate the market bar data."""
        if self.high < self.low:
            raise ValueError("High price cannot be less than low price")
        if self.open < 0 or self.close < 0:
            raise ValueError("Prices cannot be negative")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
