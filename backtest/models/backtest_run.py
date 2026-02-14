"""Backtest run configuration and account management."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from backtest.models.financial_entities import Broker, TraderAgent, TradingPair
from backtest.models.market_data import BarData


@dataclass
class BacktestRun:
    """
    Container for a backtest run.
    
    Attributes:
        broker: Broker configuration
        start_date: Start date of backtest
        end_date: End date of backtest
        trading_pairs: List of trading pairs
        agents: List of trading agents
        market_data: Dictionary of market data by symbol_timeframe
        description: Description of the backtest
    """
    broker: Broker
    start_date: datetime
    end_date: datetime
    trading_pairs: List[TradingPair]
    agents: List[TraderAgent]
    description: str = ""
    market_data: Dict[str, List[BarData]] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate backtest run."""
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        if not self.trading_pairs:
            raise ValueError("At least one trading pair is required")
        if not self.agents:
            raise ValueError("At least one agent is required")


@dataclass
class AccountBalance:
    """
    Snapshot of account balance at a point in time.
    
    Tracks available and unavailable (reserved for margin) balance.
    
    Attributes:
        account_id: Account ID
        timestamp: Snapshot timestamp
        total_balance: Total balance (available + unavailable)
        available_balance: Balance available for new trades
        unavailable_balance: Balance reserved for margin
        unrealized_pnl: Unrealized P&L from open positions
    """
    account_id: UUID
    timestamp: datetime
    total_balance: Decimal
    available_balance: Decimal
    unavailable_balance: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate balance snapshot."""
        expected_total = self.available_balance + self.unavailable_balance
        if abs(self.total_balance - expected_total) > Decimal("0.01"):
            raise ValueError(
                f"total_balance ({self.total_balance}) must equal "
                f"available_balance ({self.available_balance}) + "
                f"unavailable_balance ({self.unavailable_balance})"
            )


@dataclass
class AccountTransaction:
    """
    Account transaction for money flow tracking.
    
    Attributes:
        account_id: Account ID
        timestamp: Transaction timestamp
        amount: Transaction amount (positive = credit, negative = debit)
        transaction_type: Type of transaction (e.g., "FEE", "PNL", "MARGIN_RESERVE")
        description: Transaction description
        related_order_id: Related order ID (if applicable)
    """
    account_id: UUID
    timestamp: datetime
    amount: Decimal
    transaction_type: str
    description: str = ""
    related_order_id: Optional[UUID] = None
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate transaction."""
        if not self.transaction_type or not self.transaction_type.strip():
            raise ValueError("transaction_type cannot be empty")
