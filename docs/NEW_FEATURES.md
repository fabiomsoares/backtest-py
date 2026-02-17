# Event-Driven Backtesting System

This document describes the new event-driven backtesting system that supports both spot and trading (derivatives/futures) orders with complete order lifecycle management.

## Overview

The enhanced framework provides:

1. **Dual Order System**: SpotOrder (for direct asset exchange) and TradingOrder (for derivatives/futures)
2. **Transaction-Based Balance Management**: All balance changes tracked through immutable Transaction objects
3. **Available/Unavailable Balance Split**: Proper margin reservation and release
4. **Comprehensive Order Operations**: Create, modify, split, cancel, and close operations
5. **Partial Fills**: Realistic order execution with partial fill support

## Core Concepts

### 1. Transaction System

All balance changes flow through `Transaction` objects:

```python
from backtest.models.transaction import Transaction, TransactionType

# Reserve margin for new order
transaction = Transaction(
    account_id=account_id,
    backtest_run_id=run_id,
    timestamp=datetime.now(),
    description="Reserve margin for order",
    available_balance_change=Decimal("-1000"),
    unavailable_balance_change=Decimal("1000"),
    transaction_type=TransactionType.RESERVE_MARGIN
)
```

**Transaction Types:**
- `RESERVE_MARGIN`: Lock funds for pending order
- `RETURN_MARGIN`: Return funds from cancelled order
- `FEE_CREATE`, `FEE_FILL`, `FEE_CLOSE`, `FEE_CANCEL`: Fee charges
- `FILL_BUY`, `FILL_SELL`: Asset conversion on fills
- `CLOSE_PNL`: Realized P&L from closed positions
- `SPOT_EXCHANGE`: Spot asset exchange

### 2. Balance Management

Balances track available vs unavailable (reserved) funds:

```python
from backtest.models.balance import Balance

balance = Balance(
    account_id=account_id,
    backtest_run_id=run_id,
    timestamp=datetime.now(),
    available_balance=Decimal("95000"),  # Free to use
    unavailable_balance=Decimal("5000")   # Locked in orders
)

print(f"Total: {balance.total_balance}")
print(f"Utilization: {balance.utilization_rate}%")
```

**Balance Reconciliation:**
```python
from backtest.repositories.balance_repository import BalanceRepository

balance_repo = BalanceRepository()

# Reconcile new balance from transactions
new_balance = balance_repo.reconcile_balance(
    account_id=account_id,
    backtest_run_id=run_id,
    timestamp=current_time,
    transactions=transactions_since_last_balance,
    initial_balance=last_balance
)
```

### 3. SpotOrder Lifecycle

SpotOrders represent direct asset exchange (e.g., buying BTC with USD):

```python
from backtest.models.spot_order import SpotOrder
from backtest.models.orders import OrderDirection, OrderStatus

# Create pending order
order = SpotOrder(
    broker_id=broker_id,
    trading_pair_code="BTCUSD",
    agent_id=agent_id,
    account_id=account_id,
    backtest_run_id=run_id,
    order_number=1,
    direction=OrderDirection.LONG,
    status=OrderStatus.PENDING,
    create_timestamp=datetime.now(),
    volume=Decimal("1.5"),
    limit_price=Decimal("50000")  # None for market order
)

# Fill order (immutable, creates new copy)
filled_order = order.create_filled_copy(
    fill_timestamp=datetime.now(),
    fill_price=Decimal("50000"),
    fill_volume=Decimal("1.5"),
    fee_fill=Decimal("37.50")
)

# Partial fill
partial_fill = order.create_filled_copy(
    fill_timestamp=datetime.now(),
    fill_price=Decimal("50000"),
    fill_volume=Decimal("1.0"),  # Only 1.0 of 1.5 filled
    fee_fill=Decimal("25.00")
)
print(f"Remaining: {partial_fill.remaining_volume}")

# Cancel order
cancelled_order = order.create_cancelled_copy(
    cancel_timestamp=datetime.now(),
    cancel_volume=Decimal("1.5"),
    fee_cancel=Decimal("0")
)
```

**SpotOrder States:**
- `PENDING`: Created, waiting to fill
- `FILLED`: Order executed
- `CANCELLED`: Order cancelled before fill

### 4. TradingOrder (Existing, Enhanced)

TradingOrders represent derivatives/futures with leverage:

```python
from backtest.models.orders import TradingOrder

# TradingOrder supports additional states
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("10"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    agent_id=agent_id,
    account_id=account_id,
    broker_id=broker_id,
    backtest_run_id=run_id,
    leverage=Decimal("10"),
    stop_loss=Decimal("48000"),
    take_profit=Decimal("55000")
)
```

**TradingOrder States:**
- `PENDING`: Created, waiting to fill
- `FILLED`: Position open
- `CLOSED`: Position closed with P&L
- `CANCELLED`: Order cancelled before fill

### 5. Repository Pattern

All entities use repositories for storage and querying:

```python
from backtest.repositories.spot_order_repository import SpotOrderRepository
from backtest.repositories.transaction_repository import TransactionRepository
from backtest.repositories.balance_repository import BalanceRepository

# Create repositories
spot_repo = SpotOrderRepository()
transaction_repo = TransactionRepository()
balance_repo = BalanceRepository()

# Query patterns
pending_orders = spot_repo.get_pending_orders(agent_id, run_id)
account_transactions = transaction_repo.get_by_account(account_id, run_id)
latest_balance = balance_repo.get_latest_balance(account_id, run_id)

# Time-based queries
recent_transactions = transaction_repo.get_since_timestamp(
    account_id, 
    last_balance.timestamp
)

# Type-based queries
fee_transactions = transaction_repo.get_by_type(
    TransactionType.FEE_FILL, 
    run_id
)
```

## Design Principles

### Immutability
All domain models are **frozen dataclasses**. Changes create new instances:

```python
# ❌ Wrong - raises error
order.status = OrderStatus.FILLED

# ✅ Correct - creates new instance
filled_order = order.create_filled_copy(...)
```

### Decimal Precision
All financial calculations use `Decimal` for precision:

```python
from decimal import Decimal

# ✅ Correct
volume = Decimal("1.5")
price = Decimal("50000.00")

# ❌ Wrong - float precision issues
volume = 1.5
price = 50000.0
```

### Transaction-First
**ALL balance changes must go through Transactions**:

```python
# ✅ Correct - explicit transaction
transaction = Transaction(
    available_balance_change=Decimal("-100"),
    unavailable_balance_change=Decimal("100"),
    ...
)

# ❌ Wrong - direct balance modification
balance.available_balance -= Decimal("100")
```

## Examples

See working examples in the `examples/` directory:

1. **transaction_balance_system.py**: Demonstrates transaction-based balance tracking
2. **spot_order_lifecycle.py**: Demonstrates spot order creation, filling, and cancellation

Run examples:
```bash
PYTHONPATH=. python examples/transaction_balance_system.py
PYTHONPATH=. python examples/spot_order_lifecycle.py
```

## Testing

All new components have comprehensive unit tests:

```bash
# Test models
pytest tests/test_models/ -v

# Test repositories  
pytest tests/test_repositories/ -v

# Test all
pytest tests/ -v
```

Current test coverage:
- 36 model tests (Transaction, SpotOrder, Balance)
- 16 repository tests (TransactionRepository, BalanceRepository)
- 75 total tests passing

## Architecture

```
Models (Immutable Dataclasses)
├── SpotOrder (frozen)
├── TradingOrder (mutable, to be frozen)
├── Transaction (frozen)
├── Balance (frozen)
└── DecisionAction

Repositories (In-Memory Storage)
├── SpotOrderRepository
├── OrderRepository (TradingOrder)
├── TransactionRepository
└── BalanceRepository

Services (To Be Implemented)
├── OrderOperations
├── TransactionManager
└── BacktestRunner
```

## Roadmap

**Completed:**
- ✅ Core models (Transaction, SpotOrder, Balance, DecisionAction)
- ✅ Repository infrastructure with specialized queries
- ✅ Balance reconciliation logic
- ✅ Working examples

**In Progress:**
- 🔄 Order operations (create, modify, split, cancel, close)
- 🔄 BacktestContext enhancements
- 🔄 TradingOrder immutability

**Planned:**
- 📋 6-phase backtest execution cycle
- 📋 Strategy interface updates
- 📋 Partial fill logic
- 📋 Stop-loss/take-profit triggers
- 📋 Integration tests
- 📋 Complete documentation

## Contributing

When adding new features:

1. **Models must be frozen**: Use `@dataclass(frozen=True)`
2. **Use Decimal for money**: Never use float for financial calculations
3. **Test everything**: Add unit tests for all new code
4. **Transaction-based**: All balance changes through Transaction objects
5. **Immutable updates**: Create new instances instead of modifying

## License

MIT License - See LICENSE file for details
