"""Base repository with generic CRUD operations."""

from typing import Dict, Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar('T')


class InMemoryRepository(Generic[T]):
    """
    Generic in-memory repository with CRUD operations.
    
    Uses UUID-based storage for entities.
    
    Type Parameters:
        T: The entity type stored in this repository
    """
    
    def __init__(self):
        """Initialize empty repository."""
        self._storage: Dict[UUID, T] = {}
    
    def save(self, entity: T) -> T:
        """
        Save an entity to the repository.
        
        Args:
            entity: Entity to save (must have an 'id' attribute)
            
        Returns:
            The saved entity
            
        Raises:
            AttributeError: If entity doesn't have an 'id' attribute
        """
        if not hasattr(entity, 'id'):
            raise AttributeError(f"Entity {type(entity)} must have an 'id' attribute")
        
        entity_id = getattr(entity, 'id')
        if not isinstance(entity_id, UUID):
            raise TypeError(f"Entity id must be UUID, got {type(entity_id)}")
        
        self._storage[entity_id] = entity
        return entity
    
    def get(self, entity_id: UUID) -> Optional[T]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: UUID of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        return self._storage.get(entity_id)
    
    def get_all(self) -> List[T]:
        """
        Get all entities in the repository.
        
        Returns:
            List of all entities
        """
        return list(self._storage.values())
    
    def delete(self, entity_id: UUID) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: UUID of the entity to delete
            
        Returns:
            True if entity was deleted, False if not found
        """
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False
    
    def count(self) -> int:
        """
        Count entities in the repository.
        
        Returns:
            Number of entities
        """
        return len(self._storage)
    
    def clear(self) -> None:
        """Clear all entities from the repository."""
        self._storage.clear()
    
    def exists(self, entity_id: UUID) -> bool:
        """
        Check if an entity exists.
        
        Args:
            entity_id: UUID of the entity
            
        Returns:
            True if entity exists, False otherwise
        """
        return entity_id in self._storage
