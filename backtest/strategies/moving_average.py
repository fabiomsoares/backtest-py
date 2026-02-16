"""Moving average crossover strategy."""

from collections import deque
from typing import List, Optional
from decimal import Decimal

from backtest.strategies.base import BaseStrategy
from backtest.models.market_data import BarData
from backtest.models.orders import TradingOrder, OrderDirection
from backtest.repositories.context import BacktestContext


class MovingAverageStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy using event-driven pattern.

    Generates buy signals when the fast moving average crosses above
    the slow moving average, and sell signals when it crosses below.

    This implementation tracks price history internally and calculates
    moving averages incrementally for each bar.

    Attributes:
        fast_window (int): Period for fast moving average
        slow_window (int): Period for slow moving average

    Example:
        >>> strategy = MovingAverageStrategy(fast_window=20, slow_window=50)
        >>> engine = BacktestEngine(strategy=strategy)
        >>> results = engine.run(data)
    """

    def __init__(
        self,
        fast_window: int = 20,
        slow_window: int = 50,
        name: Optional[str] = None,
    ):
        """
        Initialize the moving average strategy.

        Args:
            fast_window: Period for fast moving average
            slow_window: Period for slow moving average
            name: Optional strategy name
        """
        super().__init__(name)
        self.fast_window = fast_window
        self.slow_window = slow_window

        if fast_window >= slow_window:
            raise ValueError("Fast window must be smaller than slow window")

        # Internal state for tracking prices and MAs
        self.prices: deque = deque(maxlen=slow_window)
        self.fast_ma: Optional[Decimal] = None
        self.slow_ma: Optional[Decimal] = None
        self.prev_fast_ma: Optional[Decimal] = None
        self.prev_slow_ma: Optional[Decimal] = None
        self.position_open = False  # Track if we have an open position

    def on_start(self, context: BacktestContext) -> None:
        """Initialize strategy state at start of backtest."""
        self.prices.clear()
        self.fast_ma = None
        self.slow_ma = None
        self.prev_fast_ma = None
        self.prev_slow_ma = None
        self.position_open = False

    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        """
        Process each bar and generate trading signals based on MA crossover.

        Args:
            bar: Current bar of market data
            context: Backtest context with access to repositories

        Returns:
            List of TradingOrder objects (buy on golden cross, sell on death cross)
        """
        # Add current close price to history
        self.prices.append(bar.close)

        # Store previous MAs for crossover detection
        self.prev_fast_ma = self.fast_ma
        self.prev_slow_ma = self.slow_ma

        # Calculate current moving averages
        if len(self.prices) >= self.fast_window:
            self.fast_ma = self._calculate_ma(self.fast_window)

        if len(self.prices) >= self.slow_window:
            self.slow_ma = self._calculate_ma(self.slow_window)

        # Check for crossovers (need both current and previous MAs)
        if (
            self.fast_ma is not None
            and self.slow_ma is not None
            and self.prev_fast_ma is not None
            and self.prev_slow_ma is not None
        ):
            # Golden cross: fast MA crosses above slow MA - BUY
            if self.prev_fast_ma <= self.prev_slow_ma and self.fast_ma > self.slow_ma:
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

            # Death cross: fast MA crosses below slow MA - SELL
            elif self.prev_fast_ma >= self.prev_slow_ma and self.fast_ma < self.slow_ma:
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

    def _calculate_ma(self, window: int) -> Decimal:
        """
        Calculate moving average for the given window.

        Args:
            window: Number of periods for the moving average

        Returns:
            Moving average as Decimal
        """
        if len(self.prices) < window:
            window = len(self.prices)

        recent_prices = list(self.prices)[-window:]
        ma = sum(recent_prices) / Decimal(str(window))
        return ma

    def __repr__(self) -> str:
        """String representation of the strategy."""
        return (
            f"MovingAverageStrategy(fast_window={self.fast_window}, "
            f"slow_window={self.slow_window})"
        )
