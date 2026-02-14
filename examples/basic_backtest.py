"""
Basic Backtest Example

This script demonstrates how to use the backtest-py framework to run a simple backtest
using a moving average crossover strategy.
"""

import pandas as pd
from datetime import datetime

from backtest import BacktestEngine
from backtest.strategies import MovingAverageStrategy
from backtest.data import DataLoader
from backtest.visualization import plot_portfolio_value, plot_drawdown, plot_returns


def main():
    """Run a basic backtest example."""
    
    print("=" * 60)
    print("Backtest-py: Basic Example")
    print("=" * 60)
    print()
    
    # 1. Load historical data
    print("Loading data...")
    try:
        # Try to load from Yahoo Finance
        loader = DataLoader()
        data = loader.load_yahoo(
            symbol='AAPL',
            start='2020-01-01',
            end='2023-12-31',
        )
        print(f"Loaded {len(data)} days of data for AAPL")
    except Exception as e:
        print(f"Could not load data from Yahoo Finance: {e}")
        print("Using sample data instead...")
        
        # Generate sample data
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        import numpy as np
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)
        
        data = pd.DataFrame({
            'open': prices + np.random.randn(len(dates)) * 0.5,
            'high': prices + abs(np.random.randn(len(dates)) * 1.5),
            'low': prices - abs(np.random.randn(len(dates)) * 1.5),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(dates)),
        }, index=dates)
        
        # Ensure valid OHLC relationships
        data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
        data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
    
    print(f"Data range: {data.index[0].date()} to {data.index[-1].date()}")
    print()
    
    # 2. Create a strategy
    print("Initializing strategy...")
    strategy = MovingAverageStrategy(
        fast_window=20,
        slow_window=50,
        name="MA_20_50"
    )
    print(f"Strategy: {strategy}")
    print()
    
    # 3. Initialize the backtest engine
    print("Setting up backtest engine...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=100000.0,
        commission=0.001,  # 0.1% commission
    )
    print(f"Initial capital: ${engine.initial_capital:,.2f}")
    print(f"Commission: {engine.commission * 100}%")
    print()
    
    # 4. Run the backtest
    print("Running backtest...")
    results = engine.run(data)
    print("Backtest completed!")
    print()
    
    # 5. Display results
    print("=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print(f"Initial Capital:      ${results['initial_capital']:,.2f}")
    print(f"Final Value:          ${results['final_value']:,.2f}")
    print(f"Total Return:         {results['total_return']:.2f}%")
    print(f"Total P&L:            ${results['total_pnl']:,.2f}")
    print(f"Number of Trades:     {results['num_trades']}")
    
    if 'sharpe_ratio' in results:
        print(f"Sharpe Ratio:         {results['sharpe_ratio']:.3f}")
    if 'max_drawdown' in results:
        print(f"Max Drawdown:         {results['max_drawdown']:.2f}%")
    if 'volatility' in results:
        print(f"Volatility:           {results['volatility']:.2f}%")
    
    print("=" * 60)
    print()
    
    # 6. Get portfolio history
    portfolio_history = engine.get_portfolio_history()
    
    # 7. Plot results (optional - requires matplotlib)
    try:
        print("Generating plots...")
        
        # Plot portfolio value
        plot_portfolio_value(
            portfolio_history['total_value'],
            title="Portfolio Value Over Time",
            show=False
        )
        
        # Plot returns
        returns = portfolio_history['total_value'].pct_change()
        plot_returns(returns, title="Strategy Returns", show=False)
        
        # Plot drawdown
        plot_drawdown(returns, title="Drawdown", show=False)
        
        print("Plots generated! Close the plot windows to continue.")
        import matplotlib.pyplot as plt
        plt.show()
        
    except ImportError:
        print("Matplotlib not available. Skipping plots.")
    except Exception as e:
        print(f"Could not generate plots: {e}")
    
    print()
    print("Example completed successfully!")
    print()


if __name__ == "__main__":
    main()
