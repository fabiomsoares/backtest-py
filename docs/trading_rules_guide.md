# Trading Rules and Configuration Guide

This guide explains how to configure brokers, assets, and trading rules in the refactored backtest-py framework.

## Table of Contents

1. [Overview](#overview)
2. [Assets and Trading Pairs](#assets-and-trading-pairs)
3. [Brokers](#brokers)
4. [Trading Rules](#trading-rules)
5. [Leverage Types](#leverage-types)
6. [Fee System](#fee-system)
7. [Complete Examples](#complete-examples)

## Overview

The new framework uses a comprehensive configuration system that models real-world broker behavior:

- **Assets**: Individual financial instruments (currencies, stocks, crypto)
- **Trading Pairs**: Combinations of base and quote assets (BTC/USD, AAPL/USD)
- **Brokers**: Trading platforms with specific rules and fees
- **Trading Rules**: Per-broker, per-pair configurations for leverage, fees, and constraints

## Assets and Trading Pairs

### Creating Assets

```python
from decimal import Decimal
from backtest.models import Asset, AssetType

# Currency
usd = Asset(
    ticker="USD",
    name="US Dollar",
    asset_type=AssetType.CURRENCY,
    min_unit=Decimal("0.01")  # Minimum tradeable unit (cents)
)

# Cryptocurrency
btc = Asset(
    ticker="BTC",
    name="Bitcoin",
    asset_type=AssetType.CRYPTO,
    min_unit=Decimal("0.00000001")  # Satoshi
)

# Stock
aapl = Asset(
    ticker="AAPL",
    name="Apple Inc",
    asset_type=AssetType.STOCK,
    min_unit=Decimal("1")  # Whole shares
)
```

### Creating Trading Pairs

```python
from backtest.models import TradingPair

# BTC/USD pair
btcusd = TradingPair(
    base_asset=btc,
    quote_asset=usd,
    contract_size=Decimal("1"),  # 1 contract = 1 BTC
    min_unit=Decimal("0.001")    # Minimum 0.001 BTC per trade
)
# pair_code is auto-generated as "BTCUSD"
```

## Brokers

Brokers represent trading platforms or exchanges:

```python
from backtest.models import Broker

binance = Broker(
    name="Binance",
    code="BINANCE",
    land="GLOBAL",
    description="Leading crypto exchange"
)

xp = Broker(
    name="XP Investimentos",
    code="XP",
    land="BR",
    description="Brazilian brokerage firm"
)
```

## Trading Rules

Trading rules define how a specific pair trades at a specific broker:

```python
from backtest.models import TradingRules, LeverageType

rules = TradingRules(
    broker_id=binance.id,
    pair_code="BTCUSD",
    leverage_type=LeverageType.MARGIN_MULTIPLIER,
    leverage_value=Decimal("10"),  # 10x leverage
    brokerage_fee=fee,  # Fee configuration (see below)
    min_volume=Decimal("0.001"),
    min_notional_amount=Decimal("10"),
    allows_long=True,
    allows_short=True
)
```

### Key Constraints

- **min_volume**: Minimum order size (in base asset units)
- **min_notional_amount**: Minimum order value (in quote asset)
- **min_margin_amount**: Minimum margin required
- **allows_long/allows_short**: Direction restrictions

## Leverage Types

### NO_LEVERAGE

No leverage - full notional value required as margin:

```python
rules = TradingRules(
    broker_id=broker.id,
    pair_code="AAPLUSD",
    leverage_type=LeverageType.NO_LEVERAGE,
    leverage_value=Decimal("1"),
    # ...
)
```

**Margin calculation**: `margin = volume * price * contract_size`

### MARGIN_MULTIPLIER

Margin as a fraction of notional (typical for crypto):

```python
rules = TradingRules(
    broker_id=broker.id,
    pair_code="BTCUSD",
    leverage_type=LeverageType.MARGIN_MULTIPLIER,
    leverage_value=Decimal("10"),  # 10x leverage = 10% margin
    # ...
)
```

**Margin calculation**: `margin = (volume * price * contract_size) / leverage_value`

Example: 0.1 BTC at $50,000 with 10x leverage = $500 margin

### FLAT_MARGIN_PER_VOLUME

Fixed margin per unit of volume:

```python
rules = TradingRules(
    broker_id=broker.id,
    pair_code="EURUSD",
    leverage_type=LeverageType.FLAT_MARGIN_PER_VOLUME,
    leverage_value=Decimal("1000"),  # $1000 margin per lot
    # ...
)
```

**Margin calculation**: `margin = volume * leverage_value`

## Fee System

The framework supports multiple fee types charged at different times.

### Fee Types

#### FLAT_PER_TRADE

Fixed fee per trade:

```python
from backtest.models import Fee, FeeType, FeeTiming

fee = Fee(
    fee_type=FeeType.FLAT_PER_TRADE,
    fee_timing=FeeTiming.ON_FILL,
    amount=Decimal("2.50")  # $2.50 per trade
)
```

#### PERCENT_OF_NOTIONAL

Percentage of trade value:

```python
fee = Fee(
    fee_type=FeeType.PERCENT_OF_NOTIONAL,
    fee_timing=FeeTiming.ON_FILL,
    amount=Decimal("0.001")  # 0.1% of trade value
)
```

#### FLAT_PER_VOLUME

Fee per unit of volume:

```python
fee = Fee(
    fee_type=FeeType.FLAT_PER_VOLUME,
    fee_timing=FeeTiming.ON_FILL,
    amount=Decimal("0.50")  # $0.50 per share/unit
)
```

#### PERCENT_OF_MARGIN

Percentage of margin (for leveraged positions):

```python
leverage_fee = Fee(
    fee_type=FeeType.PERCENT_OF_MARGIN,
    fee_timing=FeeTiming.ON_OVERNIGHT_FILLED,
    amount=Decimal("0.0002")  # 0.02% per day on margin
)
```

### Fee Timings

- **ON_CREATE**: When order is created (rare)
- **ON_FILL**: When order is filled (most common)
- **ON_CLOSE**: When position is closed
- **ON_CANCEL**: When order is cancelled
- **ON_OVERNIGHT_PENDING**: Daily while order is pending
- **ON_OVERNIGHT_FILLED**: Daily while position is open (custody/interest)

### Multiple Fees

Trading rules can have multiple fees:

```python
rules = TradingRules(
    broker_id=broker.id,
    pair_code="AAPLUSD",
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
    leverage_fee=None,  # No leverage fees for stocks
    # ...
)
```

## Complete Examples

### Example 1: Binance Crypto Trading (High Leverage)

```python
from decimal import Decimal
from backtest.models import (
    Asset, AssetType, TradingPair, Broker, TradingRules,
    LeverageType, Fee, FeeType, FeeTiming
)
from backtest.repositories import BacktestContext

# Create context
ctx = BacktestContext()

# Assets
usd = Asset(ticker="USD", name="US Dollar", asset_type=AssetType.CURRENCY)
btc = Asset(ticker="BTC", name="Bitcoin", asset_type=AssetType.CRYPTO, 
            min_unit=Decimal("0.00000001"))

ctx.assets.save(usd)
ctx.assets.save(btc)

# Broker
binance = Broker(name="Binance", code="BINANCE", land="GLOBAL")
ctx.brokers.save(binance)

# Trading pair
btcusd = TradingPair(base_asset=btc, quote_asset=usd, min_unit=Decimal("0.001"))
ctx.trading_pairs.save(btcusd)

# Trading rules
brokerage_fee = Fee(
    fee_type=FeeType.PERCENT_OF_NOTIONAL,
    fee_timing=FeeTiming.ON_FILL,
    amount=Decimal("0.001")  # 0.1% trading fee
)

rules = TradingRules(
    broker_id=binance.id,
    pair_code="BTCUSD",
    leverage_type=LeverageType.MARGIN_MULTIPLIER,
    leverage_value=Decimal("10"),  # 10x leverage
    brokerage_fee=brokerage_fee,
    min_volume=Decimal("0.001"),
    min_notional_amount=Decimal("10"),
    allows_long=True,
    allows_short=True
)
ctx.trading_rules.save(rules)

# Validate an order
volume = Decimal("0.1")
price = Decimal("50000")
available_margin = Decimal("1000")

is_valid, error = rules.validate_order(
    volume=volume,
    price=price,
    margin=available_margin,
    is_long=True
)

required_margin = rules.calculate_margin_required(volume, price)
print(f"Required margin: ${required_margin}")  # $500 (0.1 BTC * $50k / 10)
print(f"Order valid: {is_valid}")
```

### Example 2: XP Brazilian Stocks (No Leverage)

```python
# Assets
usd = Asset(ticker="USD", name="US Dollar", asset_type=AssetType.CURRENCY)
aapl = Asset(ticker="AAPL", name="Apple Inc", asset_type=AssetType.STOCK,
             min_unit=Decimal("1"))

# Broker
xp = Broker(name="XP Investimentos", code="XP", land="BR")

# Trading pair
aaplusd = TradingPair(base_asset=aapl, quote_asset=usd, min_unit=Decimal("1"))

# Trading rules
brokerage_fee = Fee(
    fee_type=FeeType.FLAT_PER_TRADE,
    fee_timing=FeeTiming.ON_FILL,
    amount=Decimal("2.50")  # $2.50 per trade
)

custody_fee = Fee(
    fee_type=FeeType.PERCENT_OF_NOTIONAL,
    fee_timing=FeeTiming.ON_OVERNIGHT_FILLED,
    amount=Decimal("0.0001")  # 0.01% per day custody
)

rules = TradingRules(
    broker_id=xp.id,
    pair_code="AAPLUSD",
    leverage_type=LeverageType.NO_LEVERAGE,
    leverage_value=Decimal("1"),
    brokerage_fee=brokerage_fee,
    custody_fee=custody_fee,
    min_volume=Decimal("1"),  # Minimum 1 share
    min_notional_amount=Decimal("1"),
    allows_long=True,
    allows_short=False  # XP doesn't allow shorting
)
```

### Example 3: Using Setup Helpers

For quick setup, use the provided helpers:

```python
from backtest.repositories import BacktestContext
from backtest.repositories.setup_helpers import setup_example_configuration

ctx = BacktestContext()
config = setup_example_configuration(ctx)

# Now you have:
# - config["assets"]: USD, EUR, BRL, BTC, ETH, AAPL, MSFT
# - config["brokers"]: BINANCE, XP, ACTIVTRADES
# - config["pairs"]: BTCUSD, ETHUSD, AAPLUSD
# - config["rules"]: Pre-configured trading rules for each broker/pair

# Retrieve trading rules
binance = ctx.brokers.get_by_code("BINANCE")
rules = ctx.trading_rules.get_by_broker_and_pair(binance.id, "BTCUSD")
print(f"BTC/USD on Binance: {rules.leverage_value}x leverage")
```

## Best Practices

1. **Use Decimal for all amounts** - Avoid floating point errors
2. **Validate orders before submission** - Use `TradingRules.validate_order()`
3. **Model real broker behavior** - Match actual broker fees and constraints
4. **Test margin calculations** - Use `calculate_margin_required()` to verify
5. **Consider overnight fees** - Important for longer holding periods
6. **Set realistic minimums** - Match actual broker min order sizes

## Next Steps

- See [order_execution.md](order_execution.md) for order lifecycle details
- See [fee_modeling.md](fee_modeling.md) for fee calculation examples
- See [examples/realistic_backtest.py](../examples/realistic_backtest.py) for complete working examples
