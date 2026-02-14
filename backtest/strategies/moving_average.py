"""Moving average crossover strategy."""

import pandas as pd
from typing import Optional

from backtest.strategies.base import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy.
    
    Generates buy signals when the fast moving average crosses above
    the slow moving average, and sell signals when it crosses below.
    
    Attributes:
        fast_window (int): Period for fast moving average
        slow_window (int): Period for slow moving average
        
    Example:
        >>> strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
        >>> signals = strategy.generate_signals(data)
    """
    
    def __init__(
        self,
        fast_window: int = 20,
        slow_window: int = 50,
        name: Optional[str] = None,
    ):
        """
        Initialize the moving average strategy.
        
        Args:
            fast_window: Period for fast moving average
            slow_window: Period for slow moving average
            name: Optional strategy name
        """
        super().__init__(name)
        self.fast_window = fast_window
        self.slow_window = slow_window
        
        if fast_window >= slow_window:
            raise ValueError("Fast window must be smaller than slow window")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on moving average crossover.
        
        Args:
            data: Historical price data with 'close' column
            
        Returns:
            DataFrame with 'signal' column:
                1 = buy (fast MA crosses above slow MA)
                -1 = sell (fast MA crosses below slow MA)
                0 = hold
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Calculate moving averages
        signals['fast_ma'] = data['close'].rolling(window=self.fast_window, min_periods=1).mean()
        signals['slow_ma'] = data['close'].rolling(window=self.slow_window, min_periods=1).mean()
        
        # Generate signals based on crossovers
        # Buy when fast MA crosses above slow MA
        signals['signal'] = 0
        
        # Create position column (1 when fast > slow, 0 otherwise)
        signals['position'] = (signals['fast_ma'] > signals['slow_ma']).astype(int)
        
        # Generate signal when position changes
        signals['signal'] = signals['position'].diff()
        
        # Clean up: only keep the signal column
        signals = signals[['signal']].fillna(0)
        
        return signals
    
    def _get_required_columns(self) -> list:
        """Get required columns for this strategy."""
        return ['close']
    
    def __repr__(self) -> str:
        """String representation of the strategy."""
        return (
            f"MovingAverageStrategy(fast_window={self.fast_window}, "
            f"slow_window={self.slow_window})"
        )
