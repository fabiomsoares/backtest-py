"""
Base strategy class for implementing trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from backtest.models.market_data import MarketBar
from backtest.models.order import Order, OrderSide, OrderType
from backtest.models.position import Position


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    
    Subclass this and implement the on_bar method to define your strategy logic.
    """
    
    def __init__(self, name: str = "Strategy"):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
        self.orders: List[Order] = []
        self.positions: Dict[str, Position] = {}
        self.bars: List[MarketBar] = []
    
    @abstractmethod
    def on_bar(self, bar: MarketBar):
        """
        Called for each new bar of market data.
        
        Implement your strategy logic here.
        
        Args:
            bar: The current market bar
        """
        pass
    
    def on_order_filled(self, order: Order):
        """
        Called when an order is filled.
        
        Override this method to handle order fills.
        
        Args:
            order: The filled order
        """
        pass
    
    def buy(self, symbol: str, quantity: float, price: Optional[float] = None) -> Order:
        """
        Create a buy order.
        
        Args:
            symbol: Trading symbol
            quantity: Quantity to buy
            price: Limit price (None for market order)
            
        Returns:
            The created order
        """
        order_type = OrderType.LIMIT if price else OrderType.MARKET
        order = Order(
            order_id=f"order_{len(self.orders)}",
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=order_type,
            quantity=quantity,
            price=price,
            timestamp=self.bars[-1].timestamp if self.bars else None
        )
        self.orders.append(order)
        return order
    
    def sell(self, symbol: str, quantity: float, price: Optional[float] = None) -> Order:
        """
        Create a sell order.
        
        Args:
            symbol: Trading symbol
            quantity: Quantity to sell
            price: Limit price (None for market order)
            
        Returns:
            The created order
        """
        order_type = OrderType.LIMIT if price else OrderType.MARKET
        order = Order(
            order_id=f"order_{len(self.orders)}",
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=order_type,
            quantity=quantity,
            price=price,
            timestamp=self.bars[-1].timestamp if self.bars else None
        )
        self.orders.append(order)
        return order
    
    def has_position(self, symbol: str) -> bool:
        """Check if the strategy has a position in the given symbol."""
        return symbol in self.positions and self.positions[symbol].quantity != 0
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get the current position for a symbol."""
        return self.positions.get(symbol)
