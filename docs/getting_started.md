# Getting Started with backtest-py

This guide will help you get started with the backtest-py framework for backtesting trading strategies.

## Installation

### From PyPI (when published)

```bash
pip install backtest-py
```

### From Source

```bash
git clone https://github.com/fabiomsoares/backtest-py.git
cd backtest-py
pip install -e .
```

### With Optional Dependencies

For API support:
```bash
pip install backtest-py[api]
```

For CLI support:
```bash
pip install backtest-py[cli]
```

For development:
```bash
pip install backtest-py[dev]
```

## Quick Start

### 1. Import the Framework

```python
from backtest import BacktestEngine, BaseStrategy
from backtest.strategies import MovingAverageStrategy
from backtest.data import DataLoader
```

### 2. Load Data

```python
# Load from Yahoo Finance
loader = DataLoader()
data = loader.load_yahoo('AAPL', start='2020-01-01', end='2023-12-31')

# Or load from CSV
data = loader.load_csv('path/to/data.csv')
```

### 3. Create a Strategy

Use a built-in strategy:

```python
strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
```

Or create a custom strategy:

```python
class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        # Your logic here
        return signals

strategy = MyStrategy()
```

### 4. Run the Backtest

```python
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=100000,
    commission=0.001
)

results = engine.run(data)
```

### 5. Analyze Results

```python
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

### 6. Visualize Results

```python
from backtest.visualization import plot_portfolio_value, plot_returns

portfolio_history = engine.get_portfolio_history()
plot_portfolio_value(portfolio_history['total_value'])
```

## Creating Custom Strategies

All strategies must inherit from `BaseStrategy` and implement the `generate_signals` method:

```python
from backtest import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1=10, name=None):
        super().__init__(name)
        self.param1 = param1
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.
        
        Returns DataFrame with 'signal' column:
        - 1 for buy
        - -1 for sell
        - 0 for hold
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Your strategy logic here
        # Example: Simple momentum
        signals['momentum'] = data['close'].pct_change(self.param1)
        signals.loc[signals['momentum'] > 0.02, 'signal'] = 1
        signals.loc[signals['momentum'] < -0.02, 'signal'] = -1
        
        return signals[['signal']]
```

## Understanding Results

The backtest engine returns a dictionary with the following metrics:

- **total_return**: Total return as a percentage
- **sharpe_ratio**: Risk-adjusted return metric
- **max_drawdown**: Maximum peak-to-trough decline
- **volatility**: Annualized volatility
- **num_trades**: Total number of trades executed
- **final_value**: Final portfolio value
- **initial_capital**: Starting capital

## Next Steps

- Explore the [API Reference](api_reference.md) for detailed documentation
- Check out more [Examples](examples.md)
- Learn about [Performance Metrics](../backtest/metrics/README.md)
- Create your own strategies
- Optimize strategy parameters

## Common Issues

### Data Loading Errors

If you encounter errors loading data from Yahoo Finance:

```python
# Install yfinance
pip install yfinance

# Or use pandas-datareader
pip install pandas-datareader
```

### Import Errors

Make sure the package is installed:

```bash
pip install -e .
```

### Missing Dependencies

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Getting Help

- Check the [examples](../examples/) directory
- Read the API documentation
- Open an issue on GitHub
- Review test cases in [tests](../tests/) directory
