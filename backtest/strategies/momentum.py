"""Momentum-based trading strategy."""

import pandas as pd
from typing import Optional

from backtest.strategies.base import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Simple momentum strategy based on rate of change.
    
    Generates buy signals when momentum is positive and above a threshold,
    and sell signals when momentum turns negative or falls below threshold.
    
    Attributes:
        lookback_period (int): Period for momentum calculation
        threshold (float): Momentum threshold for generating signals (in percentage)
        
    Example:
        >>> strategy = MomentumStrategy(lookback_period=20, threshold=2.0)
        >>> signals = strategy.generate_signals(data)
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        threshold: float = 0.0,
        name: Optional[str] = None,
    ):
        """
        Initialize the momentum strategy.
        
        Args:
            lookback_period: Period for calculating momentum
            threshold: Momentum threshold percentage for signals
            name: Optional strategy name
        """
        super().__init__(name)
        self.lookback_period = lookback_period
        self.threshold = threshold
        
        if lookback_period < 1:
            raise ValueError("Lookback period must be at least 1")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on momentum.
        
        Args:
            data: Historical price data with 'close' column
            
        Returns:
            DataFrame with 'signal' column:
                1 = buy (positive momentum above threshold)
                -1 = sell (negative momentum or below threshold)
                0 = hold
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Calculate momentum as percentage change over lookback period
        signals['momentum'] = data['close'].pct_change(periods=self.lookback_period) * 100
        
        # Generate position based on momentum and threshold
        # 1 = long position (momentum > threshold), 0 = no position
        signals['position'] = ((signals['momentum'] > self.threshold)).astype(int)
        
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
            f"MomentumStrategy(lookback_period={self.lookback_period}, "
            f"threshold={self.threshold}%)"
        )
