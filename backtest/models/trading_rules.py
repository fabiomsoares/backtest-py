"""Trading rules: Fees, leverage, and trading constraints."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from datetime import time


class LeverageType(Enum):
    """Types of leverage calculation."""
    NO_LEVERAGE = "NO_LEVERAGE"
    FLAT_MARGIN_PER_VOLUME = "FLAT_MARGIN_PER_VOLUME"  # Fixed margin per unit of volume
    MARGIN_MULTIPLIER = "MARGIN_MULTIPLIER"  # Margin = notional / multiplier


class FeeType(Enum):
    """Types of fee calculation."""
    NO_FEE = "NO_FEE"
    FLAT_PER_VOLUME = "FLAT_PER_VOLUME"  # Fee per unit of volume
    FLAT_PER_TRADE = "FLAT_PER_TRADE"  # Fixed fee per trade
    PERCENT_OF_NOTIONAL = "PERCENT_OF_NOTIONAL"  # Percentage of trade value
    PERCENT_OF_MARGIN = "PERCENT_OF_MARGIN"  # Percentage of margin


class FeeTiming(Enum):
    """When fees are charged."""
    ON_CREATE = "ON_CREATE"  # When order is created
    ON_FILL = "ON_FILL"  # When order is filled
    ON_CLOSE = "ON_CLOSE"  # When position is closed
    ON_CANCEL = "ON_CANCEL"  # When order is cancelled
    ON_OVERNIGHT_PENDING = "ON_OVERNIGHT_PENDING"  # Daily while order is pending
    ON_OVERNIGHT_FILLED = "ON_OVERNIGHT_FILLED"  # Daily while position is open


class OvernightTiming(Enum):
    """When overnight fees are charged."""
    ON_PERIOD_CHANGE = "ON_PERIOD_CHANGE"  # At timeframe change (e.g., day change)
    ON_FIXED_TIME = "ON_FIXED_TIME"  # At specific time each day


@dataclass(frozen=True)
class Fee:
    """
    Fee configuration.
    
    Attributes:
        fee_type: How the fee is calculated
        fee_timing: When the fee is charged
        amount: Fee amount (interpretation depends on fee_type)
    """
    fee_type: FeeType
    fee_timing: FeeTiming
    amount: Decimal = Decimal("0")
    
    def __post_init__(self):
        """Validate fee configuration."""
        if self.amount < 0:
            raise ValueError("Fee amount cannot be negative")


@dataclass(frozen=True)
class TradingRules:
    """
    Comprehensive trading rules for a broker and trading pair.
    
    Defines leverage, fees, and constraints for trading a specific pair at a broker.
    
    Attributes:
        broker_id: UUID of the broker
        pair_code: Trading pair code
        leverage_type: How leverage/margin is calculated
        leverage_value: Leverage multiplier or margin amount
        brokerage_fee: Fee for brokerage services
        custody_fee: Fee for custody/holding
        leverage_fee: Fee for using leverage
        overnight_timing: When overnight fees are charged
        overnight_charge_time: Specific time for overnight fees (if ON_FIXED_TIME)
        min_volume: Minimum order volume
        min_notional_amount: Minimum order value
        min_margin_amount: Minimum margin required
        allows_long: Whether long positions are allowed
        allows_short: Whether short positions are allowed
    """
    broker_id: UUID
    pair_code: str
    leverage_type: LeverageType = LeverageType.NO_LEVERAGE
    leverage_value: Decimal = Decimal("1")
    brokerage_fee: Optional[Fee] = None
    custody_fee: Optional[Fee] = None
    leverage_fee: Optional[Fee] = None
    overnight_timing: OvernightTiming = OvernightTiming.ON_PERIOD_CHANGE
    overnight_charge_time: Optional[time] = None
    min_volume: Decimal = Decimal("0")
    min_notional_amount: Decimal = Decimal("0")
    min_margin_amount: Decimal = Decimal("0")
    allows_long: bool = True
    allows_short: bool = False
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate trading rules."""
        if not self.pair_code or not self.pair_code.strip():
            raise ValueError("pair_code cannot be empty")
        
        # Validate leverage configuration
        if self.leverage_type == LeverageType.NO_LEVERAGE:
            if self.leverage_value != Decimal("1"):
                raise ValueError("NO_LEVERAGE requires leverage_value = 1")
        elif self.leverage_type == LeverageType.FLAT_MARGIN_PER_VOLUME:
            if self.leverage_value <= 0:
                raise ValueError("FLAT_MARGIN_PER_VOLUME requires positive leverage_value")
        elif self.leverage_type == LeverageType.MARGIN_MULTIPLIER:
            if self.leverage_value <= 0:
                raise ValueError("MARGIN_MULTIPLIER requires positive leverage_value")
        
        # Validate overnight timing
        if self.overnight_timing == OvernightTiming.ON_FIXED_TIME:
            if self.overnight_charge_time is None:
                raise ValueError("ON_FIXED_TIME requires overnight_charge_time to be set")
        
        # Validate constraints
        if self.min_volume < 0:
            raise ValueError("min_volume cannot be negative")
        if self.min_notional_amount < 0:
            raise ValueError("min_notional_amount cannot be negative")
        if self.min_margin_amount < 0:
            raise ValueError("min_margin_amount cannot be negative")
        
        # At least one direction must be allowed
        if not self.allows_long and not self.allows_short:
            raise ValueError("At least one of allows_long or allows_short must be True")
    
    def calculate_margin_required(
        self, 
        volume: Decimal, 
        price: Decimal, 
        contract_size: Decimal = Decimal("1")
    ) -> Decimal:
        """
        Calculate the margin required for a given position.
        
        Args:
            volume: Trading volume
            price: Entry price
            contract_size: Contract size multiplier
            
        Returns:
            Required margin amount
        """
        notional = volume * price * contract_size
        
        if self.leverage_type == LeverageType.NO_LEVERAGE:
            return notional
        elif self.leverage_type == LeverageType.FLAT_MARGIN_PER_VOLUME:
            return volume * self.leverage_value
        elif self.leverage_type == LeverageType.MARGIN_MULTIPLIER:
            return notional / self.leverage_value
        
        return notional
    
    def validate_order(
        self,
        volume: Decimal,
        price: Decimal,
        margin: Decimal,
        is_long: bool,
        contract_size: Decimal = Decimal("1")
    ) -> tuple[bool, Optional[str]]:
        """
        Validate an order against trading rules.
        
        Args:
            volume: Order volume
            price: Order price
            margin: Available margin
            is_long: Whether this is a long order
            contract_size: Contract size multiplier
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check direction
        if is_long and not self.allows_long:
            return False, "Long positions not allowed"
        if not is_long and not self.allows_short:
            return False, "Short positions not allowed"
        
        # Check minimum volume
        if volume < self.min_volume:
            return False, f"Volume {volume} below minimum {self.min_volume}"
        
        # Check minimum notional
        notional = volume * price * contract_size
        if notional < self.min_notional_amount:
            return False, f"Notional {notional} below minimum {self.min_notional_amount}"
        
        # Check minimum margin
        required_margin = self.calculate_margin_required(volume, price, contract_size)
        if required_margin < self.min_margin_amount:
            return False, f"Margin {required_margin} below minimum {self.min_margin_amount}"
        
        # Check available margin
        if margin < required_margin:
            return False, f"Insufficient margin: need {required_margin}, have {margin}"
        
        return True, None
