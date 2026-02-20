import pandas as pd
import requests
import io
from decimal import Decimal
from datetime import datetime, date, timedelta
from uuid import uuid4, UUID
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict

from backtest.strategies.base import BaseStrategy
from backtest.repositories.context import BacktestContext
from backtest.models.market_data import BarData
from backtest.models.orders import TradingOrder, OrderDirection, OrderStatus, TradingOrderHistory
from backtest.models.financial_entities import Asset, AssetType, Broker, TraderAgent, TaxRegime, TradingPair, Account
from backtest.models.backtest_run import BacktestRun, AccountBalance, AccountTransaction
from backtest.models.transaction import TransactionType, Transaction
from backtest.core.engine import BacktestEngine

# -------------------------------------------------------------------------
# Custom Brazilian Market Backtest Engine
# -------------------------------------------------------------------------

class BrazilianBacktestEngine(BacktestEngine):
    """
    Custom engine for Brazilian market structure (B3).
    Handles:
    - BRL and Asset (WIN$N) accounts separation
    - Custody fees
    - Flat margin per contract
    - 20% Income Tax with monthly consolidation
    - 1% Withholding Tax (fingers-crossing tax)
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        context: BacktestContext,
        brl_account_id: UUID,
        win_account_id: UUID,
        initial_capital: Decimal,
        contracts_per_order: int = 1
    ):
        # We pass brl_account_id as the primary account for the base engine
        super().__init__(
            strategy=strategy, 
            context=context, 
            account_id=brl_account_id, 
            initial_capital=initial_capital
        )
        self.brl_account_id = brl_account_id
        self.win_account_id = win_account_id
        self.position_size = Decimal(str(contracts_per_order))
        
        # Monthly tracking for tax
        self.monthly_pnl = Decimal("0")
        self.monthly_withholding_tax = Decimal("0")
        self.current_month: Optional[Tuple[int, int]] = None
        
        # Balance tracking
        self.current_brl_balance = initial_capital
        self.current_win_balance = Decimal("0")
        self.current_margin_reserved = Decimal("0")
        
        # Simplified tracking of open position for executing closes
        self.open_position_order: Optional[TradingOrder] = None

    def _execute_order(self, order: TradingOrder, bar: BarData) -> None:
        """
        Overridden execution to handle Open/Close logic explicitly for the example.
        """
        timestamp = bar.timestamp
        fill_price = bar.close
        
        # Snapshot 1: Pending (Initial State)
        self._record_order_history(order, bar)
        
        if order.status == OrderStatus.PENDING:
            
            # Check if this order closes an existing position
            if self.open_position_order:
                # We have an open position.
                if order.direction != self.open_position_order.direction:
                    # Closing trade
                    self._close_position(
                        order, 
                        bar, 
                        entry_price=self.open_position_order.fill_price, 
                        entry_volume=self.open_position_order.volume
                    )
                    
                    order.status = OrderStatus.FILLED
                    order.fill_timestamp = timestamp
                    order.fill_price = fill_price
                    
                    # Snapshot 2: Filled (Closed)
                    self._record_order_history(order, bar)
                    
                    self.open_position_order = None # Position closed
                    
                    # Update WIN Account (Remove units)
                    qty_change = -order.volume if order.direction == OrderDirection.LONG else order.volume
                    
                    self.current_win_balance += qty_change
                    self._record_transaction(
                        self.win_account_id,
                        timestamp,
                        qty_change,
                        Decimal("0"),
                        TransactionType.SPOT_EXCHANGE,
                        f"Close Position WIN$N",
                        order.id
                    )
                    return

            # Opening trade (if no position or same direction - adding not supported in this simple logic, assumes 1 pos max)
            if self.open_position_order is None:
                # Margin Check
                margin_per_contract = Decimal("155.00")
                margin_required = margin_per_contract * order.volume
                
                if self.current_brl_balance < margin_required:
                    order.status = OrderStatus.CANCELLED
                    order.cancel_timestamp = timestamp
                    self._record_order_history(order, bar) # Snapshot: Cancelled
                    return

                # Reserve Margin
                self.current_brl_balance -= margin_required
                self.current_margin_reserved += margin_required
                
                self._record_transaction(
                    self.brl_account_id,
                    timestamp,
                    -margin_required,
                    margin_required,
                    TransactionType.RESERVE_MARGIN,
                    f"Margin reserved",
                    order.id
                )
                
                # Update WIN Account
                qty_change = order.volume if order.direction == OrderDirection.LONG else -order.volume
                self.current_win_balance += qty_change
                
                self._record_transaction(
                    self.win_account_id,
                    timestamp,
                    qty_change,
                    Decimal("0"),
                    TransactionType.SPOT_EXCHANGE,
                    f"Open Position WIN$N",
                    order.id
                )
                
                # Custody Fee
                custody = Decimal("0.50") * order.volume
                self.current_brl_balance -= custody
                self._record_transaction(
                    self.brl_account_id,
                    timestamp,
                    -custody,
                    Decimal("0"),
                    TransactionType.FEE_FILL,
                    "Custody Fee Open",
                    order.id
                )
                
                order.status = OrderStatus.FILLED
                order.fill_timestamp = timestamp
                order.fill_price = fill_price
                order.fees_on_fill = custody
                
                # Snapshot 2: Filled (Open)
                self._record_order_history(order, bar)
                
                self.open_position_order = order # Track open position
            else:
                # Adding to position or error?
                # For simplicity, reject if already open
                order.status = OrderStatus.CANCELLED
                order.cancel_timestamp = timestamp
                self._record_order_history(order, bar)
                return

    def _process_bar(self, bar: BarData) -> None:
        """
        Process single bar: Execute strategy, then update Open Position PnL in Order History.
        """
        super()._process_bar(bar)
        
        # After execution, update history for the open position (Unrealized PnL)
        if self.open_position_order and self.open_position_order.status == OrderStatus.FILLED:
            self._record_order_history(self.open_position_order, bar)

    def _close_position(self, order: TradingOrder, bar: BarData, entry_price: Decimal, entry_volume: Decimal):
        """
        Handle closing a position: PnL, Margin Return, Tax.
        """
        fill_price = bar.close
        timestamp = bar.timestamp
        
        # 1. PnL Calculation (0.20 BRL per point)
        point_value = Decimal("0.20")
        price_diff = fill_price - entry_price
        
        if order.direction == OrderDirection.SHORT: # We are closing a LONG
             gross_pnl = price_diff * entry_volume * point_value
        else: # We are closing a SHORT
             gross_pnl = (entry_price - fill_price) * entry_volume * point_value
             
        # 2. Return Margin
        margin_per_contract = Decimal("155.00")
        margin_released = margin_per_contract * entry_volume
        
        self.current_brl_balance += margin_released
        self.current_margin_reserved -= margin_released
        
        self._record_transaction(
            self.brl_account_id,
            timestamp,
            margin_released,
            -margin_released, # unavailable decreases
            TransactionType.RETURN_MARGIN,
            f"Margin returned",
            order.id
        )

        # 3. Apply Custody Fee on Close
        custody_fee_unit = Decimal("0.50")
        total_custody_fee = custody_fee_unit * entry_volume
        self.current_brl_balance -= total_custody_fee
        
        self._record_transaction(
            self.brl_account_id,
            timestamp,
            -total_custody_fee,
            Decimal("0"),
            TransactionType.FEE_CLOSE,
            "Custody Fee on Close",
            order.id
        )

        # 4. Net PnL and Tax
        net_pnl_before_tax = gross_pnl - total_custody_fee 
        # Note: We deducted custody fee from balance already, so we add Gross PnL to balance
        
        self.current_brl_balance += gross_pnl
        
        self._record_transaction(
             self.brl_account_id,
             timestamp,
             gross_pnl,
             Decimal("0"),
             TransactionType.CLOSE_PNL,
             f"Gross PnL: {gross_pnl:.2f}",
             order.id
        )
        
        # Update monthly accumulator
        self.monthly_pnl += net_pnl_before_tax
        
        # 5. Withholding Tax (1% on positive Net PnL)
        if net_pnl_before_tax > 0:
            wht = net_pnl_before_tax * Decimal("0.01")
            self.current_brl_balance -= wht
            self.monthly_withholding_tax += wht
            
            self._record_transaction(
                 self.brl_account_id,
                 timestamp,
                 -wht,
                 Decimal("0"),
                 TransactionType.ADJUSTMENT, # Using Adjustment for Tax
                 f"Withholding Tax (1%): {wht:.2f}",
                 order.id
            )
            
        # 6. Update Month Logic
        if self.current_month is None:
            self.current_month = (timestamp.year, timestamp.month)
            
        if (timestamp.year, timestamp.month) != self.current_month:
            self._process_monthly_tax(timestamp)
            self.current_month = (timestamp.year, timestamp.month)

    def _process_monthly_tax(self, current_timestamp: datetime):
        """Process end-of-month income tax."""
        if self.monthly_pnl > 0:
            # 20% total tax
            total_tax = self.monthly_pnl * Decimal("0.20")
            # Deduct already paid withholding
            tax_due = total_tax - self.monthly_withholding_tax
            
            if tax_due > 0:
                self.current_brl_balance -= tax_due
                self._record_transaction(
                     self.brl_account_id,
                     current_timestamp,
                     -tax_due,
                     Decimal("0"),
                     TransactionType.ADJUSTMENT,
                     f"Monthly Income Tax Settlement ({self.current_month})",
                )
        
        # Reset monthly counters
        self.monthly_pnl = Decimal("0")
        self.monthly_withholding_tax = Decimal("0")

    def _record_order_history(self, order: TradingOrder, bar: BarData) -> None:
        """Record order history snapshot including unrealized PnL."""
        unrealized_pnl = Decimal("0")
        
        # Calculate Unrealized PnL if filled (and essentially Open)
        if order.status == OrderStatus.FILLED:
            point_value = Decimal("0.20")
            current_price = bar.close
            
            # Assuming fill_price is available
            fill_price = order.fill_price or current_price
            
            if order.direction == OrderDirection.LONG:
                 unrealized_pnl = (current_price - fill_price) * order.volume * point_value
            else:
                 unrealized_pnl = (fill_price - current_price) * order.volume * point_value
        
        history = TradingOrderHistory(
            order_id=order.id,
            timestamp=bar.timestamp,
            status=order.status,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=order.net_pnl, 
            current_price=bar.close
        )
        self.context.order_history.save(history)

    def _record_transaction(self, account_id, timestamp, avail_change, unavail_change, type, desc, order_id=None):
        tx = AccountTransaction(
            account_id=account_id,
            timestamp=timestamp,
            amount=avail_change + unavail_change, # Net change in total equity? Or just amount flow?
            transaction_type=type.name, # Enum to name
            description=desc,
            related_order_id=order_id
        )
        # Note: The Transaction model in codebase might differ slightly in fields, adapting to it.
        # Based on read_file of transaction.py:
        # account_id, backtest_run_id, timestamp, description, available_balance_change, unavailable_balance_change, transaction_type, order_id
        
        real_tx = Transaction(
            account_id=account_id,
            backtest_run_id=self.current_run.id if self.current_run else uuid4(),
            timestamp=timestamp,
            description=desc,
            available_balance_change=avail_change,
            unavailable_balance_change=unavail_change,
            transaction_type=type,
            order_id=order_id
        )
        self.context.account_transactions.save(real_tx)

    # Need to override _process_bar to handle closing logic if simplified engine doesn't
    # or implement a smart Strategy that tracks entry.
    # For this example, I'll rely on the Strategy `on_bar` returning valid orders.
    # And extend `_execute_order` to detect closing trades.

    # Simplified tracking of open position for executing closes
    open_position_order: Optional[TradingOrder] = None

    def _execute_order(self, order: TradingOrder, bar: BarData) -> None:
        """
        Overridden execution to handle Open/Close logic explicitly for the example.
        """
        timestamp = bar.timestamp
        fill_price = bar.close
        
        if order.status == OrderStatus.PENDING:
            
            # Check if this order closes an existing position
            if self.open_position_order:
                # We have an open position.
                if order.direction != self.open_position_order.direction:
                    # Closing trade
                    self._close_position(
                        order, 
                        bar, 
                        entry_price=self.open_position_order.fill_price, 
                        entry_volume=self.open_position_order.volume
                    )
                    
                    order.status = OrderStatus.FILLED
                    order.fill_timestamp = timestamp
                    order.fill_price = fill_price
                    
                    self.open_position_order = None # Position closed
                    
                    # Update WIN Account (Remove units)
                    qty_change = -order.volume if order.direction == OrderDirection.LONG else order.volume
                    # (Logic: if we are buying to close a short, we add back. Wait.
                    # If we held Long (+1), we Sell (-1). Qty change is -1.
                    # If we held Short (-1), we Buy (+1). Qty change is +1.
                    # Correct.)
                    
                    self.current_win_balance += qty_change
                    self._record_transaction(
                        self.win_account_id,
                        timestamp,
                        qty_change,
                        Decimal("0"),
                        TransactionType.SPOT_EXCHANGE,
                        f"Close Position WIN$N",
                        order.id
                    )
                    return

            # Opening trade (if no position or same direction - adding not supported in this simple logic, assumes 1 pos max)
            if self.open_position_order is None:
                # Execute Open Logic (Margin, etc)
                # ... (Logic from previous thought block) ...
                
                # Margin Check
                margin_per_contract = Decimal("155.00")
                margin_required = margin_per_contract * order.volume
                
                if self.current_brl_balance < margin_required:
                    order.status = OrderStatus.CANCELLED
                    return

                # Reserve Margin
                self.current_brl_balance -= margin_required
                self.current_margin_reserved += margin_required
                
                self._record_transaction(
                    self.brl_account_id,
                    timestamp,
                    -margin_required,
                    margin_required,
                    TransactionType.RESERVE_MARGIN,
                    f"Margin reserved",
                    order.id
                )
                
                # Update WIN Account
                qty_change = order.volume if order.direction == OrderDirection.LONG else -order.volume
                self.current_win_balance += qty_change
                
                self._record_transaction(
                    self.win_account_id,
                    timestamp,
                    qty_change,
                    Decimal("0"),
                    TransactionType.SPOT_EXCHANGE,
                    f"Open Position WIN$N",
                    order.id
                )
                
                # Custody Fee
                custody = Decimal("0.50") * order.volume
                self.current_brl_balance -= custody
                self._record_transaction(
                    self.brl_account_id,
                    timestamp,
                    -custody,
                    Decimal("0"),
                    TransactionType.FEE_FILL,
                    "Custody Fee Open",
                    order.id
                )
                
                order.status = OrderStatus.FILLED
                order.fill_timestamp = timestamp
                order.fill_price = fill_price
                order.fees_on_fill = custody
                
                self.open_position_order = order # Track open position
            else:
                # Adding to position or error?
                # For simplicity, reject if already open
                order.status = OrderStatus.CANCELLED
                return
    
    def _record_balance(self, timestamp: datetime) -> None:
        # Record for BRL Account
        bal_brl = AccountBalance(
            account_id=self.brl_account_id,
            timestamp=timestamp,
            total_balance=self.current_brl_balance + self.current_margin_reserved,
            available_balance=self.current_brl_balance,
            unavailable_balance=self.current_margin_reserved
        )
        self.context.account_balances.save(bal_brl)
        
        # Record for WIN Account
        bal_win = AccountBalance(
             account_id=self.win_account_id,
             timestamp=timestamp,
             total_balance=self.current_win_balance,
             available_balance=self.current_win_balance, # All available? Or locked?
             unavailable_balance=Decimal("0")
        )
        self.context.account_balances.save(bal_win)

# -------------------------------------------------------------------------
# Simple Strategy
# -------------------------------------------------------------------------
class SimpleMovingAverageStrategy(BaseStrategy):
    def __init__(self, short_window=10, long_window=30):
        super().__init__("SimpleMA")
        self.short_window = short_window
        self.long_window = long_window
        self.prices = []
        
    def on_bar(self, bar: BarData, context: BacktestContext) -> List[TradingOrder]:
        self.prices.append(float(bar.close))
        if len(self.prices) < self.long_window:
            return []
            
        short_ma = sum(self.prices[-self.short_window:]) / self.short_window
        long_ma = sum(self.prices[-self.long_window:]) / self.long_window
        
        # Simple Logic: Cross check
        # NOTE: This strategy is stateless per bar in this implementation, 
        # normally we track state.
        # But we need to know if we are already in position.
        # Check context for open orders?
        # The engine manages state too.
        
        # Fetch current position from context/engine logic?
        # Since engine tracks open_pos_order locally in my custom engine,
        # verifying state is tricky without querying engine or context.
        # We can query context.account_balances for WIN account?
        
        # Let's assume we return signal, and engine filters if already valid.
        
        orders = []
        if short_ma > long_ma:
            # Bullish Signal -> Buy
            # If we are Short, we Close Short and Open Long (Flip)
            # If we are Flat, we Open Long
            # If we are Long, we Hold
            
            # Create LONG Order
            order = TradingOrder(
                trading_pair_code=bar.symbol,
                direction=OrderDirection.LONG,
                volume=Decimal("1"),
                create_timestamp=bar.timestamp,
                create_price=bar.close,
                agent_id=uuid4(), # Placeholder
                account_id=uuid4(), # Placeholder
                broker_id=uuid4(), # Placeholder
                backtest_run_id=uuid4() # Placeholder
            )
            orders.append(order)
            
        elif short_ma < long_ma:
            # Bearish Signal -> Sell
            order = TradingOrder(
                trading_pair_code=bar.symbol,
                direction=OrderDirection.SHORT,
                volume=Decimal("1"),
                create_timestamp=bar.timestamp,
                create_price=bar.close,
                agent_id=uuid4(),
                account_id=uuid4(),
                broker_id=uuid4(),
                backtest_run_id=uuid4()
            )
            orders.append(order)
            
        return orders

# -------------------------------------------------------------------------
# Main Execution Block
# -------------------------------------------------------------------------
def run_backtest():
    # 1. Setup Context
    context = BacktestContext()
    
    # 2. Setup Entities
    # Assets
    brl = Asset(ticker="BRL", name="Brazilian Real", asset_type=AssetType.CURRENCY)
    win = Asset(ticker="WIN", name="Ibovespa Mini", asset_type=AssetType.INDICE)
    context.assets.save(brl)
    context.assets.save(win)
    
    # Broker
    xp = Broker(name="XP Investimentos", code="XP", land="BR")
    context.brokers.save(xp)
    
    # Agent
    agent = TraderAgent(name="Fábio's Bot")
    context.agents.save(agent)
    
    # Tax Regime
    br_tax = TaxRegime(name="Brazil Futures", income_tax_rate=Decimal("0.20"), withholding_tax_rate=Decimal("0.01"))
    context.tax_regimes.save(br_tax)
    
    # Accounts
    account_brl = Account(agent=agent, base_asset=brl, broker=xp, tax_regime=br_tax, initial_balance=Decimal("10000"))
    account_win = Account(agent=agent, base_asset=win, broker=xp, tax_regime=br_tax, initial_balance=Decimal("0"))
    context.accounts.save(account_brl)
    context.accounts.save(account_win)
    
    # 3. Load Data
    url = "https://www.fabiosoares.com/iamt5/WIN$NM6.csv"
    print(f"Downloading data from {url}...")
    response = requests.get(url)
    content = response.content.decode('utf-16')
    df = pd.read_csv(io.StringIO(content), names=['datetime', 'open', 'high', 'low', 'close', 'tick_volume', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # 4. Run Backtest
    strategy = SimpleMovingAverageStrategy()
    
    engine = BrazilianBacktestEngine(
        strategy=strategy,
        context=context,
        brl_account_id=account_brl.id,
        win_account_id=account_win.id,
        initial_capital=Decimal("10000")
    )
    
    print("Running backtest...")
    engine.run(df, symbol="WIN$N")
    
    # 5. Report
    print("Backtest Complete.")
    print(f"Final BRL Balance: {engine.current_brl_balance}")
    print(f"Final WIN Position: {engine.current_win_balance}")

if __name__ == "__main__":
    run_backtest()
