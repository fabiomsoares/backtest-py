# backtest-py

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A simple but sophisticated backtesting framework in Python for testing trading strategies on historical data.

## Features

- 🚀 **Easy to Use**: Simple API for quick backtesting
- 📊 **Comprehensive Metrics**: Sharpe ratio, max drawdown, volatility, and more
- 📈 **Built-in Strategies**: Moving average, momentum, and more
- 🎨 **Visualization**: Beautiful charts and reports
- 🔧 **Extensible**: Easy to create custom strategies
- 📦 **Well-Structured**: Clean, modular codebase
- 🧪 **Tested**: Comprehensive test suite
- 📚 **Documented**: Extensive documentation and examples

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/fabiomsoares/backtest-py.git
cd backtest-py
pip install -e .
```

### Basic Usage

```python
from backtest import BacktestEngine
from backtest.strategies import MovingAverageStrategy
from backtest.data import DataLoader

# Load historical data
loader = DataLoader()
data = loader.load_yahoo('AAPL', start='2020-01-01', end='2023-12-31')

# Create a strategy
strategy = MovingAverageStrategy(fast_window=20, slow_window=50)

# Run backtest
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=100000,
    commission=0.001
)

results = engine.run(data)

# Display results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

## Project Structure

```
backtest-py/
├── backtest/                 # Main package
│   ├── core/                 # Core backtesting engine
│   │   ├── engine.py         # Main backtest engine
│   │   ├── portfolio.py      # Portfolio management
│   │   ├── order.py          # Order execution
│   │   └── position.py       # Position tracking
│   ├── strategies/           # Trading strategies
│   │   ├── base.py           # Base strategy class
│   │   ├── moving_average.py # MA crossover strategy
│   │   └── momentum.py       # Momentum strategy
│   ├── data/                 # Data handling
│   │   ├── loader.py         # Data loading utilities
│   │   ├── provider.py       # Data provider interfaces
│   │   └── preprocessor.py   # Data preprocessing
│   ├── metrics/              # Performance metrics
│   │   ├── returns.py        # Return calculations
│   │   ├── risk.py           # Risk metrics
│   │   └── performance.py    # Overall performance
│   ├── visualization/        # Charts and reports
│   │   ├── plots.py          # Plotting functions
│   │   └── reports.py        # Report generation
│   └── utils/                # Utility functions
│       ├── helpers.py        # Helper functions
│       └── validators.py     # Validation utilities
├── api/                      # REST API (future)
├── cli/                      # Command-line interface (future)
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## Usage Examples

### Creating a Custom Strategy

```python
from backtest import BaseStrategy
import pandas as pd

class MyStrategy(BaseStrategy):
    def __init__(self, param1=10):
        super().__init__()
        self.param1 = param1
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Your strategy logic here
        # 1 = buy, -1 = sell, 0 = hold
        
        return signals

# Use your strategy
strategy = MyStrategy(param1=20)
engine = BacktestEngine(strategy=strategy)
results = engine.run(data)
```

### Loading Data from Different Sources

```python
from backtest.data import DataLoader

loader = DataLoader()

# From Yahoo Finance
data = loader.load_yahoo('AAPL', start='2020-01-01', end='2023-12-31')

# From CSV file
data = loader.load_csv('data/prices.csv')

# From pandas-datareader
data = loader.load_pandas_datareader('AAPL', 'yahoo', '2020-01-01')
```

### Visualizing Results

```python
from backtest.visualization import plot_portfolio_value, plot_returns, plot_drawdown

# Get portfolio history
portfolio_history = engine.get_portfolio_history()
returns = portfolio_history['total_value'].pct_change()

# Create plots
plot_portfolio_value(portfolio_history['total_value'])
plot_returns(returns)
plot_drawdown(returns)
```

### Using in Google Colab

```python
# Install from GitHub
!pip install git+https://github.com/fabiomsoares/backtest-py.git

# Use as normal
from backtest import BacktestEngine
from backtest.strategies import MovingAverageStrategy
from backtest.data import DataLoader

# ... your code ...
```

## Documentation

- [Getting Started Guide](docs/getting_started.md) - Comprehensive introduction
- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Examples](docs/examples.md) - More usage examples
- [Example Scripts](examples/) - Working example scripts

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=backtest
```

### Code Quality

```bash
# Format code
black backtest tests examples

# Lint code
flake8 backtest tests

# Type checking
mypy backtest
```

## Roadmap

### Current Features (v0.1.0)
- ✅ Core backtesting engine
- ✅ Portfolio management
- ✅ Built-in strategies (MA, Momentum)
- ✅ Performance metrics
- ✅ Visualization tools
- ✅ Data loading utilities
- ✅ Comprehensive test suite

### Planned Features
- [ ] Multi-asset portfolio support
- [ ] Options and futures support
- [ ] REST API interface (FastAPI)
- [ ] Command-line interface (CLI)
- [ ] Real-time data support
- [ ] Advanced order types
- [ ] Risk management tools
- [ ] Strategy optimization
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] Interactive dashboards
- [ ] Database integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/fabiomsoares/backtest-py.git
cd backtest-py
pip install -e .[dev]
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by popular backtesting frameworks like Backtrader and Zipline
- Built with Python, pandas, NumPy, and matplotlib
- Thanks to all contributors

## Contact

- GitHub: [@fabiomsoares](https://github.com/fabiomsoares)
- Project Link: [https://github.com/fabiomsoares/backtest-py](https://github.com/fabiomsoares/backtest-py)

## Support

If you find this project helpful, please consider giving it a ⭐️ on GitHub!

---

**Note**: This is an educational project for backtesting trading strategies. Past performance does not guarantee future results. Always do your own research before making investment decisions.
