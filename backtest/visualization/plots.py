"""Chart generation utilities."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple
import numpy as np

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_portfolio_value(
    portfolio_values: pd.Series,
    title: str = "Portfolio Value Over Time",
    figsize: Tuple[int, int] = (12, 6),
    show: bool = True,
) -> plt.Figure:
    """
    Plot portfolio value over time.
    
    Args:
        portfolio_values: Time series of portfolio values
        title: Plot title
        figsize: Figure size (width, height)
        show: Whether to display the plot
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    portfolio_values.plot(ax=ax, linewidth=2, color='#2E86AB')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_returns(
    returns: pd.Series,
    title: str = "Returns Distribution",
    figsize: Tuple[int, int] = (12, 6),
    show: bool = True,
) -> plt.Figure:
    """
    Plot returns distribution histogram.
    
    Args:
        returns: Returns series
        title: Plot title
        figsize: Figure size
        show: Whether to display the plot
        
    Returns:
        Matplotlib figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Histogram
    returns.hist(bins=50, ax=ax1, alpha=0.7, color='#A23B72')
    ax1.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label='Mean')
    ax1.axvline(returns.median(), color='green', linestyle='--', linewidth=2, label='Median')
    ax1.set_title('Returns Histogram', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Returns', fontsize=10)
    ax1.set_ylabel('Frequency', fontsize=10)
    ax1.legend()
    
    # Cumulative returns
    cumulative_returns = (1 + returns).cumprod()
    cumulative_returns.plot(ax=ax2, linewidth=2, color='#F18F01')
    ax2.set_title('Cumulative Returns', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('Cumulative Return', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_drawdown(
    returns: pd.Series,
    title: str = "Drawdown Over Time",
    figsize: Tuple[int, int] = (12, 6),
    show: bool = True,
) -> plt.Figure:
    """
    Plot drawdown over time.
    
    Args:
        returns: Returns series
        title: Plot title
        figsize: Figure size
        show: Whether to display the plot
        
    Returns:
        Matplotlib figure object
    """
    from backtest.metrics.risk import calculate_max_drawdown
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate drawdown series
    drawdown = calculate_max_drawdown(returns, return_series=True)
    
    ax.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    drawdown.plot(ax=ax, linewidth=2, color='darkred')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Add maximum drawdown line
    max_dd = drawdown.min()
    ax.axhline(max_dd, color='red', linestyle='--', linewidth=2, 
               label=f'Max Drawdown: {max_dd:.2f}%')
    ax.legend()
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_signals(
    data: pd.DataFrame,
    signals: pd.DataFrame,
    title: str = "Price and Trading Signals",
    figsize: Tuple[int, int] = (14, 7),
    show: bool = True,
) -> plt.Figure:
    """
    Plot price data with buy/sell signals.
    
    Args:
        data: Price data DataFrame
        signals: Signals DataFrame with 'signal' column
        title: Plot title
        figsize: Figure size
        show: Whether to display the plot
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot price
    data['close'].plot(ax=ax, linewidth=2, label='Price', color='#2E86AB')
    
    # Plot buy signals
    buy_signals = signals[signals['signal'] > 0]
    if len(buy_signals) > 0:
        ax.scatter(buy_signals.index, data.loc[buy_signals.index, 'close'],
                  marker='^', color='green', s=100, label='Buy', zorder=5)
    
    # Plot sell signals
    sell_signals = signals[signals['signal'] < 0]
    if len(sell_signals) > 0:
        ax.scatter(sell_signals.index, data.loc[sell_signals.index, 'close'],
                  marker='v', color='red', s=100, label='Sell', zorder=5)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_comparison(
    portfolio_values: pd.Series,
    benchmark_values: pd.Series,
    title: str = "Portfolio vs Benchmark",
    figsize: Tuple[int, int] = (12, 6),
    show: bool = True,
) -> plt.Figure:
    """
    Plot portfolio value compared to benchmark.
    
    Args:
        portfolio_values: Portfolio value series
        benchmark_values: Benchmark value series
        title: Plot title
        figsize: Figure size
        show: Whether to display the plot
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Normalize to start at 100
    portfolio_normalized = portfolio_values / portfolio_values.iloc[0] * 100
    benchmark_normalized = benchmark_values / benchmark_values.iloc[0] * 100
    
    portfolio_normalized.plot(ax=ax, linewidth=2, label='Portfolio', color='#2E86AB')
    benchmark_normalized.plot(ax=ax, linewidth=2, label='Benchmark', color='#F18F01', 
                             linestyle='--')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Normalized Value', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig
