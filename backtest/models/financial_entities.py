"""Financial entities: Assets, Brokers, Accounts, Trading Pairs."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class AssetType(Enum):
    """Types of financial assets."""
    CURRENCY = "CURRENCY"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    INDICE = "INDICE"
    COMMODITY = "COMMODITY"


@dataclass(frozen=True)
class Asset:
    """
    Represents a financial asset (stock, crypto, currency, etc.).
    
    Attributes:
        id: Unique identifier (UUID)
        ticker: Asset ticker symbol (e.g., "BTC", "AAPL", "USD")
        name: Full name of the asset
        asset_type: Type of asset (CURRENCY, STOCK, CRYPTO, etc.)
        min_unit: Minimum tradeable unit (e.g., 0.00000001 for BTC)
    """
    ticker: str
    name: str
    asset_type: AssetType
    min_unit: Decimal = Decimal("1")
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate asset data."""
        if not self.ticker or not self.ticker.strip():
            raise ValueError("Asset ticker cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Asset name cannot be empty")
        if self.min_unit <= 0:
            raise ValueError("min_unit must be positive")


@dataclass(frozen=True)
class TradingPair:
    """
    Represents a trading pair (e.g., BTC/USD, EUR/USD, AAPL/USD).
    
    Attributes:
        id: Unique identifier (UUID)
        base_asset: The asset being traded
        quote_asset: The asset used for pricing
        multiplying_factor: Price multiplier (e.g., 1000 for mini contracts)
        contract_size: Size of one contract in base asset units
        min_unit: Minimum tradeable quantity
        pair_code: Unique code for the pair (e.g., "BTCUSD")
    """
    base_asset: Asset
    quote_asset: Asset
    pair_code: str = ""
    multiplying_factor: Decimal = Decimal("1")
    contract_size: Decimal = Decimal("1")
    min_unit: Decimal = Decimal("1")
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate trading pair and generate pair_code if not provided."""
        if self.multiplying_factor <= 0:
            raise ValueError("multiplying_factor must be positive")
        if self.contract_size <= 0:
            raise ValueError("contract_size must be positive")
        if self.min_unit <= 0:
            raise ValueError("min_unit must be positive")
        
        # Generate pair_code if not provided
        if not self.pair_code:
            object.__setattr__(
                self, 
                "pair_code", 
                f"{self.base_asset.ticker}{self.quote_asset.ticker}"
            )


@dataclass(frozen=True)
class Broker:
    """
    Represents a broker/exchange.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Broker name (e.g., "Binance", "Interactive Brokers")
        code: Short broker code (e.g., "BINANCE", "IB")
        land: Country/jurisdiction (e.g., "US", "GLOBAL")
        description: Detailed description
    """
    name: str
    code: str
    land: str = "GLOBAL"
    description: str = ""
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate broker data."""
        if not self.name or not self.name.strip():
            raise ValueError("Broker name cannot be empty")
        if not self.code or not self.code.strip():
            raise ValueError("Broker code cannot be empty")


@dataclass(frozen=True)
class TraderAgent:
    """
    Represents a trading agent/strategy instance.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Agent name
        description: Agent description
    """
    name: str
    description: str = ""
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate agent data."""
        if not self.name or not self.name.strip():
            raise ValueError("Agent name cannot be empty")


@dataclass(frozen=True)
class TaxRegime:
    """
    Tax configuration for an account.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Tax regime name
        income_tax_rate: Tax rate on income/profit (as decimal, e.g., 0.15 for 15%)
        withholding_tax_rate: Withholding tax rate (as decimal)
    """
    name: str
    income_tax_rate: Decimal = Decimal("0")
    withholding_tax_rate: Decimal = Decimal("0")
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate tax regime data."""
        if not self.name or not self.name.strip():
            raise ValueError("Tax regime name cannot be empty")
        if not (0 <= self.income_tax_rate <= 1):
            raise ValueError("income_tax_rate must be between 0 and 1")
        if not (0 <= self.withholding_tax_rate <= 1):
            raise ValueError("withholding_tax_rate must be between 0 and 1")


@dataclass(frozen=True)
class Account:
    """
    Represents a trading account linking agent, asset, broker, and tax regime.
    
    Attributes:
        id: Unique identifier (UUID)
        agent: The trading agent/strategy
        base_asset: The base currency/asset of the account
        broker: The broker where account is held
        tax_regime: Tax configuration
        initial_balance: Starting balance in base_asset
    """
    agent: TraderAgent
    base_asset: Asset
    broker: Broker
    tax_regime: TaxRegime
    initial_balance: Decimal = Decimal("0")
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate account data."""
        if self.initial_balance < 0:
            raise ValueError("initial_balance cannot be negative")
