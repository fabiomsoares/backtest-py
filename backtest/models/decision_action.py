"""Decision action model for agent commands to backtest runner."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, List, Dict, Tuple
from uuid import UUID


class ActionType(Enum):
    """Types of decision actions available to trading agents."""
    CREATE_SPOT_LIMIT = auto()
    CREATE_SPOT_MARKET = auto()
    CREATE_TRADE_LIMIT = auto()
    CREATE_TRADE_MARKET = auto()
    MODIFY_SPOT_LIMIT = auto()
    MODIFY_TRADE_LIMIT = auto()
    SPLIT_SPOT_LIMIT = auto()
    SPLIT_TRADE_LIMIT = auto()
    CANCEL_SPOT_LIMIT = auto()
    CANCEL_TRADE_LIMIT = auto()
    CLOSE_TRADE = auto()


@dataclass
class DecisionAction:
    """
    Command from trading agent to backtest runner.
    
    This represents a validated action that the agent wants to execute.
    All actions are validated before being added to the action queue.
    
    Attributes:
        action_type: Type of action to execute
        timestamp: When the action was requested
        agent_id: Trading agent making the decision
        account_id: Account to use for the action
        broker_id: Broker to use
        backtest_run_id: Current backtest run
        trading_pair_code: Trading pair (e.g., "BTCUSD")
        
        # Action-specific parameters (use Optional for flexibility)
        order_id: ID of existing order (for modify/split/cancel/close)
        volume: Order volume
        price: Limit price (None for market orders)
        direction: BUY or SELL (for create actions)
        leverage: Leverage multiplier (for trade orders)
        stop_loss: Stop loss price
        take_profit: Take profit price
        
        # For split actions
        split_chunks: List of dicts with parameters for each chunk
            Format: [{"volume": Decimal, "price": Decimal, ...}, ...]
            
    Example:
        # Create spot market order
        DecisionAction(
            action_type=ActionType.CREATE_SPOT_MARKET,
            timestamp=datetime.now(),
            agent_id=agent.id,
            account_id=account.id,
            broker_id=broker.id,
            backtest_run_id=run.id,
            trading_pair_code="BTCUSD",
            volume=Decimal("1.5"),
            direction=OrderDirection.BUY
        )
        
        # Modify trade order
        DecisionAction(
            action_type=ActionType.MODIFY_TRADE_LIMIT,
            timestamp=datetime.now(),
            agent_id=agent.id,
            account_id=account.id,
            broker_id=broker.id,
            backtest_run_id=run.id,
            trading_pair_code="BTCUSD",
            order_id=existing_order.id,
            stop_loss=Decimal("45000"),
            take_profit=Decimal("55000")
        )
    """
    action_type: ActionType
    timestamp: datetime
    agent_id: UUID
    account_id: UUID
    broker_id: UUID
    backtest_run_id: UUID
    trading_pair_code: str
    
    # Action-specific parameters
    order_id: Optional[UUID] = None
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None
    direction: Optional[str] = None  # Will be converted to OrderDirection
    leverage: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    
    # For splits
    split_chunks: Optional[List[Dict]] = None
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate action before execution.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate common fields
        if not self.trading_pair_code or not self.trading_pair_code.strip():
            return False, "trading_pair_code cannot be empty"
        
        # Validate based on action type
        if self.action_type in [
            ActionType.CREATE_SPOT_MARKET,
            ActionType.CREATE_SPOT_LIMIT,
            ActionType.CREATE_TRADE_MARKET,
            ActionType.CREATE_TRADE_LIMIT
        ]:
            # Create actions require volume and direction
            if self.volume is None or self.volume <= 0:
                return False, "Create action requires positive volume"
            if self.direction is None:
                return False, "Create action requires direction"
            
            # Limit orders require price
            if self.action_type in [ActionType.CREATE_SPOT_LIMIT, ActionType.CREATE_TRADE_LIMIT]:
                if self.price is None or self.price <= 0:
                    return False, "Limit order requires positive price"
        
        elif self.action_type in [
            ActionType.MODIFY_SPOT_LIMIT,
            ActionType.MODIFY_TRADE_LIMIT,
            ActionType.CANCEL_SPOT_LIMIT,
            ActionType.CANCEL_TRADE_LIMIT,
            ActionType.CLOSE_TRADE
        ]:
            # These actions require order_id
            if self.order_id is None:
                return False, f"{self.action_type.name} requires order_id"
        
        elif self.action_type in [ActionType.SPLIT_SPOT_LIMIT, ActionType.SPLIT_TRADE_LIMIT]:
            # Split actions require order_id and split_chunks
            if self.order_id is None:
                return False, "Split action requires order_id"
            if not self.split_chunks or len(self.split_chunks) < 2:
                return False, "Split action requires at least 2 chunks"
            
            # Validate each chunk has required fields
            for i, chunk in enumerate(self.split_chunks):
                if "volume" not in chunk:
                    return False, f"Chunk {i} missing volume"
                if chunk["volume"] <= 0:
                    return False, f"Chunk {i} volume must be positive"
        
        # Validate numeric fields if present
        if self.leverage is not None and self.leverage <= 0:
            return False, "leverage must be positive if set"
        if self.stop_loss is not None and self.stop_loss <= 0:
            return False, "stop_loss must be positive if set"
        if self.take_profit is not None and self.take_profit <= 0:
            return False, "take_profit must be positive if set"
        
        return True, ""
    
    def __repr__(self) -> str:
        """String representation of decision action."""
        parts = [f"DecisionAction({self.action_type.name}"]
        
        if self.order_id:
            parts.append(f"order={str(self.order_id)[:8]}")
        if self.volume:
            parts.append(f"vol={self.volume}")
        if self.price:
            parts.append(f"price={self.price}")
        if self.direction:
            parts.append(f"dir={self.direction}")
        
        return ", ".join(parts) + ")"
