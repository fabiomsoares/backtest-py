# Order Execution and Lifecycle

This guide explains how orders work in the refactored backtest-py framework, including order types, lifecycle stages, and fee tracking.

## Table of Contents

1. [Order Model Overview](#order-model-overview)
2. [Order Lifecycle](#order-lifecycle)
3. [Order Types](#order-types)
4. [Creating Orders](#creating-orders)
5. [Order Fills](#order-fills)
6. [Stop Loss and Take Profit](#stop-loss-and-take-profit)
7. [Fee Tracking](#fee-tracking)
8. [P&L Calculation](#pl-calculation)
9. [Complete Examples](#complete-examples)

## Order Model Overview

The `TradingOrder` class tracks the complete lifecycle of an order from creation through fill and eventual close, including all fees at each stage.

### Key Attributes

```python
@dataclass
class TradingOrder:
    # Identity
    id: UUID
    trading_pair_code: str
    direction: OrderDirection  # LONG or SHORT
    volume: Decimal
    
    # Lifecycle timestamps and prices
    create_timestamp: datetime
    create_price: Decimal
    fill_timestamp: Optional[datetime]
    fill_price: Optional[Decimal]
    close_timestamp: Optional[datetime]
    close_price: Optional[Decimal]
    
    # Status
    status: OrderStatus  # PENDING, FILLED, CLOSED, CANCELLED
    
    # Advanced features
    limit_price: Optional[Decimal]  # None = market order
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    leverage: Optional[Decimal]
    
    # Fee tracking
    fees_on_create: Decimal
    fees_on_fill: Decimal
    fees_on_close: Decimal
    fees_on_cancel: Decimal
    fees_on_overnight: Decimal
    
    # Financial tracking
    margin_reserved: Decimal
    gross_pnl: Decimal
    net_pnl: Decimal
```

## Order Lifecycle

An order goes through several states:

```
PENDING → FILLED → CLOSED
    ↓
CANCELLED
```

### State Transitions

1. **PENDING**: Order created, waiting to be filled
   - Order can be cancelled from this state
   - Fees may be charged on creation (rare)

2. **FILLED**: Order filled, position open
   - Margin is reserved
   - Fill fees are charged
   - Overnight fees accumulate daily
   - Stop-loss and take-profit are monitored

3. **CLOSED**: Position closed, realized P&L calculated
   - Close fees are charged
   - Final P&L is calculated
   - Margin is released

4. **CANCELLED**: Order cancelled before fill
   - Cancellation fees may apply
   - No position was opened

## Order Types

### Market Orders

Execute immediately at the next available price:

```python
from backtest.models import TradingOrder, OrderDirection
from datetime import datetime
from decimal import Decimal

order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    limit_price=None,  # Market order
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)
```

### Limit Orders

Execute only when price reaches the limit:

```python
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    limit_price=Decimal("49000"),  # Buy when price drops to $49k
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)
```

**Fill conditions**:
- **LONG** order: Fills when `bar.low <= limit_price`
- **SHORT** order: Fills when `bar.high >= limit_price`

## Creating Orders

### Basic Order Creation

```python
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from backtest.models import TradingOrder, OrderDirection

order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=uuid4()
)

# Save to repository
ctx.orders.save(order)
```

### Order with Stop Loss and Take Profit

```python
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    stop_loss=Decimal("48000"),      # Exit if price drops to $48k
    take_profit=Decimal("55000"),    # Exit if price rises to $55k
    leverage=Decimal("10"),           # Use 10x leverage
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)
```

## Order Fills

### Filling an Order

```python
# Order is filled by the engine when conditions are met
order.fill(
    fill_timestamp=datetime.now(),
    fill_price=Decimal("50100"),
    fees_on_fill=Decimal("5.01"),     # 0.1% of $5,010 notional
    margin_reserved=Decimal("501")    # $5,010 / 10x leverage
)

print(f"Order status: {order.status}")  # FILLED
print(f"Fill price: ${order.fill_price}")
print(f"Margin reserved: ${order.margin_reserved}")
```

### Fill Price Logic

The engine determines fill price based on order type and bar OHLC:

**Market Orders**:
- Filled at bar open or close price (configurable)

**Limit Orders**:
- **LONG buy**: Filled at `max(limit_price, bar.low)` when bar crosses limit
- **SHORT sell**: Filled at `min(limit_price, bar.high)` when bar crosses limit

This provides conservative fill simulation assuming limit orders get filled at or better than the limit price when the market reaches that level.

## Stop Loss and Take Profit

### Monitoring Logic

The engine checks each bar to see if stop-loss or take-profit levels are hit:

**For LONG positions**:
```python
# Stop loss triggered when price drops
if bar.low <= order.stop_loss:
    close_price = order.stop_loss
    trigger_close(order, close_price)

# Take profit triggered when price rises
if bar.high >= order.take_profit:
    close_price = order.take_profit
    trigger_close(order, close_price)
```

**For SHORT positions**:
```python
# Stop loss triggered when price rises
if bar.high >= order.stop_loss:
    close_price = order.stop_loss
    trigger_close(order, close_price)

# Take profit triggered when price drops
if bar.low <= order.take_profit:
    close_price = order.take_profit
    trigger_close(order, close_price)
```

### Example: Setting Stop Loss and Take Profit

```python
# Long position with 4% stop loss and 10% take profit
entry_price = Decimal("50000")
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=entry_price,
    stop_loss=entry_price * Decimal("0.96"),    # 4% below entry
    take_profit=entry_price * Decimal("1.10"),  # 10% above entry
    # ...
)
```

## Fee Tracking

### Fee Accumulation

Fees are tracked separately for each lifecycle stage:

```python
# After order is filled
print(f"Fees on create: ${order.fees_on_create}")
print(f"Fees on fill: ${order.fees_on_fill}")

# After position is closed
print(f"Fees on close: ${order.fees_on_close}")
print(f"Overnight fees: ${order.fees_on_overnight}")
print(f"Total fees: ${order.total_fees}")
```

### Adding Overnight Fees

```python
# Engine adds overnight fees daily for open positions
order.add_overnight_fees(Decimal("0.50"))  # $0.50 per day

# Overnight fees accumulate
order.add_overnight_fees(Decimal("0.50"))  # Now $1.00 total
```

## P&L Calculation

### Gross vs Net P&L

```python
# Gross P&L = price movement * volume
# For LONG: (close_price - fill_price) * volume
# For SHORT: (fill_price - close_price) * volume

# Net P&L = Gross P&L - all fees
```

### Closing a Position

```python
order.close(
    close_timestamp=datetime.now(),
    close_price=Decimal("52000"),
    fees_on_close=Decimal("5.20")  # 0.1% of $5,200 notional
)

print(f"Gross P&L: ${order.gross_pnl}")  # (52000 - 50100) * 0.1 = $190
print(f"Total fees: ${order.total_fees}")  # $5.01 + $5.20 = $10.21
print(f"Net P&L: ${order.net_pnl}")  # $190 - $10.21 = $179.79
```

### Example: Complete Order Lifecycle

```python
from backtest.models import TradingOrder, OrderDirection
from decimal import Decimal
from datetime import datetime, timedelta

# Create order
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime(2024, 1, 1, 10, 0),
    create_price=Decimal("50000"),
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)

print(f"Status: {order.status.value}")  # PENDING

# Fill order
order.fill(
    fill_timestamp=datetime(2024, 1, 1, 10, 1),
    fill_price=Decimal("50100"),
    fees_on_fill=Decimal("5.01"),
    margin_reserved=Decimal("501")
)

print(f"Status: {order.status.value}")  # FILLED
print(f"Filled at: ${order.fill_price}")

# Accumulate overnight fees (position held for 3 days)
order.add_overnight_fees(Decimal("0.50"))  # Day 1
order.add_overnight_fees(Decimal("0.50"))  # Day 2
order.add_overnight_fees(Decimal("0.50"))  # Day 3

# Close position
order.close(
    close_timestamp=datetime(2024, 1, 4, 15, 30),
    close_price=Decimal("52000"),
    fees_on_close=Decimal("5.20")
)

print(f"Status: {order.status.value}")  # CLOSED
print(f"Gross P&L: ${order.gross_pnl:.2f}")  # $190.00
print(f"Fees: ${order.total_fees:.2f}")  # $11.71
print(f"Net P&L: ${order.net_pnl:.2f}")  # $178.29
```

## Complete Examples

### Example 1: Simple Market Order

```python
# Create and immediately fill a market order
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)

# Filled in next bar
order.fill(
    fill_timestamp=datetime.now(),
    fill_price=Decimal("50050"),  # Slippage from create_price
    fees_on_fill=Decimal("5.00"),
    margin_reserved=Decimal("500")
)

# Later, close position
order.close(
    close_timestamp=datetime.now(),
    close_price=Decimal("51000"),
    fees_on_close=Decimal("5.10")
)

print(f"Net P&L: ${order.net_pnl:.2f}")
```

### Example 2: Limit Order with Stop Loss

```python
# Create limit order
order = TradingOrder(
    trading_pair_code="ETHUSD",
    direction=OrderDirection.LONG,
    volume=Decimal("1.0"),
    create_timestamp=datetime(2024, 1, 1, 10, 0),
    create_price=Decimal("2500"),
    limit_price=Decimal("2400"),  # Buy at $2400 or better
    stop_loss=Decimal("2300"),    # Exit if drops to $2300
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)

# Stays PENDING until bar.low <= 2400
# ...
# Bar with low=2380 triggers fill at limit_price
order.fill(
    fill_timestamp=datetime(2024, 1, 1, 14, 0),
    fill_price=Decimal("2400"),
    fees_on_fill=Decimal("2.40"),
    margin_reserved=Decimal("480")  # 5x leverage
)

# Later, bar.low <= 2300 triggers stop loss
order.close(
    close_timestamp=datetime(2024, 1, 2, 9, 0),
    close_price=Decimal("2300"),
    fees_on_close=Decimal("2.30")
)

print(f"Stop loss triggered!")
print(f"Net P&L: ${order.net_pnl:.2f}")  # Negative due to loss and fees
```

### Example 3: Short Position

```python
# Short BTC
order = TradingOrder(
    trading_pair_code="BTCUSD",
    direction=OrderDirection.SHORT,
    volume=Decimal("0.1"),
    create_timestamp=datetime.now(),
    create_price=Decimal("50000"),
    stop_loss=Decimal("51000"),      # Exit if price rises to $51k
    take_profit=Decimal("48000"),    # Exit if price drops to $48k
    agent_id=agent.id,
    account_id=account.id,
    broker_id=broker.id,
    backtest_run_id=run_id
)

order.fill(
    fill_timestamp=datetime.now(),
    fill_price=Decimal("49950"),  # Favorable fill
    fees_on_fill=Decimal("4.995"),
    margin_reserved=Decimal("499.5")
)

# Take profit triggered at $48,000
order.close(
    close_timestamp=datetime.now(),
    close_price=Decimal("48000"),
    fees_on_close=Decimal("4.80")
)

# For SHORT: gross_pnl = (fill_price - close_price) * volume
# = (49950 - 48000) * 0.1 = $195
print(f"Gross P&L: ${order.gross_pnl:.2f}")
print(f"Net P&L: ${order.net_pnl:.2f}")
```

## Best Practices

1. **Always set stop losses** - Protect against large losses
2. **Use appropriate leverage** - Higher leverage = higher risk
3. **Account for fees** - They significantly impact profitability
4. **Model slippage** - Real fills may differ from expected prices
5. **Test edge cases** - Gaps, halts, extreme volatility
6. **Track overnight fees** - Important for positions held multiple days
7. **Validate before creating** - Use `TradingRules.validate_order()`

## Next Steps

- See [trading_rules_guide.md](trading_rules_guide.md) for broker configuration
- See [fee_modeling.md](fee_modeling.md) for detailed fee examples
- See [examples/realistic_backtest.py](../examples/realistic_backtest.py) for complete implementation
