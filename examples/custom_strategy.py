"""
Custom Strategy Example

This script demonstrates how to create a custom trading strategy
by inheriting from BaseStrategy.
"""

import pandas as pd
import numpy as np
from typing import Optional

from backtest import BacktestEngine, BaseStrategy
from backtest.data import DataLoader


class RSIStrategy(BaseStrategy):
    """
    Simple RSI (Relative Strength Index) strategy.
    
    Generates buy signals when RSI crosses below oversold threshold,
    and sell signals when RSI crosses above overbought threshold.
    """
    
    def __init__(
        self,
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70,
        name: Optional[str] = None,
    ):
        """
        Initialize RSI strategy.
        
        Args:
            period: RSI calculation period
            oversold: Oversold threshold (buy signal)
            overbought: Overbought threshold (sell signal)
            name: Strategy name
        """
        super().__init__(name or "RSI_Strategy")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on RSI.
        
        Args:
            data: Historical price data
            
        Returns:
            DataFrame with signals
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Calculate RSI
        signals['rsi'] = self.calculate_rsi(data['close'], self.period)
        
        # Generate position: 1 when RSI < oversold, 0 when RSI > overbought
        signals['position'] = 0
        signals.loc[signals['rsi'] < self.oversold, 'position'] = 1
        signals.loc[signals['rsi'] > self.overbought, 'position'] = 0
        
        # Forward fill positions (hold until opposite signal)
        signals['position'] = signals['position'].replace(0, np.nan).ffill().fillna(0)
        
        # Generate signal on position change
        signals['signal'] = signals['position'].diff()
        
        return signals[['signal']]
    
    def __repr__(self):
        return (
            f"RSIStrategy(period={self.period}, "
            f"oversold={self.oversold}, overbought={self.overbought})"
        )


def main():
    """Run custom strategy example."""
    
    print("=" * 60)
    print("Backtest-py: Custom Strategy Example")
    print("=" * 60)
    print()
    
    # Load data
    print("Loading data...")
    try:
        loader = DataLoader()
        data = loader.load_yahoo('AAPL', start='2022-01-01', end='2023-12-31')
        print(f"Loaded {len(data)} days of data")
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Using sample data...")
        
        # Generate sample data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        prices = 150 + np.cumsum(np.random.randn(len(dates)) * 2)
        
        data = pd.DataFrame({
            'close': prices,
            'high': prices + abs(np.random.randn(len(dates)) * 1.5),
            'low': prices - abs(np.random.randn(len(dates)) * 1.5),
            'volume': np.random.randint(1000000, 10000000, len(dates)),
        }, index=dates)
    
    # Create custom strategy
    print("Creating custom RSI strategy...")
    strategy = RSIStrategy(
        period=14,
        oversold=30,
        overbought=70,
    )
    print(f"Strategy: {strategy}")
    print()
    
    # Run backtest
    print("Running backtest...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=50000.0,
        commission=0.001,
    )
    
    results = engine.run(data)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Initial Capital:  ${results['initial_capital']:,.2f}")
    print(f"Final Value:      ${results['final_value']:,.2f}")
    print(f"Total Return:     {results['total_return']:.2f}%")
    print(f"Trades:           {results['num_trades']}")
    
    if 'sharpe_ratio' in results:
        print(f"Sharpe Ratio:     {results['sharpe_ratio']:.3f}")
    if 'max_drawdown' in results:
        print(f"Max Drawdown:     {results['max_drawdown']:.2f}%")
    
    print("=" * 60)
    print("\nCustom strategy example completed!")


if __name__ == "__main__":
    main()
