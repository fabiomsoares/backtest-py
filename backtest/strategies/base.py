"""Base strategy class for all trading strategies."""

from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal

from backtest.models.market_data import BarData
from backtest.models.orders import TradingOrder, OrderDirection, OrderStatus
from backtest.repositories.context import BacktestContext


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies using event-driven pattern.

    All custom strategies must inherit from this class and implement
    the on_bar method to generate trading signals bar-by-bar.

    This design supports both backtesting and live trading since it processes
    data incrementally rather than requiring the full dataset upfront.

    Attributes:
        name (str): Name of the strategy

    Lifecycle Methods:
        on_start: Called once at the beginning of the backtest
        on_bar: Called for each bar of market data
        on_end: Called once at the end of the backtest

    Example:
        >>> class MyStrategy(BaseStrategy):
        ...     def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        ...         # Generate orders based on bar data
        ...         if some_condition:
        ...             order = self.create_market_order(
        ...                 bar.trading_pair_code,
        ...                 OrderDirection.LONG,
        ...                 Decimal("1.0"),
        ...                 context
        ...             )
        ...             return [order]
        ...         return []
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the strategy.

        Args:
            name: Name of the strategy (defaults to class name)
        """
        self.name = name or self.__class__.__name__

    def on_start(self, context: BacktestContext) -> None:
        """
        Called once at the start of the backtest.

        Use this method to initialize strategy state, set up indicators,
        or validate the trading environment.

        Args:
            context: Backtest context with access to all repositories
        """
        pass

    @abstractmethod
    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        """
        Called for each bar of market data.

        This method must be implemented by all concrete strategy classes.
        Process the bar data and return a list of orders to execute.

        Args:
            bar: Current bar of market data with OHLCV
            context: Backtest context with access to repositories

        Returns:
            List of TradingOrder objects to execute (empty list if no action)

        Example:
            >>> def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
            ...     if self.should_buy(bar):
            ...         order = self.create_market_order(
            ...             bar.trading_pair_code,
            ...             OrderDirection.LONG,
            ...             Decimal("1.0"),
            ...             context
            ...         )
            ...         return [order]
            ...     return []
        """
        pass

    def on_end(self, context: BacktestContext) -> None:
        """
        Called once at the end of the backtest.

        Use this method for cleanup, final position closing,
        or logging final strategy state.

        Args:
            context: Backtest context with access to all repositories
        """
        pass

    # Helper methods for creating orders

    def create_market_order(
        self,
        trading_pair_code: str,
        direction: OrderDirection,
        volume: Decimal,
        current_price: Decimal,
        context: BacktestContext,
        account_id: Optional[str] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
    ) -> TradingOrder:
        """
        Create a market order.

        Args:
            trading_pair_code: Trading pair symbol (e.g., "BTCUSDT")
            direction: OrderDirection.LONG or OrderDirection.SHORT
            volume: Order volume in base currency
            current_price: Current market price
            context: Backtest context
            account_id: Account ID (uses first account if None)
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price

        Returns:
            TradingOrder ready to be executed
        """
        from uuid import uuid4, UUID
        from datetime import datetime

        # Get account
        if account_id is None:
            accounts = context.accounts.get_all()
            if not accounts:
                raise ValueError("No accounts available in context")
            account = accounts[0]
        else:
            account_uuid = UUID(account_id) if isinstance(account_id, str) else account_id
            account = context.accounts.get(account_uuid)
            if not account:
                raise ValueError(f"Account {account_id} not found")

        # Generate or get backtest_run_id (placeholder for now)
        # TODO: Get actual backtest_run_id from engine once BacktestRun is implemented
        backtest_run_id = uuid4()

        order = TradingOrder(
            trading_pair_code=trading_pair_code,
            direction=direction,
            volume=volume,
            create_timestamp=datetime.now(),
            create_price=current_price,
            agent_id=account.agent.id,
            account_id=account.id,
            broker_id=account.broker.id,
            backtest_run_id=backtest_run_id,
            status=OrderStatus.PENDING,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        return order

    def create_limit_order(
        self,
        trading_pair_code: str,
        direction: OrderDirection,
        volume: Decimal,
        limit_price: Decimal,
        current_price: Decimal,
        context: BacktestContext,
        account_id: Optional[str] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
    ) -> TradingOrder:
        """
        Create a limit order (for future implementation).

        Note: Currently treated as market order since limit order execution
        is not yet fully implemented in the engine.

        Args:
            trading_pair_code: Trading pair symbol
            direction: OrderDirection.LONG or OrderDirection.SHORT
            volume: Order volume
            limit_price: Limit price for the order
            current_price: Current market price
            context: Backtest context
            account_id: Account ID
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price

        Returns:
            TradingOrder ready to be executed
        """
        # For now, create as market order
        # TODO: Implement proper limit order handling in engine
        return self.create_market_order(
            trading_pair_code=trading_pair_code,
            direction=direction,
            volume=volume,
            current_price=current_price,
            context=context,
            account_id=account_id,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    def get_active_orders(self, context: BacktestContext, account_id: Optional[str] = None) -> List[TradingOrder]:
        """
        Get all active orders for the strategy.

        Args:
            context: Backtest context
            account_id: Filter by account (all accounts if None)

        Returns:
            List of active TradingOrder objects
        """
        if account_id:
            return context.orders.get_by_account(account_id)
        return context.orders.get_active_orders()

    def get_account_balance(self, context: BacktestContext, account_id: str) -> Optional[Decimal]:
        """
        Get current account balance.

        Args:
            context: Backtest context
            account_id: Account ID

        Returns:
            Current balance as Decimal, or None if account not found
        """
        # Get the most recent balance record
        from uuid import UUID
        account_uuid = UUID(account_id) if isinstance(account_id, str) else account_id

        all_balances = context.account_balances.get_all()
        account_balances = [b for b in all_balances if b.account_id == account_uuid]

        if account_balances:
            # Return the most recent balance
            latest_balance = sorted(account_balances, key=lambda x: x.timestamp)[-1]
            return latest_balance.available_balance

        # Fall back to initial balance if no records yet
        account = context.accounts.get(account_uuid)
        if account:
            return account.initial_balance
        return None

    def __repr__(self) -> str:
        """String representation of the strategy."""
        return f"{self.__class__.__name__}(name={self.name})"
