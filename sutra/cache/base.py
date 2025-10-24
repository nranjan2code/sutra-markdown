"""
Base Cache - Abstract interface for all cache implementations

Provides common functionality:
- Get/Set/Delete operations
- TTL support
- Statistics tracking
- Cache invalidation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from datetime import datetime, timedelta


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    size_bytes: int = 0
    item_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 1.0 - self.hit_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'evictions': self.evictions,
            'size_bytes': self.size_bytes,
            'item_count': self.item_count,
            'hit_rate': self.hit_rate,
            'miss_rate': self.miss_rate,
        }


class BaseCache(ABC):
    """
    Abstract base class for all cache implementations
    """
    
    def __init__(
        self,
        max_size_mb: int = 1024,
        ttl_seconds: Optional[int] = 3600,
        enable_stats: bool = True
    ):
        """
        Initialize cache
        
        Args:
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time-to-live in seconds (None = no expiration)
            enable_stats: Enable statistics tracking
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        self.enable_stats = enable_stats
        
        if enable_stats:
            self._stats = CacheStats()
        else:
            self._stats = None
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (seconds)
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed and was deleted
        """
        pass
    
    @abstractmethod
    async def clear(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired
        """
        pass
    
    @property
    def stats(self) -> Optional[CacheStats]:
        """Get cache statistics"""
        return self._stats
    
    def _update_stats_hit(self):
        """Update statistics for cache hit"""
        if self._stats:
            self._stats.hits += 1
    
    def _update_stats_miss(self):
        """Update statistics for cache miss"""
        if self._stats:
            self._stats.misses += 1
    
    def _update_stats_set(self, size_bytes: int = 0):
        """Update statistics for cache set"""
        if self._stats:
            self._stats.sets += 1
            self._stats.item_count += 1
            self._stats.size_bytes += size_bytes
    
    def _update_stats_delete(self, size_bytes: int = 0):
        """Update statistics for cache delete"""
        if self._stats:
            self._stats.deletes += 1
            self._stats.item_count = max(0, self._stats.item_count - 1)
            self._stats.size_bytes = max(0, self._stats.size_bytes - size_bytes)
    
    def _update_stats_eviction(self):
        """Update statistics for cache eviction"""
        if self._stats:
            self._stats.evictions += 1
    
    def _is_expired(self, timestamp: datetime, ttl: Optional[int] = None) -> bool:
        """
        Check if cached item is expired
        
        Args:
            timestamp: Cache timestamp
            ttl: Optional TTL override
            
        Returns:
            True if expired
        """
        if ttl is None:
            ttl = self.ttl_seconds
        
        if ttl is None:
            return False  # No expiration
        
        expiration = timestamp + timedelta(seconds=ttl)
        return datetime.now() > expiration
