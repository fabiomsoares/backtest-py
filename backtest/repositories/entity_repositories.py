"""Specialized repositories for domain entities."""

from typing import Dict, List, Optional
from uuid import UUID

from backtest.models import (
    Asset,
    Broker,
    TraderAgent,
    Account,
    TaxRegime,
    TradingPair,
    TradingRules,
)
from backtest.repositories.base import InMemoryRepository


class AssetRepository(InMemoryRepository[Asset]):
    """Repository for Asset entities with ticker-based lookup."""
    
    def __init__(self):
        """Initialize with ticker index."""
        super().__init__()
        self._ticker_index: Dict[str, UUID] = {}
    
    def save(self, entity: Asset) -> Asset:
        """Save asset and update ticker index."""
        result = super().save(entity)
        self._ticker_index[entity.ticker] = entity.id
        return result
    
    def get_by_ticker(self, ticker: str) -> Optional[Asset]:
        """
        Get asset by ticker symbol.
        
        Args:
            ticker: Ticker symbol (e.g., "BTC", "AAPL")
            
        Returns:
            Asset if found, None otherwise
        """
        asset_id = self._ticker_index.get(ticker)
        if asset_id:
            return self.get(asset_id)
        return None
    
    def clear(self) -> None:
        """Clear repository and indexes."""
        super().clear()
        self._ticker_index.clear()


class BrokerRepository(InMemoryRepository[Broker]):
    """Repository for Broker entities with code-based lookup."""
    
    def __init__(self):
        """Initialize with code index."""
        super().__init__()
        self._code_index: Dict[str, UUID] = {}
    
    def save(self, entity: Broker) -> Broker:
        """Save broker and update code index."""
        result = super().save(entity)
        self._code_index[entity.code] = entity.id
        return result
    
    def get_by_code(self, code: str) -> Optional[Broker]:
        """
        Get broker by code.
        
        Args:
            code: Broker code (e.g., "BINANCE", "IB")
            
        Returns:
            Broker if found, None otherwise
        """
        broker_id = self._code_index.get(code)
        if broker_id:
            return self.get(broker_id)
        return None
    
    def clear(self) -> None:
        """Clear repository and indexes."""
        super().clear()
        self._code_index.clear()


class TraderAgentRepository(InMemoryRepository[TraderAgent]):
    """Repository for TraderAgent entities."""
    pass


class AccountRepository(InMemoryRepository[Account]):
    """Repository for Account entities with agent and broker lookups."""
    
    def get_by_agent(self, agent_id: UUID) -> List[Account]:
        """
        Get all accounts for an agent.
        
        Args:
            agent_id: UUID of the agent
            
        Returns:
            List of accounts for the agent
        """
        return [acc for acc in self.get_all() if acc.agent.id == agent_id]
    
    def get_by_broker(self, broker_id: UUID) -> List[Account]:
        """
        Get all accounts at a broker.
        
        Args:
            broker_id: UUID of the broker
            
        Returns:
            List of accounts at the broker
        """
        return [acc for acc in self.get_all() if acc.broker.id == broker_id]


class TaxRegimeRepository(InMemoryRepository[TaxRegime]):
    """Repository for TaxRegime entities."""
    pass


class TradingPairRepository(InMemoryRepository[TradingPair]):
    """Repository for TradingPair entities with pair_code lookup."""
    
    def __init__(self):
        """Initialize with pair_code index."""
        super().__init__()
        self._pair_code_index: Dict[str, UUID] = {}
    
    def save(self, entity: TradingPair) -> TradingPair:
        """Save trading pair and update pair_code index."""
        result = super().save(entity)
        self._pair_code_index[entity.pair_code] = entity.id
        return result
    
    def get_by_pair_code(self, pair_code: str) -> Optional[TradingPair]:
        """
        Get trading pair by pair code.
        
        Args:
            pair_code: Pair code (e.g., "BTCUSD")
            
        Returns:
            TradingPair if found, None otherwise
        """
        pair_id = self._pair_code_index.get(pair_code)
        if pair_id:
            return self.get(pair_id)
        return None
    
    def clear(self) -> None:
        """Clear repository and indexes."""
        super().clear()
        self._pair_code_index.clear()


class TradingRulesRepository(InMemoryRepository[TradingRules]):
    """Repository for TradingRules entities with broker and pair lookups."""
    
    def get_by_broker_and_pair(
        self, 
        broker_id: UUID, 
        pair_code: str
    ) -> Optional[TradingRules]:
        """
        Get trading rules for a broker and trading pair.
        
        Args:
            broker_id: UUID of the broker
            pair_code: Trading pair code
            
        Returns:
            TradingRules if found, None otherwise
        """
        for rules in self.get_all():
            if rules.broker_id == broker_id and rules.pair_code == pair_code:
                return rules
        return None
    
    def get_by_broker(self, broker_id: UUID) -> List[TradingRules]:
        """
        Get all trading rules for a broker.
        
        Args:
            broker_id: UUID of the broker
            
        Returns:
            List of trading rules for the broker
        """
        return [rules for rules in self.get_all() if rules.broker_id == broker_id]
