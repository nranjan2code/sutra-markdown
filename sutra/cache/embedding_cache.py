"""
Embedding Cache - Cache for document embeddings

Uses Redis (if available) + disk caching for embeddings.
Falls back to disk-only if Redis is not available.

Features:
- Redis for fast distributed access
- Disk fallback for persistence
- Numpy array serialization
- TTL support
"""

import pickle
import hashlib
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
import numpy as np

from .base import BaseCache


class EmbeddingCache(BaseCache):
    """
    Cache for embeddings with Redis + disk storage
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        redis_url: Optional[str] = None,
        max_size_mb: int = 256,
        ttl_seconds: Optional[int] = 7200
    ):
        """
        Initialize embedding cache
        
        Args:
            cache_dir: Directory for disk cache
            redis_url: Redis connection URL (None = no Redis)
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time-to-live in seconds
        """
        super().__init__(max_size_mb, ttl_seconds)
        
        # Redis client (optional)
        self.redis_client = None
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
            except (ImportError, Exception):
                pass  # Redis not available
        
        # Disk cache
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".sutra" / "cache" / "embeddings"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for fast access
        self._memory_cache: dict[str, tuple[np.ndarray, datetime]] = {}
    
    def get_key(self, text: str, model: str = "nomic-embed-text-v1.5") -> str:
        """Generate cache key for text + model"""
        combined = f"{model}:{text}"
        hash_key = hashlib.md5(combined.encode()).hexdigest()
        return f"emb:{hash_key}"
    
    async def get(self, key: str) -> Optional[np.ndarray]:
        """Get embedding from cache"""
        # Check memory first
        if key in self._memory_cache:
            embedding, timestamp = self._memory_cache[key]
            if not self._is_expired(timestamp):
                self._update_stats_hit()
                return embedding
            else:
                del self._memory_cache[key]
        
        # Check Redis
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    cached = pickle.loads(data)
                    embedding = cached['embedding']
                    timestamp = cached['timestamp']
                    
                    if not self._is_expired(timestamp):
                        # Load into memory
                        self._memory_cache[key] = (embedding, timestamp)
                        self._update_stats_hit()
                        return embedding
            except Exception:
                pass
        
        # Check disk
        cache_file = self.cache_dir / f"{key}.npy"
        if cache_file.exists():
            try:
                data = np.load(cache_file, allow_pickle=True).item()
                embedding = data['embedding']
                timestamp = data['timestamp']
                
                if not self._is_expired(timestamp):
                    # Load into memory
                    self._memory_cache[key] = (embedding, timestamp)
                    self._update_stats_hit()
                    return embedding
                else:
                    cache_file.unlink()
            except Exception:
                pass
        
        self._update_stats_miss()
        return None
    
    async def set(
        self,
        key: str,
        value: np.ndarray,
        ttl: Optional[int] = None
    ) -> bool:
        """Set embedding in cache"""
        timestamp = datetime.now()
        use_ttl = ttl if ttl is not None else self.ttl_seconds
        
        # Store in memory
        self._memory_cache[key] = (value, timestamp)
        
        # Estimate size
        size = value.nbytes
        self._update_stats_set(size)
        
        # Store in Redis
        if self.redis_client:
            try:
                data = pickle.dumps({
                    'embedding': value,
                    'timestamp': timestamp,
                })
                if use_ttl:
                    self.redis_client.setex(key, use_ttl, data)
                else:
                    self.redis_client.set(key, data)
            except Exception:
                pass
        
        # Store in disk
        try:
            cache_file = self.cache_dir / f"{key}.npy"
            data = {
                'embedding': value,
                'timestamp': timestamp,
            }
            np.save(cache_file, data)
        except Exception:
            pass
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete embedding from cache"""
        existed = False
        
        # Delete from memory
        if key in self._memory_cache:
            del self._memory_cache[key]
            existed = True
        
        # Delete from Redis
        if self.redis_client:
            try:
                if self.redis_client.delete(key):
                    existed = True
            except Exception:
                pass
        
        # Delete from disk
        cache_file = self.cache_dir / f"{key}.npy"
        if cache_file.exists():
            cache_file.unlink()
            existed = True
        
        if existed:
            self._update_stats_delete()
        
        return existed
    
    async def clear(self) -> int:
        """Clear all cached embeddings"""
        count = len(self._memory_cache)
        
        # Clear memory
        self._memory_cache.clear()
        
        # Clear Redis
        if self.redis_client:
            try:
                # Clear all embedding keys
                pattern = "emb:*"
                keys = list(self.redis_client.scan_iter(match=pattern))
                if keys:
                    self.redis_client.delete(*keys)
                    count += len(keys)
            except Exception:
                pass
        
        # Clear disk
        for cache_file in self.cache_dir.glob("emb:*.npy"):
            cache_file.unlink()
            count += 1
        
        # Reset stats
        if self._stats:
            self._stats.item_count = 0
            self._stats.size_bytes = 0
        
        return count
    
    async def exists(self, key: str) -> bool:
        """Check if embedding exists in cache"""
        # Check memory
        if key in self._memory_cache:
            _, timestamp = self._memory_cache[key]
            return not self._is_expired(timestamp)
        
        # Check Redis
        if self.redis_client:
            try:
                if self.redis_client.exists(key):
                    return True
            except Exception:
                pass
        
        # Check disk
        cache_file = self.cache_dir / f"{key}.npy"
        return cache_file.exists()
