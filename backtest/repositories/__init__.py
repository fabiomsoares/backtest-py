"""Repository layer for data access and storage."""

from backtest.repositories.base import InMemoryRepository
from backtest.repositories.entity_repositories import (
    AssetRepository,
    BrokerRepository,
    TraderAgentRepository,
    AccountRepository,
    TaxRegimeRepository,
    TradingPairRepository,
    TradingRulesRepository,
)
from backtest.repositories.order_repositories import (
    OrderRepository,
    OrderHistoryRepository,
)
from backtest.repositories.market_data_repository import MarketDataRepository
from backtest.repositories.transaction_repository import TransactionRepository
from backtest.repositories.spot_order_repository import SpotOrderRepository
from backtest.repositories.balance_repository import BalanceRepository
from backtest.repositories.context import (
    BacktestContext,
    get_global_context,
    reset_global_context,
)

__all__ = [
    # Base
    "InMemoryRepository",
    # Entity repositories
    "AssetRepository",
    "BrokerRepository",
    "TraderAgentRepository",
    "AccountRepository",
    "TaxRegimeRepository",
    "TradingPairRepository",
    "TradingRulesRepository",
    # Order repositories
    "OrderRepository",
    "OrderHistoryRepository",
    "SpotOrderRepository",
    # Transaction and balance repositories
    "TransactionRepository",
    "BalanceRepository",
    # Market data
    "MarketDataRepository",
    # Context
    "BacktestContext",
    "get_global_context",
    "reset_global_context",
]
