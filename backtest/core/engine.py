"""Main backtesting engine module using production-grade models."""

from typing import Dict, Optional, Any
from decimal import Decimal
from uuid import uuid4, UUID
from datetime import datetime
import pandas as pd

from backtest.strategies.base import BaseStrategy
from backtest.repositories.context import BacktestContext
from backtest.repositories.setup_helpers import setup_example_configuration
from backtest.models.market_data import BarData, TimeFrame, TimeUnit
from backtest.models.orders import TradingOrder, OrderStatus, OrderDirection
from backtest.models.backtest_run import BacktestRun, AccountBalance, AccountTransaction
from backtest.models.financial_entities import Account


class BacktestEngine:
    """
    Main backtesting engine that executes event-driven strategies on historical data.

    This engine uses production-grade models with Decimal precision, realistic
    fee tracking, and comprehensive order lifecycle management.

    Attributes:
        strategy (BaseStrategy): Event-driven strategy to backtest
        context (BacktestContext): Repository context for managing state
        broker_id (UUID): ID of the broker to use
        account_id (UUID): ID of the trading account
        initial_capital (Decimal): Starting capital

    Example:
        >>> from backtest import BacktestEngine, BaseStrategy, BacktestContext
        >>> from decimal import Decimal
        >>>
        >>> context = BacktestContext()
        >>> setup_example_configuration(context)
        >>>
        >>> strategy = MyStrategy()
        >>> engine = BacktestEngine(
        ...     strategy=strategy,
        ...     context=context,
        ...     initial_capital=Decimal("100000")
        ... )
        >>> run = engine.run(data, symbol="BTCUSDT")
        >>> print(f"Total Return: {run.total_return:.2f}%")
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        context: Optional[BacktestContext] = None,
        broker_id: Optional[UUID] = None,
        account_id: Optional[UUID] = None,
        initial_capital: Decimal = Decimal("100000.0"),
    ):
        """
        Initialize the backtesting engine.

        Args:
            strategy: Event-driven strategy (must implement on_bar)
            context: BacktestContext with repositories (creates default if None)
            broker_id: Broker to use (uses first available if None)
            account_id: Account to use (creates one if None)
            initial_capital: Starting capital amount
        """
        self.strategy = strategy
        self.initial_capital = initial_capital

        # Setup context
        self.context = context
        if self.context is None:
            self.context = BacktestContext()
            setup_example_configuration(self.context)

        # Setup broker
        self.broker_id = broker_id
        if self.broker_id is None:
            brokers = self.context.brokers.get_all()
            if brokers:
                self.broker_id = brokers[0].id
            else:
                raise ValueError("No brokers available in context. Use setup_example_configuration() or add a broker.")

        # Setup account
        self.account_id = account_id
        if self.account_id is None:
            accounts = self.context.accounts.get_all()
            if accounts:
                self.account_id = accounts[0].id
            else:
                # Create a default account
                # Get required entities from context
                brokers = self.context.brokers.get_all()
                assets = self.context.assets.get_all()
                tax_regimes = self.context.tax_regimes.get_all()

                if not brokers or not assets:
                    raise ValueError(
                        "Cannot create default account: missing brokers or assets in context. "
                        "Use setup_example_configuration() to initialize."
                    )

                # Create a simple trader agent
                from backtest.models.financial_entities import TraderAgent, TaxRegime
                agent = TraderAgent(
                    id=uuid4(),
                    name="Default Agent",
                )
                self.context.agents.save(agent)

                # Get or create a simple tax regime
                if not tax_regimes:
                    tax_regime = TaxRegime(
                        id=uuid4(),
                        name="No Tax",
                        income_tax_rate=Decimal("0"),
                        withholding_tax_rate=Decimal("0"),
                    )
                    self.context.tax_regimes.save(tax_regime)
                else:
                    tax_regime = tax_regimes[0]

                account = Account(
                    id=uuid4(),
                    agent=agent,
                    base_asset=assets[0],  # Use first asset as base
                    broker=brokers[0],
                    tax_regime=tax_regime,
                    initial_balance=initial_capital,
                )
                self.context.accounts.save(account)
                self.account_id = account.id

        # Track current run
        self.current_run: Optional[BacktestRun] = None
        self.current_bar: Optional[BarData] = None
        self.current_balance: Decimal = initial_capital  # Track balance in engine

    def run(
        self,
        data: pd.DataFrame,
        symbol: str = "AAPL",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the backtest on historical data.

        Args:
            data: Historical price data with columns ['open', 'high', 'low', 'close', 'volume']
                  Index should be datetime
            symbol: Trading symbol/pair code
            start_date: Optional start date for backtest (format: 'YYYY-MM-DD')
            end_date: Optional end date for backtest (format: 'YYYY-MM-DD')

        Returns:
            Dictionary containing backtest results and metrics

        Example:
            >>> data = pd.DataFrame(...)  # Load historical data
            >>> results = engine.run(data, symbol='BTCUSDT', start_date='2020-01-01')
        """
        # 1. Prepare data
        prepared_data = self._prepare_data(data, start_date, end_date)

        # 2. Reset runtime state
        self.context.reset_runtime_state()
        self.current_balance = self.initial_capital  # Reset balance

        # 3. Create backtest run record (TODO: properly implement BacktestRun)
        self.current_run = None  # Simplified for now

        # 4. Call strategy.on_start()
        self.strategy.on_start(self.context)

        # 5. Iterate through bars
        for timestamp, row in prepared_data.iterrows():
            bar = self._create_bar_data(symbol, timestamp, row)
            self.current_bar = bar
            self._process_bar(bar)

        # 6. Call strategy.on_end()
        self.strategy.on_end(self.context)

        # 7. Close all open positions
        self._close_all_positions()

        # 8. Calculate final metrics
        return self._calculate_metrics()

    def _prepare_data(
        self,
        data: pd.DataFrame,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> pd.DataFrame:
        """
        Prepare and validate input data.

        Args:
            data: Raw historical data
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Prepared and validated DataFrame
        """
        # Make a copy to avoid modifying original
        df = data.copy()

        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'date' in df.columns:
                df.set_index('date', inplace=True)
            df.index = pd.to_datetime(df.index)

        # Filter by date range if specified
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df.index <= pd.to_datetime(end_date)]

        # Validate required columns
        required_columns = ['close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return df

    def _create_bar_data(self, symbol: str, timestamp: pd.Timestamp, row: pd.Series) -> BarData:
        """
        Create BarData from pandas row.

        Args:
            symbol: Trading pair code
            timestamp: Bar timestamp
            row: Pandas series with OHLCV data

        Returns:
            BarData object
        """
        return BarData(
            symbol=symbol,
            timeframe=TimeFrame(unit=TimeUnit.DAY, multiplier=1, offset=0),
            timestamp=timestamp.to_pydatetime(),
            open=Decimal(str(row.get('open', row['close']))),
            high=Decimal(str(row.get('high', row['close']))),
            low=Decimal(str(row.get('low', row['close']))),
            close=Decimal(str(row['close'])),
            volume=Decimal(str(row.get('volume', 0))),
        )

    def _process_bar(self, bar: BarData) -> None:
        """
        Process single bar through strategy and execute orders.

        Args:
            bar: Current bar of market data
        """
        # 1. Generate orders from strategy
        orders = self.strategy.on_bar(bar, self.context)

        # 2. Execute orders
        for order in orders:
            self._execute_order(order, bar)

        # 3. Update open positions with current prices (mark-to-market)
        self._update_open_orders(bar)

        # 4. Check stop-loss and take-profit conditions
        self._check_exit_conditions(bar)

        # 5. Record account balance snapshot
        self._record_balance(bar.timestamp)

    def _execute_order(self, order: TradingOrder, bar: BarData) -> None:
        """
        Execute a trading order.

        Args:
            order: TradingOrder to execute
            bar: Current bar for price
        """
        # Execute at close price (simplified - no slippage for now)
        fill_price = bar.close

        # Calculate fees (simplified - using flat fee for now)
        # TODO: Implement proper fee calculation based on trading rules
        fees_on_fill = fill_price * order.volume * Decimal("0.001")  # 0.1% fee

        if order.direction == OrderDirection.LONG:
            # LONG order: Open a position
            # Fill the order using TradingOrder's fill() method
            order.fill(
                fill_timestamp=bar.timestamp,
                fill_price=fill_price,
                fees_on_fill=fees_on_fill,
            )

            # Update balance - buying decreases cash
            cost = fill_price * order.volume + fees_on_fill
            self.current_balance -= cost

            # Store order in repository as an open position
            self.context.orders.save(order)

            # Record transaction
            transaction = AccountTransaction(
                account_id=self.account_id,
                timestamp=bar.timestamp,
                amount=fill_price * order.volume,
                transaction_type="FILL",
                related_order_id=order.id,
            )
            self.context.account_transactions.save(transaction)

        else:
            # SHORT order: Close open LONG positions
            # Find open LONG orders to close
            filled_orders = self.context.orders.get_filled_orders()
            long_orders = [o for o in filled_orders if o.direction == OrderDirection.LONG
                          and o.trading_pair_code == order.trading_pair_code]

            # Calculate how much volume we can close
            volume_to_close = order.volume
            volume_closed = Decimal("0")

            for long_order in long_orders:
                if volume_to_close <= Decimal("0"):
                    break

                # Close this LONG order
                close_volume = min(long_order.volume, volume_to_close)

                # Calculate fees on close
                fees_on_close = fill_price * close_volume * Decimal("0.001")

                # Close the position
                long_order.close(
                    close_timestamp=bar.timestamp,
                    close_price=fill_price,
                    fees_on_close=fees_on_close,
                )

                # Update balance - closing LONG position returns capital + P&L
                proceeds = fill_price * close_volume - fees_on_close
                self.current_balance += proceeds

                # Save the closed order
                self.context.orders.save(long_order)

                volume_closed += close_volume
                volume_to_close -= close_volume

                # Record transaction
                transaction = AccountTransaction(
                    account_id=self.account_id,
                    timestamp=bar.timestamp,
                    amount=fill_price * close_volume,
                    transaction_type="CLOSE",
                    related_order_id=long_order.id,
                )
                self.context.account_transactions.save(transaction)

            # Note: We don't save the SHORT order as a position since it's just a close signal

    def _update_open_orders(self, bar: BarData) -> None:
        """Update mark-to-market values for open orders."""
        # Get all filled orders (open positions)
        filled_orders = self.context.orders.get_filled_orders()

        for order in filled_orders:
            if order.trading_pair_code == bar.symbol:
                # Update mark-to-market value
                # TODO: More sophisticated position tracking
                pass

    def _check_exit_conditions(self, bar: BarData) -> None:
        """
        Check stop-loss and take-profit conditions for open  orders.

        Args:
            bar: Current bar
        """
        filled_orders = self.context.orders.get_filled_orders()

        for order in filled_orders:
            if order.trading_pair_code != bar.symbol:
                continue

            # Check stop-loss
            if order.stop_loss and bar.low <= order.stop_loss:
                self._close_order(order, order.stop_loss, bar.timestamp, "STOP_LOSS")

            # Check take-profit
            elif order.take_profit and bar.high >= order.take_profit:
                self._close_order(order, order.take_profit, bar.timestamp, "TAKE_PROFIT")

    def _close_order(
        self,
        order: TradingOrder,
        exit_price: Decimal,
        exit_time: datetime,
        reason: str
    ) -> None:
        """
        Close an open order/position.

        Args:
            order: Order to close
            exit_price: Exit price
            exit_time: Exit timestamp
            reason: Close reason
        """
        # Calculate fees on close
        fees_on_close = exit_price * order.volume * Decimal("0.001")  # 0.1% fee

        # Close the order using TradingOrder's close() method
        order.close(
            close_timestamp=exit_time,
            close_price=exit_price,
            fees_on_close=fees_on_close,
        )

        # Update balance
        if order.direction == OrderDirection.LONG:
            # Return capital + P&L
            self.current_balance += (exit_price * order.volume - fees_on_close)
        else:
            # Return capital - P&L
            self.current_balance -= (exit_price * order.volume + fees_on_close)

        self.context.orders.save(order)

    def _close_all_positions(self) -> None:
        """Close all open positions at end of backtest."""
        if self.current_bar is None:
            return

        filled_orders = self.context.orders.get_filled_orders()

        for order in filled_orders:
            self._close_order(
                order,
                self.current_bar.close,
                self.current_bar.timestamp,
                "END_OF_BACKTEST"
            )

    def _record_balance(self, timestamp: datetime) -> None:
        """
        Record account balance snapshot.

        Args:
            timestamp: Current timestamp
        """
        balance = AccountBalance(
            account_id=self.account_id,
            timestamp=timestamp,
            total_balance=self.current_balance,
            available_balance=self.current_balance,
        )
        self.context.account_balances.save(balance)

    def _calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate performance metrics for the backtest.

        Returns:
            Dictionary containing various performance metrics
        """
        final_balance = self.current_balance
        total_return = ((final_balance - self.initial_capital) / self.initial_capital) * Decimal("100")

        # Get all orders
        all_orders = self.context.orders.get_all()
        closed_orders = [o for o in all_orders if o.status == OrderStatus.CLOSED]

        # Calculate total P&L
        total_pnl = sum(o.net_pnl for o in closed_orders if o.net_pnl) or Decimal("0")

        # Basic metrics
        metrics = {
            'initial_capital': float(self.initial_capital),
            'final_balance': float(final_balance),
            'total_return': float(total_return),
            'total_pnl': float(total_pnl),
            'num_trades': len(closed_orders),
            'num_open_positions': len([o for o in all_orders if o.status == OrderStatus.FILLED]),
        }

        # Calculate win rate
        if closed_orders:
            winning_trades = [o for o in closed_orders if o.net_pnl and o.net_pnl > 0]
            metrics['win_rate'] = (len(winning_trades) / len(closed_orders)) * 100
            metrics['num_winning_trades'] = len(winning_trades)
            metrics['num_losing_trades'] = len(closed_orders) - len(winning_trades)

        # Get balance history for additional metrics
        balances = self.context.account_balances.get_all()
        if len(balances) > 1:
            balance_values = [float(b.total_balance) for b in sorted(balances, key=lambda x: x.timestamp)]
            metrics['max_balance'] = max(balance_values)
            metrics['min_balance'] = min(balance_values)

            # Calculate max drawdown
            peak = balance_values[0]
            max_dd = 0
            for value in balance_values:
                if value > peak:
                    peak = value
                dd = ((peak - value) / peak) * 100
                if dd > max_dd:
                    max_dd = dd
            metrics['max_drawdown'] = max_dd

        return metrics

    def get_orders(self) -> list[TradingOrder]:
        """Get all orders from the backtest."""
        return self.context.orders.get_all()

    def get_balance_history(self) -> pd.DataFrame:
        """Get account balance history as a DataFrame."""
        balances = self.context.account_balances.get_all()
        if not balances:
            return pd.DataFrame()

        data = [
            {
                'timestamp': b.timestamp,
                'balance': float(b.total_balance),
            }
            for b in sorted(balances, key=lambda x: x.timestamp)
        ]

        return pd.DataFrame(data).set_index('timestamp')

    def __repr__(self) -> str:
        """String representation of the engine."""
        return (
            f"BacktestEngine(strategy={self.strategy.__class__.__name__}, "
            f"initial_capital={self.initial_capital})"
        )
