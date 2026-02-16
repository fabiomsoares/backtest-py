"""
Basic Backtest Example

This script demonstrates how to use the backtest-py framework to run a simple backtest
using a moving average crossover strategy with the new event-driven API.
"""

import pandas as pd
import numpy as np
from decimal import Decimal

from backtest import (
    BacktestEngine,
    BacktestContext,
    setup_example_configuration,
)
from backtest.strategies import MovingAverageStrategy


def main():
    """Run a basic backtest example."""

    print("=" * 60)
    print("Backtest-py: Basic Example")
    print("=" * 60)
    print()

    # 1. Generate sample data
    print("Generating sample data...")
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)

    data = pd.DataFrame({
        'open': prices + np.random.randn(len(dates)) * 0.5,
        'high': prices + abs(np.random.randn(len(dates)) * 1.5),
        'low': prices - abs(np.random.randn(len(dates)) * 1.5),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates)),
    }, index=dates)

    # Ensure valid OHLC relationships
    data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
    data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)

    print(f"✓ Generated {len(data)} days of data")
    print(f"  Data range: {data.index[0].date()} to {data.index[-1].date()}")
    print()

    # 2. Setup BacktestContext
    print("Setting up BacktestContext...")
    context = BacktestContext()
    setup_example_configuration(context)
    print(f"✓ Context initialized")
    print()

    # 3. Create a strategy
    print("Initializing strategy...")
    strategy = MovingAverageStrategy(
        fast_window=20,
        slow_window=50,
        name="MA_20_50"
    )
    print(f"✓ Strategy: {strategy}")
    print()

    # 4. Initialize the backtest engine
    print("Setting up backtest engine...")
    engine = BacktestEngine(
        strategy=strategy,
        context=context,
        initial_capital=Decimal("100000"),
    )
    print(f"✓ Engine initialized")
    print(f"  Initial capital: ${engine.initial_capital:,.2f}")
    print()

    # 5. Run the backtest
    print("Running backtest...")
    results = engine.run(data, symbol="AAPL")
    print("✓ Backtest completed!")
    print()

    # 6. Display results
    print("=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print(f"Initial Capital:      ${results['initial_capital']:,.2f}")
    print(f"Final Balance:        ${results['final_balance']:,.2f}")
    print(f"Total Return:         {results['total_return']:.2f}%")
    print(f"Total P&L:            ${results['total_pnl']:,.2f}")
    print(f"Number of Trades:     {results['num_trades']}")

    if 'win_rate' in results:
        print(f"Win Rate:             {results['win_rate']:.2f}%")
    if 'max_drawdown' in results:
        print(f"Max Drawdown:         {results['max_drawdown']:.2f}%")

    print("=" * 60)
    print()

    # 7. Get order history
    orders = engine.get_orders()
    print(f"Order History: {len(orders)} orders")
    for i, order in enumerate(orders[:5], 1):  # Show first 5 orders
        print(f"  {i}. {order.direction.name} {float(order.volume):.2f} @ ${float(order.fill_price or 0):.2f} - {order.status.name}")
    if len(orders) > 5:
        print(f"  ... and {len(orders) - 5} more orders")
    print()

    # 8. Get balance history
    balance_history = engine.get_balance_history()
    print(f"Balance History: {len(balance_history)} snapshots")
    print()

    print("=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
