"""
Event handler for processing backtesting events.
"""

from typing import Callable, Dict, List
from enum import Enum


class EventType(Enum):
    """Types of events in the backtesting system."""
    BAR = "bar"
    ORDER_FILLED = "order_filled"
    ORDER_REJECTED = "order_rejected"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"


class EventHandler:
    """
    Event handler for managing and dispatching backtesting events.
    
    Allows strategies and components to subscribe to and react to events.
    """
    
    def __init__(self):
        """Initialize the event handler."""
        self._subscribers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type: EventType, *args, **kwargs):
        """
        Emit an event to all subscribers.
        
        Args:
            event_type: Type of event to emit
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(*args, **kwargs)
    
    def clear(self):
        """Clear all event subscribers."""
        for event_type in self._subscribers:
            self._subscribers[event_type].clear()
