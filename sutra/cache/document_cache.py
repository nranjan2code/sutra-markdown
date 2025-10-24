"""
Document Cache - Cache for parsed documents

Uses memory + disk caching for parsed documents to avoid
re-parsing the same files.

Features:
- In-memory LRU cache for fast access
- Disk-based persistent cache
- File hash-based invalidation
- Automatic eviction on size limit
"""

import hashlib
import pickle
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from collections import OrderedDict

from ..models.document import ParsedDocument
from .base import BaseCache


class DocumentCache(BaseCache):
    """
    Cache for parsed documents with memory + disk storage
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_size_mb: int = 512,
        ttl_seconds: Optional[int] = 3600,
        enable_disk: bool = True
    ):
        """
        Initialize document cache
        
        Args:
            cache_dir: Directory for disk cache (None = ~/.sutra/cache/documents)
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time-to-live in seconds
            enable_disk: Enable disk-based caching
        """
        super().__init__(max_size_mb, ttl_seconds)
        
        # Memory cache (LRU)
        self._memory_cache: OrderedDict[str, tuple[ParsedDocument, datetime, int]] = OrderedDict()
        
        # Disk cache
        self.enable_disk = enable_disk
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".sutra" / "cache" / "documents"
        
        if enable_disk:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calculate hash of file for cache key"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            # Fallback to path + mtime
            stat = Path(file_path).stat()
            key = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(key.encode()).hexdigest()
    
    def get_key(self, file_path: str) -> str:
        """Generate cache key for file path"""
        file_hash = self._get_file_hash(file_path)
        return f"doc:{file_hash}"
    
    async def get(self, key: str) -> Optional[ParsedDocument]:
        """Get document from cache"""
        # Check memory cache first
        if key in self._memory_cache:
            doc, timestamp, size = self._memory_cache[key]
            
            # Check expiration
            if not self._is_expired(timestamp):
                # Move to end (LRU)
                self._memory_cache.move_to_end(key)
                self._update_stats_hit()
                return doc
            else:
                # Expired - remove
                del self._memory_cache[key]
                self._update_stats_delete(size)
        
        # Check disk cache
        if self.enable_disk:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    doc = data['document']
                    timestamp = data['timestamp']
                    
                    # Check expiration
                    if not self._is_expired(timestamp):
                        # Load into memory cache
                        size = cache_file.stat().st_size
                        self._memory_cache[key] = (doc, timestamp, size)
                        self._memory_cache.move_to_end(key)
                        self._update_stats_hit()
                        return doc
                    else:
                        # Expired - remove
                        cache_file.unlink()
                
                except Exception:
                    pass
        
        self._update_stats_miss()
        return None
    
    async def set(
        self,
        key: str,
        value: ParsedDocument,
        ttl: Optional[int] = None
    ) -> bool:
        """Set document in cache"""
        timestamp = datetime.now()
        
        # Estimate size
        size = len(pickle.dumps(value))
        
        # Check size limit and evict if needed
        await self._evict_if_needed(size)
        
        # Store in memory cache
        self._memory_cache[key] = (value, timestamp, size)
        self._memory_cache.move_to_end(key)
        self._update_stats_set(size)
        
        # Store in disk cache
        if self.enable_disk:
            try:
                cache_file = self.cache_dir / f"{key}.pkl"
                data = {
                    'document': value,
                    'timestamp': timestamp,
                }
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            except Exception:
                pass
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete document from cache"""
        existed = False
        size = 0
        
        # Delete from memory
        if key in self._memory_cache:
            _, _, size = self._memory_cache[key]
            del self._memory_cache[key]
            existed = True
        
        # Delete from disk
        if self.enable_disk:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                cache_file.unlink()
                existed = True
        
        if existed:
            self._update_stats_delete(size)
        
        return existed
    
    async def clear(self) -> int:
        """Clear all cached documents"""
        count = len(self._memory_cache)
        
        # Clear memory
        self._memory_cache.clear()
        
        # Clear disk
        if self.enable_disk:
            for cache_file in self.cache_dir.glob("doc:*.pkl"):
                cache_file.unlink()
                count += 1
        
        # Reset stats
        if self._stats:
            self._stats.item_count = 0
            self._stats.size_bytes = 0
        
        return count
    
    async def exists(self, key: str) -> bool:
        """Check if document exists in cache"""
        # Check memory
        if key in self._memory_cache:
            _, timestamp, _ = self._memory_cache[key]
            return not self._is_expired(timestamp)
        
        # Check disk
        if self.enable_disk:
            cache_file = self.cache_dir / f"{key}.pkl"
            return cache_file.exists()
        
        return False
    
    async def _evict_if_needed(self, incoming_size: int):
        """Evict entries if cache is full"""
        if not self._stats:
            return
        
        # Check if we need to evict
        while (self._stats.size_bytes + incoming_size > self.max_size_bytes and 
               self._memory_cache):
            # Evict oldest entry (LRU)
            key, (doc, timestamp, size) = self._memory_cache.popitem(last=False)
            self._update_stats_delete(size)
            self._update_stats_eviction()
            
            # Also remove from disk
            if self.enable_disk:
                cache_file = self.cache_dir / f"{key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
