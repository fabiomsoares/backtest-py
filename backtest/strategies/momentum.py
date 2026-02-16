"""Momentum-based trading strategy."""

from collections import deque
from typing import List, Optional
from decimal import Decimal

from backtest.strategies.base import BaseStrategy
from backtest.models.market_data import BarData
from backtest.models.orders import TradingOrder, OrderDirection
from backtest.repositories.context import BacktestContext


class MomentumStrategy(BaseStrategy):
    """
    Simple momentum strategy based on rate of change using event-driven pattern.

    Generates buy signals when momentum is positive and above a threshold,
    and sell signals when momentum turns negative or falls below threshold.

    This implementation tracks price history internally and calculates
    momentum incrementally for each bar.

    Attributes:
        lookback_period (int): Period for momentum calculation
        threshold (Decimal): Momentum threshold for generating signals (in percentage)

    Example:
        >>> strategy = MomentumStrategy(lookback_period=20, threshold=Decimal("2.0"))
        >>> engine = BacktestEngine(strategy=strategy)
        >>> results = engine.run(data)
    """

    def __init__(
        self,
        lookback_period: int = 20,
        threshold: float = 0.0,
        name: Optional[str] = None,
    ):
        """
        Initialize the momentum strategy.

        Args:
            lookback_period: Period for calculating momentum
            threshold: Momentum threshold percentage for signals
            name: Optional strategy name
        """
        super().__init__(name)
        self.lookback_period = lookback_period
        self.threshold = Decimal(str(threshold))

        if lookback_period < 1:
            raise ValueError("Lookback period must be at least 1")

        # Internal state for tracking prices and momentum
        self.prices: deque = deque(maxlen=lookback_period + 1)
        self.momentum: Optional[Decimal] = None
        self.prev_momentum: Optional[Decimal] = None
        self.position_open = False  # Track if we have an open position

    def on_start(self, context: BacktestContext) -> None:
        """Initialize strategy state at start of backtest."""
        self.prices.clear()
        self.momentum = None
        self.prev_momentum = None
        self.position_open = False

    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        """
        Process each bar and generate trading signals based on momentum.

        Args:
            bar: Current bar of market data
            context: Backtest context with access to repositories

        Returns:
            List of TradingOrder objects (buy on positive momentum, sell on negative)
        """
        # Add current close price to history
        self.prices.append(bar.close)

        # Need at least lookback_period + 1 prices to calculate momentum
        if len(self.prices) <= self.lookback_period:
            return []

        # Store previous momentum for signal detection
        self.prev_momentum = self.momentum

        # Calculate momentum as percentage change over lookback period
        old_price = self.prices[0]  # Oldest price in the deque
        current_price = self.prices[-1]  # Current price

        if old_price > Decimal("0"):
            self.momentum = ((current_price - old_price) / old_price) * Decimal("100")
        else:
            self.momentum = Decimal("0")

        # Generate signals based on momentum threshold crossings
        if self.prev_momentum is not None:
            # Buy signal: momentum crosses above threshold
            if self.prev_momentum <= self.threshold and self.momentum > self.threshold:
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

            # Sell signal: momentum crosses below threshold
            elif self.prev_momentum >= self.threshold and self.momentum < self.threshold:
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

    def __repr__(self) -> str:
        """String representation of the strategy."""
        return (
            f"MomentumStrategy(lookback_period={self.lookback_period}, "
            f"threshold={self.threshold}%)"
        )
