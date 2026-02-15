"""Market data models: Bar data and time frames."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class TimeUnit(Enum):
    """Time units for time frames."""
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


@dataclass(frozen=True)
class TimeFrame:
    """
    Represents a time frame for market data.
    
    Attributes:
        unit: Time unit (MINUTE, HOUR, DAY, WEEK, MONTH)
        multiplier: Multiplier for the unit (e.g., 5 for 5-minute bars)
        offset: Offset within the unit (e.g., 30 for half-past)
        code: Generated code (e.g., "5m", "1h", "1d")
    """
    unit: TimeUnit
    multiplier: int = 1
    offset: int = 0
    code: str = ""
    
    def __post_init__(self):
        """Validate time frame and generate code if not provided."""
        if self.multiplier <= 0:
            raise ValueError("multiplier must be positive")
        if self.offset < 0:
            raise ValueError("offset cannot be negative")
        
        # Generate code if not provided
        if not self.code:
            unit_codes = {
                TimeUnit.MINUTE: "m",
                TimeUnit.HOUR: "h",
                TimeUnit.DAY: "d",
                TimeUnit.WEEK: "w",
                TimeUnit.MONTH: "M",
            }
            code = f"{self.multiplier}{unit_codes[self.unit]}"
            object.__setattr__(self, "code", code)
    
    def __str__(self) -> str:
        """String representation."""
        return self.code


@dataclass(frozen=True)
class BarData:
    """
    Represents OHLCV bar data for a specific time period.
    
    Attributes:
        symbol: Trading symbol/pair code
        timeframe: Time frame of the bar
        timestamp: Bar start timestamp
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
    """
    symbol: str
    timeframe: TimeFrame
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal = Decimal("0")
    
    def __post_init__(self):
        """Validate bar data."""
        if not self.symbol or not self.symbol.strip():
            raise ValueError("symbol cannot be empty")
        
        # Validate OHLC relationships
        if self.high < self.low:
            raise ValueError(f"high ({self.high}) cannot be less than low ({self.low})")
        if self.open < self.low or self.open > self.high:
            raise ValueError(f"open ({self.open}) must be between low ({self.low}) and high ({self.high})")
        if self.close < self.low or self.close > self.high:
            raise ValueError(f"close ({self.close}) must be between low ({self.low}) and high ({self.high})")
        
        if self.volume < 0:
            raise ValueError("volume cannot be negative")
    
    @property
    def typical_price(self) -> Decimal:
        """Calculate typical price (HLC/3)."""
        return (self.high + self.low + self.close) / Decimal("3")
    
    @property
    def range(self) -> Decimal:
        """Calculate price range (high - low)."""
        return self.high - self.low
