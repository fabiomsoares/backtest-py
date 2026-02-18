"""Transaction model for tracking all balance changes."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID, uuid4


class TransactionType(Enum):
    """Types of transactions affecting account balance."""
    RESERVE_MARGIN = auto()     # Lock funds for pending order
    RETURN_MARGIN = auto()      # Return funds from cancelled order
    FEE_CREATE = auto()         # Fee charged when creating order
    FEE_FILL = auto()           # Fee charged when order fills
    FEE_CLOSE = auto()          # Fee charged when closing position
    FEE_CANCEL = auto()         # Fee charged when cancelling order
    FEE_OVERNIGHT = auto()      # Overnight/holding fee
    FILL_BUY = auto()           # Quote → Base conversion on buy
    FILL_SELL = auto()          # Base → Quote conversion on sell
    CLOSE_PNL = auto()          # Realized P&L from closed position
    SPOT_EXCHANGE = auto()      # Spot asset exchange
    ADJUSTMENT = auto()         # Manual balance adjustment


@dataclass(frozen=True)
class Transaction:
    """
    Represents any movement affecting account balance.
    
    All balance changes in the system MUST go through Transaction objects.
    This ensures complete audit trail and accurate balance reconciliation.
    
    Attributes:
        account_id: Account affected by this transaction
        backtest_run_id: ID of the backtest run
        timestamp: When the transaction occurred
        description: Human-readable description
        available_balance_change: Change to available balance (can be +/-)
        unavailable_balance_change: Change to unavailable balance (can be +/-)
        transaction_type: Category of transaction
        order_id: Reference to triggering order (if applicable)
        transaction_id: Unique identifier
        
    Example:
        # Reserve margin for new order
        Transaction(
            account_id=account.id,
            backtest_run_id=run.id,
            timestamp=datetime.now(),
            description="Reserve margin for order #123",
            available_balance_change=Decimal("-1000"),
            unavailable_balance_change=Decimal("1000"),
            transaction_type=TransactionType.RESERVE_MARGIN,
            order_id=order.id
        )
        
        # PnL from closed position
        Transaction(
            account_id=account.id,
            backtest_run_id=run.id,
            timestamp=datetime.now(),
            description="Closed position with profit",
            available_balance_change=Decimal("500"),
            unavailable_balance_change=Decimal("0"),
            transaction_type=TransactionType.CLOSE_PNL,
            order_id=order.id
        )
    """
    account_id: UUID
    backtest_run_id: UUID
    timestamp: datetime
    description: str
    available_balance_change: Decimal
    unavailable_balance_change: Decimal
    transaction_type: TransactionType
    order_id: Optional[UUID] = None
    transaction_id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate transaction data."""
        if not self.description or not self.description.strip():
            raise ValueError("Transaction description cannot be empty")
    
    @property
    def total_balance_change(self) -> Decimal:
        """Total balance change (available + unavailable)."""
        return self.available_balance_change + self.unavailable_balance_change
    
    def __repr__(self) -> str:
        """String representation of transaction."""
        return (
            f"Transaction({self.transaction_type.name}, "
            f"avail={self.available_balance_change}, "
            f"unavail={self.unavailable_balance_change}, "
            f"desc='{self.description[:30]}...')"
        )
