"""Trading orders and order history."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class OrderDirection(Enum):
    """Direction of trading order."""
    LONG = "LONG"  # Buy/long position
    SHORT = "SHORT"  # Sell/short position


class OrderStatus(Enum):
    """Status of trading order."""
    PENDING = "PENDING"  # Order created, waiting to be filled
    FILLED = "FILLED"  # Order filled, position open
    CANCELLED = "CANCELLED"  # Order cancelled before fill
    CLOSED = "CLOSED"  # Position closed


@dataclass
class TradingOrder:
    """
    Comprehensive trading order with lifecycle tracking.
    
    Tracks the complete lifecycle of an order from creation through fill,
    and eventual close, including all fees at each stage.
    
    Attributes:
        trading_pair_code: Trading pair code (e.g., "BTCUSD")
        direction: LONG or SHORT
        volume: Order volume
        status: Current order status
        
        # Lifecycle timestamps and prices
        create_timestamp: When order was created
        create_price: Price when order was created
        fill_timestamp: When order was filled
        fill_price: Price at which order was filled
        close_timestamp: When position was closed
        close_price: Price at which position was closed
        cancel_timestamp: When order was cancelled
        
        # Advanced order types
        limit_price: Limit price (None for market orders)
        stop_loss: Stop loss price
        take_profit: Take profit price
        leverage: Leverage multiplier (None for no leverage)
        
        # Fee tracking at each stage
        fees_on_create: Fees charged when order created
        fees_on_fill: Fees charged when order filled
        fees_on_close: Fees charged when position closed
        fees_on_cancel: Fees charged when order cancelled
        fees_on_overnight: Accumulated overnight fees
        
        # Financial tracking
        margin_reserved: Margin reserved for this order
        gross_pnl: Gross P&L (before fees)
        net_pnl: Net P&L (after all fees)
        
        # Order relationships
        parent_order_id: ID of parent order (for modifications)
        root_order_id: ID of original root order
        
        # Metadata
        agent_id: Trading agent ID
        account_id: Account ID
        broker_id: Broker ID
        backtest_run_id: Backtest run ID
    """
    trading_pair_code: str
    direction: OrderDirection
    volume: Decimal
    create_timestamp: datetime
    create_price: Decimal
    agent_id: UUID
    account_id: UUID
    broker_id: UUID
    backtest_run_id: UUID
    
    # Status
    status: OrderStatus = OrderStatus.PENDING
    
    # Fill information
    fill_timestamp: Optional[datetime] = None
    fill_price: Optional[Decimal] = None
    
    # Close information
    close_timestamp: Optional[datetime] = None
    close_price: Optional[Decimal] = None
    
    # Cancel information
    cancel_timestamp: Optional[datetime] = None
    
    # Advanced order features
    limit_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    leverage: Optional[Decimal] = None
    
    # Fee tracking
    fees_on_create: Decimal = Decimal("0")
    fees_on_fill: Decimal = Decimal("0")
    fees_on_close: Decimal = Decimal("0")
    fees_on_cancel: Decimal = Decimal("0")
    fees_on_overnight: Decimal = Decimal("0")
    
    # Financial tracking
    margin_reserved: Decimal = Decimal("0")
    gross_pnl: Decimal = Decimal("0")
    net_pnl: Decimal = Decimal("0")
    
    # Order relationships
    parent_order_id: Optional[UUID] = None
    root_order_id: Optional[UUID] = None
    
    # Unique identifier
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate order data."""
        if not self.trading_pair_code or not self.trading_pair_code.strip():
            raise ValueError("trading_pair_code cannot be empty")
        if self.volume <= 0:
            raise ValueError("volume must be positive")
        if self.create_price <= 0:
            raise ValueError("create_price must be positive")
        
        # Set root_order_id if not set
        if self.root_order_id is None:
            if self.parent_order_id is None:
                self.root_order_id = self.id
            # else root_order_id should be explicitly set
        
        # Validate leverage
        if self.leverage is not None and self.leverage <= 0:
            raise ValueError("leverage must be positive if set")
        
        # Validate limit price
        if self.limit_price is not None and self.limit_price <= 0:
            raise ValueError("limit_price must be positive if set")
    
    @property
    def is_pending(self) -> bool:
        """Check if order is pending."""
        return self.status == OrderStatus.PENDING
    
    @property
    def is_filled(self) -> bool:
        """Check if order is filled."""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_closed(self) -> bool:
        """Check if position is closed."""
        return self.status == OrderStatus.CLOSED
    
    @property
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED
    
    @property
    def is_active(self) -> bool:
        """Check if order is active (pending or filled)."""
        return self.status in [OrderStatus.PENDING, OrderStatus.FILLED]
    
    @property
    def total_fees(self) -> Decimal:
        """Calculate total fees across all stages."""
        return (
            self.fees_on_create +
            self.fees_on_fill +
            self.fees_on_close +
            self.fees_on_cancel +
            self.fees_on_overnight
        )
    
    @property
    def is_market_order(self) -> bool:
        """Check if this is a market order (no limit price)."""
        return self.limit_price is None
    
    @property
    def is_limit_order(self) -> bool:
        """Check if this is a limit order."""
        return self.limit_price is not None
    
    def fill(
        self,
        fill_timestamp: datetime,
        fill_price: Decimal,
        fees_on_fill: Decimal = Decimal("0"),
        margin_reserved: Decimal = Decimal("0")
    ) -> None:
        """
        Fill the order.
        
        Args:
            fill_timestamp: When order was filled
            fill_price: Price at which order was filled
            fees_on_fill: Fees charged on fill
            margin_reserved: Margin reserved for position
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot fill order with status {self.status}")
        
        self.fill_timestamp = fill_timestamp
        self.fill_price = fill_price
        self.fees_on_fill = fees_on_fill
        self.margin_reserved = margin_reserved
        self.status = OrderStatus.FILLED
    
    def close(
        self,
        close_timestamp: datetime,
        close_price: Decimal,
        fees_on_close: Decimal = Decimal("0")
    ) -> None:
        """
        Close the position.
        
        Args:
            close_timestamp: When position was closed
            close_price: Price at which position was closed
            fees_on_close: Fees charged on close
        """
        if self.status != OrderStatus.FILLED:
            raise ValueError(f"Cannot close order with status {self.status}")
        if self.fill_price is None:
            raise ValueError("Order must be filled before closing")
        
        self.close_timestamp = close_timestamp
        self.close_price = close_price
        self.fees_on_close = fees_on_close
        self.status = OrderStatus.CLOSED
        
        # Calculate P&L
        if self.direction == OrderDirection.LONG:
            self.gross_pnl = (close_price - self.fill_price) * self.volume
        else:  # SHORT
            self.gross_pnl = (self.fill_price - close_price) * self.volume
        
        self.net_pnl = self.gross_pnl - self.total_fees
    
    def cancel(
        self,
        cancel_timestamp: datetime,
        fees_on_cancel: Decimal = Decimal("0")
    ) -> None:
        """
        Cancel the order.
        
        Args:
            cancel_timestamp: When order was cancelled
            fees_on_cancel: Fees charged on cancellation
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot cancel order with status {self.status}")
        
        self.cancel_timestamp = cancel_timestamp
        self.fees_on_cancel = fees_on_cancel
        self.status = OrderStatus.CANCELLED
        self.net_pnl = -self.total_fees
    
    def add_overnight_fees(self, fees: Decimal) -> None:
        """
        Add overnight fees to the order.
        
        Args:
            fees: Overnight fees to add
        """
        if fees < 0:
            raise ValueError("fees cannot be negative")
        self.fees_on_overnight += fees
        
        # Update net P&L if position is closed
        if self.status == OrderStatus.CLOSED:
            self.net_pnl = self.gross_pnl - self.total_fees


@dataclass(frozen=True)
class TradingOrderHistory:
    """
    Snapshot of order history at a point in time.
    
    Used for tracking realized and unrealized P&L over time.
    
    Attributes:
        order_id: ID of the order
        timestamp: Snapshot timestamp
        status: Order status at snapshot time
        unrealized_pnl: Unrealized P&L at snapshot time
        realized_pnl: Realized P&L at snapshot time
        current_price: Current market price at snapshot time
        total_fees: Total fees accumulated at snapshot time
    """
    order_id: UUID
    timestamp: datetime
    status: OrderStatus
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    current_price: Optional[Decimal] = None
    total_fees: Decimal = Decimal("0")
    id: UUID = field(default_factory=uuid4)
