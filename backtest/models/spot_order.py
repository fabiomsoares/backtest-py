"""Spot order model for direct asset exchange."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from backtest.models.orders import OrderDirection, OrderStatus


@dataclass(frozen=True)
class SpotOrder:
    """
    Order for direct asset exchange in spot markets.
    
    Unlike TradingOrder (derivatives/futures), SpotOrder:
    - Exchanges one asset for another directly (e.g., USD for BTC)
    - Updates available balance immediately after fill
    - No contract binding, no leverage
    - States: PENDING → FILLED or PENDING → CANCELLED
    
    Attributes:
        broker_id: Broker where order is placed
        trading_pair_code: Trading pair (e.g., "BTCUSD")
        agent_id: Trading agent ID
        account_id: Account ID
        backtest_run_id: Backtest run ID
        order_number: Sequential order number for this agent
        direction: BUY or SELL
        status: PENDING, FILLED, or CANCELLED
        create_timestamp: When order was created
        volume: Order volume in base asset
        limit_price: Limit price (None = market order)
        id: Unique order identifier
        parent_id: Parent order ID (for splits/modifications)
        root_id: Root order ID (original order in chain)
        fill_timestamp: When order was filled
        fill_price: Price at which order was filled
        fill_volume: Volume that was filled (for partial fills)
        cancel_timestamp: When order was cancelled
        cancel_volume: Volume that was cancelled
        fee_create: Fee charged on creation
        fee_fill: Fee charged on fill
        fee_cancel: Fee charged on cancellation
        
    Example:
        # Market order to buy BTC with USD
        SpotOrder(
            broker_id=broker.id,
            trading_pair_code="BTCUSD",
            agent_id=agent.id,
            account_id=account.id,
            backtest_run_id=run.id,
            order_number=1,
            direction=OrderDirection.BUY,
            status=OrderStatus.PENDING,
            create_timestamp=datetime.now(),
            volume=Decimal("1.5"),
            limit_price=None  # Market order
        )
    """
    broker_id: UUID
    trading_pair_code: str
    agent_id: UUID
    account_id: UUID
    backtest_run_id: UUID
    order_number: int
    direction: OrderDirection
    status: OrderStatus
    create_timestamp: datetime
    volume: Decimal
    limit_price: Optional[Decimal] = None
    
    # Identifiers
    id: UUID = field(default_factory=uuid4)
    parent_id: Optional[UUID] = None
    root_id: Optional[UUID] = None
    
    # Fill information
    fill_timestamp: Optional[datetime] = None
    fill_price: Optional[Decimal] = None
    fill_volume: Optional[Decimal] = None
    
    # Cancel information
    cancel_timestamp: Optional[datetime] = None
    cancel_volume: Optional[Decimal] = None
    
    # Fees at each stage
    fee_create: Optional[Decimal] = None
    fee_fill: Optional[Decimal] = None
    fee_cancel: Optional[Decimal] = None
    
    def __post_init__(self):
        """Validate spot order data and set root_id if needed."""
        if not self.trading_pair_code or not self.trading_pair_code.strip():
            raise ValueError("trading_pair_code cannot be empty")
        if self.volume <= 0:
            raise ValueError("volume must be positive")
        if self.order_number < 0:
            raise ValueError("order_number must be non-negative")
        
        # Set root_id if not set
        if self.root_id is None:
            if self.parent_id is None:
                # This is an original order, it is its own root
                object.__setattr__(self, "root_id", self.id)
            # else root_id should be explicitly set by caller
        
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
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED
    
    @property
    def is_active(self) -> bool:
        """Check if order is active (pending)."""
        return self.status == OrderStatus.PENDING
    
    @property
    def is_market_order(self) -> bool:
        """Check if this is a market order (no limit price)."""
        return self.limit_price is None
    
    @property
    def is_limit_order(self) -> bool:
        """Check if this is a limit order."""
        return self.limit_price is not None
    
    @property
    def total_fees(self) -> Decimal:
        """Calculate total fees across all stages."""
        total = Decimal("0")
        if self.fee_create:
            total += self.fee_create
        if self.fee_fill:
            total += self.fee_fill
        if self.fee_cancel:
            total += self.fee_cancel
        return total
    
    @property
    def remaining_volume(self) -> Decimal:
        """Calculate remaining unfilled volume."""
        filled = self.fill_volume or Decimal("0")
        cancelled = self.cancel_volume or Decimal("0")
        return self.volume - filled - cancelled
    
    def create_filled_copy(
        self,
        fill_timestamp: datetime,
        fill_price: Decimal,
        fill_volume: Optional[Decimal] = None,
        fee_fill: Optional[Decimal] = None
    ) -> "SpotOrder":
        """
        Create a new filled version of this order.
        
        Since SpotOrder is frozen, we create a new instance with updated fields.
        
        Args:
            fill_timestamp: When order was filled
            fill_price: Price at which order was filled
            fill_volume: Volume filled (defaults to full volume)
            fee_fill: Fee charged on fill
            
        Returns:
            New SpotOrder instance with FILLED status
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot fill order with status {self.status}")
        
        fill_vol = fill_volume or self.volume
        if fill_vol <= 0 or fill_vol > self.volume:
            raise ValueError("Invalid fill volume")
        
        return SpotOrder(
            broker_id=self.broker_id,
            trading_pair_code=self.trading_pair_code,
            agent_id=self.agent_id,
            account_id=self.account_id,
            backtest_run_id=self.backtest_run_id,
            order_number=self.order_number,
            direction=self.direction,
            status=OrderStatus.FILLED,
            create_timestamp=self.create_timestamp,
            volume=self.volume,
            limit_price=self.limit_price,
            id=self.id,
            parent_id=self.parent_id,
            root_id=self.root_id,
            fill_timestamp=fill_timestamp,
            fill_price=fill_price,
            fill_volume=fill_vol,
            cancel_timestamp=self.cancel_timestamp,
            cancel_volume=self.cancel_volume,
            fee_create=self.fee_create,
            fee_fill=fee_fill,
            fee_cancel=self.fee_cancel
        )
    
    def create_cancelled_copy(
        self,
        cancel_timestamp: datetime,
        cancel_volume: Optional[Decimal] = None,
        fee_cancel: Optional[Decimal] = None
    ) -> "SpotOrder":
        """
        Create a new cancelled version of this order.
        
        Args:
            cancel_timestamp: When order was cancelled
            cancel_volume: Volume cancelled (defaults to remaining volume)
            fee_cancel: Fee charged on cancellation
            
        Returns:
            New SpotOrder instance with CANCELLED status
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot cancel order with status {self.status}")
        
        cancel_vol = cancel_volume or self.remaining_volume
        if cancel_vol <= 0 or cancel_vol > self.remaining_volume:
            raise ValueError("Invalid cancel volume")
        
        return SpotOrder(
            broker_id=self.broker_id,
            trading_pair_code=self.trading_pair_code,
            agent_id=self.agent_id,
            account_id=self.account_id,
            backtest_run_id=self.backtest_run_id,
            order_number=self.order_number,
            direction=self.direction,
            status=OrderStatus.CANCELLED,
            create_timestamp=self.create_timestamp,
            volume=self.volume,
            limit_price=self.limit_price,
            id=self.id,
            parent_id=self.parent_id,
            root_id=self.root_id,
            fill_timestamp=self.fill_timestamp,
            fill_price=self.fill_price,
            fill_volume=self.fill_volume,
            cancel_timestamp=cancel_timestamp,
            cancel_volume=cancel_vol,
            fee_create=self.fee_create,
            fee_fill=self.fee_fill,
            fee_cancel=fee_cancel
        )
    
    def __repr__(self) -> str:
        """String representation of spot order."""
        return (
            f"SpotOrder(#{self.order_number}, {self.direction.name}, "
            f"{self.volume} @ {self.limit_price or 'MARKET'}, "
            f"status={self.status.name})"
        )
