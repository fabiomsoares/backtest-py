"""
Example: Working with the new domain models.

This example demonstrates how to use the new production-grade models
without requiring the full engine refactor. It shows:

1. Creating assets, brokers, and trading pairs
2. Configuring trading rules with fees and leverage
3. Creating and managing orders
4. Tracking P&L and fees
5. Using the repository context

This is a standalone example that works with the current state of the refactoring.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4

from backtest.models import (
    Asset, AssetType, TradingPair, Broker, TraderAgent, Account, TaxRegime,
    TradingRules, LeverageType, FeeType, FeeTiming, Fee,
    TradingOrder, OrderDirection, OrderStatus,
    BarData, TimeFrame, TimeUnit
)
from backtest.repositories import BacktestContext
from backtest.repositories.setup_helpers import setup_example_configuration


def example_1_basic_models():
    """Example 1: Basic model creation and validation."""
    print("=" * 70)
    print("Example 1: Basic Models")
    print("=" * 70)
    
    # Create assets
    usd = Asset(
        ticker="USD",
        name="US Dollar",
        asset_type=AssetType.CURRENCY,
        min_unit=Decimal("0.01")
    )
    
    btc = Asset(
        ticker="BTC",
        name="Bitcoin",
        asset_type=AssetType.CRYPTO,
        min_unit=Decimal("0.00000001")
    )
    
    print(f"✓ Created {usd.ticker} ({usd.asset_type.value})")
    print(f"✓ Created {btc.ticker} ({btc.asset_type.value})")
    
    # Create trading pair
    pair = TradingPair(
        base_asset=btc,
        quote_asset=usd,
        contract_size=Decimal("1"),
        min_unit=Decimal("0.001")
    )
    
    print(f"✓ Created trading pair: {pair.pair_code}")
    print()


def example_2_repository_usage():
    """Example 2: Using repositories to store and retrieve data."""
    print("=" * 70)
    print("Example 2: Repository Usage")
    print("=" * 70)
    
    # Create context
    ctx = BacktestContext()
    
    # Use setup helpers to populate with example data
    config = setup_example_configuration(ctx)
    
    print(f"✓ Setup complete!")
    print(f"  Assets: {len(config['assets'])}")
    print(f"  Brokers: {len(config['brokers'])}")
    print(f"  Trading Pairs: {len(config['pairs'])}")
    print(f"  Trading Rules: {len(config['rules'])}")
    
    # Retrieve data
    btc = ctx.assets.get_by_ticker("BTC")
    print(f"\n✓ Retrieved asset by ticker: {btc.name}")
    
    binance = ctx.brokers.get_by_code("BINANCE")
    print(f"✓ Retrieved broker by code: {binance.name}")
    
    rules = ctx.trading_rules.get_by_broker_and_pair(binance.id, "BTCUSD")
    print(f"✓ Retrieved trading rules: {binance.code}/{rules.pair_code}")
    print(f"  Leverage: {rules.leverage_value}x")
    print(f"  Fee: {rules.brokerage_fee.amount * 100}%")
    print()


def example_3_order_lifecycle():
    """Example 3: Complete order lifecycle with P&L calculation."""
    print("=" * 70)
    print("Example 3: Order Lifecycle")
    print("=" * 70)
    
    # Setup
    ctx = BacktestContext()
    config = setup_example_configuration(ctx)
    
    # Create agent and account
    agent = TraderAgent(name="Example Strategy")
    tax_regime = TaxRegime(name="Standard", income_tax_rate=Decimal("0.15"))
    usd = ctx.assets.get_by_ticker("USD")
    binance = ctx.brokers.get_by_code("BINANCE")
    
    account = Account(
        agent=agent,
        base_asset=usd,
        broker=binance,
        tax_regime=tax_regime,
        initial_balance=Decimal("10000")
    )
    
    ctx.agents.save(agent)
    ctx.tax_regimes.save(tax_regime)
    ctx.accounts.save(account)
    
    # Create a long order
    print("Creating LONG order for 0.1 BTC...")
    order = TradingOrder(
        trading_pair_code="BTCUSD",
        direction=OrderDirection.LONG,
        volume=Decimal("0.1"),
        create_timestamp=datetime(2024, 1, 1, 10, 0),
        create_price=Decimal("50000"),
        stop_loss=Decimal("48000"),
        take_profit=Decimal("55000"),
        leverage=Decimal("10"),
        agent_id=agent.id,
        account_id=account.id,
        broker_id=binance.id,
        backtest_run_id=uuid4()
    )
    
    ctx.orders.save(order)
    print(f"✓ Order created (ID: {order.id})")
    print(f"  Status: {order.status.value}")
    print(f"  Direction: {order.direction.value}")
    print(f"  Volume: {order.volume} BTC")
    print(f"  Stop Loss: ${order.stop_loss}")
    print(f"  Take Profit: ${order.take_profit}")
    
    # Fill order
    print("\nFilling order at $50,100...")
    order.fill(
        fill_timestamp=datetime(2024, 1, 1, 10, 5),
        fill_price=Decimal("50100"),
        fees_on_fill=Decimal("5.01"),  # 0.1% of $5,010 notional
        margin_reserved=Decimal("501")  # $5,010 / 10x = $501
    )
    
    print(f"✓ Order filled")
    print(f"  Fill Price: ${order.fill_price}")
    print(f"  Margin Reserved: ${order.margin_reserved}")
    print(f"  Fees on Fill: ${order.fees_on_fill}")
    
    # Add overnight fees (position held for 3 days)
    print("\nAdding overnight fees...")
    order.add_overnight_fees(Decimal("0.50"))
    order.add_overnight_fees(Decimal("0.50"))
    order.add_overnight_fees(Decimal("0.50"))
    print(f"✓ Overnight fees accumulated: ${order.fees_on_overnight}")
    
    # Close position at take profit
    print("\nClosing position at take profit ($55,000)...")
    order.close(
        close_timestamp=datetime(2024, 1, 4, 14, 30),
        close_price=Decimal("55000"),
        fees_on_close=Decimal("5.50")  # 0.1% of $5,500 notional
    )
    
    print(f"✓ Position closed")
    print(f"  Close Price: ${order.close_price}")
    print(f"  Status: {order.status.value}")
    
    # P&L Summary
    print("\n" + "-" * 40)
    print("P&L Summary:")
    print("-" * 40)
    print(f"Fill Price:     ${order.fill_price:>10}")
    print(f"Close Price:    ${order.close_price:>10}")
    print(f"Volume:         {order.volume:>10} BTC")
    print(f"Gross P&L:      ${order.gross_pnl:>10.2f}")
    print()
    print("Fees Breakdown:")
    print(f"  On Fill:      ${order.fees_on_fill:>10.2f}")
    print(f"  On Close:     ${order.fees_on_close:>10.2f}")
    print(f"  Overnight:    ${order.fees_on_overnight:>10.2f}")
    print(f"  Total Fees:   ${order.total_fees:>10.2f}")
    print()
    print(f"Net P&L:        ${order.net_pnl:>10.2f}")
    print()


def example_4_trading_rules_validation():
    """Example 4: Validating orders against trading rules."""
    print("=" * 70)
    print("Example 4: Trading Rules Validation")
    print("=" * 70)
    
    # Setup
    ctx = BacktestContext()
    config = setup_example_configuration(ctx)
    
    binance = ctx.brokers.get_by_code("BINANCE")
    rules = ctx.trading_rules.get_by_broker_and_pair(binance.id, "BTCUSD")
    
    print(f"Testing orders against {binance.code}/{rules.pair_code} rules:")
    print(f"  Min Volume: {rules.min_volume}")
    print(f"  Min Notional: ${rules.min_notional_amount}")
    print(f"  Leverage: {rules.leverage_value}x")
    print()
    
    # Test 1: Valid order
    print("Test 1: Valid order")
    volume = Decimal("0.1")
    price = Decimal("50000")
    margin = Decimal("1000")
    
    required_margin = rules.calculate_margin_required(volume, price)
    is_valid, error = rules.validate_order(volume, price, margin, is_long=True)
    
    print(f"  Volume: {volume} BTC")
    print(f"  Price: ${price}")
    print(f"  Available Margin: ${margin}")
    print(f"  Required Margin: ${required_margin}")
    print(f"  Result: {'✓ VALID' if is_valid else f'✗ INVALID - {error}'}")
    print()
    
    # Test 2: Insufficient margin
    print("Test 2: Insufficient margin")
    margin = Decimal("400")  # Not enough
    
    is_valid, error = rules.validate_order(volume, price, margin, is_long=True)
    print(f"  Volume: {volume} BTC")
    print(f"  Available Margin: ${margin}")
    print(f"  Required Margin: ${required_margin}")
    print(f"  Result: {'✓ VALID' if is_valid else f'✗ INVALID - {error}'}")
    print()
    
    # Test 3: Volume too small
    print("Test 3: Volume too small")
    volume = Decimal("0.0001")  # Below minimum
    
    is_valid, error = rules.validate_order(volume, price, Decimal("1000"), is_long=True)
    print(f"  Volume: {volume} BTC")
    print(f"  Min Volume: {rules.min_volume}")
    print(f"  Result: {'✓ VALID' if is_valid else f'✗ INVALID - {error}'}")
    print()


def example_5_market_data():
    """Example 5: Working with market data."""
    print("=" * 70)
    print("Example 5: Market Data")
    print("=" * 70)
    
    ctx = BacktestContext()
    
    # Create timeframe
    tf = TimeFrame(unit=TimeUnit.HOUR, multiplier=1)
    print(f"✓ Created timeframe: {tf.code}")
    
    # Create sample bars
    base_time = datetime(2024, 1, 1, 0, 0)
    bars = []
    
    for i in range(24):
        bar = BarData(
            symbol="BTCUSD",
            timeframe=tf,
            timestamp=base_time + timedelta(hours=i),
            open=Decimal("50000") + Decimal(i * 10),
            high=Decimal("50000") + Decimal(i * 10 + 50),
            low=Decimal("50000") + Decimal(i * 10 - 50),
            close=Decimal("50000") + Decimal(i * 10 + 20),
            volume=Decimal("100")
        )
        bars.append(bar)
    
    # Save to repository
    ctx.market_data.save_bars(bars)
    print(f"✓ Saved {len(bars)} bars")
    
    # Retrieve data
    all_bars = ctx.market_data.get_bars("BTCUSD", "1h")
    print(f"✓ Retrieved {len(all_bars)} bars")
    
    # Get latest bar
    latest = ctx.market_data.get_latest_bar("BTCUSD", "1h")
    print(f"✓ Latest bar: {latest.timestamp}, Close: ${latest.close}")
    
    # Get last N bars
    last_5 = ctx.market_data.get_historical_bars("BTCUSD", "1h", 5)
    print(f"✓ Last 5 bars: {last_5[0].timestamp} to {last_5[-1].timestamp}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("=" * 70)
    print("BACKTEST-PY: NEW DOMAIN MODELS EXAMPLES")
    print("=" * 70)
    print()
    
    example_1_basic_models()
    example_2_repository_usage()
    example_3_order_lifecycle()
    example_4_trading_rules_validation()
    example_5_market_data()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
