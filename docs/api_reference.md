# API Reference

This document provides detailed API reference for the backtest-py framework.

## Core Classes

### BacktestEngine

Main engine for running backtests.

```python
BacktestEngine(strategy, initial_capital=100000.0, commission=0.0)
```

**Parameters:**
- `strategy` (BaseStrategy): Trading strategy to backtest
- `initial_capital` (float): Starting capital amount
- `commission` (float): Commission per trade (percentage if < 1, fixed if >= 1)

**Methods:**

#### run(data, start_date=None, end_date=None)

Run the backtest on historical data.

**Parameters:**
- `data` (DataFrame): Historical OHLCV data
- `start_date` (str, optional): Start date for backtest
- `end_date` (str, optional): End date for backtest

**Returns:** Dictionary with backtest results and metrics

#### get_metrics()

Get performance metrics.

**Returns:** Dictionary with performance metrics

#### get_portfolio_history()

Get portfolio value history.

**Returns:** DataFrame with portfolio values over time

#### get_transactions()

Get transaction history.

**Returns:** DataFrame with all transactions

---

### BaseStrategy

Abstract base class for all trading strategies.

```python
class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # Implementation
        pass
```

**Methods:**

#### generate_signals(data)

Generate trading signals (must be implemented by subclasses).

**Parameters:**
- `data` (DataFrame): Historical price data

**Returns:** DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)

#### validate_data(data)

Validate input data.

**Parameters:**
- `data` (DataFrame): Data to validate

**Raises:** ValueError if data is invalid

---

### Portfolio

Manages portfolio positions and cash.

```python
Portfolio(initial_capital, commission=0.0)
```

**Attributes:**
- `cash` (float): Current cash balance
- `positions` (dict): Current positions by symbol
- `total_value` (float): Total portfolio value

**Methods:**

#### execute_order(order, fill_price, timestamp=None)

Execute an order.

#### update_prices(prices)

Update current prices for positions.

#### get_position(symbol)

Get position for a symbol.

---

### Order

Represents a trading order.

```python
Order(symbol, order_type, side, quantity, price=None)
```

**Parameters:**
- `symbol` (str): Trading symbol
- `order_type` (OrderType): MARKET, LIMIT, STOP, STOP_LIMIT
- `side` (OrderSide): BUY or SELL
- `quantity` (float): Number of shares
- `price` (float, optional): Limit/stop price

---

### Position

Tracks an open position.

```python
Position(symbol, quantity, entry_price, entry_time=None)
```

**Attributes:**
- `unrealized_pnl` (float): Unrealized profit/loss
- `market_value` (float): Current market value
- `entry_price` (float): Average entry price

---

## Strategies

### MovingAverageStrategy

Simple moving average crossover strategy.

```python
MovingAverageStrategy(fast_window=20, slow_window=50, name=None)
```

**Parameters:**
- `fast_window` (int): Fast MA period
- `slow_window` (int): Slow MA period

### MomentumStrategy

Momentum-based strategy.

```python
MomentumStrategy(lookback_period=20, threshold=0.0, name=None)
```

**Parameters:**
- `lookback_period` (int): Momentum calculation period
- `threshold` (float): Momentum threshold percentage

---

## Data Module

### DataLoader

Utility for loading data from various sources.

```python
DataLoader.load_yahoo(symbol, start=None, end=None, interval='1d')
```

Load data from Yahoo Finance.

```python
DataLoader.load_csv(filepath, date_column='date')
```

Load data from CSV file.

---

## Metrics

### Returns

Calculate return metrics.

```python
from backtest.metrics import calculate_returns, calculate_cumulative_returns

returns = calculate_returns(prices, method='simple')
cum_returns = calculate_cumulative_returns(returns)
```

### Risk Metrics

Calculate risk metrics.

```python
from backtest.metrics import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_volatility
)

sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)
max_dd = calculate_max_drawdown(returns)
vol = calculate_volatility(returns)
```

### PerformanceMetrics

Comprehensive metrics calculator.

```python
from backtest.metrics import PerformanceMetrics

metrics = PerformanceMetrics(
    portfolio_values,
    transactions,
    initial_capital=100000
)

results = metrics.calculate_all()
metrics.print_summary()
```

---

## Visualization

### Plot Functions

```python
from backtest.visualization import (
    plot_portfolio_value,
    plot_returns,
    plot_drawdown,
    plot_signals
)

# Plot portfolio value
plot_portfolio_value(portfolio_values)

# Plot returns distribution
plot_returns(returns)

# Plot drawdown
plot_drawdown(returns)

# Plot price with signals
plot_signals(data, signals)
```

---

## Utilities

### Helpers

```python
from backtest.utils import format_currency, calculate_position_size

formatted = format_currency(12345.67)  # "$12,345.67"
size = calculate_position_size(
    capital=100000,
    risk_per_trade=0.02,
    entry_price=150,
    stop_loss_price=145
)
```

### Validators

```python
from backtest.utils import validate_data, validate_strategy

validate_data(data, required_columns=['close'])
validate_strategy(strategy)
```

---

## Enums

### OrderType

- `MARKET`: Market order
- `LIMIT`: Limit order
- `STOP`: Stop order
- `STOP_LIMIT`: Stop-limit order

### OrderSide

- `BUY`: Buy order
- `SELL`: Sell order

### OrderStatus

- `PENDING`: Order pending
- `FILLED`: Order filled
- `PARTIALLY_FILLED`: Partially filled
- `CANCELLED`: Order cancelled
- `REJECTED`: Order rejected
