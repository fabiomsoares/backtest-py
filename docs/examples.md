# Examples

This document provides various examples of using the backtest-py framework.

## Basic Examples

### 1. Simple Moving Average Strategy

```python
from backtest import BacktestEngine
from backtest.strategies import MovingAverageStrategy
from backtest.data import DataLoader

# Load data
loader = DataLoader()
data = loader.load_yahoo('AAPL', start='2020-01-01', end='2023-12-31')

# Create strategy
strategy = MovingAverageStrategy(fast_window=20, slow_window=50)

# Run backtest
engine = BacktestEngine(strategy=strategy, initial_capital=100000)
results = engine.run(data)

# Print results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
```

### 2. Momentum Strategy

```python
from backtest.strategies import MomentumStrategy

strategy = MomentumStrategy(lookback_period=20, threshold=2.0)
engine = BacktestEngine(strategy=strategy, initial_capital=50000, commission=0.001)

results = engine.run(data)
```

## Custom Strategy Examples

### 3. RSI Strategy

```python
import pandas as pd
import numpy as np
from backtest import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__()
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices):
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def generate_signals(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['rsi'] = self.calculate_rsi(data['close'])
        
        signals['position'] = 0
        signals.loc[signals['rsi'] < self.oversold, 'position'] = 1
        signals.loc[signals['rsi'] > self.overbought, 'position'] = 0
        signals['position'] = signals['position'].replace(0, np.nan).ffill().fillna(0)
        
        signals['signal'] = signals['position'].diff()
        return signals[['signal']]

# Use the strategy
strategy = RSIStrategy(period=14, oversold=30, overbought=70)
engine = BacktestEngine(strategy=strategy)
results = engine.run(data)
```

### 4. Bollinger Bands Strategy

```python
class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, period=20, num_std=2):
        super().__init__()
        self.period = period
        self.num_std = num_std
    
    def generate_signals(self, data):
        signals = pd.DataFrame(index=data.index)
        
        # Calculate Bollinger Bands
        signals['ma'] = data['close'].rolling(window=self.period).mean()
        signals['std'] = data['close'].rolling(window=self.period).std()
        signals['upper'] = signals['ma'] + (signals['std'] * self.num_std)
        signals['lower'] = signals['ma'] - (signals['std'] * self.num_std)
        
        # Generate signals
        signals['signal'] = 0
        signals.loc[data['close'] < signals['lower'], 'signal'] = 1  # Buy
        signals.loc[data['close'] > signals['upper'], 'signal'] = -1  # Sell
        
        return signals[['signal']]
```

## Advanced Examples

### 5. Multi-Asset Portfolio

```python
# TODO: Implement multi-asset support
# This is a placeholder for future functionality
```

### 6. Walk-Forward Analysis

```python
from backtest.utils import split_train_test

# Split data
train_data, test_data = split_train_test(data, train_ratio=0.7)

# Train on first period
strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
engine = BacktestEngine(strategy=strategy)
train_results = engine.run(train_data)

# Test on second period
engine2 = BacktestEngine(strategy=strategy)
test_results = engine2.run(test_data)

print("Train Return:", train_results['total_return'])
print("Test Return:", test_results['total_return'])
```

### 7. Parameter Optimization

```python
import pandas as pd

results = []

for fast in range(10, 30, 5):
    for slow in range(40, 100, 10):
        strategy = MovingAverageStrategy(fast_window=fast, slow_window=slow)
        engine = BacktestEngine(strategy=strategy)
        result = engine.run(data)
        
        results.append({
            'fast': fast,
            'slow': slow,
            'return': result['total_return'],
            'sharpe': result.get('sharpe_ratio', 0)
        })

results_df = pd.DataFrame(results)
best = results_df.loc[results_df['sharpe'].idxmax()]
print(f"Best parameters: fast={best['fast']}, slow={best['slow']}")
print(f"Best Sharpe: {best['sharpe']:.3f}")
```

### 8. Visualizing Results

```python
from backtest.visualization import (
    plot_portfolio_value,
    plot_returns,
    plot_drawdown
)

# Run backtest
strategy = MovingAverageStrategy()
engine = BacktestEngine(strategy=strategy)
results = engine.run(data)

# Get history
portfolio_history = engine.get_portfolio_history()
returns = portfolio_history['total_value'].pct_change()

# Create plots
plot_portfolio_value(portfolio_history['total_value'])
plot_returns(returns)
plot_drawdown(returns)
```

### 9. Generating Reports

```python
from backtest.visualization import generate_report
from backtest.metrics import PerformanceMetrics

# Run backtest
strategy = MovingAverageStrategy()
engine = BacktestEngine(strategy=strategy)
results = engine.run(data)

# Calculate detailed metrics
portfolio_history = engine.get_portfolio_history()
transactions = engine.get_transactions()

metrics_calc = PerformanceMetrics(
    portfolio_values=portfolio_history['total_value'],
    transactions=transactions,
    initial_capital=100000
)

all_metrics = metrics_calc.calculate_all()

# Print summary
metrics_calc.print_summary()

# Generate text report
report = generate_report(all_metrics, portfolio_history, transactions)
print(report)

# Save to file
with open('backtest_report.txt', 'w') as f:
    f.write(report)
```

### 10. Using with Google Colab

```python
# Install from GitHub
!pip install git+https://github.com/fabiomsoares/backtest-py.git

# Import and use
from backtest import BacktestEngine
from backtest.strategies import MovingAverageStrategy
from backtest.data import DataLoader

# Load data
loader = DataLoader()
data = loader.load_yahoo('AAPL', start='2022-01-01', end='2023-12-31')

# Run backtest
strategy = MovingAverageStrategy()
engine = BacktestEngine(strategy=strategy)
results = engine.run(data)

# Display results
from backtest.visualization import plot_portfolio_value
import matplotlib.pyplot as plt

plot_portfolio_value(engine.get_portfolio_history()['total_value'])
plt.show()

print(f"Total Return: {results['total_return']:.2f}%")
```

## See Also

- [Getting Started Guide](getting_started.md)
- [API Reference](api_reference.md)
- Example scripts in [examples/](../examples/) directory
