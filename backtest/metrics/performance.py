"""Overall performance metrics calculation."""

import pandas as pd
from typing import Dict, Any, Optional

from backtest.metrics.returns import (
    calculate_returns,
    calculate_cumulative_returns,
    calculate_annualized_return,
    calculate_cagr,
)
from backtest.metrics.risk import (
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_calmar_ratio,
    calculate_var,
    calculate_cvar,
)


class PerformanceMetrics:
    """
    Calculate comprehensive performance metrics for backtest results.
    
    Example:
        >>> metrics = PerformanceMetrics(portfolio_values, transactions)
        >>> results = metrics.calculate_all()
        >>> print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    """
    
    def __init__(
        self,
        portfolio_values: pd.Series,
        transactions: Optional[pd.DataFrame] = None,
        initial_capital: float = 100000.0,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252,
    ):
        """
        Initialize performance metrics calculator.
        
        Args:
            portfolio_values: Time series of portfolio values
            transactions: DataFrame of transactions (optional)
            initial_capital: Initial capital amount
            risk_free_rate: Risk-free rate for Sharpe/Sortino calculations
            periods_per_year: Number of periods per year (252 for daily)
        """
        self.portfolio_values = portfolio_values
        self.transactions = transactions
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.periods_per_year = periods_per_year
        
        # Calculate returns
        self.returns = calculate_returns(portfolio_values)
    
    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all performance metrics.
        
        Returns:
            Dictionary containing all metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['initial_capital'] = self.initial_capital
        metrics['final_value'] = self.portfolio_values.iloc[-1]
        metrics['total_return'] = (
            (metrics['final_value'] - self.initial_capital) / self.initial_capital * 100
        )
        
        # Time metrics
        start_date = self.portfolio_values.index[0]
        end_date = self.portfolio_values.index[-1]
        years = (end_date - start_date).days / 365.25
        
        metrics['start_date'] = start_date
        metrics['end_date'] = end_date
        metrics['duration_years'] = years
        
        # Return metrics
        metrics['annualized_return'] = calculate_annualized_return(
            self.returns.dropna(), self.periods_per_year
        )
        metrics['cagr'] = calculate_cagr(
            self.initial_capital, metrics['final_value'], years
        )
        metrics['cumulative_returns'] = calculate_cumulative_returns(
            self.returns.dropna()
        ).iloc[-1] * 100
        
        # Risk metrics
        metrics['volatility'] = calculate_volatility(
            self.returns.dropna(), self.periods_per_year
        )
        metrics['sharpe_ratio'] = calculate_sharpe_ratio(
            self.returns.dropna(), self.risk_free_rate, self.periods_per_year
        )
        metrics['sortino_ratio'] = calculate_sortino_ratio(
            self.returns.dropna(), self.risk_free_rate, self.periods_per_year
        )
        metrics['max_drawdown'] = calculate_max_drawdown(self.returns.dropna())
        metrics['calmar_ratio'] = calculate_calmar_ratio(
            self.returns.dropna(), self.periods_per_year
        )
        
        # Value at Risk
        metrics['var_95'] = calculate_var(self.returns.dropna(), 0.95)
        metrics['cvar_95'] = calculate_cvar(self.returns.dropna(), 0.95)
        
        # Transaction metrics
        if self.transactions is not None and len(self.transactions) > 0:
            metrics['num_trades'] = len(self.transactions)
            
            # Win rate
            if 'realized_pnl' in self.transactions.columns:
                winning_trades = self.transactions[
                    self.transactions['realized_pnl'] > 0
                ]
                metrics['num_winning_trades'] = len(winning_trades)
                metrics['num_losing_trades'] = (
                    len(self.transactions[self.transactions['realized_pnl'] < 0])
                )
                metrics['win_rate'] = (
                    len(winning_trades) / len(self.transactions) * 100
                    if len(self.transactions) > 0 else 0
                )
                
                # Average win/loss
                if len(winning_trades) > 0:
                    metrics['avg_win'] = winning_trades['realized_pnl'].mean()
                if metrics['num_losing_trades'] > 0:
                    losing_trades = self.transactions[
                        self.transactions['realized_pnl'] < 0
                    ]
                    metrics['avg_loss'] = losing_trades['realized_pnl'].mean()
                
                # Profit factor
                total_wins = winning_trades['realized_pnl'].sum() if len(winning_trades) > 0 else 0
                total_losses = abs(
                    self.transactions[self.transactions['realized_pnl'] < 0]['realized_pnl'].sum()
                )
                metrics['profit_factor'] = (
                    total_wins / total_losses if total_losses > 0 else 0
                )
        
        return metrics
    
    def print_summary(self) -> None:
        """Print a formatted summary of all metrics."""
        metrics = self.calculate_all()
        
        print("=" * 60)
        print("BACKTEST PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"\nPeriod: {metrics['start_date'].date()} to {metrics['end_date'].date()}")
        print(f"Duration: {metrics['duration_years']:.2f} years")
        print(f"\n{'Return Metrics':-^60}")
        print(f"Initial Capital:      ${metrics['initial_capital']:,.2f}")
        print(f"Final Value:          ${metrics['final_value']:,.2f}")
        print(f"Total Return:         {metrics['total_return']:,.2f}%")
        print(f"Annualized Return:    {metrics['annualized_return']:.2f}%")
        print(f"CAGR:                 {metrics['cagr']:.2f}%")
        print(f"\n{'Risk Metrics':-^60}")
        print(f"Volatility:           {metrics['volatility']:.2f}%")
        print(f"Sharpe Ratio:         {metrics['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio:        {metrics['sortino_ratio']:.2f}")
        print(f"Maximum Drawdown:     {metrics['max_drawdown']:.2f}%")
        print(f"Calmar Ratio:         {metrics['calmar_ratio']:.2f}")
        print(f"VaR (95%):            {metrics['var_95']:.2f}%")
        print(f"CVaR (95%):           {metrics['cvar_95']:.2f}%")
        
        if 'num_trades' in metrics:
            print(f"\n{'Trading Metrics':-^60}")
            print(f"Number of Trades:     {metrics['num_trades']}")
            if 'win_rate' in metrics:
                print(f"Win Rate:             {metrics['win_rate']:.2f}%")
                print(f"Winning Trades:       {metrics['num_winning_trades']}")
                print(f"Losing Trades:        {metrics['num_losing_trades']}")
        
        print("=" * 60)
