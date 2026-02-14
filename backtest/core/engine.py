"""
Core backtesting engine for executing trading strategies.
"""

from typing import Dict, List, Optional
from datetime import datetime
from backtest.models.strategy import Strategy
from backtest.models.market_data import MarketBar
from backtest.models.portfolio import Portfolio
from backtest.models.order import Order, OrderStatus, OrderSide
from backtest.models.position import Position
from backtest.repositories.market_data_repository import MarketDataRepository
from backtest.repositories.order_repository import OrderRepository
from backtest.repositories.position_repository import PositionRepository
from backtest.repositories.portfolio_repository import PortfolioRepository
from backtest.core.performance import PerformanceMetrics


class BacktestEngine:
    """
    Main backtesting engine that executes trading strategies.
    
    Coordinates data flow, order execution, and portfolio management.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize the backtest engine.
        
        Args:
            initial_capital: Starting capital for the backtest
        """
        self.initial_capital = initial_capital
        self.market_data_repo = MarketDataRepository()
        self.order_repo = OrderRepository()
        self.position_repo = PositionRepository()
        self.portfolio_repo = PortfolioRepository()
        self.current_bar: Optional[MarketBar] = None
    
    def run(self, strategy: Strategy, bars: List[MarketBar]) -> PerformanceMetrics:
        """
        Run a backtest with the given strategy and market data.
        
        Args:
            strategy: Trading strategy to test
            bars: List of market bars to process
            
        Returns:
            Performance metrics for the backtest
        """
        # Initialize portfolio
        portfolio = Portfolio(
            initial_capital=self.initial_capital,
            cash=self.initial_capital
        )
        self.portfolio_repo.save(portfolio)
        
        # Add bars to repository
        self.market_data_repo.add_bars(bars)
        
        # Process each bar
        for bar in sorted(bars, key=lambda b: b.timestamp):
            self.current_bar = bar
            strategy.bars.append(bar)
            
            # Update positions with current prices
            if self.position_repo.exists(bar.symbol):
                position = self.position_repo.get(bar.symbol)
                position.update_price(bar.close)
                self.position_repo.update(position)
            
            # Execute strategy
            strategy.on_bar(bar)
            
            # Process pending orders
            self._process_orders(strategy)
        
        # Calculate performance metrics
        return self._calculate_performance(portfolio)
    
    def _process_orders(self, strategy: Strategy):
        """
        Process pending orders from the strategy.
        
        Args:
            strategy: The trading strategy
        """
        portfolio = self.portfolio_repo.get()
        if not portfolio or not self.current_bar:
            return
        
        for order in strategy.orders:
            if order.status != OrderStatus.PENDING:
                continue
            
            # For market orders, fill immediately at current price
            if order.order_type.value == "market":
                fill_price = self.current_bar.close
                
                # Check if we have enough cash (for buy orders)
                if order.side == OrderSide.BUY:
                    required_cash = order.quantity * fill_price
                    if portfolio.cash < required_cash:
                        order.status = OrderStatus.REJECTED
                        continue
                
                # Fill the order
                order.fill(order.quantity, fill_price)
                self.order_repo.add(order)
                
                # Update portfolio and positions
                self._execute_order(order, portfolio, strategy)
                
                # Notify strategy
                strategy.on_order_filled(order)
    
    def _execute_order(self, order: Order, portfolio: Portfolio, strategy: Strategy):
        """
        Execute a filled order by updating positions and cash.
        
        Args:
            order: The filled order
            portfolio: Current portfolio
            strategy: The trading strategy
        """
        if order.side == OrderSide.BUY:
            # Deduct cash
            cost = order.filled_quantity * order.filled_price
            portfolio.cash -= cost
            
            # Add or update position
            if portfolio.has_position(order.symbol):
                position = portfolio.get_position(order.symbol)
                # Update average entry price
                total_quantity = position.quantity + order.filled_quantity
                total_cost = (position.quantity * position.entry_price) + cost
                position.quantity = total_quantity
                position.entry_price = total_cost / total_quantity
                position.current_price = order.filled_price
            else:
                position = Position(
                    symbol=order.symbol,
                    quantity=order.filled_quantity,
                    entry_price=order.filled_price,
                    entry_time=order.timestamp,
                    current_price=order.filled_price
                )
                portfolio.add_position(position)
                self.position_repo.add(position)
                strategy.positions[order.symbol] = position
        
        elif order.side == OrderSide.SELL:
            # Add cash
            proceeds = order.filled_quantity * order.filled_price
            portfolio.cash += proceeds
            
            # Update or remove position
            if portfolio.has_position(order.symbol):
                position = portfolio.get_position(order.symbol)
                position.quantity -= order.filled_quantity
                
                if position.quantity <= 0:
                    portfolio.remove_position(order.symbol)
                    self.position_repo.delete(order.symbol)
                    if order.symbol in strategy.positions:
                        del strategy.positions[order.symbol]
                else:
                    position.current_price = order.filled_price
                    self.position_repo.update(position)
                    strategy.positions[order.symbol] = position
        
        # Record transaction
        portfolio.record_transaction({
            "timestamp": order.timestamp,
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.filled_quantity,
            "price": order.filled_price,
            "value": order.filled_quantity * order.filled_price
        })
        
        self.portfolio_repo.save(portfolio)
    
    def _calculate_performance(self, portfolio: Portfolio) -> PerformanceMetrics:
        """
        Calculate performance metrics for the backtest.
        
        Args:
            portfolio: Final portfolio state
            
        Returns:
            Performance metrics
        """
        return PerformanceMetrics(
            initial_capital=self.initial_capital,
            final_equity=portfolio.equity,
            total_return=portfolio.total_pnl_percent,
            total_trades=len(portfolio.transaction_history),
            portfolio=portfolio
        )
