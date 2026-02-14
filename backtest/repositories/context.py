"""Central context for managing all repositories and backtest state."""

from typing import Optional

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
from backtest.models import (
    BacktestRun,
    AccountBalance,
    AccountTransaction,
)


class BacktestContext:
    """
    Central context managing all repositories.
    
    Provides access to all domain entity repositories and manages
    the lifecycle of backtest data.
    
    Attributes:
        assets: Repository for Asset entities
        brokers: Repository for Broker entities
        agents: Repository for TraderAgent entities
        accounts: Repository for Account entities
        tax_regimes: Repository for TaxRegime entities
        trading_pairs: Repository for TradingPair entities
        trading_rules: Repository for TradingRules entities
        orders: Repository for TradingOrder entities
        order_history: Repository for TradingOrderHistory snapshots
        market_data: Repository for market bar data
        backtest_runs: Repository for BacktestRun configurations
        account_balances: Repository for AccountBalance snapshots
        account_transactions: Repository for AccountTransaction records
    """
    
    def __init__(self):
        """Initialize all repositories."""
        # Static configuration repositories (persist across runs)
        self.assets = AssetRepository()
        self.brokers = BrokerRepository()
        self.agents = TraderAgentRepository()
        self.accounts = AccountRepository()
        self.tax_regimes = TaxRegimeRepository()
        self.trading_pairs = TradingPairRepository()
        self.trading_rules = TradingRulesRepository()
        self.market_data = MarketDataRepository()
        
        # Runtime repositories (cleared between runs)
        self.orders = OrderRepository()
        self.order_history = OrderHistoryRepository()
        self.backtest_runs = InMemoryRepository[BacktestRun]()
        self.account_balances = InMemoryRepository[AccountBalance]()
        self.account_transactions = InMemoryRepository[AccountTransaction]()
    
    def reset_runtime_state(self) -> None:
        """
        Clear runtime state for a new backtest run.
        
        Clears orders, history, runs, balances, and transactions
        while keeping assets, brokers, agents, accounts, and market data.
        """
        self.orders.clear()
        self.order_history.clear()
        self.backtest_runs.clear()
        self.account_balances.clear()
        self.account_transactions.clear()
    
    def reset_all(self) -> None:
        """
        Clear all repositories.
        
        Use with caution - this removes all configuration and runtime data.
        """
        self.assets.clear()
        self.brokers.clear()
        self.agents.clear()
        self.accounts.clear()
        self.tax_regimes.clear()
        self.trading_pairs.clear()
        self.trading_rules.clear()
        self.market_data.clear()
        self.reset_runtime_state()
    
    def get_statistics(self) -> dict:
        """
        Get statistics about repository contents.
        
        Returns:
            Dictionary with counts for each repository
        """
        return {
            "assets": self.assets.count(),
            "brokers": self.brokers.count(),
            "agents": self.agents.count(),
            "accounts": self.accounts.count(),
            "tax_regimes": self.tax_regimes.count(),
            "trading_pairs": self.trading_pairs.count(),
            "trading_rules": self.trading_rules.count(),
            "orders": self.orders.count(),
            "order_history": self.order_history.count(),
            "backtest_runs": self.backtest_runs.count(),
            "account_balances": self.account_balances.count(),
            "account_transactions": self.account_transactions.count(),
            "market_data_symbols": len(self.market_data.get_symbols()),
        }
    
    def __repr__(self) -> str:
        """String representation with statistics."""
        stats = self.get_statistics()
        return (
            f"BacktestContext(\n"
            f"  Configuration: {stats['assets']} assets, {stats['brokers']} brokers, "
            f"{stats['trading_rules']} rules\n"
            f"  Runtime: {stats['orders']} orders, {stats['accounts']} accounts\n"
            f"  Market Data: {stats['market_data_symbols']} symbols\n"
            f")"
        )


# Global context instance (singleton pattern)
_global_context: Optional[BacktestContext] = None


def get_global_context() -> BacktestContext:
    """
    Get or create the global backtest context.
    
    Returns:
        Global BacktestContext instance
    """
    global _global_context
    if _global_context is None:
        _global_context = BacktestContext()
    return _global_context


def reset_global_context() -> BacktestContext:
    """
    Reset and return the global backtest context.
    
    Returns:
        New BacktestContext instance
    """
    global _global_context
    _global_context = BacktestContext()
    return _global_context
