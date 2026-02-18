"""Balance model for tracking account balances over time."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Balance:
    """
    Snapshot of account balance at a specific point in time.
    
    Tracks both available and unavailable (reserved) balances.
    
    Attributes:
        account_id: Account this balance belongs to
        backtest_run_id: Backtest run ID
        timestamp: When this balance was recorded
        available_balance: Balance available for new orders
        unavailable_balance: Balance locked in pending orders or open positions
        balance_id: Unique identifier
        
    Example:
        Balance(
            account_id=account.id,
            backtest_run_id=run.id,
            timestamp=datetime.now(),
            available_balance=Decimal("95000"),
            unavailable_balance=Decimal("5000")
        )
        
        # Total balance is 100000, but only 95000 is available for new orders
    """
    account_id: UUID
    backtest_run_id: UUID
    timestamp: datetime
    available_balance: Decimal
    unavailable_balance: Decimal
    balance_id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate balance data."""
        if self.available_balance < 0:
            raise ValueError("available_balance cannot be negative")
        if self.unavailable_balance < 0:
            raise ValueError("unavailable_balance cannot be negative")
    
    @property
    def total_balance(self) -> Decimal:
        """Total balance (available + unavailable)."""
        return self.available_balance + self.unavailable_balance
    
    @property
    def utilization_rate(self) -> Decimal:
        """Percentage of balance that is unavailable (reserved)."""
        if self.total_balance == 0:
            return Decimal("0")
        return (self.unavailable_balance / self.total_balance) * Decimal("100")
    
    def __repr__(self) -> str:
        """String representation of balance."""
        return (
            f"Balance(total={self.total_balance}, "
            f"avail={self.available_balance}, "
            f"unavail={self.unavailable_balance}, "
            f"util={self.utilization_rate:.1f}%)"
        )
