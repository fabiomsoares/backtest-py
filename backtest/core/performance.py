"""
Performance metrics calculation for backtesting results.
"""

from dataclasses import dataclass
from typing import List, Optional
from backtest.models.portfolio import Portfolio


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for a backtest.
    
    Attributes:
        initial_capital: Starting capital
        final_equity: Ending equity
        total_return: Total return percentage
        total_trades: Number of trades executed
        portfolio: Final portfolio state
    """
    initial_capital: float
    final_equity: float
    total_return: float
    total_trades: int
    portfolio: Portfolio
    
    @property
    def profit_loss(self) -> float:
        """Calculate absolute profit/loss."""
        return self.final_equity - self.initial_capital
    
    @property
    def roi(self) -> float:
        """Calculate return on investment percentage."""
        if self.initial_capital == 0:
            return 0.0
        return ((self.final_equity - self.initial_capital) / self.initial_capital) * 100
    
    def __str__(self) -> str:
        """String representation of performance metrics."""
        return f"""
Backtest Performance Metrics
=============================
Initial Capital: ${self.initial_capital:,.2f}
Final Equity: ${self.final_equity:,.2f}
Profit/Loss: ${self.profit_loss:,.2f}
Total Return: {self.total_return:.2f}%
ROI: {self.roi:.2f}%
Total Trades: {self.total_trades}
        """.strip()
