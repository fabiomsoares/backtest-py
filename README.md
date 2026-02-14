# backtest-py

A simple but sophisticated backtesting framework in Python for testing trading strategies with historical market data.

## Overview

backtest-py is a Python-based backtesting framework designed to help traders and quantitative analysts test their trading strategies using historical data. The framework uses an in-memory database for fast data access and manipulation during backtesting simulations.

## Features

- **In-Memory Database**: Fast data storage and retrieval for efficient backtesting
- **Modular Architecture**: Clean separation between models, data repositories, and core functionality
- **Strategy Testing**: Framework for implementing and testing custom trading strategies
- **Historical Data Support**: Process and analyze historical market data
- **Performance Metrics**: Calculate key performance indicators for trading strategies

## Project Structure

```
backtest-py/
├── backtest/
│   ├── models/          # Data models and entities
│   ├── repositories/    # Data access layer (in-memory database operations)
│   ├── core/           # Core backtesting functionality
│   └── __init__.py
├── tests/              # Unit and integration tests
├── examples/           # Example strategies and usage
├── README.md
└── requirements.txt
```

### Directory Descriptions

- **models/**: Contains data models representing trading entities such as:
  - Market data (OHLCV - Open, High, Low, Close, Volume)
  - Trading positions
  - Orders
  - Portfolio state

- **repositories/**: Data access layer providing an abstraction over the in-memory database:
  - Market data repository
  - Position repository
  - Order repository
  - Portfolio repository

- **core/**: Core backtesting engine and strategy execution:
  - Backtesting engine
  - Strategy base classes
  - Event handling
  - Performance calculation

## Installation

```bash
# Clone the repository
git clone https://github.com/fabiomsoares/backtest-py.git
cd backtest-py

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from backtest.core.engine import BacktestEngine
from backtest.models.strategy import Strategy
from backtest.repositories.market_data_repository import MarketDataRepository

# Initialize the backtesting engine
engine = BacktestEngine()

# Define your trading strategy
class MyStrategy(Strategy):
    def on_bar(self, bar):
        # Implement your strategy logic here
        pass

# Load historical data
market_data = MarketDataRepository()
market_data.load_data('path/to/data.csv')

# Run the backtest
strategy = MyStrategy()
results = engine.run(strategy, market_data)

# Analyze results
print(f"Total Return: {results.total_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
```

## Usage

### Creating a Custom Strategy

Extend the `Strategy` base class and implement your trading logic:

```python
from backtest.models.strategy import Strategy
from backtest.models.order import Order, OrderType

class MovingAverageCrossover(Strategy):
    def __init__(self, short_window=20, long_window=50):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
    
    def on_bar(self, bar):
        # Calculate moving averages
        short_ma = self.get_moving_average(self.short_window)
        long_ma = self.get_moving_average(self.long_window)
        
        # Generate signals
        if short_ma > long_ma and not self.has_position():
            self.buy(bar.close, quantity=100)
        elif short_ma < long_ma and self.has_position():
            self.sell(bar.close, quantity=100)
```

### Loading Market Data

The framework supports loading historical market data into the in-memory database:

```python
from backtest.repositories.market_data_repository import MarketDataRepository

# Initialize repository
repo = MarketDataRepository()

# Load data from CSV
repo.load_from_csv('historical_data.csv')

# Or add data programmatically
from backtest.models.market_data import MarketBar
repo.add_bar(MarketBar(
    timestamp='2023-01-01 09:30:00',
    open=100.0,
    high=102.0,
    low=99.5,
    close=101.5,
    volume=1000000
))
```

## Architecture

The framework follows a clean architecture pattern:

1. **Models Layer**: Defines the data structures and entities
2. **Repository Layer**: Handles data persistence and retrieval (in-memory)
3. **Core Layer**: Contains business logic and backtesting engine
4. **Strategy Layer**: User-defined trading strategies

This separation ensures:
- Easy testing and mocking
- Clear dependencies
- Maintainable and extensible code
- Fast in-memory operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Contact

Fabio Soares - fabio@fabiosoares.com

Project Link: [https://github.com/fabiomsoares/backtest-py](https://github.com/fabiomsoares/backtest-py)
