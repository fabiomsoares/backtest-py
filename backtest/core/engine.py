"""Main backtesting engine module."""

from typing import Dict, Optional, Any
import pandas as pd
from datetime import datetime

from backtest.core.portfolio import Portfolio
from backtest.core.order import Order, OrderType, OrderSide
from backtest.strategies.base import BaseStrategy


class BacktestEngine:
    """
    Main backtesting engine that executes strategies on historical data.
    
    This class orchestrates the backtesting process, including data iteration,
    signal generation, order execution, and performance tracking.
    
    Attributes:
        strategy (BaseStrategy): Trading strategy to backtest
        initial_capital (float): Starting capital
        commission (float): Commission per trade
        portfolio (Portfolio): Portfolio manager
        
    Example:
        >>> from backtest import BacktestEngine, BaseStrategy
        >>> strategy = MyStrategy()
        >>> engine = BacktestEngine(
        ...     strategy=strategy,
        ...     initial_capital=100000,
        ...     commission=0.001
        ... )
        >>> results = engine.run(data)
        >>> metrics = engine.get_metrics()
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 100000.0,
        commission: float = 0.0,
    ):
        """
        Initialize the backtesting engine.
        
        Args:
            strategy: Trading strategy to backtest
            initial_capital: Starting capital amount
            commission: Commission per trade (fixed amount or percentage if < 1)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.portfolio = Portfolio(initial_capital=initial_capital, commission=commission)
        self.data: Optional[pd.DataFrame] = None
        self.results: Dict[str, Any] = {}
    
    def run(
        self,
        data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the backtest on historical data.
        
        Args:
            data: Historical price data with columns ['open', 'high', 'low', 'close', 'volume']
                  Index should be datetime
            start_date: Optional start date for backtest (format: 'YYYY-MM-DD')
            end_date: Optional end date for backtest (format: 'YYYY-MM-DD')
            
        Returns:
            Dictionary containing backtest results and metrics
            
        Example:
            >>> data = pd.DataFrame(...)  # Load historical data
            >>> results = engine.run(data, start_date='2020-01-01', end_date='2021-12-31')
        """
        # Validate and prepare data
        self.data = self._prepare_data(data, start_date, end_date)
        
        # Validate data with strategy
        self.strategy.validate_data(self.data)
        
        # Generate signals
        signals = self.strategy.generate_signals(self.data)
        
        # Execute backtest
        self._execute_backtest(signals)
        
        # Calculate metrics
        self.results = self.get_metrics()
        
        return self.results
    
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
    
    def _execute_backtest(self, signals: pd.DataFrame) -> None:
        """
        Execute the backtest by processing signals and managing portfolio.
        
        Args:
            signals: DataFrame with trading signals
        """
        # Merge data and signals
        data_with_signals = self.data.join(signals, how='left')
        
        # Iterate through each time period
        for timestamp, row in data_with_signals.iterrows():
            # Get current prices
            current_price = row['close']
            prices = {'default': current_price}
            
            # Update portfolio prices
            self.portfolio.update_prices(prices)
            
            # Process trading signals
            # TODO: Support multiple symbols
            signal = row.get('signal', 0)
            symbol = 'default'
            
            if signal != 0:
                self._process_signal(
                    symbol=symbol,
                    signal=signal,
                    price=current_price,
                    timestamp=timestamp,
                )
            
            # Record portfolio value
            self.portfolio.record_portfolio_value(timestamp)
    
    def _process_signal(
        self,
        symbol: str,
        signal: float,
        price: float,
        timestamp: datetime,
    ) -> None:
        """
        Process a trading signal and generate orders.
        
        Args:
            symbol: Trading symbol
            signal: Signal value (1 for buy, -1 for sell, 0 for hold)
            price: Current price
            timestamp: Current timestamp
        """
        current_position = self.portfolio.get_position(symbol)
        
        # Buy signal
        if signal > 0:
            # Only buy if we don't have a position or want to add
            if current_position is None:
                # Calculate position size (use all available cash for now)
                # TODO: Implement position sizing strategies
                quantity = int(self.portfolio.cash * 0.95 / price)
                
                if quantity > 0:
                    order = Order(
                        symbol=symbol,
                        order_type=OrderType.MARKET,
                        side=OrderSide.BUY,
                        quantity=quantity,
                        timestamp=timestamp,
                    )
                    self.portfolio.execute_order(order, fill_price=price, timestamp=timestamp)
        
        # Sell signal
        elif signal < 0:
            # Only sell if we have a position
            if current_position is not None and current_position.quantity > 0:
                order = Order(
                    symbol=symbol,
                    order_type=OrderType.MARKET,
                    side=OrderSide.SELL,
                    quantity=current_position.quantity,
                    timestamp=timestamp,
                )
                self.portfolio.execute_order(order, fill_price=price, timestamp=timestamp)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Calculate performance metrics for the backtest.
        
        Returns:
            Dictionary containing various performance metrics
            
        Example:
            >>> metrics = engine.get_metrics()
            >>> print(f"Total Return: {metrics['total_return']:.2f}%")
        """
        if self.portfolio.portfolio_history:
            portfolio_df = self.portfolio.get_portfolio_history_df()
            
            # Calculate returns
            portfolio_df['returns'] = portfolio_df['total_value'].pct_change()
            
            # Basic metrics
            total_return = (
                (self.portfolio.total_value - self.initial_capital) / self.initial_capital * 100
            )
            
            # Calculate additional metrics
            # TODO: Import and use metrics module for more sophisticated calculations
            metrics = {
                'initial_capital': self.initial_capital,
                'final_value': self.portfolio.total_value,
                'total_return': total_return,
                'total_pnl': self.portfolio.total_pnl,
                'cash': self.portfolio.cash,
                'positions_value': self.portfolio.positions_value,
                'num_trades': len(self.portfolio.transaction_history),
                'num_positions': len(self.portfolio.positions),
            }
            
            # Add more metrics if we have enough data
            if len(portfolio_df) > 1:
                returns = portfolio_df['returns'].dropna()
                if len(returns) > 0:
                    metrics['volatility'] = returns.std() * (252 ** 0.5) * 100  # Annualized
                    metrics['sharpe_ratio'] = (
                        returns.mean() / returns.std() * (252 ** 0.5) if returns.std() != 0 else 0
                    )
                    
                    # Maximum drawdown
                    cumulative = (1 + returns).cumprod()
                    running_max = cumulative.expanding().max()
                    drawdown = (cumulative - running_max) / running_max
                    metrics['max_drawdown'] = drawdown.min() * 100
            
            return metrics
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': self.portfolio.total_value,
            'total_return': 0.0,
            'total_pnl': 0.0,
        }
    
    def get_portfolio_history(self) -> pd.DataFrame:
        """Get portfolio value history as a DataFrame."""
        return self.portfolio.get_portfolio_history_df()
    
    def get_transactions(self) -> pd.DataFrame:
        """Get transaction history as a DataFrame."""
        return self.portfolio.get_transactions_df()
    
    def __repr__(self) -> str:
        """String representation of the engine."""
        return (
            f"BacktestEngine(strategy={self.strategy.__class__.__name__}, "
            f"initial_capital={self.initial_capital}, commission={self.commission})"
        )
