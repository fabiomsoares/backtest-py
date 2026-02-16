# backtest-py

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-grade backtesting framework in Python for testing trading strategies on historical data with realistic order execution, fee tracking, and comprehensive performance metrics.

## Features

- 🚀 **Event-Driven Architecture**: Modern on_bar() pattern supporting real-time trading workflows
- 💰 **Production-Grade Models**: Decimal precision, realistic fees, leverage support, and P&L tracking
- 📊 **Comprehensive Metrics**: Total return, win rate, max drawdown, and more
- 📈 **Built-in Strategies**: Moving average crossover, momentum, RSI, and more
- 🔧 **Extensible**: Easy to create custom event-driven strategies
- 📦 **Well-Structured**: Clean repository pattern with BacktestContext
- 🧪 **Tested**: Comprehensive test suite with validation
- 📚 **Documented**: Extensive documentation and working examples

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
from backtest import (
    BacktestEngine,
    BacktestContext,
    setup_example_configuration,
)
from backtest.strategies import MovingAverageStrategy
from decimal import Decimal
import pandas as pd

# Load your historical data (DataFrame with 'close' column and datetime index)
# data = pd.read_csv('your_data.csv', index_col='date', parse_dates=True)

# Setup BacktestContext (manages brokers, accounts, orders, etc.)
context = BacktestContext()
setup_example_configuration(context)

# Create an event-driven strategy
strategy = MovingAverageStrategy(fast_window=20, slow_window=50)

# Initialize the backtest engine
engine = BacktestEngine(
    strategy=strategy,
    context=context,
    initial_capital=Decimal("100000"),
)

# Run backtest
results = engine.run(data, symbol="AAPL")

# Display results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Number of Trades: {results['num_trades']}")
if 'win_rate' in results:
    print(f"Win Rate: {results['win_rate']:.2f}%")
if 'max_drawdown' in results:
    print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

## Project Structure

```
backtest-py/
├── backtest/                 # Main package
│   ├── core/                 # Core backtesting engine
│   │   └── engine.py         # Main backtest engine with event-driven execution
│   ├── models/               # Production-grade domain models
│   │   ├── orders.py         # TradingOrder with fees, leverage, P&L tracking
│   │   ├── financial_entities.py  # Account, Broker, Asset, TradingPair
│   │   ├── market_data.py    # BarData, TimeFrame for OHLCV data
│   │   ├── trading_rules.py  # Fee schedules and trading rules
│   │   └── backtest_run.py   # BacktestRun, AccountBalance, AccountTransaction
│   ├── repositories/         # Repository pattern for state management
│   │   ├── context.py        # BacktestContext - central repository manager
│   │   ├── order_repositories.py   # Order and order history repositories
│   │   ├── entity_repositories.py  # Asset, broker, account repositories
│   │   └── setup_helpers.py  # Configuration helpers (Binance, XP, etc.)
│   ├── strategies/           # Event-driven trading strategies
│   │   ├── base.py           # BaseStrategy with on_bar() lifecycle
│   │   ├── moving_average.py # MA crossover strategy
│   │   └── momentum.py       # Momentum strategy
│   ├── metrics/              # Performance metrics
│   │   └── performance.py    # Comprehensive performance calculations
│   └── utils/                # Utility functions
│       └── helpers.py        # Helper functions
├── tests/                    # Test suite
├── examples/                 # Working examples
│   ├── basic_backtest.py     # Simple MA strategy example
│   ├── custom_strategy.py    # Custom RSI strategy example
│   └── new_models_demo.py    # Production features demo
├── docs/                     # Documentation
│   ├── NEW_MODELS.md         # Production models overview
│   ├── trading_rules_guide.md # Fee and trading rules guide
│   └── order_execution.md    # Order lifecycle documentation
└── scripts/                  # Utility scripts
```

## Usage Examples

### Creating a Custom Strategy

```python
from backtest import BaseStrategy, BacktestContext, TradingOrder, OrderDirection
from backtest.models.market_data import BarData
from decimal import Decimal
from typing import List

class MyCustomStrategy(BaseStrategy):
    """Example custom strategy using event-driven pattern."""

    def __init__(self, param1: int = 10):
        super().__init__(name="MyCustomStrategy")
        self.param1 = param1
        self.position_open = False

    def on_start(self, context: BacktestContext) -> None:
        """Called once at start of backtest - initialize state."""
        self.position_open = False
        print(f"Strategy started with param1={self.param1}")

    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        """
        Called for each bar of data - implement your strategy logic here.

        Returns:
            List of TradingOrder objects to execute
        """
        orders = []

        # Your strategy logic here
        # Example: Buy if price drops below threshold
        if bar.close < Decimal("100") and not self.position_open:
            # Calculate position size
            accounts = context.accounts.get_all()
            if accounts:
                account_id = str(accounts[0].id)
                balance = self.get_account_balance(context, account_id)

                volume = (balance * Decimal("0.95")) / bar.close

                order = self.create_market_order(
                    trading_pair_code=bar.symbol,
                    direction=OrderDirection.LONG,
                    volume=volume,
                    current_price=bar.close,
                    context=context,
                    account_id=account_id,
                )
                orders.append(order)
                self.position_open = True

        # Example: Sell if price rises above threshold
        elif bar.close > Decimal("150") and self.position_open:
            # Close position
            accounts = context.accounts.get_all()
            if accounts:
                agent_id = accounts[0].agent.id
                active_orders = context.orders.get_active_orders(agent_id)
                long_orders = [o for o in active_orders if o.direction == OrderDirection.LONG]

                if long_orders:
                    total_volume = sum(o.volume for o in long_orders)
                    account_id = str(accounts[0].id)

                    order = self.create_market_order(
                        trading_pair_code=bar.symbol,
                        direction=OrderDirection.SHORT,
                        volume=total_volume,
                        current_price=bar.close,
                        context=context,
                        account_id=account_id,
                    )
                    orders.append(order)
                    self.position_open = False

        return orders

    def on_end(self, context: BacktestContext) -> None:
        """Called once at end of backtest - cleanup or final reporting."""
        print("Strategy completed")

# Use your strategy
context = BacktestContext()
setup_example_configuration(context)

strategy = MyCustomStrategy(param1=20)
engine = BacktestEngine(strategy=strategy, context=context)
results = engine.run(data)
```

### Loading Data

The framework accepts any pandas DataFrame with a datetime index and at minimum a 'close' column. Optional columns include 'open', 'high', 'low', 'volume'.

```python
import pandas as pd
import yfinance as yf

# From Yahoo Finance (using yfinance)
data = yf.download('AAPL', start='2020-01-01', end='2023-12-31')

# From CSV file
data = pd.read_csv('data/prices.csv', index_col='date', parse_dates=True)

# From your own data source
data = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
}, index=pd.date_range('2020-01-01', periods=100))

# Run backtest with your data
results = engine.run(data, symbol="AAPL")
```

### Accessing Backtest Results

```python
# Run backtest
results = engine.run(data, symbol="AAPL")

# Access metrics
print(f"Initial Capital: ${results['initial_capital']:,.2f}")
print(f"Final Balance: ${results['final_balance']:,.2f}")
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Total P&L: ${results['total_pnl']:,.2f}")
print(f"Number of Trades: {results['num_trades']}")
print(f"Win Rate: {results.get('win_rate', 0):.2f}%")
print(f"Max Drawdown: {results.get('max_drawdown', 0):.2f}%")

# Get order history
orders = engine.get_orders()
for order in orders:
    print(f"{order.direction.name} {order.volume} @ ${order.fill_price}")
    print(f"  P&L: ${order.net_pnl}")

# Get balance history
balance_history = engine.get_balance_history()
print(balance_history)

# You can plot with matplotlib
import matplotlib.pyplot as plt
balance_history['balance'].plot(title='Account Balance Over Time')
plt.ylabel('Balance ($)')
plt.show()
```

## Documentation

- [NEW_MODELS.md](docs/NEW_MODELS.md) - Comprehensive guide to production-grade models
- [trading_rules_guide.md](docs/trading_rules_guide.md) - Fee schedules and trading rules
- [order_execution.md](docs/order_execution.md) - Order lifecycle and execution details
- [Examples](examples/) - Working example scripts demonstrating various features

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

### Current Features (v0.2.0)
- ✅ Event-driven backtesting engine with on_bar() lifecycle
- ✅ Production-grade models with Decimal precision
- ✅ Realistic fee tracking and order execution
- ✅ Repository pattern for state management (BacktestContext)
- ✅ Comprehensive TradingOrder lifecycle (PENDING → FILLED → CLOSED)
- ✅ Built-in strategies (MA crossover, Momentum, RSI)
- ✅ Performance metrics (return, win rate, max drawdown)
- ✅ Stop-loss and take-profit support
- ✅ Account and broker management
- ✅ LONG and SHORT order support
- ✅ P&L tracking with fees
- ✅ Working examples and comprehensive documentation

### Planned Features
- [ ] Multi-asset portfolio support
- [ ] Options and futures support
- [ ] Advanced order types (limit, stop-limit, trailing stop)
- [ ] Slippage modeling
- [ ] Real-time data support
- [ ] REST API interface (FastAPI)
- [ ] Command-line interface (CLI)
- [ ] Strategy optimization and parameter tuning
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] Interactive dashboards
- [ ] Database integration
- [ ] Risk management tools (position sizing, portfolio allocation)

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

## Version History

### v0.2.0 (Current) - Breaking Changes
This release represents a major refactoring with breaking changes:
- **Event-Driven Architecture**: Strategies now use `on_bar()` instead of `generate_signals()`
- **Production Models**: Complete transition to Decimal-based models with realistic fees
- **Repository Pattern**: Introduced BacktestContext for state management
- **Enhanced Order Lifecycle**: Full TradingOrder implementation with P&L tracking
- **Removed**: Old core classes (Order, Portfolio, Position) replaced by production models

To migrate from v0.1.x, see [NEW_MODELS.md](docs/NEW_MODELS.md) for the new API patterns.
