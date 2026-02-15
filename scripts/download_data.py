"""
Data Download Utility Script

This script provides utilities for downloading and saving historical price data
from various sources.
"""

import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime

from backtest.data import DataLoader


def download_data(
    symbol: str,
    start_date: str,
    end_date: str,
    output_dir: str = "data/raw",
    source: str = "yahoo",
):
    """
    Download historical data and save to CSV.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_dir: Directory to save data
        source: Data source (yahoo, pandas_datareader)
    """
    print(f"Downloading data for {symbol}...")
    print(f"Period: {start_date} to {end_date}")
    print(f"Source: {source}")
    
    loader = DataLoader()
    
    try:
        if source == "yahoo":
            data = loader.load_yahoo(symbol, start=start_date, end=end_date)
        elif source == "pandas_datareader":
            data = loader.load_pandas_datareader(symbol, "yahoo", start_date, end_date)
        else:
            raise ValueError(f"Unknown source: {source}")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{symbol}_{start_date}_{end_date}_{timestamp}.csv"
        filepath = output_path / filename
        
        data.to_csv(filepath)
        
        print(f"Successfully downloaded {len(data)} rows")
        print(f"Data saved to: {filepath}")
        print(f"\nData preview:")
        print(data.head())
        print(f"\nData info:")
        print(f"Columns: {list(data.columns)}")
        print(f"Date range: {data.index[0]} to {data.index[-1]}")
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        return False
    
    return True


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Download historical price data"
    )
    parser.add_argument(
        "symbol",
        type=str,
        help="Stock ticker symbol (e.g., AAPL, MSFT)"
    )
    parser.add_argument(
        "--start",
        type=str,
        default="2020-01-01",
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw",
        help="Output directory"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="yahoo",
        choices=["yahoo", "pandas_datareader"],
        help="Data source"
    )
    
    args = parser.parse_args()
    
    success = download_data(
        symbol=args.symbol,
        start_date=args.start,
        end_date=args.end,
        output_dir=args.output,
        source=args.source,
    )
    
    if success:
        print("\n✓ Download completed successfully!")
    else:
        print("\n✗ Download failed!")
        exit(1)


if __name__ == "__main__":
    main()
