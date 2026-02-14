"""
Simple example demonstrating a basic moving average crossover strategy.
"""

from datetime import datetime, timedelta
from backtest.core.engine import BacktestEngine
from backtest.models.strategy import Strategy
from backtest.models.market_data import MarketBar


class SimpleMovingAverageStrategy(Strategy):
    """
    A simple moving average crossover strategy.
    
    Buys when short MA crosses above long MA.
    Sells when short MA crosses below long MA.
    """
    
    def __init__(self, short_window: int = 10, long_window: int = 20):
        super().__init__(name="MA Crossover")
        self.short_window = short_window
        self.long_window = long_window
    
    def on_bar(self, bar: MarketBar):
        """Process each bar and make trading decisions."""
        # Need enough bars for calculation
        if len(self.bars) < self.long_window:
            return
        
        # Calculate moving averages
        recent_bars = self.bars[-self.long_window:]
        short_ma = sum(b.close for b in recent_bars[-self.short_window:]) / self.short_window
        long_ma = sum(b.close for b in recent_bars) / self.long_window
        
        # Generate trading signals
        if short_ma > long_ma and not self.has_position(bar.symbol):
            # Buy signal
            self.buy(bar.symbol, quantity=100)
            print(f"{bar.timestamp}: BUY at ${bar.close:.2f}")
        
        elif short_ma < long_ma and self.has_position(bar.symbol):
            # Sell signal
            position = self.get_position(bar.symbol)
            if position:
                self.sell(bar.symbol, quantity=position.quantity)
                print(f"{bar.timestamp}: SELL at ${bar.close:.2f}")


def generate_sample_data(symbol: str, days: int = 100) -> list:
    """Generate sample market data for testing."""
    import random
    
    bars = []
    start_date = datetime.now() - timedelta(days=days)
    price = 100.0
    
    for i in range(days):
        # Random walk price movement
        change = random.uniform(-2, 2)
        price = max(price + change, 1.0)
        
        high = price + random.uniform(0, 2)
        low = price - random.uniform(0, 2)
        open_price = price + random.uniform(-1, 1)
        close = price
        volume = random.randint(100000, 1000000)
        
        bar = MarketBar(
            timestamp=start_date + timedelta(days=i),
            symbol=symbol,
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        bars.append(bar)
    
    return bars


def main():
    """Run the example backtest."""
    print("Running Moving Average Crossover Strategy Backtest")
    print("=" * 50)
    
    # Generate sample data
    bars = generate_sample_data("AAPL", days=100)
    
    # Create strategy
    strategy = SimpleMovingAverageStrategy(short_window=10, long_window=20)
    
    # Create and run backtest engine
    engine = BacktestEngine(initial_capital=10000.0)
    results = engine.run(strategy, bars)
    
    # Print results
    print("\n" + str(results))


if __name__ == "__main__":
    main()
