# New Production-Grade Models (In Progress)

This document explains the new production-grade backtesting framework being added to backtest-py. This is a work-in-progress refactoring that adds realistic broker modeling, advanced order types, and comprehensive fee tracking.

## What's New

### 🎯 Production-Grade Domain Models

The framework now includes comprehensive models for realistic backtesting:

- **Financial Entities**: Assets, Trading Pairs, Brokers, Accounts with tax regimes
- **Trading Rules**: Per-broker, per-pair configurations for leverage, fees, and constraints
- **Advanced Orders**: Stop-loss, take-profit, limit orders with lifecycle tracking
- **Fee System**: Multiple fee types (flat, percentage, margin-based) at different stages
- **Market Data**: TimeFrame-aware bar data with Decimal precision

### 💼 Repository Layer

Type-safe, in-memory data access layer:

- Generic repository pattern with UUID-based storage
- Specialized repositories for assets, brokers, orders, market data
- BacktestContext for centralized data management
- Example configurations (Binance, XP brokers)

### 📚 Comprehensive Documentation

- [Trading Rules Guide](docs/trading_rules_guide.md) - How to configure brokers and trading rules
- [Order Execution Guide](docs/order_execution.md) - Order lifecycle and P&L tracking
- [Working Examples](examples/new_models_demo.py) - Runnable code demonstrations

## Quick Start with New Models

### Installation

```bash
git clone https://github.com/fabiomsoares/backtest-py.git
cd backtest-py
pip install -e .
```

### Basic Example

```python
from decimal import Decimal
from datetime import datetime
from backtest.models import (
    Asset, AssetType, TradingPair, Broker,
    TradingRules, LeverageType, FeeType, FeeTiming, Fee,
    TradingOrder, OrderDirection
)
from backtest.repositories import BacktestContext
from backtest.repositories.setup_helpers import setup_example_configuration

# Create context and load example configuration
ctx = BacktestContext()
config = setup_example_configuration(ctx)

# Get Binance broker and BTC/USD rules
binance = ctx.brokers.get_by_code("BINANCE")
rules = ctx.trading_rules.get_by_broker_and_pair(binance.id, "BTCUSD")

print(f"Leverage: {rules.leverage_value}x")
print(f"Fee: {rules.brokerage_fee.amount * 100}%")

# Calculate required margin for 0.1 BTC at $50k
margin = rules.calculate_margin_required(
    volume=Decimal("0.1"),
    price=Decimal("50000")
)
print(f"Required margin: ${margin}")  # $500 with 10x leverage
```

### Order Lifecycle Example

```python
from uuid import uuid4

# Create a long order with stop-loss and take-profit
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    stop_loss=Decimal("48000"),      # 4% below entry
    take_profit=Decimal("55000"),    # 10% above entry
    leverage=Decimal("10"),
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=uuid4()
)

# Fill the order
order.fill(
    fill_timestamp=datetime.now(),
    fill_price=Decimal("50100"),
    fees_on_fill=Decimal("5.01"),
    margin_reserved=Decimal("501")
)

# Close at take profit
order.close(
    close_timestamp=datetime.now(),
    close_price=Decimal("55000"),
    fees_on_close=Decimal("5.50")
)

print(f"Gross P&L: ${order.gross_pnl:.2f}")
print(f"Net P&L: ${order.net_pnl:.2f}")
```

## Key Features

### 1. Realistic Broker Modeling

Configure brokers with real-world rules:

```python
# Binance - crypto with 10x leverage
binance_rules = TradingRules(
    broker_id=binance.id,
    pair_code="BTCUSD",
    leverage_type=LeverageType.MARGIN_MULTIPLIER,
    leverage_value=Decimal("10"),
    brokerage_fee=Fee(
        fee_type=FeeType.PERCENT_OF_NOTIONAL,
        fee_timing=FeeTiming.ON_FILL,
        amount=Decimal("0.001")  # 0.1%
    ),
    min_volume=Decimal("0.001"),
    allows_long=True,
    allows_short=True
)

# XP - Brazilian stocks, no leverage
xp_rules = TradingRules(
    broker_id=xp.id,
    pair_code="AAPLUSD",
    leverage_type=LeverageType.NO_LEVERAGE,
    brokerage_fee=Fee(
        fee_type=FeeType.FLAT_PER_TRADE,
        fee_timing=FeeTiming.ON_FILL,
        amount=Decimal("2.50")
    ),
    custody_fee=Fee(
        fee_type=FeeType.PERCENT_OF_NOTIONAL,
        fee_timing=FeeTiming.ON_OVERNIGHT_FILLED,
        amount=Decimal("0.0001")  # 0.01% per day
    ),
    allows_long=True,
    allows_short=False
)
```

### 2. Advanced Order Types

- **Market Orders**: Fill immediately at next available price
- **Limit Orders**: Fill when price reaches limit
- **Stop Loss**: Automatic exit on price breach
- **Take Profit**: Automatic exit at target price
- **Leverage**: Configurable margin-based trading

### 3. Comprehensive Fee Tracking

Track fees at every stage:

- **On Create**: Order placement fees (rare)
- **On Fill**: Most common - brokerage fees
- **On Close**: Position closing fees
- **On Cancel**: Cancellation fees
- **Overnight**: Daily custody/interest fees

### 4. Decimal Precision

All financial calculations use Python's `Decimal` type to avoid floating-point errors:

```python
from decimal import Decimal

# Correct
price = Decimal("50000.12")
volume = Decimal("0.1")
notional = price * volume  # Exact calculation

# Avoid
price = 50000.12  # float - may have precision issues
```

### 5. Validation

Built-in validation ensures correct configuration:

```python
# Validate order against trading rules
is_valid, error = rules.validate_order(
    volume=Decimal("0.1"),
    price=Decimal("50000"),
    margin=Decimal("1000"),
    is_long=True
)

if not is_valid:
    print(f"Order rejected: {error}")
```

## Examples

### Run the Demo

```bash
python examples/new_models_demo.py
```

This demonstrates:
1. Basic model creation
2. Repository usage
3. Order lifecycle with P&L
4. Trading rules validation
5. Market data management

### Example Output

```
======================================================================
Example 3: Order Lifecycle
======================================================================
Creating LONG order for 0.1 BTC...
✓ Order created
  Status: PENDING
  Stop Loss: $48000
  Take Profit: $55000

Filling order at $50,100...
✓ Order filled
  Margin Reserved: $501

Closing position at take profit ($55,000)...
✓ Position closed

P&L Summary:
----------------------------------------
Gross P&L:      $    490.00
Total Fees:     $     12.01
Net P&L:        $    477.99
```

## Migration Path

The new models are **additive** and don't break existing code. The current simple backtesting API remains unchanged:

```python
# OLD API - Still works
from backtest import BacktestEngine
from backtest.strategies import MovingAverageStrategy

strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
engine = BacktestEngine(strategy=strategy, initial_capital=100000)
results = engine.run(data)

# NEW API - Production-grade (when engine refactor is complete)
from backtest.models import TradingOrder, OrderDirection
from backtest.repositories import BacktestContext

ctx = BacktestContext()
# ... use new models
```

## What's Not Yet Implemented

This is a work-in-progress. The following are planned but not yet implemented:

- [ ] Refactored BacktestEngine to use new models
- [ ] Event-driven order execution with OHLC price matching
- [ ] Fee calculation engine integrated with orders
- [ ] Margin management and balance tracking
- [ ] Updated strategy interface with callbacks
- [ ] Data loaders for TimeFrame-aware bar data
- [ ] Updated metrics and visualization
- [ ] Complete integration examples
- [ ] Google Colab compatibility testing

## Current Status

✅ **Completed**:
- Domain models with validation
- Repository layer with in-memory storage
- Documentation and examples
- Example broker configurations

🔄 **In Progress**:
- Core engine refactoring (Phase 3)
- Strategy interface updates (Phase 4)

📋 **Planned**:
- Data loader integration
- Metrics updates
- Visualization updates
- Complete examples
- Testing suite

## Documentation

- [Trading Rules Guide](docs/trading_rules_guide.md) - Complete guide with leverage, fees, and constraints
- [Order Execution Guide](docs/order_execution.md) - Order lifecycle, stop-loss, take-profit, and P&L
- [Main README](../README.md) - Original simple API documentation

## Contributing

This is a major refactoring effort. Contributions are welcome! Areas where help is needed:

1. **Engine Refactoring**: Implementing event-driven order execution
2. **Testing**: Writing tests for new models and logic
3. **Examples**: Creating realistic strategy examples
4. **Documentation**: Expanding guides and tutorials
5. **Performance**: Optimizing for large backtests

## Questions?

- See the [examples](examples/new_models_demo.py) for working code
- Read the [guides](docs/) for detailed documentation
- Check the [issues](https://github.com/fabiomsoares/backtest-py/issues) for known limitations

## License

MIT - Same as the main project
