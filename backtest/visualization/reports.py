"""Report generation utilities."""

import pandas as pd
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from datetime import datetime


def generate_report(
    metrics: Dict[str, Any],
    portfolio_history: pd.DataFrame,
    transactions: Optional[pd.DataFrame] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a comprehensive backtest report.
    
    Args:
        metrics: Dictionary of performance metrics
        portfolio_history: DataFrame with portfolio values over time
        transactions: Optional DataFrame with transaction history
        output_path: Optional path to save the report
        
    Returns:
        Report as a string
        
    Example:
        >>> report = generate_report(metrics, portfolio_history)
        >>> print(report)
    """
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("BACKTEST PERFORMANCE REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Summary metrics
    report_lines.append("-" * 80)
    report_lines.append("SUMMARY")
    report_lines.append("-" * 80)
    
    if 'start_date' in metrics and 'end_date' in metrics:
        report_lines.append(
            f"Period: {metrics['start_date'].date()} to {metrics['end_date'].date()}"
        )
        report_lines.append(f"Duration: {metrics.get('duration_years', 0):.2f} years")
    
    report_lines.append(f"Initial Capital: ${metrics.get('initial_capital', 0):,.2f}")
    report_lines.append(f"Final Value: ${metrics.get('final_value', 0):,.2f}")
    report_lines.append(f"Total Return: {metrics.get('total_return', 0):.2f}%")
    report_lines.append("")
    
    # Return metrics
    report_lines.append("-" * 80)
    report_lines.append("RETURN METRICS")
    report_lines.append("-" * 80)
    report_lines.append(f"Annualized Return: {metrics.get('annualized_return', 0):.2f}%")
    report_lines.append(f"CAGR: {metrics.get('cagr', 0):.2f}%")
    report_lines.append(
        f"Cumulative Returns: {metrics.get('cumulative_returns', 0):.2f}%"
    )
    report_lines.append("")
    
    # Risk metrics
    report_lines.append("-" * 80)
    report_lines.append("RISK METRICS")
    report_lines.append("-" * 80)
    report_lines.append(f"Volatility (Annual): {metrics.get('volatility', 0):.2f}%")
    report_lines.append(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
    report_lines.append(f"Sortino Ratio: {metrics.get('sortino_ratio', 0):.3f}")
    report_lines.append(f"Maximum Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
    report_lines.append(f"Calmar Ratio: {metrics.get('calmar_ratio', 0):.3f}")
    report_lines.append(f"VaR (95%): {metrics.get('var_95', 0):.2f}%")
    report_lines.append(f"CVaR (95%): {metrics.get('cvar_95', 0):.2f}%")
    report_lines.append("")
    
    # Trading metrics
    if 'num_trades' in metrics:
        report_lines.append("-" * 80)
        report_lines.append("TRADING METRICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Trades: {metrics.get('num_trades', 0)}")
        
        if 'win_rate' in metrics:
            report_lines.append(f"Win Rate: {metrics.get('win_rate', 0):.2f}%")
            report_lines.append(
                f"Winning Trades: {metrics.get('num_winning_trades', 0)}"
            )
            report_lines.append(
                f"Losing Trades: {metrics.get('num_losing_trades', 0)}"
            )
            
            if 'avg_win' in metrics:
                report_lines.append(f"Average Win: ${metrics.get('avg_win', 0):.2f}")
            if 'avg_loss' in metrics:
                report_lines.append(f"Average Loss: ${metrics.get('avg_loss', 0):.2f}")
            if 'profit_factor' in metrics:
                report_lines.append(
                    f"Profit Factor: {metrics.get('profit_factor', 0):.2f}"
                )
        
        report_lines.append("")
    
    # Transaction summary
    if transactions is not None and len(transactions) > 0:
        report_lines.append("-" * 80)
        report_lines.append("RECENT TRANSACTIONS (Last 10)")
        report_lines.append("-" * 80)
        
        recent = transactions.tail(10)
        for _, txn in recent.iterrows():
            report_lines.append(
                f"{txn['timestamp'].strftime('%Y-%m-%d')}: "
                f"{txn['side']} {txn['quantity']:.0f} {txn['symbol']} @ "
                f"${txn['price']:.2f}"
            )
        
        report_lines.append("")
    
    # Footer
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    report = "\n".join(report_lines)
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report)
    
    return report


def generate_html_report(
    metrics: Dict[str, Any],
    portfolio_history: pd.DataFrame,
    transactions: Optional[pd.DataFrame] = None,
    output_path: str = "backtest_report.html",
) -> str:
    """
    Generate an HTML backtest report with charts.
    
    Args:
        metrics: Dictionary of performance metrics
        portfolio_history: DataFrame with portfolio values over time
        transactions: Optional DataFrame with transaction history
        output_path: Path to save the HTML report
        
    Returns:
        Path to the generated HTML file
        
    Note:
        TODO: Implement full HTML report generation with embedded charts
    """
    # Placeholder for HTML report generation
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backtest Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2E86AB; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #2E86AB; color: white; }}
        </style>
    </head>
    <body>
        <h1>Backtest Performance Report</h1>
        <h2>Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Initial Capital</td><td>${metrics.get('initial_capital', 0):,.2f}</td></tr>
            <tr><td>Final Value</td><td>${metrics.get('final_value', 0):,.2f}</td></tr>
            <tr><td>Total Return</td><td>{metrics.get('total_return', 0):.2f}%</td></tr>
            <tr><td>Sharpe Ratio</td><td>{metrics.get('sharpe_ratio', 0):.3f}</td></tr>
            <tr><td>Max Drawdown</td><td>{metrics.get('max_drawdown', 0):.2f}%</td></tr>
        </table>
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path
