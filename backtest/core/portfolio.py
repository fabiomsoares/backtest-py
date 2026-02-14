"""Portfolio management and tracking module."""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from backtest.core.position import Position
from backtest.core.order import Order, OrderSide, OrderStatus


class Portfolio:
    """
    Manages portfolio positions, cash, and transaction history.
    
    This class tracks all positions, cash balance, portfolio value over time,
    and maintains a complete transaction history for analysis.
    
    Attributes:
        initial_capital (float): Starting capital
        cash (float): Current cash balance
        positions (Dict[str, Position]): Current open positions by symbol
        transaction_history (List[Dict]): History of all transactions
        portfolio_history (List[Dict]): History of portfolio values over time
        
    Example:
        >>> portfolio = Portfolio(initial_capital=100000)
        >>> portfolio.execute_order(order, fill_price=150.0)
        >>> print(portfolio.total_value)
    """
    
    def __init__(self, initial_capital: float, commission: float = 0.0):
        """
        Initialize a new portfolio.
        
        Args:
            initial_capital: Starting capital amount
            commission: Commission per trade as a fixed amount or percentage
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.positions: Dict[str, Position] = {}
        self.transaction_history: List[Dict] = []
        self.portfolio_history: List[Dict] = []
        self.closed_positions: List[Position] = []
    
    def execute_order(
        self,
        order: Order,
        fill_price: float,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Execute an order and update portfolio.
        
        Args:
            order: Order to execute
            fill_price: Price at which to fill the order
            timestamp: Execution timestamp (defaults to now)
            
        Returns:
            True if order was successfully executed, False otherwise
        """
        timestamp = timestamp or datetime.now()
        
        # Calculate transaction cost
        transaction_value = fill_price * order.quantity
        commission_cost = self._calculate_commission(transaction_value)
        total_cost = transaction_value + commission_cost
        
        # Check if we have enough cash for buy orders
        if order.side == OrderSide.BUY:
            if self.cash < total_cost:
                order.reject()
                return False
        
        # Execute the order
        try:
            if order.side == OrderSide.BUY:
                self._execute_buy(order, fill_price, commission_cost, timestamp)
            else:
                self._execute_sell(order, fill_price, commission_cost, timestamp)
            
            order.fill(order.quantity, fill_price)
            return True
        except Exception as e:
            print(f"Error executing order: {e}")
            order.reject()
            return False
    
    def _execute_buy(
        self,
        order: Order,
        fill_price: float,
        commission: float,
        timestamp: datetime,
    ) -> None:
        """Execute a buy order."""
        total_cost = fill_price * order.quantity + commission
        
        # Update cash
        self.cash -= total_cost
        
        # Update or create position
        if order.symbol in self.positions:
            self.positions[order.symbol].add_shares(order.quantity, fill_price)
        else:
            self.positions[order.symbol] = Position(
                symbol=order.symbol,
                quantity=order.quantity,
                entry_price=fill_price,
                entry_time=timestamp,
            )
        
        # Record transaction
        self._record_transaction(
            timestamp=timestamp,
            symbol=order.symbol,
            side="BUY",
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            cash_flow=-total_cost,
        )
    
    def _execute_sell(
        self,
        order: Order,
        fill_price: float,
        commission: float,
        timestamp: datetime,
    ) -> None:
        """Execute a sell order."""
        if order.symbol not in self.positions:
            raise ValueError(f"Cannot sell {order.symbol}: no position exists")
        
        position = self.positions[order.symbol]
        if order.quantity > position.quantity:
            raise ValueError(
                f"Cannot sell {order.quantity} shares: only {position.quantity} available"
            )
        
        # Close shares and calculate P&L
        realized_pnl = position.close_shares(order.quantity, fill_price)
        proceeds = fill_price * order.quantity - commission
        
        # Update cash
        self.cash += proceeds
        
        # Remove position if fully closed
        if position.is_closed:
            self.closed_positions.append(self.positions.pop(order.symbol))
        
        # Record transaction
        self._record_transaction(
            timestamp=timestamp,
            symbol=order.symbol,
            side="SELL",
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            cash_flow=proceeds,
            realized_pnl=realized_pnl,
        )
    
    def _calculate_commission(self, transaction_value: float) -> float:
        """
        Calculate commission for a transaction.
        
        Args:
            transaction_value: Value of the transaction
            
        Returns:
            Commission amount
        """
        # TODO: Support different commission structures (fixed, percentage, tiered)
        if self.commission < 1:  # Assume percentage if < 1
            return transaction_value * self.commission
        return self.commission
    
    def _record_transaction(
        self,
        timestamp: datetime,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        commission: float,
        cash_flow: float,
        realized_pnl: float = 0.0,
    ) -> None:
        """Record a transaction in the history."""
        self.transaction_history.append({
            "timestamp": timestamp,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "commission": commission,
            "cash_flow": cash_flow,
            "realized_pnl": realized_pnl,
            "cash_balance": self.cash,
        })
    
    def update_prices(self, prices: Dict[str, float]) -> None:
        """
        Update current prices for all positions.
        
        Args:
            prices: Dictionary mapping symbols to current prices
        """
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.update_price(prices[symbol])
    
    def record_portfolio_value(self, timestamp: datetime) -> None:
        """
        Record current portfolio value in history.
        
        Args:
            timestamp: Current timestamp
        """
        self.portfolio_history.append({
            "timestamp": timestamp,
            "cash": self.cash,
            "positions_value": self.positions_value,
            "total_value": self.total_value,
        })
    
    @property
    def positions_value(self) -> float:
        """Calculate total value of all positions."""
        return sum(pos.market_value for pos in self.positions.values())
    
    @property
    def total_value(self) -> float:
        """Calculate total portfolio value (cash + positions)."""
        return self.cash + self.positions_value
    
    @property
    def total_pnl(self) -> float:
        """Calculate total profit/loss."""
        return self.total_value - self.initial_capital
    
    @property
    def total_pnl_percent(self) -> float:
        """Calculate total P&L as a percentage."""
        return (self.total_pnl / self.initial_capital) * 100
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol."""
        return self.positions.get(symbol)
    
    def get_transactions_df(self) -> pd.DataFrame:
        """Get transaction history as a DataFrame."""
        if not self.transaction_history:
            return pd.DataFrame()
        return pd.DataFrame(self.transaction_history)
    
    def get_portfolio_history_df(self) -> pd.DataFrame:
        """Get portfolio value history as a DataFrame."""
        if not self.portfolio_history:
            return pd.DataFrame()
        return pd.DataFrame(self.portfolio_history)
    
    def __repr__(self) -> str:
        """String representation of the portfolio."""
        return (
            f"Portfolio(cash={self.cash:.2f}, "
            f"positions_value={self.positions_value:.2f}, "
            f"total_value={self.total_value:.2f}, "
            f"total_pnl={self.total_pnl:.2f} ({self.total_pnl_percent:.2f}%))"
        )
