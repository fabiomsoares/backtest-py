"""Data preprocessing utilities."""

import pandas as pd
import numpy as np
from typing import Optional, List


class DataPreprocessor:
    """
    Utility class for preprocessing and cleaning financial data.
    
    Provides methods for handling missing data, outliers, and data transformations.
    
    Example:
        >>> preprocessor = DataPreprocessor()
        >>> clean_data = preprocessor.clean(raw_data)
    """
    
    @staticmethod
    def clean(
        data: pd.DataFrame,
        drop_na: bool = True,
        fill_method: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Clean data by handling missing values.
        
        Args:
            data: Raw data DataFrame
            drop_na: Whether to drop rows with NaN values
            fill_method: Method to fill NaN ('ffill', 'bfill', 'interpolate')
            
        Returns:
            Cleaned DataFrame
        """
        df = data.copy()
        
        if drop_na:
            df = df.dropna()
        elif fill_method:
            if fill_method == 'interpolate':
                df = df.interpolate(method='linear')
            else:
                df = df.fillna(method=fill_method)
        
        return df
    
    @staticmethod
    def remove_outliers(
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        n_std: float = 3.0,
    ) -> pd.DataFrame:
        """
        Remove outliers using standard deviation method.
        
        Args:
            data: Input DataFrame
            columns: Columns to check for outliers (None = all numeric columns)
            n_std: Number of standard deviations for outlier threshold
            
        Returns:
            DataFrame with outliers removed
        """
        df = data.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            mean = df[col].mean()
            std = df[col].std()
            df = df[abs(df[col] - mean) <= n_std * std]
        
        return df
    
    @staticmethod
    def add_returns(data: pd.DataFrame, column: str = 'close') -> pd.DataFrame:
        """
        Add returns columns to data.
        
        Args:
            data: Price data
            column: Column to calculate returns from
            
        Returns:
            DataFrame with additional returns columns
        """
        df = data.copy()
        
        # Simple returns
        df['returns'] = df[column].pct_change()
        
        # Log returns
        df['log_returns'] = np.log(df[column] / df[column].shift(1))
        
        return df
    
    @staticmethod
    def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """
        Add common technical indicators to data.
        
        Args:
            data: OHLCV price data
            
        Returns:
            DataFrame with additional technical indicator columns
            
        Note:
            TODO: Implement additional technical indicators
            - RSI (Relative Strength Index)
            - MACD (Moving Average Convergence Divergence)
            - Bollinger Bands
            - ATR (Average True Range)
        """
        df = data.copy()
        
        # Simple moving averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential moving averages
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        return df
    
    @staticmethod
    def normalize(
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'minmax',
    ) -> pd.DataFrame:
        """
        Normalize data using specified method.
        
        Args:
            data: Input DataFrame
            columns: Columns to normalize (None = all numeric columns)
            method: Normalization method ('minmax' or 'zscore')
            
        Returns:
            Normalized DataFrame
        """
        df = data.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if method == 'minmax':
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            elif method == 'zscore':
                df[col] = (df[col] - df[col].mean()) / df[col].std()
        
        return df
