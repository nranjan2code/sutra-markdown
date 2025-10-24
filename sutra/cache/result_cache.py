"""
Result Cache - Cache for conversion results

Caches final Markdown conversion results to avoid
re-conversion of the same documents.

Features:
- Disk-based storage
- Compressed storage (gzip)
- File hash-based keys
- TTL support
"""

import pickle
import gzip
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..converters.base import ConversionResult
from .base import BaseCache


class ResultCache(BaseCache):
    """
    Cache for conversion results with disk storage
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_size_mb: int = 1024,
        ttl_seconds: Optional[int] = 86400,  # 24 hours
        compress: bool = True
    ):
        """
        Initialize result cache
        
        Args:
            cache_dir: Directory for cache
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time-to-live in seconds
            compress: Use gzip compression
        """
        super().__init__(max_size_mb, ttl_seconds)
        
        self.compress = compress
        
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".sutra" / "cache" / "results"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_key(
        self,
        file_path: str,
        tier: str,
        options: Optional[dict] = None
    ) -> str:
        """Generate cache key"""
        # Include file hash + tier + options
        file_hash = self._get_file_hash(file_path)
        options_str = str(sorted(options.items())) if options else ""
        combined = f"{file_hash}:{tier}:{options_str}"
        hash_key = hashlib.md5(combined.encode()).hexdigest()
        return f"result:{hash_key}"
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get file hash"""
        try:
            stat = Path(file_path).stat()
            key = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(key.encode()).hexdigest()
        except Exception:
            return hashlib.md5(file_path.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[ConversionResult]:
        """Get result from cache"""
        cache_file = self.cache_dir / f"{key}.pkl.gz" if self.compress else self.cache_dir / f"{key}.pkl"
        
        if not cache_file.exists():
            self._update_stats_miss()
            return None
        
        try:
            if self.compress:
                with gzip.open(cache_file, 'rb') as f:
                    data = pickle.load(f)
            else:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
            
            result = data['result']
            timestamp = data['timestamp']
            
            # Check expiration
            if not self._is_expired(timestamp):
                self._update_stats_hit()
                return result
            else:
                # Expired - remove
                cache_file.unlink()
                self._update_stats_miss()
                return None
        
        except Exception:
            self._update_stats_miss()
            return None
    
    async def set(
        self,
        key: str,
        value: ConversionResult,
        ttl: Optional[int] = None
    ) -> bool:
        """Set result in cache"""
        timestamp = datetime.now()
        
        data = {
            'result': value,
            'timestamp': timestamp,
        }
        
        try:
            cache_file = self.cache_dir / f"{key}.pkl.gz" if self.compress else self.cache_dir / f"{key}.pkl"
            
            if self.compress:
                with gzip.open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            else:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            
            size = cache_file.stat().st_size
            self._update_stats_set(size)
            return True
        
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete result from cache"""
        cache_file_gz = self.cache_dir / f"{key}.pkl.gz"
        cache_file = self.cache_dir / f"{key}.pkl"
        
        existed = False
        if cache_file_gz.exists():
            cache_file_gz.unlink()
            existed = True
        if cache_file.exists():
            cache_file.unlink()
            existed = True
        
        if existed:
            self._update_stats_delete()
        
        return existed
    
    async def clear(self) -> int:
        """Clear all cached results"""
        count = 0
        
        for cache_file in self.cache_dir.glob("result:*.pkl*"):
            cache_file.unlink()
            count += 1
        
        # Reset stats
        if self._stats:
            self._stats.item_count = 0
            self._stats.size_bytes = 0
        
        return count
    
    async def exists(self, key: str) -> bool:
        """Check if result exists in cache"""
        cache_file_gz = self.cache_dir / f"{key}.pkl.gz"
        cache_file = self.cache_dir / f"{key}.pkl"
        return cache_file_gz.exists() or cache_file.exists()
