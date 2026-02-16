"""
Custom Strategy Example

This script demonstrates how to create a custom trading strategy
using the event-driven pattern with on_bar() method.
"""

import pandas as pd
import numpy as np
from decimal import Decimal
from collections import deque
from typing import Optional, List

from backtest import (
    BacktestEngine,
    BaseStrategy,
    BacktestContext,
    setup_example_configuration,
    TradingOrder,
    OrderDirection,
)
from backtest.models.market_data import BarData


class RSIStrategy(BaseStrategy):
    """
    Simple RSI (Relative Strength Index) strategy using event-driven pattern.

    Generates buy signals when RSI crosses below oversold threshold,
    and sell signals when RSI crosses above overbought threshold.
    """

    def __init__(
        self,
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70,
        name: Optional[str] = None,
    ):
        """
        Initialize RSI strategy.

        Args:
            period: RSI calculation period
            oversold: Oversold threshold (buy signal)
            overbought: Overbought threshold (sell signal)
            name: Strategy name
        """
        super().__init__(name or "RSI_Strategy")
        self.period = period
        self.oversold = Decimal(str(oversold))
        self.overbought = Decimal(str(overbought))

        # Internal state
        self.prices: deque = deque(maxlen=period + 1)
        self.rsi: Optional[Decimal] = None
        self.prev_rsi: Optional[Decimal] = None
        self.position_open = False

    def on_start(self, context: BacktestContext) -> None:
        """Initialize strategy state at start of backtest."""
        self.prices.clear()
        self.rsi = None
        self.prev_rsi = None
        self.position_open = False

    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        """
        Process each bar and generate trading signals based on RSI.

        Args:
            bar: Current bar of market data
            context: Backtest context with access to repositories

        Returns:
            List of TradingOrder objects
        """
        # Add current close price to history
        self.prices.append(bar.close)

        # Need at least period + 1 prices to calculate RSI
        if len(self.prices) <= self.period:
            return []

        # Store previous RSI for crossover detection
        self.prev_rsi = self.rsi

        # Calculate RSI
        self.rsi = self._calculate_rsi()

        # Generate signals based on RSI threshold crossings
        if self.prev_rsi is not None:
            # Buy signal: RSI crosses below oversold threshold
            if self.prev_rsi >= self.oversold and self.rsi < self.oversold:
                if not self.position_open:
                    # Calculate position size (95% of account balance)
                    accounts = context.accounts.get_all()
                    if accounts:
                        account = accounts[0]
                        account_id = str(account.id)
                        balance = self.get_account_balance(context, account_id)

                        if balance:
                            volume = (balance * Decimal("0.95")) / bar.close

                            if volume > Decimal("0"):
                                order = self.create_market_order(
                                    trading_pair_code=bar.symbol,
                                    direction=OrderDirection.LONG,
                                    volume=volume,
                                    current_price=bar.close,
                                    context=context,
                                    account_id=account_id,
                                )
                                self.position_open = True
                                return [order]

            # Sell signal: RSI crosses above overbought threshold
            elif self.prev_rsi <= self.overbought and self.rsi > self.overbought:
                if self.position_open:
                    # Close position by getting active orders
                    accounts = context.accounts.get_all()
                    if accounts:
                        agent_id = accounts[0].agent.id
                        active_orders = context.orders.get_active_orders(agent_id)
                        if active_orders:
                            # Get the order volume to close
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
                                self.position_open = False
                                return [order]

        return []

    def on_end(self, context: BacktestContext) -> None:
        """Close any remaining positions at end of backtest."""
        if self.position_open:
            # Force close any remaining positions
            # This will be handled by the engine's close_all_positions method
            pass

    def _calculate_rsi(self) -> Decimal:
        """
        Calculate RSI for the given window.

        Returns:
            RSI as Decimal (0-100)
        """
        # Get price changes
        prices_list = list(self.prices)
        gains = []
        losses = []

        for i in range(1, len(prices_list)):
            change = prices_list[i] - prices_list[i-1]
            if change > 0:
                gains.append(change)
                losses.append(Decimal("0"))
            else:
                gains.append(Decimal("0"))
                losses.append(abs(change))

        # Calculate average gain and loss
        avg_gain = sum(gains[-self.period:]) / Decimal(str(self.period))
        avg_loss = sum(losses[-self.period:]) / Decimal(str(self.period))

        if avg_loss == 0:
            return Decimal("100")  # Maximum RSI when no losses

        rs = avg_gain / avg_loss
        rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))

        return rsi

    def __repr__(self):
        return (
            f"RSIStrategy(period={self.period}, "
            f"oversold={self.oversold}, overbought={self.overbought})"
        )


def main():
    """Run custom strategy example."""

    print("=" * 60)
    print("Backtest-py: Custom Strategy Example")
    print("=" * 60)
    print()

    # 1. Generate sample data
    print("Generating sample data...")
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    prices = 150 + np.cumsum(np.random.randn(len(dates)) * 2)

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
    print()

    # 2. Setup BacktestContext
    print("Setting up BacktestContext...")
    context = BacktestContext()
    setup_example_configuration(context)
    print(f"✓ Context initialized")
    print()

    # 3. Create custom RSI strategy
    print("Creating custom RSI strategy...")
    strategy = RSIStrategy(
        period=14,
        oversold=30,
        overbought=70,
    )
    print(f"✓ Strategy: {strategy}")
    print()

    # 4. Run backtest
    print("Running backtest...")
    engine = BacktestEngine(
        strategy=strategy,
        context=context,
        initial_capital=Decimal("50000"),
    )

    results = engine.run(data, symbol="AAPL")
    print("✓ Backtest completed!")
    print()

    # 5. Display results
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Initial Capital:  ${results['initial_capital']:,.2f}")
    print(f"Final Balance:    ${results['final_balance']:,.2f}")
    print(f"Total Return:     {results['total_return']:.2f}%")
    print(f"Trades:           {results['num_trades']}")

    if 'win_rate' in results:
        print(f"Win Rate:         {results['win_rate']:.2f}%")
    if 'max_drawdown' in results:
        print(f"Max Drawdown:     {results['max_drawdown']:.2f}%")

    print("=" * 60)
    print()

    print("=" * 60)
    print("✅ Custom strategy example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
